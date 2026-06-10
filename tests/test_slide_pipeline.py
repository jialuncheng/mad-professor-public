"""PIPE-SLIDES：SlidePipeline 簡報策略管線 pytest。

C1：Factory 策略分派與註冊（含 pipelines/__init__ import 路、C7-hotfix 教訓鎖）。
後續 commit 逐步追加：C2 P1 / C3 P2 / C4 P3 / C5 P4 / C6 補全（含 §7.2 key-changing 整合）。
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ─────────────────── C1：策略分派與註冊 ───────────────────
def test_slides_registered_in_factory():
    """`pipelines` 套件 import 即觸發 @register('slides')（__init__ import 路、防 C7-hotfix 同型）。"""
    import pipelines  # noqa: F401  套件入口（runtime 同路徑）
    from pipelines.factory import PipelineFactory
    assert 'slides' in PipelineFactory._registry


def test_get_strategy_returns_slide_pipeline():
    """get_strategy('slides') 回 SlidePipeline 實體、非 NullStrategy。"""
    from pipelines.base_strategy import NullStrategy
    from pipelines.factory import PipelineFactory
    from pipelines.slide_pipeline import SlidePipeline
    strategy = PipelineFactory.get_strategy('slides')
    assert isinstance(strategy, SlidePipeline)
    assert not isinstance(strategy, NullStrategy)


def test_slide_rag_char_threshold_is_3():
    """U11：Vision 短文檔門檻 ≥3（保 'SiC'/'THD' 級短技術詞、同 resume 先例）。"""
    from pipelines.slide_pipeline import SlidePipeline
    assert SlidePipeline.rag_char_threshold == 3


def test_stub_phases_raise_not_implemented():
    """C1 stub 合約：四 Phase 未落地前拋 NotImplementedError（影子 B 軌安全攔截）。"""
    from pipelines.factory import PipelineFactory
    strategy = PipelineFactory.get_strategy('slides')
    for phase in ('run_phase1', 'run_phase2', 'run_phase3', 'run_phase4'):
        with pytest.raises(NotImplementedError):
            getattr(strategy, phase)(ctx=None)
