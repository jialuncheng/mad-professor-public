"""一次性遷移：papers_index.json + chat_history.json → SQLite DB。

Phase 0 提供但**不自動執行**；Phase 1 第一步才正式跑。

用法：
    python scripts/migrate_to_db.py --dry-run     # 只報告計畫，不寫入、不搬檔
    python scripts/migrate_to_db.py               # 正式遷移（idempotent，可重跑）
    python scripts/migrate_to_db.py --rollback    # 還原：目錄搬回 + 刪 .db

行為：
- admin user 取自 settings.AUTH_USERNAME / AUTH_PASSWORD_HASH（role=admin）
- 每筆 papers_index entry → papers（owner=admin, paper_uuid=舊 id, status=done）
- 每篇 chat_history.json → conversations（grounding_sources=NULL，舊資料無此欄）
- output/{id}/ → output/{admin_id}/{id}/
- idempotent：以唯一鍵 get-or-create，已遷移者略過
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import settings  # noqa: E402

OUTPUT_DIR = ROOT / "output"
PAPERS_INDEX = OUTPUT_DIR / "papers_index.json"


def _log(msg: str) -> None:
    print(f"[migrate] {msg}")


def _mtime(path: Path):
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(
            tzinfo=None
        )
    except OSError:
        return datetime.utcnow()


def _load_index() -> list:
    if not PAPERS_INDEX.exists():
        return []
    try:
        return json.loads(PAPERS_INDEX.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _resolve_paper_src(paper_uuid: str, admin_id) -> Path | None:
    """回傳此 paper 目前實際所在目錄（未遷移 = output/{id}；已遷移 = output/{admin_id}/{id}）。"""
    legacy = OUTPUT_DIR / paper_uuid
    if legacy.is_dir():
        return legacy
    if admin_id is not None:
        moved = OUTPUT_DIR / str(admin_id) / paper_uuid
        if moved.is_dir():
            return moved
    return None


def do_dry_run() -> int:
    index = _load_index()
    total_conv = 0
    for entry in index:
        pid = entry.get("id")
        src = OUTPUT_DIR / str(pid)
        hist = src / "chat_history.json"
        if hist.exists():
            try:
                total_conv += len(json.loads(hist.read_text(encoding="utf-8")) or [])
            except (json.JSONDecodeError, OSError):
                pass
    _log("=== DRY RUN（不寫入、不搬檔）===")
    _log(f"admin user：{settings.AUTH_USERNAME}"
         f"{'（警告：AUTH_PASSWORD_HASH 為空）' if not settings.AUTH_PASSWORD_HASH else ''}")
    _log(f"papers 待建立：{len(index)} 筆")
    _log(f"conversations 待建立：約 {total_conv} 則（grounding_sources=NULL）")
    _log(f"目錄搬移：output/<id>/ → output/<admin_id>/<id>/（{len(index)} 個）")
    _log("未做任何變更。")
    return 0


def do_migrate() -> int:
    import db
    from models import Conversation, Paper, User

    db.init_db()
    index = _load_index()

    with db.SessionLocal() as s:
        admin = s.query(User).filter_by(username=settings.AUTH_USERNAME).one_or_none()
        if admin is None:
            admin = User(
                username=settings.AUTH_USERNAME,
                password_hash=settings.AUTH_PASSWORD_HASH or "",
                display_name=settings.AUTH_USERNAME,
                role="admin",
                is_active=True,
            )
            s.add(admin)
            s.commit()
            _log(f"建立 admin user：{admin.username} (id={admin.id})")
        else:
            _log(f"admin user 已存在：{admin.username} (id={admin.id})")
        admin_id = admin.id

        owner_root = OUTPUT_DIR / str(admin_id)
        owner_root.mkdir(parents=True, exist_ok=True)

        for entry in index:
            pid = str(entry.get("id"))
            paper = (
                s.query(Paper)
                .filter_by(owner_id=admin_id, paper_uuid=pid)
                .one_or_none()
            )
            src = _resolve_paper_src(pid, admin_id)
            ts = _mtime(src) if src else datetime.utcnow()
            if paper is None:
                paper = Paper(
                    owner_id=admin_id,
                    paper_uuid=pid,
                    title=entry.get("title"),
                    translated_title=entry.get("translated_title"),
                    domain=None,
                    doc_type=None,
                    status="done",
                    created_at=ts,
                    updated_at=ts,
                    ready_for_reading_at=ts,
                    ready_for_chat_at=ts,
                )
                s.add(paper)
                s.commit()
                _log(f"建立 paper：{pid} (id={paper.id})")
            else:
                _log(f"paper 已存在，略過：{pid} (id={paper.id})")

            existing_conv = (
                s.query(Conversation).filter_by(paper_id=paper.id).count()
            )
            if existing_conv:
                _log(f"  conversations 已存在（{existing_conv} 則），略過")
            else:
                hist_path = (src / "chat_history.json") if src else None
                msgs = []
                if hist_path and hist_path.exists():
                    try:
                        msgs = json.loads(hist_path.read_text(encoding="utf-8")) or []
                    except (json.JSONDecodeError, OSError):
                        msgs = []
                for m in msgs:
                    if not isinstance(m, dict):
                        continue
                    s.add(Conversation(
                        paper_id=paper.id,
                        user_id=admin_id,
                        role=m.get("role", "user"),
                        content=m.get("content", ""),
                        grounding_sources=None,
                        created_at=ts,
                    ))
                if msgs:
                    s.commit()
                    _log(f"  匯入 conversations：{len(msgs)} 則")

            # 搬目錄（idempotent）
            legacy = OUTPUT_DIR / pid
            dest = owner_root / pid
            if legacy.is_dir() and not dest.exists():
                shutil.move(str(legacy), str(dest))
                _log(f"  搬移目錄：output/{pid} → output/{admin_id}/{pid}")
            elif dest.exists():
                _log("  目錄已在新位置，略過搬移")
            else:
                _log(f"  警告：找不到來源目錄 output/{pid}（僅建 DB 紀錄）")

    _log("遷移完成。")
    return 0


def do_rollback() -> int:
    import db

    index = _load_index()
    # 推得 admin_id（dir 命名）：掃 output/ 下純數字目錄
    moved = False
    for child in OUTPUT_DIR.iterdir() if OUTPUT_DIR.exists() else []:
        if child.is_dir() and child.name.isdigit():
            for paper_dir in list(child.iterdir()):
                target = OUTPUT_DIR / paper_dir.name
                if paper_dir.is_dir() and not target.exists():
                    shutil.move(str(paper_dir), str(target))
                    _log(f"還原目錄：{child.name}/{paper_dir.name} → {paper_dir.name}")
                    moved = True
            try:
                child.rmdir()
            except OSError:
                pass
    if not moved:
        _log("無目錄需還原（或已還原）。")

    url = db.DATABASE_URL
    if url.startswith("sqlite:///"):
        dbfile = Path(url.split("sqlite:///", 1)[-1])
        for suffix in ("", "-wal", "-shm"):
            f = Path(str(dbfile) + suffix)
            if f.exists():
                f.unlink()
                _log(f"刪除 DB 檔：{f.name}")
    _log("rollback 完成。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="papers_index/chat_history → SQLite 遷移")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="只報告計畫，不寫入")
    g.add_argument("--rollback", action="store_true", help="目錄搬回 + 刪 .db")
    args = ap.parse_args()
    if args.dry_run:
        return do_dry_run()
    if args.rollback:
        return do_rollback()
    return do_migrate()


if __name__ == "__main__":
    raise SystemExit(main())
