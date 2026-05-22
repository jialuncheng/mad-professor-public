"""Phase 4.7? MODEL-8 C3: tools/regen_rag.py CLI 驗證。

依據:
- plan §3.4 + §5.1 C3 部分
- 含修正 5: 用既有 get_paper_db_id
- 含修正 6: cmd_init 反向導入測試（test_cmd_init_reverse_import_from_faiss）

fixture 完全沿用 C1 + C2 已 ship 的 pattern（monkeypatch.setattr db.engine、不 reload models）。
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    """file-based SQLite + FK PRAGMA、對齊 C1 / C2 fixture pattern。"""
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


def _make_paper(db_mod_param, models_mod, owner_id=1, paper_uuid='c3_test_paper'):
    """建 paper 並回 paper_db_id。"""
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


def _seed_paper_chunks(pm, pid, model='gemini-embedding-2', dim=768, n=3):
    """為 paper 填 n 個 chunks。"""
    rows = [
        {
            "chunk_index": i,
            "chunk_key": f"sec_{i}",
            "raw_text": f"chunk {i} content",
            "translated_text": None,
            "doc_type": "academic",
            "metadata_json": json.dumps(
                {"Header": f"section {i}"}, ensure_ascii=False
            ),
            "embedding_model": model,
            "output_dimensions": dim,
            "chunk_filter_version": "B2-2026-05-22",
        }
        for i in range(n)
    ]
    pm.replace_paper_chunks(pid, rows)


# ─────────────────── 1. --check no mismatch ───────────────────


def test_check_no_mismatch(temp_db, capsys):
    """settings 沒改 → --check 印 [OK]、return 0。"""
    db_mod_p, models_mod, pm = temp_db
    import settings

    pid = _make_paper(db_mod_p, models_mod)
    _seed_paper_chunks(
        pm, pid,
        model=settings.EMBEDDING_MODEL_NAME,
        dim=settings.EMBEDDING_OUTPUT_DIMENSIONS,
    )

    from tools.regen_rag import cmd_check
    mismatch_count = cmd_check()

    captured = capsys.readouterr()
    assert '[OK]' in captured.out
    assert mismatch_count == 0


# ─────────────────── 2. --check mismatch detected ───────────────────


def test_check_mismatch_detected(temp_db, monkeypatch, capsys):
    """monkeypatch EMBEDDING_MODEL_NAME → --check 印 [MISMATCH]、return > 0。"""
    db_mod_p, models_mod, pm = temp_db

    pid = _make_paper(db_mod_p, models_mod)
    _seed_paper_chunks(pm, pid, model='OLD-MODEL', dim=768)

    import settings
    monkeypatch.setattr(settings, 'EMBEDDING_MODEL_NAME', 'NEW-MODEL')

    from tools.regen_rag import cmd_check
    mismatch_count = cmd_check()

    captured = capsys.readouterr()
    assert '[MISMATCH]' in captured.out
    assert mismatch_count >= 1


# ─────────────────── 3. --paper 重 embed（mock FAISS）───────────────────


def test_regen_single_paper(temp_db, monkeypatch, tmp_path):
    """--paper → paper_chunks rows.embedding_model 更新、FAISS save 被呼叫。"""
    db_mod_p, models_mod, pm = temp_db

    pid = _make_paper(db_mod_p, models_mod)
    _seed_paper_chunks(pm, pid, model='OLD-MODEL', dim=768)

    import settings
    monkeypatch.setattr(settings, 'EMBEDDING_MODEL_NAME', 'NEW-MODEL')
    monkeypatch.setattr(settings, 'OUTPUT_DIR', tmp_path)

    mock_vs = MagicMock()
    with patch(
        'langchain_community.vectorstores.faiss.FAISS.from_documents',
        return_value=mock_vs,
    ), patch(
        'config.EmbeddingModel.get_instance', return_value=MagicMock(),
    ):
        from tools.regen_rag import cmd_regen
        cmd_regen(pid, 1, 'c3_test_paper', force=False)

    mock_vs.save_local.assert_called_once()
    rows = list(pm.iter_paper_chunks(pid))
    assert all(r['embedding_model'] == 'NEW-MODEL' for r in rows)


# ─────────────────── 4. --all 批次 ───────────────────


def test_regen_all(temp_db, monkeypatch, tmp_path):
    """--all 批次處理多 paper。"""
    db_mod_p, models_mod, pm = temp_db

    pid1 = _make_paper(db_mod_p, models_mod, paper_uuid='paper_a')
    pid2 = _make_paper(db_mod_p, models_mod, paper_uuid='paper_b')
    _seed_paper_chunks(pm, pid1, model='OLD-MODEL')
    _seed_paper_chunks(pm, pid2, model='OLD-MODEL')

    import settings
    monkeypatch.setattr(settings, 'EMBEDDING_MODEL_NAME', 'NEW-MODEL')
    monkeypatch.setattr(settings, 'OUTPUT_DIR', tmp_path)

    mock_vs = MagicMock()
    with patch(
        'langchain_community.vectorstores.faiss.FAISS.from_documents',
        return_value=mock_vs,
    ), patch(
        'config.EmbeddingModel.get_instance', return_value=MagicMock(),
    ):
        from tools.regen_rag import cmd_all
        cmd_all()

    assert mock_vs.save_local.call_count == 2


# ─────────────────── 5. --force 略過 mismatch 檢查 ───────────────────


def test_regen_force_skips_mismatch_check(temp_db, monkeypatch, tmp_path):
    """settings 沒變、--force 仍重 embed（不會 [SKIP]）。"""
    db_mod_p, models_mod, pm = temp_db

    pid = _make_paper(db_mod_p, models_mod)
    import settings
    _seed_paper_chunks(
        pm, pid,
        model=settings.EMBEDDING_MODEL_NAME,
        dim=settings.EMBEDDING_OUTPUT_DIMENSIONS,
    )
    monkeypatch.setattr(settings, 'OUTPUT_DIR', tmp_path)

    mock_vs = MagicMock()
    with patch(
        'langchain_community.vectorstores.faiss.FAISS.from_documents',
        return_value=mock_vs,
    ), patch(
        'config.EmbeddingModel.get_instance', return_value=MagicMock(),
    ):
        from tools.regen_rag import cmd_regen
        cmd_regen(pid, 1, 'c3_test_paper', force=True)

    # force=True 應重 embed（即使 model match）
    mock_vs.save_local.assert_called_once()


# ─────────────────── 6. --dry-run ───────────────────


def test_regen_dry_run(temp_db, capsys):
    """--dry-run 印 [DRY-RUN]、不實際寫 FAISS / DB。"""
    db_mod_p, models_mod, pm = temp_db

    pid = _make_paper(db_mod_p, models_mod)
    _seed_paper_chunks(pm, pid)

    from tools.regen_rag import cmd_regen
    cmd_regen(pid, 1, 'c3_test_paper', dry_run=True)

    captured = capsys.readouterr()
    assert '[DRY-RUN]' in captured.out


# ─────────────────── 7. --init 反向導入（修正 6 關鍵驗證）───────────────────


def test_cmd_init_reverse_import_from_faiss(temp_db, monkeypatch, tmp_path):
    """修正 6: vectors/ 含 FAISS docstore + paper_chunks 空 → --init 後有 rows。"""
    db_mod_p, models_mod, pm = temp_db

    pid = _make_paper(
        db_mod_p, models_mod,
        owner_id=1, paper_uuid='init_test_paper',
    )
    # 注意：故意不呼 _seed_paper_chunks、paper_chunks 空著

    # 建假的 vectors/ 目錄結構（OUTPUT_DIR/<owner>/<uuid>/vectors/）
    vectors_dir = tmp_path / '1' / 'init_test_paper' / 'vectors'
    vectors_dir.mkdir(parents=True)
    (vectors_dir / 'index.faiss').touch()

    # mock FAISS.load_local 回傳含 docstore 的 vs
    from langchain_core.documents import Document
    mock_docs = {
        'doc1': Document(
            page_content='hello world 1',
            metadata={'Header': 'Section A'},
        ),
        'doc2': Document(
            page_content='hello world 2',
            metadata={'Header': 'Section B'},
        ),
    }
    mock_vs = MagicMock()
    mock_vs.docstore._dict = mock_docs

    import settings
    monkeypatch.setattr(settings, 'OUTPUT_DIR', tmp_path)

    with patch(
        'langchain_community.vectorstores.faiss.FAISS.load_local',
        return_value=mock_vs,
    ), patch(
        'config.EmbeddingModel.get_instance', return_value=MagicMock(),
    ):
        from tools.regen_rag import cmd_init
        cmd_init()

    rows = list(pm.iter_paper_chunks(pid))
    assert len(rows) == 2
    raw_texts = {r['raw_text'] for r in rows}
    assert raw_texts == {'hello world 1', 'hello world 2'}
    # Q16: doc_type 為空字串
    assert all(r['doc_type'] == '' for r in rows)
    # index_meta.json 寫入
    assert (vectors_dir / 'index_meta.json').exists()
