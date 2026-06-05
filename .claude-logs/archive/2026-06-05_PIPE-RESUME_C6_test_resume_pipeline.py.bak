# === [PIPE-RESUME C6 START] ===
"""PIPE-RESUME C6：ResumePipeline 策略分派與四 Phase 契約單元測試。

依據：plan §6.1 + tasks §8 C6。全程 mock LLM/Embedding（不實打 API）；
以 monkeypatch 隔離既有 processor 與真理源，驗證四 Phase 合約交付與關鍵行為。
"""
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import paper_manager  # noqa: E402
import settings  # noqa: E402
import pipelines.resume_pipeline as rp  # noqa: E402
from pipelines.context import PipelineContext  # noqa: E402
from pipelines.contracts import (  # noqa: E402
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory  # noqa: E402
from pipelines.resume_pipeline import ResumePipeline  # noqa: E402
from processor.rag_processor import _is_chunk_meaningful  # noqa: E402


def _doc(text: str):
    """最小 LangChain Document 替身（_is_chunk_meaningful 只讀 page_content）。"""
    return types.SimpleNamespace(page_content=text, metadata={})


def _ctx(**kw) -> PipelineContext:
    base = dict(doc_type="resume", paper_id="p1", pdf_path="/tmp/p1.pdf", owner_id=7)
    base.update(kw)
    return PipelineContext(**base)


# ─────────────────── 1. 策略分派 ───────────────────


def test_factory_dispatch_resume():
    """① get_strategy('resume') 回 ResumePipeline 實例、門檻 ≥3。"""
    s = PipelineFactory.get_strategy("resume")
    assert type(s).__name__ == "ResumePipeline"
    assert isinstance(s, ResumePipeline)
    assert s.rag_char_threshold == 3


def test_no_doctype_branch_in_strategy():
    """② 策略內無 doc_type 硬編碼路由分支（doc_type 僅作參數/風格傳遞）。"""
    import inspect

    src = inspect.getsource(rp)
    assert "doc_type ==" not in src
    assert "doc_type==" not in src


# ─────────────────── 2. P1 私有輔助（純邏輯）───────────────────


def test_detect_source_lang():
    """③ source_lang 啟發式：CJK 顯著 → zh、ASCII → en。"""
    assert ResumePipeline._detect_source_lang("這是一份中文履歷內容範例" * 3) == "zh"
    assert ResumePipeline._detect_source_lang("John Doe Software Engineer Python") == "en"


def test_extract_contact():
    """④ phone/email regex 抽取（既有 metadata_extractor 無此二欄）。"""
    s = ResumePipeline()
    phone, email = s._extract_contact("Email: john@example.com Tel: 0912-345-678")
    assert email == "john@example.com"
    assert "912" in phone


def test_resolve_title_priority():
    """⑤ title：candidate_name（最可信）→ 首個 # 行 → paper_name。"""
    s = ResumePipeline()
    assert s._resolve_title({"candidate_name": {"value": "王小明"}}, "# 別人\n", "stem") == "王小明"
    assert s._resolve_title({}, "# 李大華\n內容", "stem") == "李大華"
    assert s._resolve_title({}, "no heading line", "stem") == "stem"


def test_load_tiles(tmp_path):
    """⑥ tiled JSON：dict→取 sections list、list→直接用。"""
    f = tmp_path / "t.json"
    f.write_text(json.dumps({"sections": [{"a": 1}]}), encoding="utf-8")
    assert ResumePipeline._load_tiles(f) == [{"a": 1}]
    f.write_text(json.dumps([{"x": 2}]), encoding="utf-8")
    assert ResumePipeline._load_tiles(f) == [{"x": 2}]


# ─────────────────── 3. P1 Ingestion 契約 ───────────────────


def _mock_p1_processors(monkeypatch):
    class FakeRP:
        def __init__(self, *a, **k):
            pass

        def parse(self, pdf, outdir):
            md = Path(outdir) / "p1.md"
            md.write_text("# 王小明\nPython Docker 工程師\njohn@x.com", encoding="utf-8")
            return str(md)

    class FakeDA:
        def __init__(self, *a, **k):
            pass

        def analyze(self, p, dt):
            return p

    class FakeMd:
        def __init__(self, *a, **k):
            pass

        def process(self, i, o):
            Path(o).write_text(json.dumps({"sections": []}), encoding="utf-8")
            return o

    class FakeTiling:
        def __init__(self, *a, **k):
            pass

        def process(self, i, o, doc_type=""):
            Path(o).write_text(
                json.dumps({"sections": [{"type": "text"}]}), encoding="utf-8"
            )
            return o

    monkeypatch.setattr(rp, "ResumeProcessor", FakeRP)
    monkeypatch.setattr(rp, "DocAnalyzer", FakeDA)
    monkeypatch.setattr(rp, "MarkdownProcessor", FakeMd)
    monkeypatch.setattr(rp, "JsonProcessor", FakeMd)
    monkeypatch.setattr(rp, "TilingProcessor", FakeTiling)
    monkeypatch.setattr(
        ResumePipeline, "_extract_metadata",
        lambda self, p: {
            "candidate_name": {"value": "王小明"},
            "domain": {"value": "程式設計"},
        },
    )


def test_run_phase1_contract(tmp_path, monkeypatch):
    """⑦ P1 交付 IngestionMetadataSpec：title=candidate_name、不含 Abstract/LCC/Glossary、_raw_meta 穿線。"""
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)
    _mock_p1_processors(monkeypatch)
    pdf = tmp_path / "p1.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    s = ResumePipeline()
    spec = s.run_phase1(_ctx(pdf_path=str(pdf)))

    assert isinstance(spec, IngestionMetadataSpec)
    assert spec.title == "王小明"
    # 不含 Abstract/LCC/Glossary：凍結合約結構保證（extra='forbid'）
    for forbidden in ("abstract", "lcc", "glossary", "translated_abstract", "domain_name"):
        assert not hasattr(spec, forbidden)
    assert len(spec.tiles) == 1
    # interim 穿線（custom_metadata 硬前置）
    assert s._raw_meta["domain"] == "程式設計"
    assert s._raw_meta["email"] == "john@x.com"


