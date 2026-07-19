# === [GLOSSARY-TERMMAP C1] ===
"""GLOSSARY-TERMMAP C1：build_termmap（事前定案術語表）單元測試。

依 plan v2 §2.1 五步硬規格 + tasks §8 C1 ⑤：
N1 切塊三態 / N2 census 只認詞（單塊失敗 soft）/ N3a 正規化去重 /
**N3b 廢早退回歸（Q1：DB 已有詞仍抽仍寫）** / N4 已知詞零翻譯呼叫 /
N5 定案 upsert 屬性 / builder 整體失敗軟降級。

LLM 一律 mock（不實打 API）；DB 沿 test_glossary_core file-based SQLite fixture 範式。
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import Base, GlobalGlossary  # noqa: E402
from processor import glossary_extractor as ge  # noqa: E402
from processor.glossary_extractor import GlossaryManager  # noqa: E402


# ─────────────────── fixtures ───────────────────


@pytest.fixture
def session_factory():
    """每測試一個獨立 file-based SQLite + FK ON（沿 test_glossary_core 範式）。"""
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


class _TermmapMockLLM:
    """路由式 mock：census prompt 回專名陣列、翻譯 prompt 回逐行 [i] 譯法。"""

    def __init__(self, census_terms=None, fail_census_on_call=None):
        self.census_terms = census_terms if census_terms is not None else []
        self.fail_census_on_call = fail_census_on_call
        self.census_calls = 0
        self.translate_calls = 0
        self.last_translate_terms = []

    def chat(self, messages, temperature=0.5, stream=True, model=None):
        system = messages[0]["content"]
        user = messages[-1]["content"]
        if "普查器" in system:                      # census 路
            self.census_calls += 1
            if self.fail_census_on_call == self.census_calls:
                raise RuntimeError("census boom")
            return json.dumps(self.census_terms, ensure_ascii=False)
        if "術語翻譯" in system:                    # N4 批次翻譯路
            self.translate_calls += 1
            lines = []
            self.last_translate_terms = []
            for ln in user.splitlines():
                if ln.strip().startswith("["):
                    idx, term = ln.strip().split("] ", 1)
                    self.last_translate_terms.append(term)
                    # 確定性譯法：SpaceX 類慣例不譯詞回原文、其餘加 [譯] 前綴
                    out = term if term == "SpaceX" else f"[譯]{term}"
                    lines.append(f"{idx}] {out}")
            return "\n".join(lines)
        raise AssertionError(f"未知 prompt 路由: {system[:30]}")


def _seed(session_factory, term_key, translation, domain="tech"):
    with session_factory() as s:
        with s.begin():
            s.add(GlobalGlossary(
                source_lang="en", target_lang="zh-tw", term_key=term_key,
                original_term=term_key, translation=translation,
                domain=domain, source="seed",
            ))


def _rows(session_factory):
    with session_factory() as s:
        return list(s.execute(select(GlobalGlossary)).scalars().all())


# ─────────────────── N1 切塊 ───────────────────


class TestSplitCensusChunks:
    def test_paragraph_boundary_accumulation(self):
        text = "\n\n".join(f"para{i} " + "x" * 50 for i in range(10))
        chunks = GlossaryManager._split_census_chunks(text, 120)
        assert len(chunks) > 1
        # 不切句中：每塊皆由完整段落組成
        for c in chunks:
            for p in c.split("\n\n"):
                assert p.startswith("para")

    def test_oversized_single_paragraph_own_chunk(self):
        text = "short one\n\n" + "y" * 500 + "\n\nshort two"
        chunks = GlossaryManager._split_census_chunks(text, 100)
        assert any(len(c) > 100 for c in chunks)     # 超長段自成一塊、不硬切

    def test_short_text_single_chunk_and_empty(self):
        assert len(GlossaryManager._split_census_chunks("a\n\nb", 6000)) == 1
        assert GlossaryManager._split_census_chunks("", 6000) == []


# ─────────────────── N2 census ───────────────────


class TestCensus:
    def test_census_prompt_forbids_translation(self):
        assert "不要翻譯" in ge._CENSUS_SYSTEM_PROMPT or "不翻譯" in ge._CENSUS_SYSTEM_PROMPT.replace("絕對不要翻譯", "不翻譯")
        assert "JSON 字串陣列" in ge._CENSUS_SYSTEM_PROMPT

    def test_single_chunk_failure_is_soft(self, session_factory):
        llm = _TermmapMockLLM(census_terms=["SpaceX"], fail_census_on_call=1)
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        result = gm.build_termmap(
            "p1\n\np2", "abs", "譯abs", "en", "zh-tw", "tech",
            chunk_chars=3, max_workers=1,     # 兩塊：第 1 塊 census 失敗、第 2 塊成功
        )
        assert llm.census_calls == 2
        assert "spacex" in result             # 第 2 塊仍收詞、整體不阻斷


# ─────────────────── N3 去重與分流（含 Q1 廢早退回歸）───────────────────


class TestDedupAndSplit:
    def test_normalize_dedup_multiform(self, session_factory):
        llm = _TermmapMockLLM(census_terms=["SpaceX", "spacex ", "SPACEX"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        gm.build_termmap("only one para", "a", "b", "en", "zh-tw", "tech")
        # 多形一份：翻譯清單只收到一個 SpaceX 形
        assert len(llm.last_translate_terms) == 1

    def test_no_early_return_when_db_has_terms(self, session_factory):
        """Q1 廢早退回歸：DB 已有詞（舊行為會直接 return）→ 仍 census、仍翻未知、仍寫庫。"""
        _seed(session_factory, "starship", "星艦")
        llm = _TermmapMockLLM(census_terms=["Starship", "Raptor"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        result = gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert llm.census_calls >= 1                      # 未因 DB 有詞而跳過 census
        assert llm.last_translate_terms == ["Raptor"]     # 僅未知詞入翻譯
        assert result["starship"] == "星艦"                # 已知沿用 DB 定譯
        assert result["raptor"] == "[譯]Raptor"           # 新詞入定案表
        keys = {r.term_key for r in _rows(session_factory)}
        assert "raptor" in keys                           # 新詞已寫庫（飛輪滾動）

    def test_known_terms_zero_translate_calls(self, session_factory):
        """N4：census 全為已知詞 → 翻譯呼叫數 0（已知免翻）。"""
        _seed(session_factory, "starship", "星艦")
        llm = _TermmapMockLLM(census_terms=["Starship"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        result = gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert llm.translate_calls == 0
        assert result == {"starship": "星艦"}


# ─────────────────── N4/N5 翻譯與定案寫入 ───────────────────


class TestTranslateAndDecide:
    def test_single_batch_translate_call(self, session_factory):
        """N4：未知詞不論多少、一次批次呼叫。"""
        llm = _TermmapMockLLM(census_terms=["Alpha", "Beta", "Gamma"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert llm.translate_calls == 1

    def test_upsert_source_termmap_decided(self, session_factory):
        llm = _TermmapMockLLM(census_terms=["Raptor"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        rows = _rows(session_factory)
        assert rows and all(r.source == "termmap_decided" for r in rows)

    def test_identical_translation_preserved(self, session_factory):
        """譯法＝原文（慣例不譯詞）原樣入定案表（供免括號約束消費）。"""
        llm = _TermmapMockLLM(census_terms=["SpaceX"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        result = gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert result["spacex"] == "SpaceX"


# ─────────────────── 軟降級 ───────────────────


class TestSoftDegrade:
    def test_builder_failure_falls_back_to_cascade(self, session_factory, monkeypatch):
        _seed(session_factory, "starship", "星艦")
        gm = GlossaryManager(llm=_TermmapMockLLM(), session_factory=session_factory)
        monkeypatch.setattr(
            GlossaryManager, "_split_census_chunks",
            staticmethod(lambda *a: (_ for _ in ()).throw(RuntimeError("boom"))),
        )
        result = gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert result == {"starship": "星艦"}    # 降級回 query_cascade、不阻斷

    def test_translate_failure_returns_known_only(self, session_factory, monkeypatch):
        _seed(session_factory, "starship", "星艦")
        llm = _TermmapMockLLM(census_terms=["Starship", "Raptor"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        monkeypatch.setattr(
            GlossaryManager, "_translate_unknown_terms",
            lambda self, *a, **k: {},            # N4 soft 失敗（回 {}）
        )
        result = gm.build_termmap("para", "a", "b", "en", "zh-tw", "tech")
        assert result == {"starship": "星艦"}    # 已知仍交付、未知該次缺席
        assert all(r.source == "seed" for r in _rows(session_factory))  # 未寫入任何收割物
# === [GLOSSARY-TERMMAP C1 END] ===


# === [GLOSSARY-TERMMAP C2 START] §7.2 跨 Phase 整合測試（WORKFLOW_SOP §7.2、Checkout 必驗）===
class TestCrossPhaseIntegration:
    """P2 build_termmap 定案表 → InjectionContext.glossary → translator 逐單元注入。

    key-changing transform：非同字詞之定案譯文≠原文（`[譯]` 前綴）——純 mock 同 key
    兩端不予承認；斷言接縫不變式：多並行單元注入完全一致（全篇一致之結構性保證）、
    同字定案存在、免括號 System constraint 句存在、旗標關零注入回歸。
    """

    def _build(self, session_factory):
        llm = _TermmapMockLLM(census_terms=["Sentient Sun", "SpaceX", "Starship"])
        gm = GlossaryManager(llm=llm, session_factory=session_factory)
        text = "\n\n".join([
            "para1: Sentient Sun rises over SpaceX.",
            "para2: the Sentient Sun again.",
            "para3: Starship built by SpaceX.",
        ])
        return gm.build_termmap(text, "abs", "譯abs", "en", "zh-tw", "tech")

    def test_termmap_injection_consistent_across_units(self, session_factory, monkeypatch):
        import settings as st
        from processor.translator import InjectionContext, Translator

        termmap = self._build(session_factory)
        # key-changing：非同字詞譯文≠原文；SpaceX 同字定案
        assert termmap["sentient sun"] == "[譯]Sentient Sun"
        assert termmap["spacex"] == "SpaceX"

        monkeypatch.setattr(st, "LLM_USE_GLOSSARY_ALIGN", True)
        inj = InjectionContext(lcc="tech", glossary=termmap, doc_type="news")
        # 模擬 P3 多並行翻譯單元：每單元 system prompt 各自組建
        prompts = [Translator()._build_system_prompt(inj, "content") for _ in range(3)]
        for p in prompts:
            assert "- sentient sun → [譯]Sentient Sun" in p    # 定案行逐單元注入
            assert "- spacex → SpaceX" in p                     # 同字定案行
            assert "不得另加括號注解原文" in p                    # 免括號 System constraint 句
        assert len(set(prompts)) == 1    # 各單元注入完全一致 → 全篇譯法唯一之結構性保證

    def test_flag_off_zero_injection_regression(self, session_factory, monkeypatch):
        import settings as st
        from processor.translator import InjectionContext, Translator

        monkeypatch.setattr(st, "LLM_USE_GLOSSARY_ALIGN", False)
        inj = InjectionContext(lcc="tech", glossary={"a": "乙"}, doc_type="news")
        p = Translator()._build_system_prompt(inj, "content")
        assert "術語強約束" not in p
        assert "不得另加括號注解原文" not in p    # 旗標關＝gated 區塊整段缺席（回歸）
# === [GLOSSARY-TERMMAP C2 END] ===
