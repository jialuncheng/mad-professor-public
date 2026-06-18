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


@pytest.mark.parametrize("phase", ["run_phase1", "run_phase2", "run_phase3", "run_phase4"])
def test_litedoc_phases_are_strict_stub(phase):
    """C2 骨架：四 Phase 為 strict stub、拋 NotImplementedError（防靜默跑空通過）。"""
    strat = LiteDocPipeline()
    with pytest.raises(NotImplementedError):
        getattr(strat, phase)(None)
