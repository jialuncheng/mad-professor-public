"""論文資料存取層（Phase 1.3+：DB-backed 最終版，無過渡相容）。

- DB（models.Paper）為論文清單唯一真實來源；不再讀寫 papers_index.json。
- 路徑一律 output/{owner_id}/{paper_uuid}/（無 legacy fallback、無 symlink）。
- owner_id 由呼叫端（web_server 從 session 解析）顯式傳入。
- 對外 paper 識別 = paper_uuid（= sanitize_paper_id 字串），URL 不變；
  paper.id（DB INT PK）僅內部。
- 對話歷史已存 conversations 表（Phase 1.6）；chat_history.json 完全廢除。
  load/save_chat_history 接收 paper.id（INT），不是 paper_uuid。
"""
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Optional

import settings
import db
from models import User, Paper, Conversation, Folder, PaperChunk

logger = logging.getLogger(__name__)


# ─────────────────────── 純函式 ───────────────────────

def sanitize_paper_id(filename: str) -> str:
    """清理檔名，產生合法的 paper_uuid（對外字串）。"""
    stem = Path(filename).stem
    paper_id = re.sub(r'[^\w\-]', '_', stem)
    paper_id = re.sub(r'_+', '_', paper_id).strip('_')
    return paper_id


def _read_title_from_rag_tree(final_paths: dict) -> tuple:
    title, translated_title = "", ""
    rag_tree = final_paths.get('rag_tree') if final_paths else None
    if rag_tree and Path(rag_tree).exists():
        try:
            with open(rag_tree, 'r', encoding='utf-8') as f:
                tree_data = json.load(f)
                title = tree_data.get('title', '')
                translated_title = tree_data.get('translated_title', '')
        except Exception as e:
            logger.error(f"讀取 rag_tree 標題失敗: {str(e)}")
    return title, translated_title


# ─────────────────────── DB / user ───────────────────────

def _ensure_db() -> None:
    try:
        db.init_db()
    except Exception as e:
        logger.error(f"init_db 失敗: {str(e)}")


def get_user_by_username(username: str):
    """回傳 (id, username) 或 None（供 web_server 解析 session）。"""
    if not username:
        return None
    _ensure_db()
    with db.SessionLocal() as s:
        u = s.query(User).filter_by(username=username).one_or_none()
        return (u.id, u.username) if u else None


def ensure_admin():
    """確保 admin user 存在，回傳 (id, username)。"""
    _ensure_db()
    with db.SessionLocal() as s:
        u = s.query(User).filter_by(username=settings.AUTH_USERNAME).one_or_none()
        if u is None:
            u = User(
                username=settings.AUTH_USERNAME,
                password_hash=settings.AUTH_PASSWORD_HASH or "",
                display_name=settings.AUTH_USERNAME,
                role="admin",
                is_active=True,
            )
            s.add(u)
            s.commit()
            logger.info(f"建立 admin user: {u.username} (id={u.id})")
        return (u.id, u.username)


# ─────────────────────── 路徑推導（唯一規範） ───────────────────────

def paper_dir(output_dir, owner_id: int, paper_uuid: str) -> Path:
    return Path(output_dir) / str(owner_id) / paper_uuid


def article_zh_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / f"final_{paper_uuid}_zh.md"


def article_en_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / f"final_{paper_uuid}_en.md"


def rag_tree_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / f"final_{paper_uuid}_rag_tree.json"


def rag_md_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / f"final_{paper_uuid}_rag.md"


def vectors_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / "vectors"


def images_path(output_dir, owner_id, paper_uuid) -> Path:
    return paper_dir(output_dir, owner_id, paper_uuid) / "images"


