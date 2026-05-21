"""Phase 4.7d Commit 17-1：paper_manager.append_chat_message tests.

針對「後端 chat endpoint 內單筆 append」新 API 補測試。tmp_db fixture
建立 in-memory SQLite、覆寫 db.engine / db.SessionLocal、建空 schema、
建一筆測試 paper 後使用。不依賴真實 data/mad-professor.db。
"""
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db as db_mod  # noqa: E402
from models import Base, User, Paper  # noqa: E402
import paper_manager  # noqa: E402


@pytest.fixture
def tmp_db(monkeypatch):
    """每測試一個獨立 in-memory SQLite。覆寫 db 模組的 engine / SessionLocal。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, class_=Session
    )
    monkeypatch.setattr(db_mod, 'engine', engine)
    monkeypatch.setattr(db_mod, 'SessionLocal', TestSession)
    # paper_manager 內有 _ensure_db() 護欄，本測試不必觸發
    monkeypatch.setattr(paper_manager, '_ensure_db', lambda: None)
    yield engine
    engine.dispose()


def _create_test_paper(engine) -> int:
    """建一個 user + paper、回傳 paper.id。"""
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    with SessionLocal() as s:
        u = User(username='test', password_hash='x')
        s.add(u)
        s.flush()
        p = Paper(
            owner_id=u.id, paper_uuid='test-paper-uuid',
            title='Test', status='done',
        )
        s.add(p)
        s.commit()
        return p.id


def test_append_chat_message_inserts_one(tmp_db):
    """append 後 DB 增加一筆、load 回讀正確"""
    db_id = _create_test_paper(tmp_db)

    cid = paper_manager.append_chat_message(
        db_id, user_id=1, role='user', content='hello world'
    )
    assert cid > 0

    history = paper_manager.load_chat_history(db_id, user_id=1)
    assert len(history) == 1
    assert history[0]['role'] == 'user'
    assert history[0]['content'] == 'hello world'


def test_append_chat_message_order_preserved(tmp_db):
    """多次 append 依 id 順序（= 插入序）排列"""
    db_id = _create_test_paper(tmp_db)
    paper_manager.append_chat_message(db_id, 1, 'user', 'q1')
    paper_manager.append_chat_message(db_id, 1, 'assistant', 'a1')
    paper_manager.append_chat_message(db_id, 1, 'user', 'q2')
    paper_manager.append_chat_message(db_id, 1, 'assistant', 'a2')

    history = paper_manager.load_chat_history(db_id, 1)
    assert [m['content'] for m in history] == ['q1', 'a1', 'q2', 'a2']
    assert [m['role'] for m in history] == ['user', 'assistant', 'user', 'assistant']


def test_append_chat_message_with_grounding_sources(tmp_db):
    """grounding_sources 正確存取（list[dict]）"""
    db_id = _create_test_paper(tmp_db)
    gs = [{'uri': 'http://x.com', 'title': 'X'},
          {'uri': 'http://y.com', 'title': 'Y'}]
    paper_manager.append_chat_message(
        db_id, 1, 'assistant', 'see sources', grounding_sources=gs
    )
    history = paper_manager.load_chat_history(db_id, 1)
    assert len(history) == 1
    assert history[0]['grounding_sources'] == gs


def test_append_chat_message_empty_grounding_stored_as_none(tmp_db):
    """grounding_sources=None 或空 list 不寫進 DB（節省欄位）"""
    db_id = _create_test_paper(tmp_db)
    paper_manager.append_chat_message(
        db_id, 1, 'assistant', 'no sources', grounding_sources=None
    )
    paper_manager.append_chat_message(
        db_id, 1, 'assistant', 'still no', grounding_sources=[]
    )
    history = paper_manager.load_chat_history(db_id, 1)
    # load_chat_history 對 None 不附 grounding_sources 鍵
    assert 'grounding_sources' not in history[0]
    assert 'grounding_sources' not in history[1]
