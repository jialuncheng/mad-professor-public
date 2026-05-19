"""論文資料存取層（Phase 1.2：改為 DB-backed）。

對外函式簽名與舊版相容，讓 web_server / pipeline_core / ai_core 在
Phase 1.3-1.5 之前不需修改：
  - sanitize_paper_id(filename) -> str            （純函式，不變）
  - load_papers_index(output_dir) -> list[dict]   （改查 DB，dict 結構與舊版相容）
  - update_papers_index(output_dir, paper_id, final_paths) -> None  （改為 upsert DB）
  - delete_paper(output_dir, paper_id) -> bool    （DB row + 檔案目錄）
  - load_chat_history(output_dir, paper_id) -> list（仍走 JSON；Phase 1.6 改 DB）
  - save_chat_history(output_dir, paper_id, messages) -> None（仍走 JSON）
  - preload_vector_stores(output_dir, ai_core) -> None（改查 DB）
  - load_paper_resources(output_dir, paper_id, final_paths, ai_core) -> None

設計：
  - DB（models.Paper）為論文清單的唯一真實來源，不再讀寫 papers_index.json
  - 路徑由 (owner_id, paper_uuid) 推導；相容兩種實體位置：
      * 已遷移： output/{owner_id}/{paper_uuid}/
      * 新上傳： output/{paper_uuid}/（pipeline_core 未改，仍寫此處）
  - Phase 1.2 尚未接 session，owner 一律用 admin（settings.AUTH_USERNAME）
  - 對外 paper_id == paper_uuid（= 舊 paper_id 字串），URL 不變；
    paper.id（DB INT PK）僅內部使用

⚠ 過渡相容 symlink（Phase 1.2 → 1.3 暫時措施）：
  web_server 的 content/image/save-history/cleanup 端點仍硬編
  OUTPUT_DIR/{paper_uuid}/...（Phase 1.3 才改）。為讓已遷移論文
  （實體在 output/{owner_id}/{paper_uuid}）仍能被這些端點讀到，
  本模組在 preload / load_paper_resources / update_papers_index 時
  建立相對 symlink  output/{paper_uuid} -> {owner_id}/{paper_uuid}。
  Phase 1.3 改完 web_server 路徑後應移除此 symlink 機制。
"""
import os
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Optional

import settings
import db
from models import User, Paper, Conversation

logger = logging.getLogger(__name__)


# ─────────────────────── 純函式（不變） ───────────────────────

def sanitize_paper_id(filename: str) -> str:
    """清理檔名，產生合法的 paper_id（= paper_uuid，對外字串）。"""
    stem = Path(filename).stem
    paper_id = re.sub(r'[^\w\-]', '_', stem)
    paper_id = re.sub(r'_+', '_', paper_id).strip('_')
    return paper_id


def _read_title_from_rag_tree(final_paths: dict) -> tuple:
    """從 rag_tree 讀取標題（與舊版行為一致）。"""
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


# ─────────────────────── DB / owner 輔助 ───────────────────────

def _ensure_db() -> None:
    """確保資料表存在（idempotent；Phase 1.1 遷移通常已建立）。"""
    try:
        db.init_db()
    except Exception as e:
        logger.error(f"init_db 失敗: {str(e)}")


def _get_admin(session) -> User:
    """取得（或建立）預設 owner = admin。Phase 1.3 接 session 後改為依登入者。"""
    admin = session.query(User).filter_by(
        username=settings.AUTH_USERNAME
    ).one_or_none()
    if admin is None:
        admin = User(
            username=settings.AUTH_USERNAME,
            password_hash=settings.AUTH_PASSWORD_HASH or "",
            display_name=settings.AUTH_USERNAME,
            role="admin",
            is_active=True,
        )
        session.add(admin)
        session.commit()
        logger.info(f"建立 admin user: {admin.username} (id={admin.id})")
    return admin


# ─────────────────────── 路徑推導 ───────────────────────

def paper_dir(output_dir: Path, owner_id: int, paper_uuid: str) -> Path:
    """論文實體目錄；相容已遷移(output/{owner}/{uuid}) 與新上傳(output/{uuid})。"""
    output_dir = Path(output_dir)
    owned = output_dir / str(owner_id) / paper_uuid
    if owned.exists():
        return owned
    legacy = output_dir / paper_uuid
    if legacy.exists():
        return legacy
    # 皆不存在：回傳 owner 規範路徑（未來標準）
    return owned


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
    return paper_dir(output_dir, owner_id, paper_uuid) / "original.pdf"