def original_pdf_path(output_dir, owner_id, paper_uuid) -> Path:
    """回傳論文的 PDF 路徑。

    新規範（Phase 4.7b）：檔名 = paper_uuid + .pdf（與資料夾名一致，便於辨識）。
    向後相容：若新檔名不存在但舊 original.pdf 存在，回傳舊路徑（讓既有
    DB 資料仍可讀；新建論文一律走新規範）。皆不存在 → 回新規範路徑
    （供上傳寫入用）。
    """
    dir_ = paper_dir(output_dir, owner_id, paper_uuid)
    new_path = dir_ / f"{paper_uuid}.pdf"
    old_path = dir_ / "original.pdf"
    if new_path.exists():
        return new_path
    if old_path.exists():
        return old_path
    return new_path


def _rel(output_dir, p: Path) -> str:
    try:
        return str(Path(p).relative_to(Path(output_dir)))
    except ValueError:
        return str(p)


def _paths_dict(output_dir, owner_id, paper_uuid) -> dict:
    return {
        'article_en': _rel(output_dir, article_en_path(output_dir, owner_id, paper_uuid)),
        'article_zh': _rel(output_dir, article_zh_path(output_dir, owner_id, paper_uuid)),
        'rag_md': _rel(output_dir, rag_md_path(output_dir, owner_id, paper_uuid)),
        'rag_tree': _rel(output_dir, rag_tree_path(output_dir, owner_id, paper_uuid)),
        'rag_vector_store': _rel(output_dir, vectors_path(output_dir, owner_id, paper_uuid)),
        'images': _rel(output_dir, images_path(output_dir, owner_id, paper_uuid)),
        'original_pdf': _rel(output_dir, original_pdf_path(output_dir, owner_id, paper_uuid)),
    }


# ─────────────────────── Repository ───────────────────────

def _to_dict(output_dir, p: Paper) -> dict:
    meta = None
    if p.metadata_json:
        try:
            meta = json.loads(p.metadata_json)
        except Exception:
            meta = None
    return {
        'id': p.paper_uuid,
        'title': p.title or '',
        'translated_title': p.translated_title or '',
        'folder_id': p.folder_id,
        'doc_type': p.doc_type,      # Phase 4.7c：前端 resolveDisplayTitle 判斷 resume 用
        'metadata': meta,            # Phase 4.5；舊資料/解析失敗為 None（前端 optional）
        'original_filename': p.original_filename,  # Phase 4.7a；舊資料為 None
        'paths': _paths_dict(output_dir, p.owner_id, p.paper_uuid),
    }


def list_papers(output_dir, owner_id: int) -> list:
    """該 owner 的論文清單（dict list，欄位與前端相容）。"""
    _ensure_db()
    with db.SessionLocal() as s:
        rows = (
            s.query(Paper)
            .filter_by(owner_id=owner_id)
            .order_by(Paper.id)
            .all()
        )
        return [_to_dict(output_dir, p) for p in rows]


def get_paper(output_dir, owner_id: int, paper_uuid: str) -> Optional[dict]:
    _ensure_db()
    with db.SessionLocal() as s:
        p = s.query(Paper).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).one_or_none()
        return _to_dict(output_dir, p) if p else None


def paper_exists(owner_id: int, paper_uuid: str) -> bool:
    _ensure_db()
    with db.SessionLocal() as s:
        return s.query(Paper.id).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).first() is not None


