"""Phase 4.7? MODEL-3 B2: 公式穿透合併驗證。

驗證 _merge_small_text_blocks 在 B2 改寫後行為：
- text + formula + text 合併為單一 chunk（穿透）
- table / heading / image_caption 為硬邊界、截斷 buffer
- 修正 3：formula 無論長度都合進 buffer、不 flush
- 修正 1：text + formula 合併用空格、不用 \\n\\n

依據：plan §4.2 + §3.5 修正 1 + §3.7 修正 3
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_processor(min_length=500, max_length=2500):
    """繞過 embedder 建構 TilingProcessor。"""
    from processor.tiling_processor import TilingProcessor
    return TilingProcessor(min_length=min_length, max_length=max_length, embedder=None)


# ─────────────────── 1. text + formula + text 穿透合併 ───────────────────


def test_text_formula_text_merged():
    """小 text + 小 formula + 小 text → 單一 chunk（穿透合併）。"""
    p = _make_processor()
    content = [
        {'type': 'text', 'content': 'The value of', 'index': 0},
        {'type': 'formula', 'content': 'x = mc^2', 'index': 1},
        {'type': 'text', 'content': 'is positive.', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    assert len(result) == 1
    # 修正 1：應該用空格連接、不是 \n\n
    assert '\n\n' not in result[0]['content']
    # 應該包含三個原始 fragments
    assert 'The value of' in result[0]['content']
    assert 'x = mc^2' in result[0]['content']
    assert 'is positive.' in result[0]['content']


# ─────────────────── 2. 硬邊界截斷測試（3 個）───────────────────


def test_table_breaks_buffer():
    """text + table + text → 3 個獨立 chunks（table 是硬邊界）。"""
    p = _make_processor()
    content = [
        {'type': 'text', 'content': 'before table', 'index': 0},
        {'type': 'table', 'content': '| a | b |\n|---|---|', 'index': 1},
        {'type': 'text', 'content': 'after table', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    assert len(result) == 3
    types = [r.get('type') for r in result]
    assert types == ['text', 'table', 'text']


def test_heading_breaks_buffer():
    """text + heading + text → 3 個獨立 chunks（heading 是硬邊界）。"""
    p = _make_processor()
    content = [
        {'type': 'text', 'content': 'intro', 'index': 0},
        {'type': 'heading', 'content': '## Section', 'index': 1},
        {'type': 'text', 'content': 'body', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    assert len(result) == 3
    types = [r.get('type') for r in result]
    assert types == ['text', 'heading', 'text']


def test_image_caption_treated_as_hard_boundary():
    """text + image_caption + text → 3 個獨立 chunks（image_caption 是硬邊界）。"""
    p = _make_processor()
    content = [
        {'type': 'text', 'content': 'before image', 'index': 0},
        {'type': 'image_caption', 'content': 'Figure 1: ...', 'index': 1},
        {'type': 'text', 'content': 'after image', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    assert len(result) == 3
    types = [r.get('type') for r in result]
    assert types == ['text', 'image_caption', 'text']


# ─────────────────── 3. formula-only section ───────────────────


def test_formula_only_section_handled():
    """整 section 只有 formulas → 合併成 1 個 chunk。"""
    p = _make_processor()
    content = [
        {'type': 'formula', 'content': 'a = 1', 'index': 0},
        {'type': 'formula', 'content': 'b = 2', 'index': 1},
        {'type': 'formula', 'content': 'c = a + b', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    assert len(result) == 1
    # 修正 1：formula + formula 用空格
    assert '\n\n' not in result[0]['content']
    # 內容應該含全部 fragments
    assert 'a = 1' in result[0]['content']
    assert 'b = 2' in result[0]['content']
    assert 'c = a + b' in result[0]['content']


# ─────────────────── 4. 修正 3 關鍵驗證：長 formula 不觸發 flush ───────────────────


def test_long_formula_does_not_break_buffer():
    """修正 3：長 LaTeX formula（> min_length）跟周圍 text 留同 chunk、不 flush。

    例：~2000 字 LaTeX formula 字元數虛高、舊版可能誤判為「大文本塊」觸發 flush、
    把公式跟前後 text 截斷。修正 3 後 formula 無條件合進 buffer。
    """
    p = _make_processor(min_length=500)
    long_latex = '\\sum_{i=0}^{n} \\alpha_i \\cdot \\beta_i ' * 50  # ~2000 字
    assert len(long_latex) > 500  # 確認超過 min_length

    content = [
        {'type': 'text', 'content': 'The equation is:', 'index': 0},
        {'type': 'formula', 'content': long_latex, 'index': 1},
        {'type': 'text', 'content': 'where i is index.', 'index': 2},
    ]
    result = p._merge_small_text_blocks(content)
    # 應該全部合在同一個 chunk、不應該因 formula 長度 flush
    assert len(result) == 1
    assert 'The equation is:' in result[0]['content']
    assert 'where i is index.' in result[0]['content']
    # 修正 1：text + formula + text 用空格
    assert '\n\n' not in result[0]['content']
