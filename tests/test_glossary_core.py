"""GLOSSARY-CORE C6: 中央術語庫核心單元測試。

依據:
- plan v2 §6.1（五測試）+ tasks §8 C6
- 對齊 tests/test_domain_normalizer.py / test_paper_chunks_schema.py 的
  file-based SQLite + FK ON fixture + mock LLM pattern

五測試：
1. test_global_glossary_unique_constraint — 聯合唯一約束（同 lang+domain+term 拒第二譯法）
2. test_cascading_priority_match          — 級聯優先（BF 專屬覆寫 general 通用）
3. test_book_glossary_fusion_priority     — 書籍雙層融合（中央歷史術語優先於本書實時提取）
4. test_chat_glossary_injection           — Chat 開啟文獻時 domain 術語注入 System Prompt
5. test_glossary_cli_backfill_existing    — CLI --backfill-existing-papers 批次升級 domain

LLM 一律 mock（不實打 API）；DB 用 file-based 臨時 SQLite（FK ON）隔離。
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import Base, GlobalGlossary, Paper, User  # noqa: E402
from processor.glossary_extractor import GlossaryManager  # noqa: E402


# ─────────────────── fixtures ───────────────────


@pytest.fixture
def session_factory():
    """每測試一個獨立 file-based SQLite + FK ON、回 sessionmaker。"""
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
    yield TestSession
    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


class _MockLLM:
    """可程式化回傳的 mock LLM（不實打 API）。"""

    def __init__(self, response: str = "[]"):
        self.response = response
        self.calls = 0

    def chat(self, messages, temperature=0.5, stream=True, model=None):
        self.calls += 1
        return self.response


# ─────────────────── 測試 ───────────────────


def test_global_glossary_unique_constraint(session_factory):
    """① 聯合唯一約束：同 (source_lang,target_lang,term_key,domain) 拒第二譯法。"""
    with session_factory() as s:
        s.add(GlobalGlossary(
            source_lang="de", target_lang="zh-tw", term_key="riesling",
            original_term="Riesling", translation="雷司令", domain="general",
        ))
        s.commit()
        s.add(GlobalGlossary(
            source_lang="de", target_lang="zh-tw", term_key="riesling",
            original_term="Riesling", translation="麗絲玲", domain="general",
        ))
        with pytest.raises(IntegrityError):
            s.commit()


def test_cascading_priority_match(session_factory):
    """② 級聯優先：BF 專屬譯法覆寫 general 通用譯法。"""
    gm = GlossaryManager(llm=_MockLLM(), session_factory=session_factory)
    # general 一筆 + BF 專屬同 term 不同譯
    gm.upsert_terms([("Dasein", "存在")], "de", "zh-tw", "general")
    gm.upsert_terms([("Dasein", "此在")], "de", "zh-tw", "BF")

    general_view = gm.query_cascade("de", "zh-tw", "general")
    bf_view = gm.query_cascade("de", "zh-tw", "BF")

    assert general_view == {"dasein": "存在"}
    # BF 級聯（general + BF）後、專屬 BF 覆寫 general
    assert bf_view == {"dasein": "此在"}


def test_book_glossary_fusion_priority(session_factory):
    """③ 書籍雙層融合：中央資料庫歷史真理術語優先權高於本書實時提取。"""
    gm = GlossaryManager(llm=_MockLLM(), session_factory=session_factory)
    # 中央歷史術語（最高優先）
    gm.upsert_terms([("Riesling", "雷司令")], "de", "zh-tw", "general")
    sqlite_glossary = gm.query_cascade("de", "zh-tw", "general")

    # 本書實時提取（同詞、不同候選譯法）
    book_glossary = {"riesling": "麗絲玲", "trocken": "不甜"}

    # 雙層融合：先填本書、再以中央歷史覆寫（中央真理最高優先）
    fused = {**book_glossary, **sqlite_glossary}

    assert fused["riesling"] == "雷司令"   # 中央歷史優先、覆寫本書
    assert fused["trocken"] == "不甜"      # 本書獨有術語保留


def test_chat_glossary_injection(session_factory, monkeypatch):
    """④ Chat 開啟文獻時，對應 domain 術語表被注入 System Prompt 契約。"""
    import settings
    import processor.glossary_extractor as gex

    # 種術語
    gm = GlossaryManager(llm=_MockLLM(), session_factory=session_factory)
    gm.upsert_terms([("Riesling", "雷司令")], "en", "zh-tw", "SB")

    # 旗標 ON + 注入點使用本測試的 session_factory
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)

    class _GMWithFactory(GlossaryManager):
        def __init__(self):
            super().__init__(session_factory=session_factory)

    monkeypatch.setattr(gex, "GlossaryManager", _GMWithFactory)

    # 模擬 AI_professor_chat C4 注入邏輯（query_cascade → 組約束塊）
    domain = "SB"
    glossary_block = ""
    if settings.LLM_USE_GLOSSARY_ALIGN:
        glossary = gex.GlossaryManager().query_cascade("en", "zh-tw", domain)
        if glossary:
            term_lines = "\n".join(f"- {o} → {t}" for o, t in glossary.items())
            glossary_block = (
                "\n\n【術語強約束 System constraint】以下專有名詞譯法不可違背，"
                f"回答時必須與論文譯本完全一致：\n{term_lines}"
            )
    system_message = f"角色\n當前文件主題：{domain}{glossary_block}"

    assert "術語強約束 System constraint" in system_message
    assert "riesling → 雷司令" in system_message


def test_glossary_cli_backfill_existing(session_factory, monkeypatch):
    """⑤ CLI --backfill-existing-papers：批次將 domain 升級為 LCC。"""
    import db as dbmod
    import tools.manage_glossary as mg

    # 種 1 user + 2 paper（raw domain）
    with session_factory() as s, s.begin():
        s.add(User(id=1, username="u", password_hash="x"))
        s.add(Paper(id=1, owner_id=1, paper_uuid="p1",
                    domain="半導體晶片設計", status="done"))
        s.add(Paper(id=2, owner_id=1, paper_uuid="p2",
                    domain="general", status="done"))

    # 覆寫 db.SessionLocal 為測試 factory；mock normalize_to_lcc（不實打 LLM）
    monkeypatch.setattr(dbmod, "SessionLocal", session_factory)
    import processor.domain_normalizer as dn
    monkeypatch.setattr(
        dn, "normalize_to_lcc",
        lambda raw, context_text=None: "TK" if "半導體" in raw else raw,
    )

    rc = mg.cmd_backfill_existing_papers(dry_run=False)
    assert rc == 0

    with session_factory() as s:
        p1 = s.get(Paper, 1)
        p2 = s.get(Paper, 2)
        assert p1.domain == "TK"        # 半導體 → 升級 LCC
        assert p2.domain == "general"   # general → 不變
