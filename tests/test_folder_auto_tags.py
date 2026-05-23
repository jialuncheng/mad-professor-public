"""RAG-1 R3：資料夾自動標籤驗證。

依據:
- plan: .claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md §4.2 + §6.3
- UI Plan v3: .claude-logs/ref/2026-05-23_RAG-1_UI_Fixes_Implementation_Plan.md 附錄 C §2

7 個 case：
1. 移到 HR/CV → 自動加 ['hr', 'cv']
2. 移到 4 層 A/B/C/D → 自動加 ['a', 'b', 'c', 'd']
3. lowercase 標準化（共用 R2 _normalize_tag）
4. 既有 user tag dedup（lowercase 比對、保留 existing 原始）
5. 移到未分類（folder_id=None） → 既有 tag 保留不刪
6. corrupt metadata_json → graceful（不爆、初始化為 {})
7. root → folder + folder → root 對稱
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
from models import Base, Folder, Paper, User  # noqa: E402
import paper_manager  # noqa: E402


# ─────────────────── fixture ───────────────────


@pytest.fixture
def temp_db(monkeypatch):
    """file-based SQLite + FK PRAGMA、沿用既有 fixture pattern。"""
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


def _make_user(s, models_mod, owner_id=1):
    user = s.query(models_mod.User).filter_by(id=owner_id).first()
    if not user:
        user = models_mod.User(
            id=owner_id, username=f'u{owner_id}', password_hash='x'
        )
        s.add(user)
        s.commit()
    return user


def _make_folder_chain(s, models_mod, owner_id, names):
    """建巢狀 folder 鏈 root→leaf、回 leaf folder.id。"""
    parent_id = None
    for name in names:
        f = models_mod.Folder(
            owner_id=owner_id, parent_id=parent_id, name=name, sort_order=0
        )
        s.add(f)
        s.commit()
        parent_id = f.id
    return parent_id  # leaf id


def _make_paper(s, models_mod, owner_id=1, paper_uuid='r3_test',
                initial_metadata=None):
    p = models_mod.Paper(
        owner_id=owner_id,
        paper_uuid=paper_uuid,
        status='ready',
        original_filename=f'{paper_uuid}.pdf',
        metadata_json=json.dumps(initial_metadata or {}),
    )
    s.add(p)
    s.commit()
    return p


def _read_user_tags(db_mod_p, models_mod, paper_uuid):
    with db_mod_p.SessionLocal() as s:
        p = s.query(models_mod.Paper).filter_by(paper_uuid=paper_uuid).one()
        meta = json.loads(p.metadata_json) if p.metadata_json else {}
        return list(meta.get("user_tags", []) or [])


# ─────────────────── 1. 基本：移到 HR/CV ───────────────────


def test_move_paper_to_folder_auto_adds_path_tags(temp_db):
    """移到 HR/CV → 自動加 ['hr', 'cv'](lowercase + 2 層)。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['HR', 'CV'])
        _make_paper(s, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_test')
    assert tags == ['hr', 'cv']


# ─────────────────── 2. 多層（4 層）─────────────────


def test_move_to_nested_folder_adds_all_levels(temp_db):
    """移到 4 層 A/B/C/D → 自動加 ['a','b','c','d']。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['A', 'B', 'C', 'D'])
        _make_paper(s, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_test')
    assert tags == ['a', 'b', 'c', 'd']


# ─────────────────── 3. lowercase 標準化（v3 強化整合）─────────


def test_auto_tag_lowercase_standardization(temp_db):
    """大寫 folder 名 → 自動加 lowercase tag（共用 _normalize_tag）。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['ENGINEERING', 'BackEnd'])
        _make_paper(s, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_test')
    assert tags == ['engineering', 'backend']


# ─────────────────── 4. dedup：既有 user tag 不重複（lowercase 比對）─


def test_auto_tag_dedups_against_existing(temp_db):
    """既有 user_tags 含 'hr'、移到 HR/CV → 只新增 'cv'、不重複加 'hr'。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['HR', 'CV'])
        _make_paper(s, models_mod, initial_metadata={
            "user_tags": ["hr", "manual_tag"]
        })

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_test')
    # 既有 ['hr', 'manual_tag'] + 自動加 'cv'（'hr' 已存在不重複）
    assert tags == ['hr', 'manual_tag', 'cv']


# ─────────────────── 5. 移到未分類（folder_id=None）：舊 tag 保留 ───


def test_move_to_unclassified_keeps_existing_tags(temp_db):
    """從 HR/CV 移回未分類（folder_id=None） → 既有自動 tag 保留不刪（Q6/Q7）。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['HR', 'CV'])
        _make_paper(s, models_mod)

    # 先移到 HR/CV、自動加 ['hr', 'cv']
    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)
    assert _read_user_tags(db_mod_p, models_mod, 'r3_test') == ['hr', 'cv']

    # 再移回未分類、tag 應保留
    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', None)
    assert _read_user_tags(db_mod_p, models_mod, 'r3_test') == ['hr', 'cv']


# ─────────────────── 6. corrupt metadata_json → graceful ───────────


def test_apply_helper_handles_corrupt_metadata_json(temp_db):
    """metadata_json 為非 dict / 非 JSON 時、不爆、初始化為 {}、補上自動 tag。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['HR'])
        # 故意寫 corrupt JSON
        p = models_mod.Paper(
            owner_id=1, paper_uuid='r3_corrupt',
            status='ready', original_filename='r3_corrupt.pdf',
            metadata_json='not a valid json',
        )
        s.add(p)
        s.commit()

    # 移到 HR、不應該爆、且應補上 'hr'
    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_corrupt', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_corrupt')
    assert tags == ['hr']


# ─────────────────── 7. 中文 folder 保留原樣（_normalize_tag 對中文無效）─


def test_chinese_folder_name_preserved_as_tag(temp_db):
    """中文 folder 名 → 自動加保留原樣（中文 `.lower()` 無效）。"""
    db_mod_p, models_mod, pm = temp_db
    with db_mod_p.SessionLocal() as s:
        _make_user(s, models_mod)
        leaf_id = _make_folder_chain(s, models_mod, 1, ['人資', '履歷'])
        _make_paper(s, models_mod)

    with db_mod_p.SessionLocal() as s:
        pm.set_paper_folder(s, 1, 'r3_test', leaf_id)

    tags = _read_user_tags(db_mod_p, models_mod, 'r3_test')
    assert tags == ['人資', '履歷']
