"""PIPE-LITEDOC 測試（第 3 路 news/web/unknown）。

C2：策略分派——`get_strategy('litedoc'/'news'/'web')` 回 LiteDocPipeline、未知 doc_type
經 factory fallback 亦回 LiteDocPipeline。後續 C3-C7 追加 P1-P4 契約 + §7.2 key-changing 整合。
"""

import pytest

import pipelines  # 觸發 __init__ 註冊（litedoc_pipeline import）  # noqa: F401
from pipelines.factory import PipelineFactory
from pipelines.litedoc_pipeline import LiteDocPipeline


# ──────────────────────────────────────────────────────────────────────────
# C2：三 key 註冊 + unknown fallback 分派
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("doc_type", ["litedoc", "news", "web"])
def test_litedoc_registered_keys_dispatch(doc_type):
    """litedoc / news / web 三 key 皆分派至 LiteDocPipeline。"""
    strat = PipelineFactory.get_strategy(doc_type)
    assert isinstance(strat, LiteDocPipeline)


def test_unknown_doc_type_falls_back_to_litedoc():
    """未知 doc_type → factory fallback（_FALLBACK_DOC_TYPE='litedoc'）→ LiteDocPipeline。"""
    strat = PipelineFactory.get_strategy("某種未註冊文體_xyz")
    assert isinstance(strat, LiteDocPipeline)


def test_litedoc_rag_char_threshold_is_10():
    """litedoc 為長篇散文型、RAG 門檻 ≥10（非 slides/resume ≥3）。"""
    assert LiteDocPipeline().rag_char_threshold == 10


@pytest.mark.parametrize("phase", ["run_phase2", "run_phase3", "run_phase4"])
def test_litedoc_phases_are_strict_stub(phase):
    """C2 骨架：P2-P4 仍為 strict stub、拋 NotImplementedError（C4-C6 才實作；P1 已於 C3 實作）。"""
    strat = LiteDocPipeline()
    with pytest.raises(NotImplementedError):
        getattr(strat, phase)(None)


# ──────────────────────────────────────────────────────────────────────────
# C3：P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）
# ──────────────────────────────────────────────────────────────────────────
import json as _json
from pathlib import Path

import settings
from pipelines import litedoc_pipeline as lp
from pipelines.context import PipelineContext
from pipelines.contracts import IngestionMetadataSpec


def _setup_p1_mocks(monkeypatch, tmp_path, *, llm_json, capture=None):
    """patch 攝入 processor + LLM + 旗標；capture dict 記 DocAnalyzer 收到的 doc_type。"""
    md = tmp_path / "doc.md"

    class _FakePDF:
        def parse(self, pdf, outdir):
            md.write_text("# Sample Headline\n\nBody text here.", encoding="utf-8")
            return str(md)

    class _FakeCleaner:
        def clean(self, p):
            return p

    class _FakeAnalyzer:
        def analyze(self, p, doc_type):
            if capture is not None:
                capture["analyzer_doc_type"] = doc_type
            return p

    class _FakeMd:
        def process(self, a, b):
            Path(b).write_text("{}", encoding="utf-8")

    class _FakeJson:
        def process(self, a, b):
            Path(b).write_text("{}", encoding="utf-8")

    class _FakeTiling:
        def process(self, a, b, doc_type=""):
            Path(b).write_text(
                _json.dumps({"sections": [
                    {"title": "Sample Headline",
                     "content": [{"type": "text", "content": "Body text here."}], "children": []}
                ]}), encoding="utf-8")
            return Path(b)

    class _FakeLLM:
        def chat(self, messages=None, **kw):
            return llm_json

    monkeypatch.setattr(lp, "PDFProcessor", _FakePDF)
    monkeypatch.setattr(lp, "MarkdownCleaner", _FakeCleaner)
    monkeypatch.setattr(lp, "DocAnalyzer", _FakeAnalyzer)
    monkeypatch.setattr(lp, "MarkdownProcessor", _FakeMd)
    monkeypatch.setattr(lp, "JsonProcessor", _FakeJson)
    monkeypatch.setattr(lp, "TilingProcessor", _FakeTiling)
    import llm.client
    monkeypatch.setattr(llm.client.LLMClient, "get_instance", classmethod(lambda cls: _FakeLLM()))
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(settings, "LLM_USE_META_NORM", False)   # 飛輪關：normalize_fields 直回原樣