def upsert_paper(output_dir, owner_id: int, paper_uuid: str,
                 final_paths: dict, metadata: Optional[dict] = None,
                 domain: Optional[str] = None,
                 doc_type: Optional[str] = None,
                 original_filename: Optional[str] = None) -> None:
    """pipeline 完成時呼叫：upsert Paper row。

    Phase 4.5：title 來源改為 metadata（fallback 鏈 metadata→rag_tree→paper_uuid，
    見 metadata_extractor.resolve_title），不破壞既有行為（metadata=None 時等同舊
    版以 rag_tree 為準）。metadata 整包存 metadata_json，title/translated_title
    同步鏡寫既有欄位以相容 _to_dict / 列表 / 排序。

    domain / doc_type 由 pipeline_core 從 output_paths 帶入（_domain /
    _confirmed_doc_type）；None 或空字串視為「未提供」，create 時不寫、update
    時不覆蓋既有值（避免一次失敗的 detect_domain 清掉先前正確的 domain）。

    original_filename（Phase 4.7a）：使用者上傳的原始檔名（未 sanitize）；
    同 domain/doc_type 的空值不覆蓋策略。
    """
    _ensure_db()
    rt_title, rt_tt = _read_title_from_rag_tree(final_paths)
    from processor.metadata_extractor import resolve_title  # 延遲 import 避免循環
    title = resolve_title(metadata, final_paths.get('rag_tree'), paper_uuid,
                          original_filename=original_filename)
    if not title:                       # resolve_title 理論上不會空，雙保險
        title = rt_title or paper_uuid
    m_tt = (metadata.get('translated_title', {}).get('value')
            if metadata else None)
    translated_title = m_tt or rt_tt or ''
    meta_json = None
    if metadata is not None:
        try:
            meta_json = json.dumps(metadata, ensure_ascii=False)
        except Exception:
            meta_json = None
    domain_val = (domain or '').strip() or None
    doc_type_val = (doc_type or '').strip() or None
    orig_fn_val = (original_filename or '').strip() or None
    with db.SessionLocal() as s:
        p = s.query(Paper).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).one_or_none()
        if p is None:
            p = Paper(
                owner_id=owner_id,
                paper_uuid=paper_uuid,
                title=title,
                translated_title=translated_title,
                domain=domain_val,
                doc_type=doc_type_val,
                status='done',
                metadata_json=meta_json,
                original_filename=orig_fn_val,
            )
            s.add(p)
        else:
            if title:
                p.title = title
            if translated_title:
                p.translated_title = translated_title
            if domain_val:
                p.domain = domain_val
            if doc_type_val:
                p.doc_type = doc_type_val
            if orig_fn_val:
                p.original_filename = orig_fn_val
            if meta_json is not None:
                p.metadata_json = meta_json
            p.status = 'done'
        s.commit()
    logger.info(f"papers DB 更新完成: owner={owner_id} {paper_uuid}")


def delete_paper(output_dir, owner_id: int, paper_uuid: str) -> bool:
    """刪 DB row（cascade conversations）+ 實體目錄。"""
    _ensure_db()
    with db.SessionLocal() as s:
        p = s.query(Paper).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).one_or_none()
        if p is not None:
            s.delete(p)
            s.commit()
    d = paper_dir(output_dir, owner_id, paper_uuid)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    logger.info(f"論文已刪除: owner={owner_id} {paper_uuid}")
    return True


def cleanup_orphaned(output_dir, owner_id: int, ai_core=None) -> list:
    """只清該 owner 目錄 output/{owner_id}/ 內、不在 DB 的殘餘論文目錄。

    Phase 4.7d Commit 9：同步清記憶體 cache（避免「鬼魂 paper」）。
    若 ai_core 傳入，呼叫 ai_core.remove_paper(owner_id, paper_uuid)
    清 _paper_cache + retriever 三個 dict（vector_stores /
    paper_vector_paths / rag_trees）。processing_tasks 由 caller 負責清。
    """
    _ensure_db()
    output_dir = Path(output_dir)
    owner_root = output_dir / str(owner_id)
    if not owner_root.is_dir():
        return []
    with db.SessionLocal() as s:
        valid = {
            u for (u,) in s.query(Paper.paper_uuid).filter_by(owner_id=owner_id).all()
        }
    removed = []
    for item in owner_root.iterdir():
        if item.is_dir() and item.name not in valid:
            shutil.rmtree(item, ignore_errors=True)
            removed.append(item.name)
            logger.info(f"清理殘餘目錄: {owner_id}/{item.name}")
            # 同步清記憶體 cache（避免鬼魂 paper：檔案刪了但 ai_core /
            # retriever 仍記得、後續查詢炸或給亂結果）
            if ai_core is not None:
                try:
                    ai_core.remove_paper(owner_id, item.name)
                    logger.info(
                        f"清理殘檔 cache 完成: owner={owner_id} {item.name}"
                    )
                except Exception as e:
                    logger.warning(
                        f"清理殘檔 cache 失敗（soft，忽略）: "
                        f"owner={owner_id} {item.name} - {e}"
                    )
    return removed