# ─────────────────── 4. P2 Glossary & Context Prep 契約 ───────────────────


def _mock_p2_common(monkeypatch, summary="原文摘要", translated="中文摘要", domain_name="Computer Science"):
    class FakeTr:
        def __init__(self, *a, **k):
            pass

        def translate(self, text, ctx, mode, text_type="content"):
            return translated

    monkeypatch.setattr(rp, "Translator", FakeTr)
    monkeypatch.setattr(ResumePipeline, "_read_source_text", lambda self, ctx: "履歷全文 Python")
    monkeypatch.setattr(ResumePipeline, "_make_summary", lambda self, t: summary)
    monkeypatch.setattr(ResumePipeline, "_resolve_domain_name", lambda self, lcc: domain_name)


def _ctx_with_ingestion(source_lang="en"):
    ctx = _ctx()
    ctx.ingestion = IngestionMetadataSpec(title="王小明", source_lang=source_lang, tiles=[])
    return ctx


def test_run_phase2_flag_off(monkeypatch):
    """⑧ 旗標 OFF：glossary={}、lcc=raw（normalize 直回）、abstract/translated/domain_name 交付。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    monkeypatch.setattr(rp, "normalize_to_lcc", lambda raw, context_text=None: raw or "general")
    _mock_p2_common(monkeypatch)
    s = ResumePipeline()
    s._raw_meta = {"domain": "程式設計"}
    spec = s.run_phase2(_ctx_with_ingestion())
    assert isinstance(spec, GlossaryReadySpec)
    assert spec.abstract == "原文摘要"
    assert spec.translated_abstract == "中文摘要"
    assert spec.domain_name == "Computer Science"
    assert spec.glossary == {}
    assert spec.lcc == "程式設計"


def test_run_phase2_lcc_fallback_general(monkeypatch):
    """⑨ raw_domain 為空 → lcc fallback 'general'。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    monkeypatch.setattr(rp, "normalize_to_lcc", lambda raw, context_text=None: raw or "")
    _mock_p2_common(monkeypatch)
    s = ResumePipeline()
    s._raw_meta = {"domain": ""}
    spec = s.run_phase2(_ctx_with_ingestion())
    assert spec.lcc == "general"


