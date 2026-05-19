"""論文資料存取層（Phase 1.3+：DB-backed 最終版，無過渡相容）。

- DB（models.Paper）為論文清單唯一真實來源；不再讀寫 papers_index.json。
- 路徑一律 output/{owner_id}/{paper_uuid}/（無 legacy fallback、無 symlink）。
- owner_id 由呼叫端（web_server 從 session 解析）顯式傳入。
- 對外 paper 識別 = paper_uuid（= sanitize_paper_id 字串），URL 不變；
  paper.id（DB INT PK）僅內部。
- chat_history 仍走 JSON（Phase 1.6 才改 conversations 表），
  路徑為 output/{owner_id}/{paper_uuid}/chat_history.json。
"""
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Optional

import settings
import db
from models import User, Paper

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
    return paper_dir(output_dir, owner_id, paper_uuid) / "original.pdf"


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
    return {
        'id': p.paper_uuid,
        'title': p.title or '',
        'translated_title': p.translated_title or '',
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
                 final_paths: dict) -> None:
    """pipeline 完成時呼叫：upsert Paper row。"""
    _ensure_db()
    title, translated_title = _read_title_from_rag_tree(final_paths)
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


def cleanup_orphaned(output_dir, owner_id: int) -> list:
    """只清該 owner 目錄 output/{owner_id}/ 內、不在 DB 的殘餘論文目錄。"""
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
    return removed


# ─────────────────────── 對話紀錄（仍走 JSON；Phase 1.6 改 DB） ───────────────────────

def load_chat_history(output_dir, owner_id: int, paper_uuid: str) -> list:
    history_path = paper_dir(output_dir, owner_id, paper_uuid) / "chat_history.json"
    if not history_path.exists():
        return []
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_chat_history(output_dir, owner_id: int, paper_uuid: str,
                      messages: list) -> None:
    history_path = paper_dir(output_dir, owner_id, paper_uuid) / "chat_history.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logger.info(f"對話紀錄已儲存: owner={owner_id} {paper_uuid}")


# ─────────────────────── 向量庫 / 資源載入 ───────────────────────

def preload_vector_stores(output_dir, ai_core) -> None:
    """啟動時預載：DB 所有 status='done' 的 papers。"""
    _ensure_db()
    output_dir = Path(output_dir)
    with db.SessionLocal() as s:
        items = [
            (p.owner_id, p.paper_uuid)
            for p in s.query(Paper).filter_by(status='done').all()
        ]
    for owner_id, paper_uuid in items:
        vstore = vectors_path(output_dir, owner_id, paper_uuid)
        rtree = rag_tree_path(output_dir, owner_id, paper_uuid)
        if vstore.exists():
            ai_core.add_paper_vector_store(paper_uuid, str(vstore))
            logger.info(f"預載向量庫: {paper_uuid}")
        if rtree.exists():
            ai_core.load_paper_cache(paper_uuid, str(rtree))


def load_paper_resources(output_dir, owner_id: int, paper_uuid: str,
                          ai_core) -> None:
    _ensure_db()
    output_dir = Path(output_dir)
    vstore = vectors_path(output_dir, owner_id, paper_uuid)
    rtree = rag_tree_path(output_dir, owner_id, paper_uuid)
    if vstore.exists():
        ai_core.add_paper_vector_store(paper_uuid, str(vstore))
    if rtree.exists():
        ai_core.load_paper_cache(paper_uuid, str(rtree))
    logger.info(f"論文資源載入完成: owner={owner_id} {paper_uuid}")