# ─────────────────────── 對話紀錄（conversations 表，Phase 1.6） ───────────────────────

def get_paper_db_id(owner_id: int, paper_uuid: str) -> Optional[int]:
    """由 (owner_id, paper_uuid) 取 Paper.id（INT PK）；無則 None。"""
    _ensure_db()
    with db.SessionLocal() as s:
        row = s.query(Paper.id).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).one_or_none()
        return row[0] if row else None


def load_chat_history(paper_db_id: int, user_id: int) -> list:
    """讀該 paper 的對話（依 id 順序＝寫入順序）。

    回傳 list[{role, content, grounding_sources?, created_at}]。
    grounding_sources 僅在非空時附帶；created_at 為 ISO 字串。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        rows = (
            s.query(Conversation)
            .filter_by(paper_id=paper_db_id)
            .order_by(Conversation.id)
            .all()
        )
        out = []
        for c in rows:
            item = {"role": c.role, "content": c.content}
            if c.grounding_sources:
                item["grounding_sources"] = c.grounding_sources
            if c.created_at is not None:
                item["created_at"] = c.created_at.isoformat()
            out.append(item)
        return out


def append_chat_message(paper_db_id: int, user_id: int, role: str,
                         content: str, grounding_sources=None) -> int:
    """新增單筆對話、回傳 conversation.id。

    Phase 4.7d Commit 17-1：取代 save_chat_history 整包覆寫的依賴。
    順序 = 插入序 = id 序（既有 load_chat_history 依 id 排序）。
    後端 chat endpoint 進入時寫 user query、stream 結束時寫 assistant
    完整回答，不再靠前端 saveChatHistory 整包 POST（解切走切回 bug）。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        c = Conversation(
            paper_id=paper_db_id, user_id=user_id, role=role,
            content=content, grounding_sources=grounding_sources or None,
        )
        s.add(c)
        s.commit()
        cid = c.id
    logger.info(
        f"對話訊息已 append: paper_id={paper_db_id} role={role} "
        f"len={len(content)} id={cid}"
    )
    return cid


