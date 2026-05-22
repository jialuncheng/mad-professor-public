"""Phase 4.7? MODEL-8 C2: rag_processor 寫入 paper_chunks + index_meta.json 驗證。

依據:
- plan §3.2 + §3.3 + §5.1 C2 部分 + Q12 / Q13 / Q14
- 含修正 3: rows 無 tiling_method 欄位
- 含修正 4: module-level write_index_meta_json

fixture 對齊 tests/test_paper_chunks_schema.py：用 monkeypatch.setattr 改 db.engine，
不 reload models（避免 ORM mapper 重複註冊污染其他 test）。
"""
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, event
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
    """fresh file-based SQLite + FK PRAGMA、對齊 C1 test_paper_chunks_schema.py fixture pattern。"""
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


def _make_paper(db_mod_param, models_mod, owner_id=1, paper_uuid='c2_test'):
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


def _make_mock_docs(n=3):
    """模擬 MarkdownHeaderTextSplitter 輸出（metadata 只含 Header、依修正 3）。"""
    from langchain_core.documents import Document
    return [
        Document(
            page_content=f"chunk {i} content",
            metadata={"Header": f"section {i}"},
        )
        for i in range(n)
    ]


def _make_rag_processor():
    """繞過 __init__（不需 embedder）建空 RagProcessor instance。"""
    from processor.rag_processor import RagProcessor
    rp = RagProcessor.__new__(RagProcessor)
    rp.logger = MagicMock()
    return rp


# ─────────────────── 1. paper_chunks 寫入 ───────────────────


def test_chunks_written_after_create_vector_store(temp_db):
    """C2: paper_db_id 提供後 → paper_chunks 有對應 rows、無 tiling_method（修正 3）。"""
    db_mod_p, models_mod, pm = temp_db
    pid = _make_paper(db_mod_p, models_mod)
    rp = _make_rag_processor()

    docs = _make_mock_docs(3)
    rp._write_paper_chunks_to_db(docs, pid, doc_type='academic')

    rows = list(pm.iter_paper_chunks(pid))
    assert len(rows) == 3
    assert rows[0]['raw_text'] == 'chunk 0 content'
    assert rows[0]['chunk_key'] == 'section 0'
    assert rows[0]['doc_type'] == 'academic'
    assert rows[0]['translated_text'] is None  # Q14
    # 修正 3：rows 字典內無 tiling_method 鍵
    assert 'tiling_method' not in rows[0]


# ─────────────────── 2. 覆寫式重跑 ───────────────────


def test_chunks_overwrite_on_rerun(temp_db):
    """C2: 同 paper 跑兩次 → 第二次 rows 覆寫第一次（不累積）。"""
    db_mod_p, models_mod, pm = temp_db
    pid = _make_paper(db_mod_p, models_mod)
    rp = _make_rag_processor()

    rp._write_paper_chunks_to_db(_make_mock_docs(3), pid, doc_type='academic')
    rp._write_paper_chunks_to_db(_make_mock_docs(2), pid, doc_type='academic')

    rows = list(pm.iter_paper_chunks(pid))
    assert len(rows) == 2  # 覆寫、不累積


# ─────────────────── 3. index_meta.json（修正 4 module-level）───────────────────


def test_index_meta_json_written(tmp_path):
    """C2 修正 4: module-level write_index_meta_json 寫入 vectors/index_meta.json。"""
    from processor.rag_processor import write_index_meta_json

    vectors_dir = tmp_path / "vectors"
    vectors_dir.mkdir()

    write_index_meta_json(vectors_dir, chunks_total=42)

    meta_path = vectors_dir / "index_meta.json"
    assert meta_path.exists()

    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    assert 'embedding_model' in meta
    assert 'output_dimensions' in meta
    assert 'chunk_filter_version' in meta
    assert meta['chunks_total'] == 42
    assert 'tiling_config_signature' in meta
    assert 'created_at' in meta
    assert meta['rag_processor_version'] == 'MODEL-8-C2'


# ─────────────────── 4. metadata 完整保留 ───────────────────


def test_chunk_metadata_preserved(temp_db):
    """C2: 從 paper_chunks.metadata_json 反序列化 == 原 doc.metadata（含 Header）。"""
    db_mod_p, models_mod, pm = temp_db
    pid = _make_paper(db_mod_p, models_mod)
    rp = _make_rag_processor()

    from langchain_core.documents import Document
    original_meta = {"Header": "Introduction"}
    docs = [Document(page_content="hello", metadata=original_meta)]
    rp._write_paper_chunks_to_db(docs, pid, doc_type='academic')

    rows = list(pm.iter_paper_chunks(pid))
    restored = json.loads(rows[0]['metadata_json'])
    assert restored == original_meta


# ─────────────────── 5. paper_db_id=None 優雅降級（Q13）───────────────────


def test_paper_db_id_none_skips_write_with_warning(tmp_path, monkeypatch):
    """C2 / Q13: paper_db_id=None 時 _create_vector_store 內走 warning 分支、_write_paper_chunks_to_db 不被呼叫。

    透過 monkeypatch 注入假 FAISS / embedder、直接驗證 _create_vector_store 內 None 分支。
    """
    from processor import rag_processor as rag_mod

    rp = _make_rag_processor()

    # 準備假 md 檔（含 1 個 chunk）
    md_path = tmp_path / "fake.md"
    md_path.write_text("# Section A\n\nHello world content " * 5, encoding='utf-8')
    vectors_dir = tmp_path / "vectors"

    # 攔截 FAISS.from_documents + embedder（避免真的呼 Gemini API）
    fake_vs = MagicMock()
    fake_vs.save_local = MagicMock()
    monkeypatch.setattr(rag_mod.FAISS, 'from_documents', lambda **kw: fake_vs)
    rp.embedder = MagicMock()

    # spy _write_paper_chunks_to_db 應該不被呼叫
    rp._write_paper_chunks_to_db = MagicMock()

    rp._create_vector_store(
        str(md_path), str(vectors_dir),
        doc_type='academic', paper_db_id=None,
    )

    rp._write_paper_chunks_to_db.assert_not_called()
    # Q13 warning 應該被印
    warning_calls = [
        c for c in rp.logger.warning.call_args_list
        if '[paper_chunks]' in str(c) and 'paper_db_id 未提供' in str(c)
    ]
    assert len(warning_calls) >= 1
    # index_meta.json 仍應該寫入
    assert (vectors_dir / "index_meta.json").exists()