def _rel(output_dir: Path, p: Path) -> str:
    """回傳相對 output_dir 的字串（與舊 papers_index paths 格式一致）。"""
    try:
        return str(Path(p).relative_to(Path(output_dir)))
    except ValueError:
        return str(p)


def _paths_dict(output_dir: Path, owner_id: int, paper_uuid: str) -> dict:
    """組舊版 papers_index 相容的 paths（相對字串）。"""
    return {
        'article_en': _rel(output_dir, article_en_path(output_dir, owner_id, paper_uuid)),
        'article_zh': _rel(output_dir, article_zh_path(output_dir, owner_id, paper_uuid)),
        'rag_md': _rel(output_dir, rag_md_path(output_dir, owner_id, paper_uuid)),
        'rag_tree': _rel(output_dir, rag_tree_path(output_dir, owner_id, paper_uuid)),
        'rag_vector_store': _rel(output_dir, vectors_path(output_dir, owner_id, paper_uuid)),
        'images': _rel(output_dir, images_path(output_dir, owner_id, paper_uuid)),
        'original_pdf': _rel(output_dir, original_pdf_path(output_dir, owner_id, paper_uuid)),
    }


def _ensure_legacy_link(output_dir: Path, owner_id: int, paper_uuid: str) -> None:
    """⚠ 過渡：若實體在 output/{owner}/{uuid}，建相對 symlink output/{uuid}。

    讓 Phase 1.3 之前仍硬編 OUTPUT_DIR/{paper_uuid} 的 web_server 端點可運作。
    新上傳（實體就在 output/{uuid}）不需要、也不會建立。
    """
    output_dir = Path(output_dir)
    owned = output_dir / str(owner_id) / paper_uuid
    legacy = output_dir / paper_uuid
    if not owned.is_dir():
        return
    if legacy.exists() or legacy.is_symlink():
        return
    try:
        os.symlink(Path(str(owner_id)) / paper_uuid, legacy, target_is_directory=True)
        logger.info(f"建立相容 symlink: output/{paper_uuid} -> {owner_id}/{paper_uuid}")
    except OSError as e:
        logger.warning(f"建立相容 symlink 失敗（{paper_uuid}）: {str(e)}；"
                       f"此論文內容端點在 Phase 1.3 前可能無法載入")


# ─────────────────────── Repository ───────────────────────

def _paper_to_dict(output_dir: Path, p: Paper) -> dict:
    """轉為與舊 papers_index 相容的 dict（id=paper_uuid 對外字串）。"""
    return {
        'id': p.paper_uuid,
        'title': p.title or '',
        'translated_title': p.translated_title or '',
        'paths': _paths_dict(output_dir, p.owner_id, p.paper_uuid),
    }