def test_run_phase2_glossary_selfheal_injects_summary_and_lcc(monkeypatch):
    """⑩ 旗標 ON 缺詞自癒：extract_terms 注入原文摘要(source_text)與 LCC(domain)、upsert 冪等。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)
    monkeypatch.setattr(rp, "normalize_to_lcc", lambda raw, context_text=None: "QA")
    _mock_p2_common(monkeypatch)
    captured = {}

    class FakeGM:
        def __init__(self, *a, **k):
            pass

        def query_cascade(self, s, t, domain):
            return {}  # 缺詞

        def extract_terms(self, src, tgt, s, t, domain):
            captured.update(src=src, tgt=tgt, domain=domain)
            return [("Python", "派森")]

        def upsert_terms(self, pairs, s, t, domain):
            captured["upsert"] = len(pairs)
            return len(pairs)

    monkeypatch.setattr(rp, "GlossaryManager", FakeGM)
    s = ResumePipeline()
    s._raw_meta = {"domain": "程式設計"}
    spec = s.run_phase2(_ctx_with_ingestion())
    assert captured["src"] == "原文摘要"     # 原文摘要注入抽詞 source
    assert captured["tgt"] == "中文摘要"     # 譯文摘要為 translated（雙用）
    assert captured["domain"] == "QA"        # LCC 注入 domain
    assert captured["upsert"] == 1
    assert spec.glossary == {"Python": "派森"}


def test_run_phase2_cache_hit_zero_extract(monkeypatch):
    """⑪ query_cascade 命中（cache hit）→ 不呼 extract_terms（0 抽詞 LLM）。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)
    monkeypatch.setattr(rp, "normalize_to_lcc", lambda raw, context_text=None: "QA")
    _mock_p2_common(monkeypatch)

    class FakeGM:
        def __init__(self, *a, **k):
            pass

        def query_cascade(self, s, t, domain):
            return {"AI": "人工智慧"}  # 命中

        def extract_terms(self, *a, **k):
            raise AssertionError("cache hit 不應呼叫 extract_terms")

        def upsert_terms(self, *a, **k):
            raise AssertionError("cache hit 不應呼叫 upsert_terms")

    monkeypatch.setattr(rp, "GlossaryManager", FakeGM)
    s = ResumePipeline()
    s._raw_meta = {"domain": "程式設計"}
    spec = s.run_phase2(_ctx_with_ingestion())
    assert spec.glossary == {"AI": "人工智慧"}


# ─────────────────── 5. P3 Translation & Restore 契約 ───────────────────


def test_run_phase3_bypass_doctype_and_carryforward(tmp_path, monkeypatch):
    """⑫ P3：100% Bypass（整份 1 次 content 翻譯）、InjectionContext.doc_type='resume'、translated_abstract 沿用 P2。"""
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)
    captured = {}

    class FakeTr:
        def __init__(self, *a, **k):
            pass

        def translate(self, text, ctx, mode, text_type="content"):
            captured["ctx"] = ctx
            captured["text_type"] = text_type
            captured["calls"] = captured.get("calls", 0) + 1
            return "中文譯文"

    monkeypatch.setattr(rp, "Translator", FakeTr)
    monkeypatch.setattr(
        ResumePipeline, "_read_source_text", lambda self, ctx: "English resume Python"
    )
    s = ResumePipeline()
    ctx = _ctx()
    ctx.ingestion = IngestionMetadataSpec(title="x", source_lang="en", tiles=[])
    ctx.glossary_ready = GlossaryReadySpec(
        abstract="a", lcc="QA", glossary={"Python": "派森"},
        translated_abstract="中文摘要", domain_name="CS",
    )
    spec = s.run_phase3(ctx)

    assert isinstance(spec, BilingualMarkdownSpec)
    assert captured["calls"] == 1                     # 100% Bypass：整份一次
    assert captured["text_type"] == "content"
    assert captured["ctx"].doc_type == "resume"       # 正式商務中文風格
    assert captured["ctx"].zh_summary == "中文摘要"    # zh_summary←translated_abstract
    assert spec.translated_abstract == "中文摘要"      # 沿用 P2（必填）
    assert Path(spec.final_zh_path).read_text(encoding="utf-8") == "中文譯文"
    assert Path(spec.final_en_path).read_text(encoding="utf-8") == "English resume Python"


