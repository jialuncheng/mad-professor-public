"""RAG-1 R1: paper_manager.set_paper_tags 寫入路徑驗證。

依據:
- plan: .claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md
  §4.1 子項 A + §4.3 R1 行 + §6.2 R1 行
- UI Fixes Plan v3 L23-31
- 含修正：strip 空白 + 過濾空字串 + 整批覆寫（跟 R3 _apply_folder_path_tags append 互補）

fixture 對齊 tests/test_paper_chunks_schema.py：monkeypatch.setattr 改 db.engine、
不 reload models（避免 ORM mapper 重複註冊污染其他 test）。
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db as db_mod  # noqa: E402
from models import Base, Paper, User  # noqa: E402
import paper_manager  # noqa: E402


# ─────────────────── fixture（沿用 C1/C2 pattern）───────────────────


@pytest.fixture
def temp_db(monkeypatch):
    """fresh file-based SQLite、覆寫 db.engine / SessionLocal。"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON")
        finally:
            cur.close()

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, class_=Session
    )
    monkeypatch.setattr(db_mod, 'engine', engine)
    monkeypatch.setattr(db_mod, 'SessionLocal', TestSession)
    monkeypatch.setattr(paper_manager, '_ensure_db', lambda: None)
    yield db_mod, sys.modules['models'], paper_manager
    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


def _make_paper(db_mod_param, models_mod, owner_id=1, paper_uuid='r1_test'):
    """建 1 個 User + 1 個 Paper、metadata_json 初始為空 dict。"""
    with db_mod_param.SessionLocal() as s:
        user = s.query(models_mod.User).filter_by(id=owner_id).first()
        if not user:
            user = models_mod.User(
                id=owner_id, username=f'user{owner_id}', password_hash='x'
            )
            s.add(user)
            s.commit()
        p = models_mod.Paper(
            owner_id=owner_id,
            paper_uuid=paper_uuid,
            status='ready',
            original_filename=f'{paper_uuid}.pdf',
            metadata_json=json.dumps({}),
        )
        s.add(p)
        s.commit()
        return p.id


# ─────────────────── 1. 寫入後讀回一致 ───────────────────


def test_set_paper_tags_upsert(temp_db):
    """寫入 user_tags 後讀回 metadata 一致。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(
            s, owner_id=1, paper_uuid='r1_test',
            tags=['plant', 'complex system'],
        )

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r1_test').one()
        meta = json.loads(p.metadata_json)
        assert meta['user_tags'] == ['plant', 'complex system']


# ─────────────────── 2. 第二次覆寫第一次 ───────────────────


def test_set_paper_tags_overwrite(temp_db):
    """同 paper 連續寫 → 第二次覆寫第一次（整批覆寫策略）。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(
            s, owner_id=1, paper_uuid='r1_test',
            tags=['old_a', 'old_b'],
        )
    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(
            s, owner_id=1, paper_uuid='r1_test',
            tags=['new_only'],
        )

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r1_test').one()
        meta = json.loads(p.metadata_json)
        assert meta['user_tags'] == ['new_only']
        assert 'old_a' not in meta['user_tags']
        assert 'old_b' not in meta['user_tags']


# ─────────────────── 3. strip 空白 + 過濾空字串 / None ───────────────────


def test_set_paper_tags_strips_whitespace_and_empty(temp_db):
    """strip 空白 + 過濾 None / 空字串 / 全空白字串。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(
            s, owner_id=1, paper_uuid='r1_test',
            tags=['  plant  ', '', '   ', 'system', None, 42],  # 含非 str
        )

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r1_test').one()
        meta = json.loads(p.metadata_json)
        # strip 空白 + 過濾 None / 空字串 / 全空白 / 非 str
        assert meta['user_tags'] == ['plant', 'system']
