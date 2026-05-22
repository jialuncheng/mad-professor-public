"""Phase 4.7? MODEL-8 C1: PaperChunk ORM schema + DAL helper + OUTPUT_DIR env 驗證。

依據:
- plan §3.1 + §3.6 + §5.1 C1 部分
- 含修正 3: 無 tiling_method 欄位
- 含修正 5: 不重做 get_paper_db_id（既有 paper_manager.py:336 已存在）
- 含修正 7: OUTPUT_DIR env override
"""
import importlib
import json
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db as db_mod  # noqa: E402
from models import Base, Paper, PaperChunk, User  # noqa: E402
import paper_manager  # noqa: E402


# ─────────────────── fixture ───────────────────


@pytest.fixture
def temp_db(monkeypatch):
    """每測試一個獨立 file-based SQLite + FK ON pragma、覆寫 db 模組 engine/SessionLocal。

    避免 importlib.reload(models) 造成 mapper 重複註冊、破壞其他 test。
    對齊既有 tests/test_paper_manager.py::tmp_db pattern。

    使用 file-based 而非 in-memory：file-based 支援多個獨立 connection 共享同一 DB（FK
    cascade 跨 session 驗證需要）；in-memory 同一程序內每個 connection 是獨立 DB。
    """
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    # 啟用 FK 強制（對齊 db.py 既有 PRAGMA）以驗證 cascade 行為
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


def _make_paper(db_mod_param, models_mod, owner_id=1, paper_uuid='test_paper'):
    """fixture helper: 建 1 個 User + 1 個 Paper、回 paper.id (INT PK)。"""
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
        )
        s.add(p)
        s.commit()
        return p.id


def _make_chunk_row(idx=0, raw='hello world'):
    return {
        "chunk_index": idx,
        "chunk_key": f"sec_{idx}",
        "raw_text": raw,
        "translated_text": None,
        "doc_type": "academic",
        "metadata_json": json.dumps(
            {"Header": f"section {idx}"}, ensure_ascii=False
        ),
        "embedding_model": "gemini-embedding-2",
        "output_dimensions": 768,
        "chunk_filter_version": "B2-2026-05-22",
    }


# ─────────────────── 1. Schema 驗證（含修正 3）───────────────────


def test_paper_chunks_table_created(temp_db):
    """init_db() 後 paper_chunks 表存在、欄位完整、無 tiling_method（修正 3）。"""
    db_mod, _models, _pm = temp_db
    from sqlalchemy import inspect
    insp = inspect(db_mod.engine)
    assert 'paper_chunks' in insp.get_table_names()
    cols = {c['name'] for c in insp.get_columns('paper_chunks')}
    expected = {
        'id', 'paper_id', 'chunk_index', 'chunk_key', 'raw_text',
        'translated_text', 'doc_type', 'metadata_json',
        'embedding_model', 'output_dimensions', 'chunk_filter_version',
        'created_at',
    }
    assert expected <= cols
    # 修正 3：不應有 tiling_method 欄位（MarkdownHeaderTextSplitter metadata 不含）
    assert 'tiling_method' not in cols


# ─────────────────── 2. FK + cascade ───────────────────


def test_paper_chunks_foreign_key_cascade(temp_db):
    """刪 Paper → 對應 PaperChunk 全部刪除（FK + WAL pragma 物理生效）。"""
    db_mod, models_mod, pm = temp_db
    pid = _make_paper(db_mod, models_mod)
    pm.replace_paper_chunks(pid, [_make_chunk_row(0), _make_chunk_row(1)])

    with db_mod.SessionLocal() as s:
        assert (
            s.query(models_mod.PaperChunk).filter_by(paper_id=pid).count() == 2
        )
        s.query(models_mod.Paper).filter_by(id=pid).delete()
        s.commit()

    with db_mod.SessionLocal() as s:
        assert (
            s.query(models_mod.PaperChunk).filter_by(paper_id=pid).count() == 0
        )