# ─────────────────── 6. P4 Async RAG ───────────────────


def test_is_chunk_meaningful_resume_threshold():
    """⑬ P4 過濾：resume ≥3 保技能詞、email/phone/url 保留、純數字/空過濾、academic ≥10。"""
    assert _is_chunk_meaningful(_doc("Python"), "resume") is True
    assert _is_chunk_meaningful(_doc("Docker"), "resume") is True
    assert _is_chunk_meaningful(_doc("john@example.com"), "resume") is True   # email
    assert _is_chunk_meaningful(_doc("0912-345-678"), "resume") is True       # phone
    assert _is_chunk_meaningful(_doc("https://github.com/x"), "resume") is True  # url
    assert _is_chunk_meaningful(_doc("2024"), "resume") is False              # 純數字
    assert _is_chunk_meaningful(_doc(""), "resume") is False                  # 空
    assert _is_chunk_meaningful(_doc("Python"), "academic") is False          # academic ≥10


def test_run_phase4_failure_isolation(tmp_path, monkeypatch):
    """⑭ P4 失敗隔離：拋出（交 Orchestrator 標 failed）、不動 reading_ready。"""
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(rp.paper_manager, "get_paper_db_id", lambda o, p: None)

    class FakeRag:
        def __init__(self, *a, **k):
            pass

        def _create_vector_store(self, *a, **k):
            raise RuntimeError("embed fail")

    monkeypatch.setattr(rp, "RagProcessor", FakeRag)
    s = ResumePipeline()
    ctx = _ctx()
    ctx.bilingual = BilingualMarkdownSpec(
        final_zh_path=str(tmp_path / "zh.md"), final_en_path=str(tmp_path / "en.md"),
        translated_abstract="x",
    )
    ctx.reading_ready = True  # 主鏈已解鎖
    with pytest.raises(RuntimeError):
        s.run_phase4(ctx)
    assert ctx.reading_ready is True  # P4 失敗不影響主鏈


def test_run_phase4_success(tmp_path, monkeypatch):
    """⑮ P4 成功：讀 index_meta.json（chunks_total）交付 RagDbSpec。"""
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(rp.paper_manager, "get_paper_db_id", lambda o, p: 42)

    class FakeRag:
        def __init__(self, *a, **k):
            pass

        def _create_vector_store(self, md, vpath, doc_type="", paper_db_id=None):
            Path(vpath).mkdir(parents=True, exist_ok=True)
            (Path(vpath) / "index_meta.json").write_text(
                json.dumps({"chunks_total": 5}), encoding="utf-8"
            )
            return vpath

    monkeypatch.setattr(rp, "RagProcessor", FakeRag)
    s = ResumePipeline()
    ctx = _ctx()
    ctx.bilingual = BilingualMarkdownSpec(
        final_zh_path=str(tmp_path / "zh.md"), final_en_path="x", translated_abstract="x",
    )
    spec = s.run_phase4(ctx)
    assert isinstance(spec, RagDbSpec)
    assert spec.paper_chunk_count == 5
    assert spec.index_meta["chunks_total"] == 5
# === [PIPE-RESUME C6 END] ===
