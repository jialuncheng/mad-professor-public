"""META-NORM 測試。

C1：MetaField/MetaFieldAlias 表結構（PK/FK CASCADE/sort_weight）+ seed 種子註冊冪等。
後續 commit 追加：C2 MetaNormalizer 飛輪 / C6 §7.2 key-changing 整合。
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, inspect, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import Base, MetaField, MetaFieldAlias  # noqa: E402


# === [META-NORM C1 START] ===
# seed 與 db.py init_db 同源（測試獨立 DB、不污染正式庫）。
_SEEDS = [
    {"canonical_key": "course", "label_zh": "課程", "label_en": "Course",
     "category": "cover", "source": "manual", "sort_weight": 10},
    {"canonical_key": "instructor", "label_zh": "講師", "label_en": "Instructor",
     "category": "cover", "source": "manual", "sort_weight": 20},
    {"canonical_key": "organization", "label_zh": "組織/機構", "label_en": "Organization",
     "category": "cover", "source": "manual", "sort_weight": 30},
    {"canonical_key": "date", "label_zh": "日期", "label_en": "Date",
     "category": "cover", "source": "manual", "sort_weight": 40},
    {"canonical_key": "venue", "label_zh": "發表地點/期刊", "label_en": "Venue",
     "category": "cover", "source": "manual", "sort_weight": 50},
    {"canonical_key": "doi", "label_zh": "DOI", "label_en": "DOI",
     "category": "cover", "source": "manual", "sort_weight": 60},
]


@pytest.fixture
def session_factory():
    """每測試獨立 file-based SQLite + FK ON（鏡像 GLOSSARY-CORE 範式）。"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}, future=True)

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON")
        finally:
            cur.close()

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, class_=Session)
    yield TestSession
    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


def _run_seed(session_factory):
    """重現 db.py init_db 之 seed 冪等註冊邏輯。"""
    with session_factory() as session:
        with session.begin():
            for seed in _SEEDS:
                session.execute(
                    sqlite_insert(MetaField).values(**seed).on_conflict_do_nothing())


def test_meta_norm_schema_and_seeds(session_factory):
    """U1/U2：兩表結構 + seed 6 欄註冊 + 標籤/sort_weight 正確。"""
    # 表結構
    with session_factory() as session:
        insp = inspect(session.bind)
        assert "meta_fields" in insp.get_table_names()
        assert "meta_field_aliases" in insp.get_table_names()
        mf_cols = {c["name"] for c in insp.get_columns("meta_fields")}
        assert {"canonical_key", "label_zh", "label_en", "category",
                "source", "sort_weight", "created_at"} <= mf_cols
        pk = insp.get_pk_constraint("meta_fields")["constrained_columns"]
        assert pk == ["canonical_key"]

    # seed 註冊
    _run_seed(session_factory)
    with session_factory() as session:
        rows = session.execute(select(MetaField)).scalars().all()
        by_key = {r.canonical_key: r for r in rows}
        for seed in _SEEDS:
            r = by_key[seed["canonical_key"]]
            assert r.label_zh == seed["label_zh"] and r.label_en == seed["label_en"]
            assert r.sort_weight == seed["sort_weight"] and r.source == "manual"
        assert by_key["course"].label_zh == "課程"


def test_seed_idempotent(session_factory):
    """seed 重複跑（init_db 可重複呼叫）→ on_conflict_do_nothing 不重複不報錯。"""
    _run_seed(session_factory)
    _run_seed(session_factory)   # 二次
    with session_factory() as session:
        n = len(session.execute(select(MetaField)).scalars().all())
        assert n == len(_SEEDS)   # 仍 6 筆、無重複


def test_alias_fk_cascade(session_factory):
    """BS6：MetaFieldAlias FK ondelete=CASCADE——刪 MetaField 連帶刪 alias。"""
    _run_seed(session_factory)
    with session_factory() as session:
        with session.begin():
            session.add(MetaFieldAlias(raw_key="課程", canonical_key="course"))
    with session_factory() as session:
        assert session.get(MetaFieldAlias, "課程") is not None
    with session_factory() as session:
        with session.begin():
            session.delete(session.get(MetaField, "course"))   # 刪 canonical（begin 內 get）
    with session_factory() as session:
        assert session.get(MetaFieldAlias, "課程") is None      # alias 連帶刪（CASCADE）
# === [META-NORM C1 END] ===