def _p1_ctx(tmp_path, doc_type="news", paper_id="p1"):
    pdf = tmp_path / "in.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    return PipelineContext(doc_type=doc_type, paper_id=paper_id, pdf_path=str(pdf), owner_id=1)


def test_p1_delivers_ingestion_spec(monkeypatch, tmp_path):
    """P1 交付 IngestionMetadataSpec：title/authors/venue（publisher）/source_lang/tiles。"""
    llm_json = _json.dumps({
        "title": "Big AI News", "authors": ["John Doe", "Jane Roe"],
        "date": "2026-06-19", "publisher": "CNN", "url": "https://cnn.com/x",
    })
    _setup_p1_mocks(monkeypatch, tmp_path, llm_json=llm_json)
    spec = LiteDocPipeline().run_phase1(_p1_ctx(tmp_path))
    assert isinstance(spec, IngestionMetadataSpec)
    assert spec.title == "Big AI News"
    assert spec.authors == ["John Doe", "Jane Roe"]
    assert spec.venue == "CNN"                       # publisher 承接 venue
    assert spec.source_lang == "en"
    assert len(spec.tiles) == 1


def test_p1_raw_metadata_sidechannel(monkeypatch, tmp_path):
    """date/url/organization 走 ctx.raw_metadata 旁路；publisher 亦入旁路（值 dict）。"""
    llm_json = _json.dumps({
        "title": "T", "authors": [], "date": "2026-06-19",
        "publisher": "Reuters", "url": "https://reuters.com/a",
    })
    _setup_p1_mocks(monkeypatch, tmp_path, llm_json=llm_json)
    ctx = _p1_ctx(tmp_path)
    LiteDocPipeline().run_phase1(ctx)
    assert ctx.raw_metadata["date"]["value"] == "2026-06-19"
    assert ctx.raw_metadata["url"]["value"] == "https://reuters.com/a"
    assert ctx.raw_metadata["publisher"]["value"] == "Reuters"


def test_p1_url_publisher_decode(monkeypatch, tmp_path):
    """URL→publisher 解碼：LLM 由 nytimes.com 解出 publisher（cover-prompt 指引），承接 venue。"""
    llm_json = _json.dumps({
        "title": "T", "authors": [], "date": "",
        "publisher": "The New York Times", "url": "https://nytimes.com/x",
    })
    _setup_p1_mocks(monkeypatch, tmp_path, llm_json=llm_json)
    spec = LiteDocPipeline().run_phase1(_p1_ctx(tmp_path))
    assert spec.venue == "The New York Times"


@pytest.mark.parametrize("doc_type,expected", [
    ("news", "news"), ("web", "web"), ("litedoc", "web"), ("某未知", "web"),
])
def test_p1_docanalyzer_mapping(monkeypatch, tmp_path, doc_type, expected):
    """U2.1：news/web 原樣傳 DocAnalyzer；litedoc/unknown → 'web' 扁平 prompt（防 fallback academic）。"""
    cap = {}
    _setup_p1_mocks(monkeypatch, tmp_path, llm_json='{"title":"T","authors":[]}', capture=cap)
    LiteDocPipeline().run_phase1(_p1_ctx(tmp_path, doc_type=doc_type))
    assert cap["analyzer_doc_type"] == expected


def test_p1_shadow_title_suffix(monkeypatch, tmp_path):
    """_shadow paper_id → title 綴 (測試)。"""
    _setup_p1_mocks(monkeypatch, tmp_path, llm_json='{"title":"News X","authors":[]}')
    spec = LiteDocPipeline().run_phase1(_p1_ctx(tmp_path, paper_id="p1_shadow"))
    assert spec.title == "News X (測試)"
