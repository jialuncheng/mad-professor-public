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
    """stub 合約：未落地 Phase 拋 NotImplementedError（影子 B 軌安全攔截）。

    # === [PIPE-SLIDES C2 START] === phase1 已於 C2 落地、自清單移除（C3/C4/C5 落地時遞減）
    """
    from pipelines.factory import PipelineFactory
    strategy = PipelineFactory.get_strategy('slides')
    for phase in ('run_phase2', 'run_phase3', 'run_phase4'):
        with pytest.raises(NotImplementedError):
            getattr(strategy, phase)(ctx=None)
    # === [PIPE-SLIDES C2 END] ===


# === [PIPE-SLIDES C2 START] === P1 Vision Ingestion 測試（mock fitz 渲染 + Vision、零真 API）
class _FakeVision:
    """假 LLMClient：依圖片 bytes 對映回應、記錄 temperature 與 prompt。"""

    def __init__(self, responses: dict):
        self.responses = responses          # img_bytes -> json str
        self.calls = []                     # (prompt, temperature, img_bytes)

    def chat_with_images(self, messages, images, temperature=None, **kw):
        img = images[0][0]
        self.calls.append((messages[0]["content"], temperature, img))
        return self.responses[img]


def _make_ctx(tmp_path, monkeypatch, paper_id='deck1'):
    import settings
    from pipelines.context import PipelineContext
    monkeypatch.setattr(settings, 'OUTPUT_DIR', tmp_path)
    return PipelineContext(doc_type='slides', paper_id=paper_id,
                           pdf_path=str(tmp_path / '產品簡報.pdf'), owner_id=1)


def _run_p1(monkeypatch, tmp_path, responses, paper_id='deck1'):
    """共用 harness：mock _render_pages + LLMClient → 跑 run_phase1。"""
    import llm.client as llm_client
    from pipelines.slide_pipeline import SlidePipeline
    imgs = list(responses.keys())
    fake = _FakeVision(responses)
    monkeypatch.setattr(SlidePipeline, '_render_pages', staticmethod(lambda p: imgs))
    monkeypatch.setattr(llm_client.LLMClient, 'get_instance', classmethod(lambda cls: fake))
    ctx = _make_ctx(tmp_path, monkeypatch, paper_id)
    spec = SlidePipeline().run_phase1(ctx)
    return spec, ctx, fake


def _resp(title='', content='', desc='', cover=None):
    d = {"title": title, "markdown_content": content, "figure_description": desc}
    if cover is not None:
        d["is_cover"] = bool(cover)
        d["cover"] = cover if isinstance(cover, dict) else {}
    import json as _j
    return _j.dumps(d, ensure_ascii=False)


def test_p1_cover_metadata_and_image_saved(monkeypatch, tmp_path):
    """U2 封面路：title/authors 入 spec、company/date 入 raw_metadata 旁路；存圖 page-01。"""
    responses = {
        b'p0': _resp('AI 資料中心電源', '', '封面示意圖',
                     cover={"title": "AI 資料中心電源", "company": "STMicro",
                            "date": "2026-05", "authors": ["Paolo", "Gianni"]}),
        b'p1': _resp('架構', '- 800V 演進', ''),
    }
    spec, ctx, fake = _run_p1(monkeypatch, tmp_path, responses)
    assert spec.title == 'AI 資料中心電源'
    assert spec.authors == ['Paolo', 'Gianni']
    assert ctx.raw_metadata['company'] == 'STMicro' and ctx.raw_metadata['date'] == '2026-05'
    assert (tmp_path / '1' / 'deck1' / 'images' / 'page-01.jpg').exists()
    assert spec.tiles[0]['is_cover'] is True


def test_p1_no_cover_title_fallback_filename(monkeypatch, tmp_path):
    """U2 非封面路：title fallback 檔名 stem、不幻覺 metadata。"""
    responses = {
        b'p0': _resp('議程', '- 第一節', '', cover=False),
        b'p1': _resp('內容', '- 細節', ''),
    }
    spec, ctx, _ = _run_p1(monkeypatch, tmp_path, responses)
    assert spec.title == '產品簡報'          # 檔名 stem fallback、非空
    assert 'company' not in ctx.raw_metadata


def test_p1_dedupe_headers_excludes_cover(monkeypatch, tmp_path):
    """U3/Q2 統計去重：短行出現於全部非封面頁 → 剔除；封面排除統計與剔除。"""
    noise = 'ACME Corp'
    responses = {
        b'p0': _resp('封面', f'{noise}\n大標題', '',
                     cover={"title": "T", "company": "ACME", "date": "", "authors": []}),
        b'p1': _resp('一', f'{noise}\n- 內容一', ''),
        b'p2': _resp('二', f'{noise}\n- 內容二', ''),
        b'p3': _resp('三', f'{noise}\n- 內容三', ''),
    }
    spec, _, _ = _run_p1(monkeypatch, tmp_path, responses)
    for u in spec.tiles[1:]:
        assert noise not in u['content']      # 非封面頁剔除
    assert noise in spec.tiles[0]['content']  # 封面保留


def test_p1_blank_unit_skipped(monkeypatch, tmp_path):
    """空白單位（三欄皆空）跳過、不存圖不入 tiles。"""
    responses = {
        b'p0': _resp('首頁', '- 內容', '', cover=False),
        b'p1': _resp('', '', ''),             # 空白頁
        b'p2': _resp('尾頁', '- 結論', ''),
    }
    spec, _, _ = _run_p1(monkeypatch, tmp_path, responses)
    assert len(spec.tiles) == 2
    assert [u['page'] for u in spec.tiles] == [1, 2]   # 頁序連續重編


def test_p1_rolling_default_off_and_trigger(monkeypatch, tmp_path):
    """Q1 滾動：預設關（每單位一次呼叫、無前頁注入）；標題含 (續) 觸發重轉錄注入前頁。"""
    responses = {
        b'p0': _resp('規格表', '| A | 1 |', '', cover=False),
        b'p1': _resp('規格表 (續)', '| B | 2 |', ''),
    }
    spec, _, fake = _run_p1(monkeypatch, tmp_path, responses)
    # 並行 2 次 + 觸發滾動補救 1 次 = 3；滾動那次 prompt 含前頁注入
    assert len(fake.calls) == 3
    assert any('上一頁內容' in c[0] for c in fake.calls)
    # 對照：無觸發場景不滾動
    responses2 = {b'q0': _resp('一', '- a', '', cover=False), b'q1': _resp('二', '- b', '')}
    _, _, fake2 = _run_p1(monkeypatch, tmp_path, responses2, paper_id='deck2')
    assert len(fake2.calls) == 2
    assert all('上一頁內容' not in c[0] for c in fake2.calls)


def test_p1_vision_temperature_wired(monkeypatch, tmp_path):
    """§1.3.1：每次 Vision 呼叫帶 temperature=settings.LLM_VISION_TEMPERATURE（預設 0）。"""
    import settings
    responses = {b'p0': _resp('一', '- a', '', cover=False)}
    _, _, fake = _run_p1(monkeypatch, tmp_path, responses, paper_id='deck3')
    assert all(t == settings.LLM_VISION_TEMPERATURE for _, t, _ in fake.calls)
# === [PIPE-SLIDES C2 END] ===