# ─────────────────── 3. UNIQUE constraint ───────────────────


def test_paper_chunks_unique_constraint(temp_db):
    """同 paper_id + chunk_index 重複 INSERT 拋 IntegrityError。"""
    db_mod, models_mod, _pm = temp_db
    pid = _make_paper(db_mod, models_mod)

    from sqlalchemy import insert
    with db_mod.SessionLocal() as s:
        s.execute(
            insert(models_mod.PaperChunk),
            [{**_make_chunk_row(0), "paper_id": pid}],
        )
        s.commit()

    with pytest.raises(IntegrityError):
        with db_mod.SessionLocal() as s:
            s.execute(
                insert(models_mod.PaperChunk),
                [{**_make_chunk_row(0), "paper_id": pid}],
            )
            s.commit()


# ─────────────────── 4. replace_paper_chunks 覆寫 ───────────────────


def test_replace_paper_chunks_overwrite(temp_db):
    """replace_paper_chunks(pid, [a, b]) → replace(pid, [c]) → 表內只剩 c。"""
    db_mod, models_mod, pm = temp_db
    pid = _make_paper(db_mod, models_mod)

    pm.replace_paper_chunks(pid, [
        _make_chunk_row(0, 'A'),
        _make_chunk_row(1, 'B'),
    ])
    with db_mod.SessionLocal() as s:
        assert (
            s.query(models_mod.PaperChunk).filter_by(paper_id=pid).count() == 2
        )

    pm.replace_paper_chunks(pid, [_make_chunk_row(0, 'C')])
    with db_mod.SessionLocal() as s:
        rows = s.query(models_mod.PaperChunk).filter_by(paper_id=pid).all()
        assert len(rows) == 1
        assert rows[0].raw_text == 'C'


# ─────────────────── 5. iter_paper_chunks 順序 ───────────────────


def test_iter_paper_chunks_order(temp_db):
    """iter_paper_chunks 依 chunk_index 升序回（INSERT 順序顛倒也是）。"""
    db_mod, models_mod, pm = temp_db
    pid = _make_paper(db_mod, models_mod)

    # 故意倒序 INSERT
    pm.replace_paper_chunks(pid, [
        _make_chunk_row(2, 'C'),
        _make_chunk_row(0, 'A'),
        _make_chunk_row(1, 'B'),
    ])

    yielded = list(pm.iter_paper_chunks(pid))
    assert [r['chunk_index'] for r in yielded] == [0, 1, 2]
    assert [r['raw_text'] for r in yielded] == ['A', 'B', 'C']


# ─────────────────── 6. OUTPUT_DIR env override（修正 7）───────────────────


def test_output_dir_env_override(monkeypatch, tmp_path):
    """修正 7: OUTPUT_DIR=/custom/path 生效。

    使用 try/finally + reload 以確保測試後 settings 模組狀態恢復、
    避免污染其他依賴 settings.OUTPUT_DIR 的 test。
    """
    custom_path = str(tmp_path / "custom_output")
    monkeypatch.setenv('OUTPUT_DIR', custom_path)

    import settings
    try:
        importlib.reload(settings)
        assert str(settings.OUTPUT_DIR) == custom_path
    finally:
        # 還原（monkeypatch 在 fixture 退出時撤回 env、再 reload 一次回預設）
        monkeypatch.delenv('OUTPUT_DIR', raising=False)
        importlib.reload(settings)


def test_output_dir_defaults_to_base_dir_output(monkeypatch):
    """OUTPUT_DIR 未設時、預設值 = _BASE_DIR / 'output'。"""
    monkeypatch.delenv('OUTPUT_DIR', raising=False)

    import settings
    importlib.reload(settings)

    assert settings.OUTPUT_DIR.name == 'output'
    assert settings.OUTPUT_DIR == settings._BASE_DIR / "output"