def save_chat_history(paper_db_id: int, user_id: int, history: list) -> None:
    """整包覆寫：刪該 paper 既有 conversations，再批次 insert。

    history 每筆 dict 可選帶 grounding_sources（list）。寫入順序＝id 順序。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        s.query(Conversation).filter_by(paper_id=paper_db_id).delete()
        for m in history or []:
            if not isinstance(m, dict):
                continue
            gs = m.get("grounding_sources")
            s.add(Conversation(
                paper_id=paper_db_id,
                user_id=user_id,
                role=m.get("role", "user"),
                content=m.get("content", ""),
                grounding_sources=gs if gs else None,
            ))
        s.commit()
    logger.info(f"對話紀錄已儲存: paper_id={paper_db_id}（{len(history or [])} 則）")


def delete_conversations(paper_db_id: int) -> None:
    """刪除該 paper 的所有對話（刪 paper 時 DB 已 cascade，此為顯式輔助）。"""
    _ensure_db()
    with db.SessionLocal() as s:
        s.query(Conversation).filter_by(paper_id=paper_db_id).delete()
        s.commit()


# ─────────────────────── 向量庫 / 資源載入 ───────────────────────

def preload_vector_stores(output_dir, ai_core) -> None:
    """啟動時預載：DB 所有 status='done' 的 papers。"""
    _ensure_db()
    output_dir = Path(output_dir)
    with db.SessionLocal() as s:
        items = [
            (p.owner_id, p.paper_uuid, p.domain)
            for p in s.query(Paper).filter_by(status='done').all()
        ]
    for owner_id, paper_uuid, domain in items:
        vstore = vectors_path(output_dir, owner_id, paper_uuid)
        rtree = rag_tree_path(output_dir, owner_id, paper_uuid)
        if vstore.exists():
            ai_core.add_paper_vector_store(owner_id, paper_uuid, str(vstore))
            logger.info(f"預載向量庫: owner={owner_id} {paper_uuid}")
        if rtree.exists():
            ai_core.load_paper_cache(owner_id, paper_uuid, str(rtree))
            # 注入 domain 到 ai_core 的 paper_cache（沿用 translate_processor:233-235 範式）
            cache = ai_core._paper_cache.get((owner_id, paper_uuid))
            if cache is not None and domain:
                cache['_domain'] = domain


def load_paper_resources(output_dir, owner_id: int, paper_uuid: str,
                          ai_core) -> None:
    _ensure_db()
    output_dir = Path(output_dir)
    vstore = vectors_path(output_dir, owner_id, paper_uuid)
    rtree = rag_tree_path(output_dir, owner_id, paper_uuid)
    if vstore.exists():
        ai_core.add_paper_vector_store(owner_id, paper_uuid, str(vstore))
    if rtree.exists():
        ai_core.load_paper_cache(owner_id, paper_uuid, str(rtree))
        # 注入 domain 到 ai_core 的 paper_cache（沿用 translate_processor:233-235 範式）
        with db.SessionLocal() as s:
            row = s.query(Paper.domain).filter_by(
                owner_id=owner_id, paper_uuid=paper_uuid
            ).one_or_none()
            domain = row[0] if row else None
        cache = ai_core._paper_cache.get((owner_id, paper_uuid))
        if cache is not None and domain:
            cache['_domain'] = domain
    logger.info(f"論文資源載入完成: owner={owner_id} {paper_uuid}")


# ─────────────────────── 資料夾（Phase 3.1） ───────────────────────
# 注意：以下函式接收外部傳入的 SQLAlchemy session（與 web_server 端點共用一個
# session/交易），mutation 內部 commit；唯讀函式不 commit。owner_id 一律由
# 呼叫端（session 解析）顯式提供，跨 owner 視為不存在。

UNSET = object()  # PATCH sentinel：區分「未提供」vs「設為 None」
MAX_FOLDER_DEPTH = 5
MAX_FOLDER_NAME = 50


def _folder_to_dict(f: Folder) -> dict:
    return {
        'id': f.id,
        'name': f.name,
        'parent_id': f.parent_id,
        'sort_order': f.sort_order,
        'created_at': f.created_at.isoformat() if f.created_at is not None else None,
    }


def _get_folder_row(session, owner_id: int, folder_id: int):
    return session.query(Folder).filter_by(
        id=folder_id, owner_id=owner_id
    ).one_or_none()


def _folder_depth(session, owner_id: int, folder_id) -> int:
    """folder_id 該資料夾自身的深度（root=1）；folder_id None → 0。"""
    depth = 0
    pid = folder_id
    seen = set()
    while pid is not None and pid not in seen:
        seen.add(pid)
        f = _get_folder_row(session, owner_id, pid)
        if f is None:
            break
        depth += 1
        pid = f.parent_id
    return depth


def _descendant_ids(session, owner_id: int, folder_id: int) -> set:
    """folder_id 自身 + 所有子孫 id（防環用）。"""
    result = {folder_id}
    stack = [folder_id]
    while stack:
        cur = stack.pop()
        for (cid,) in session.query(Folder.id).filter_by(
            owner_id=owner_id, parent_id=cur
        ).all():
            if cid not in result:
                result.add(cid)
                stack.append(cid)
    return result


def _check_name(name: str) -> str:
    n = (name or "").strip()
    if not (1 <= len(n) <= MAX_FOLDER_NAME):
        raise ValueError(f"資料夾名稱需 1–{MAX_FOLDER_NAME} 字元")
    return n


def _check_sibling_dup(session, owner_id, parent_id, name, exclude_id=None):
    q = session.query(Folder.id).filter_by(
        owner_id=owner_id, parent_id=parent_id, name=name
    )
    if exclude_id is not None:
        q = q.filter(Folder.id != exclude_id)
    if q.first() is not None:
        raise ValueError(f"同層已存在同名資料夾「{name}」")


def list_folders(session, owner_id: int) -> list:
    """flat list（前端自行建樹）；依 parent_id、sort_order、id 排序。"""
    rows = (
        session.query(Folder)
        .filter_by(owner_id=owner_id)
        .order_by(Folder.parent_id.asc().nullsfirst(),
                  Folder.sort_order.asc(), Folder.id.asc())
        .all()
    )
    return [_folder_to_dict(f) for f in rows]


def get_folder(session, owner_id: int, folder_id: int):
    """單一資料夾（owner 不符回 None）。"""
    return _get_folder_row(session, owner_id, folder_id)


def create_folder(session, owner_id: int, name: str,
                   parent_id=None) -> Folder:
    name = _check_name(name)
    if parent_id is not None:
        parent = _get_folder_row(session, owner_id, parent_id)
        if parent is None:
            raise ValueError("上層資料夾不存在")
    new_depth = _folder_depth(session, owner_id, parent_id) + 1
    if new_depth > MAX_FOLDER_DEPTH:
        raise ValueError(f"資料夾巢狀深度上限為 {MAX_FOLDER_DEPTH} 層")
    _check_sibling_dup(session, owner_id, parent_id, name)
    f = Folder(owner_id=owner_id, name=name, parent_id=parent_id, sort_order=0)
    session.add(f)
    session.commit()
    logger.info(f"建立資料夾: owner={owner_id} id={f.id} {name}")
    return f


def update_folder(session, owner_id: int, folder_id: int,
                   name=None, parent_id=UNSET, sort_order=None) -> Folder:
    f = _get_folder_row(session, owner_id, folder_id)
    if f is None:
        raise ValueError("資料夾不存在")

    new_name = f.name if name is None else _check_name(name)
    new_parent = f.parent_id if parent_id is UNSET else parent_id

    if parent_id is not UNSET and new_parent is not None:
        if new_parent == folder_id:
            raise ValueError("不可將資料夾移到自己底下")
        parent = _get_folder_row(session, owner_id, new_parent)
        if parent is None:
            raise ValueError("目標上層資料夾不存在")
        if new_parent in _descendant_ids(session, owner_id, folder_id):
            raise ValueError("不可將資料夾移到自己的子孫底下")
        # 深度：新位置（父深度 + 自身子樹高度）不可超限
        sub = _descendant_ids(session, owner_id, folder_id)
        max_rel = 0
        for sid in sub:
            d = _folder_depth(session, owner_id, sid)
            base = _folder_depth(session, owner_id, folder_id)
            max_rel = max(max_rel, d - base)
        if _folder_depth(session, owner_id, new_parent) + 1 + max_rel > MAX_FOLDER_DEPTH:
            raise ValueError(f"移動後巢狀深度將超過 {MAX_FOLDER_DEPTH} 層")

    if new_name != f.name or new_parent != f.parent_id:
        _check_sibling_dup(session, owner_id, new_parent, new_name,
                           exclude_id=folder_id)

    f.name = new_name
    if parent_id is not UNSET:
        f.parent_id = new_parent
    if sort_order is not None:
        f.sort_order = sort_order
    session.commit()
    logger.info(f"更新資料夾: owner={owner_id} id={folder_id}")
    return f


def delete_folder(session, owner_id: int, folder_id: int) -> int:
    """刪除資料夾。子資料夾 DB CASCADE、論文 folder_id DB SET NULL。

    回傳被刪除的資料夾數（自身 + 子孫）。
    """
    f = _get_folder_row(session, owner_id, folder_id)
    if f is None:
        raise ValueError("資料夾不存在")
    removed = len(_descendant_ids(session, owner_id, folder_id))
    session.delete(f)
    session.commit()
    logger.info(f"刪除資料夾: owner={owner_id} id={folder_id}（含子共 {removed} 個）")
    return removed


def set_paper_folder(session, owner_id: int, paper_uuid: str,
                     folder_id):
    """把論文移到某資料夾（folder_id=None → 未分類/根）。回傳更新後 Paper。"""
    p = session.query(Paper).filter_by(
        owner_id=owner_id, paper_uuid=paper_uuid
    ).one_or_none()
    if p is None:
        raise ValueError("論文不存在")
    if folder_id is not None:
        if _get_folder_row(session, owner_id, folder_id) is None:
            raise ValueError("目標資料夾不存在")
    p.folder_id = folder_id
    session.commit()
    logger.info(f"論文歸檔: owner={owner_id} {paper_uuid} → folder={folder_id}")
    return p


# ─────────────────── MODEL-8 C1: paper_chunks DAL helper ───────────────────
# 依 plan §3.1（含修正 3 移除 tiling_method、修正 5 不重做 get_paper_db_id）
# 詳見 .claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md §3.1

def replace_paper_chunks(paper_db_id: int, chunks: list) -> int:
    """覆寫式批次 INSERT：清掉舊 chunks、批量寫入新的。

    依 plan §3.1 + db_analysis §4 效能要求（< 50ms/千筆 chunks）。

    Args:
        paper_db_id: Paper.id（INT PK）、不是 paper_uuid
        chunks: list of dict、每筆含
            chunk_index, chunk_key, raw_text, translated_text, doc_type,
            metadata_json (JSON 字串),
            embedding_model, output_dimensions, chunk_filter_version
            （修正 3：無 tiling_method 欄位）

    Returns:
        寫入筆數
    """
    _ensure_db()
    with db.SessionLocal() as s:
        s.query(PaperChunk).filter_by(paper_id=paper_db_id).delete()
        if chunks:
            from sqlalchemy import insert
            s.execute(insert(PaperChunk), [
                {**c, "paper_id": paper_db_id} for c in chunks
            ])
        s.commit()
    return len(chunks)


def iter_paper_chunks(paper_db_id: int):
    """逐 chunk 讀取（regen 用）、yield dict（含 raw_text + metadata_json）。

    依 plan §3.1：依 chunk_index 升序回。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        rows = (
            s.query(PaperChunk)
            .filter_by(paper_id=paper_db_id)
            .order_by(PaperChunk.chunk_index)
            .all()
        )
        for c in rows:
            yield {
                "chunk_index": c.chunk_index,
                "chunk_key": c.chunk_key,
                "raw_text": c.raw_text,
                "translated_text": c.translated_text,
                "doc_type": c.doc_type,
                "metadata_json": c.metadata_json,
                "embedding_model": c.embedding_model,
                "output_dimensions": c.output_dimensions,
                "chunk_filter_version": c.chunk_filter_version,
            }


def list_papers_with_chunks(owner_id: Optional[int] = None) -> list:
    """掃所有有 paper_chunks 的 paper、供 regen_rag --check 用。

    依 plan §3.1：JOIN papers + paper_chunks、回 distinct paper × embedding model。

    Returns:
        list of dict: paper_db_id / owner_id / paper_uuid / embedding_model / output_dimensions
    """
    _ensure_db()
    with db.SessionLocal() as s:
        q = (
            s.query(
                Paper.id, Paper.owner_id, Paper.paper_uuid,
                PaperChunk.embedding_model, PaperChunk.output_dimensions,
            )
            .join(PaperChunk, PaperChunk.paper_id == Paper.id)
            .distinct()
        )
        if owner_id is not None:
            q = q.filter(Paper.owner_id == owner_id)
        return [
            {
                "paper_db_id": r[0],
                "owner_id": r[1],
                "paper_uuid": r[2],
                "embedding_model": r[3],
                "output_dimensions": r[4],
            }
            for r in q.all()
        ]