def list_papers(output_dir: Path, owner_id: Optional[int] = None) -> list:
    """列出論文（dict list，與舊 load_papers_index 結構相容）。

    owner_id=None → 預設 admin（Phase 1.3 接 session 後改為依登入者）。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        if owner_id is None:
            owner_id = _get_admin(s).id
        rows = (
            s.query(Paper)
            .filter_by(owner_id=owner_id)
            .order_by(Paper.id)
            .all()
        )
        return [_paper_to_dict(output_dir, p) for p in rows]


def get_paper(output_dir: Path, paper_uuid: str,
              owner_id: Optional[int] = None) -> Optional[dict]:
    _ensure_db()
    with db.SessionLocal() as s:
        if owner_id is None:
            owner_id = _get_admin(s).id
        p = s.query(Paper).filter_by(
            owner_id=owner_id, paper_uuid=paper_uuid
        ).one_or_none()
        return _paper_to_dict(output_dir, p) if p else None


def load_papers_index(output_dir: Path) -> list:
    """[相容 API] 舊名；現由 DB 回傳 list[dict]。"""
    return list_papers(output_dir)


def update_papers_index(output_dir: Path, paper_id: str, final_paths: dict) -> None:
    """[相容 API] pipeline 完成時呼叫：upsert Paper row（取代 papers_index.json）。"""
    _ensure_db()
    title, translated_title = _read_title_from_rag_tree(final_paths)
    with db.SessionLocal() as s:
        owner = _get_admin(s)
        p = s.query(Paper).filter_by(
            owner_id=owner.id, paper_uuid=paper_id
        ).one_or_none()
        if p is None:
            p = Paper(
                owner_id=owner.id,
                paper_uuid=paper_id,
                title=title,
                translated_title=translated_title,
                status='done',
            )
            s.add(p)
        else:
            if title:
                p.title = title
            if translated_title:
                p.translated_title = translated_title
            p.status = 'done'
        s.commit()
        owner_id = owner.id
    _ensure_legacy_link(output_dir, owner_id, paper_id)
    logger.info(f"papers DB 更新完成: {paper_id}")


def delete_paper(output_dir: Path, paper_id: str) -> bool:
    """[相容 API] 刪 DB row（cascade conversations）+ 實體目錄 + 相容 symlink。"""
    _ensure_db()
    output_dir = Path(output_dir)
    with db.SessionLocal() as s:
        owner = _get_admin(s)
        p = s.query(Paper).filter_by(
            owner_id=owner.id, paper_uuid=paper_id
        ).one_or_none()
        owner_id = owner.id
        if p is not None:
            s.delete(p)  # conversations 由 ORM cascade/DB ON DELETE 處理
            s.commit()

    real = paper_dir(output_dir, owner_id, paper_id)
    legacy = output_dir / paper_id
    # 先移除相容 symlink（若 legacy 是 symlink 且不是 real 本身）
    if legacy.is_symlink():
        try:
            legacy.unlink()
        except OSError as e:
            logger.warning(f"移除 symlink 失敗 {paper_id}: {str(e)}")
    if real.exists() and not real.is_symlink():
        shutil.rmtree(real, ignore_errors=True)
    logger.info(f"論文已刪除: {paper_id}")
    return True


# ─────────────────────── 對話紀錄（Phase 1.2 仍走 JSON） ───────────────────────
# NOTE: Phase 1.6 才改為寫 conversations 表；此處僅把路徑改成新位置。

def _chat_history_file(output_dir: Path, paper_id: str) -> Path:
    _ensure_db()
    with db.SessionLocal() as s:
        owner = _get_admin(s)
        owner_id = owner.id
    return paper_dir(output_dir, owner_id, paper_id) / "chat_history.json"


def load_chat_history(output_dir: Path, paper_id: str) -> list:
    """[相容 API] 仍走 JSON；路徑改 output/{owner_id}/{paper_uuid}/chat_history.json。"""
    history_path = _chat_history_file(output_dir, paper_id)
    if not history_path.exists():
        return []
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_chat_history(output_dir: Path, paper_id: str, messages: list) -> None:
    """[相容 API] 仍走 JSON；路徑改新位置。"""
    history_path = _chat_history_file(output_dir, paper_id)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logger.info(f"對話紀錄已儲存: {paper_id}")


# ─────────────────────── 向量庫 / 資源載入 ───────────────────────

def preload_vector_stores(output_dir: Path, ai_core) -> None:
    """[相容 API] 啟動時預載：改查 DB 所有 status='done' 的 papers。"""
    _ensure_db()
    output_dir = Path(output_dir)
    with db.SessionLocal() as s:
        rows = s.query(Paper).filter_by(status='done').all()
        items = [(p.owner_id, p.paper_uuid) for p in rows]

    for owner_id, paper_uuid in items:
        _ensure_legacy_link(output_dir, owner_id, paper_uuid)
        vstore = vectors_path(output_dir, owner_id, paper_uuid)
        rtree = rag_tree_path(output_dir, owner_id, paper_uuid)
        if vstore.exists():
            ai_core.add_paper_vector_store(paper_uuid, str(vstore))
            logger.info(f"預載向量庫: {paper_uuid}")
        if rtree.exists():
            ai_core.load_paper_cache(paper_uuid, str(rtree))


def load_paper_resources(output_dir: Path, paper_id: str,
                          final_paths: dict, ai_core) -> None:
    """[相容 API] 處理完成後載入向量庫與快取（路徑由 DB owner + uuid 推導）。"""
    _ensure_db()
    output_dir = Path(output_dir)
    with db.SessionLocal() as s:
        owner = _get_admin(s)
        owner_id = owner.id

    _ensure_legacy_link(output_dir, owner_id, paper_id)
    vstore = vectors_path(output_dir, owner_id, paper_id)
    rtree = rag_tree_path(output_dir, owner_id, paper_id)

    if vstore.exists():
        ai_core.add_paper_vector_store(paper_id, str(vstore))
    if rtree.exists():
        ai_core.load_paper_cache(paper_id, str(rtree))
    logger.info(f"論文資源載入完成: {paper_id}")
