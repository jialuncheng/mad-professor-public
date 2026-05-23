"""RAG-1 R2 v3 強化：_normalize_tag helper + set_paper_tags 整合驗證。

依據:
- plan: .claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md §4.2.1 Q4
- UI Plan v3 強化段：所有 tag 寫入路徑強制 lowercase
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


# ─────────────────── _normalize_tag 基本行為 ───────────────────


def test_normalize_lowercase_english():
    from paper_manager import _normalize_tag
    assert _normalize_tag("HR") == "hr"
    assert _normalize_tag("Machine_Learning") == "machine_learning"
    assert _normalize_tag("Engineering") == "engineering"


def test_normalize_strips_whitespace():
    from paper_manager import _normalize_tag
    assert _normalize_tag("  HR  ") == "hr"
    assert _normalize_tag("\thr\n") == "hr"
    assert _normalize_tag(" plant ") == "plant"


def test_normalize_empty_returns_empty():
    from paper_manager import _normalize_tag
    assert _normalize_tag("") == ""
    assert _normalize_tag(None) == ""
    assert _normalize_tag("   ") == ""
    assert _normalize_tag(42) == ""  # 非字串


def test_normalize_chinese_unaffected():
    from paper_manager import _normalize_tag
    # 中文無大小寫概念、`.lower()` 原樣保留
    assert _normalize_tag("人資") == "人資"
    assert _normalize_tag("工程") == "工程"
    assert _normalize_tag("  人資  ") == "人資"


def test_normalize_preserves_special_chars():
    from paper_manager import _normalize_tag
    assert _normalize_tag("machine-learning") == "machine-learning"
    assert _normalize_tag("plant_systems") == "plant_systems"
    assert _normalize_tag("2024") == "2024"
    assert _normalize_tag("📚book") == "📚book"


# ─────────────────── set_paper_tags 整合 _normalize_tag ───────────────────


@pytest.fixture
def temp_db(monkeypatch):
    """file-based SQLite、沿用既有 fixture pattern。"""
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


def _make_paper(db_mod_param, models_mod, owner_id=1, paper_uuid='r2_test'):
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


def test_set_paper_tags_lowercases_input(temp_db):
    """v3 強化：寫入 `HR / Engineering` → DB 內存為 `['hr', 'engineering']`。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(s, owner_id=1, paper_uuid='r2_test',
                          tags=['HR', 'Engineering'])

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r2_test').one()
        meta = json.loads(p.metadata_json)
        assert meta['user_tags'] == ['hr', 'engineering']


def test_set_paper_tags_dedups_after_lowercase(temp_db):
    """v3 強化：`['HR', 'hr', 'Hr']` → DB 內存為 `['hr']` 1 個（保留首次出現順序）。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(s, owner_id=1, paper_uuid='r2_test',
                          tags=['HR', 'hr', 'Hr'])

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r2_test').one()
        meta = json.loads(p.metadata_json)
        assert meta['user_tags'] == ['hr']


def test_set_paper_tags_chinese_preserved(temp_db):
    """中文 tag 原樣保留（`.lower()` 無效）。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_tags(s, owner_id=1, paper_uuid='r2_test',
                          tags=['人資', '工程', '  人資  '])

    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid='r2_test').one()
        meta = json.loads(p.metadata_json)
        # `人資` 跟 `  人資  ` strip 後相同、去重後 1 個
        assert meta['user_tags'] == ['人資', '工程']
