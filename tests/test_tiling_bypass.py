"""Phase 4.7? MODEL-3 B1: 短文 Fast-path Bypass 驗證。

驗證：
- 總字數 < TILING_BYPASS_CHAR_LIMIT (5000) → bypass
- 總字數 >= 5000 → 走原 _process_sections
- bypass 模式合 text/formula、保留 non-text 原始 index
- 修正 1：inline formula 用空格而非 \\n\\n 連接
- 修正 2：figure / table 原始 index 不被重寫

依據：plan §4.0 + §4.1 + §3.5 修正 1 + §3.6 修正 2
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_data(total_text_chars: int, doc_type='academic'):
    """產生 mock processed.json 結構、總字數可控。"""
    return {
        'doc_type': doc_type,
        'sections': [
            {
                'type': 'section',
                'content': [
                    {'type': 'text', 'content': 'x' * total_text_chars, 'index': 0}
                ]
            }
        ]
    }


def _make_processor(max_length=None):
    """繞過 embedder 建構 TilingProcessor、避免 MODEL-1+2 連線。"""
    from processor.tiling_processor import TilingProcessor
    return TilingProcessor(min_length=500, max_length=max_length, embedder=None)


# ─────────────────── Bypass 觸發 / 不觸發 ───────────────────


def test_bypass_under_5000_chars(tmp_path):
    """總字數 4000 → 走 bypass、output chunk tiling_method='bypass'。"""
    p = _make_processor()
    data = _make_data(4000)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path), doc_type='resume')

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    assert len(chunks) == 1
    assert chunks[0].get('tiling_method') == 'bypass'


def test_no_bypass_over_5000_chars(tmp_path):
    """總字數 6000 → 走原 _process_sections（非 bypass）。"""
    p = _make_processor()
    data = _make_data(6000)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path), doc_type='academic')

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    # 走完整 _process_content、不應有 'bypass' 標記
    assert chunks[0].get('tiling_method') != 'bypass'


# ─────────────────── doc_type 行為 ───────────────────


def test_bypass_resume_doc_type(tmp_path):
    """doc_type='resume' + 4000 字 → bypass + metadata tiling_method='bypass'。"""
    p = _make_processor()
    data = _make_data(4000, doc_type='resume')
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path), doc_type='resume')

    out = json.loads(out_path.read_text(encoding='utf-8'))
    assert out['sections'][0]['content'][0]['tiling_method'] == 'bypass'


# ─────────────────── Bypass 行為：非 text/formula pass-through ───────────────────


def test_bypass_passthrough_non_text_types(tmp_path):
    """section 含 table → bypass 模式下 table 保留原 type、不合進 buffer。"""
    p = _make_processor()
    data = {
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': 'short text', 'index': 0},
                {'type': 'table', 'content': '| a | b |\n|---|---|\n| 1 | 2 |', 'index': 1},
                {'type': 'text', 'content': 'after table', 'index': 2},
            ]
        }]
    }
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    types = [c.get('type') for c in chunks]
    assert 'table' in types
    # 預期 3 個 chunk：text(merged buffer-1) / table / text(merged buffer-2)
    assert len(chunks) == 3


def test_bypass_merges_text_formula_continuous(tmp_path):
    """bypass 模式下 text + formula + text 連續合併為單一 chunk、不含 \\n\\n（修正 1 預兆）。"""
    p = _make_processor()
    data = {
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': 'The value of', 'index': 0},
                {'type': 'formula', 'content': 'x = mc^2', 'index': 1},
                {'type': 'text', 'content': 'is positive.', 'index': 2},
            ]
        }]
    }
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    assert len(chunks) == 1
    # 修正 1：text + formula 用空格、不用 \n\n
    assert '\n\n' not in chunks[0]['content']
    # 內容應該含所有部分
    assert 'The value of' in chunks[0]['content']
    assert 'x = mc^2' in chunks[0]['content']
    assert 'is positive.' in chunks[0]['content']


# ─────────────────── env override ───────────────────


def test_env_override_bypass_char_limit(tmp_path, monkeypatch):
    """TILING_BYPASS_CHAR_LIMIT=3000 生效（3500 字 > 3000、不走 bypass）。"""
    monkeypatch.setenv('TILING_BYPASS_CHAR_LIMIT', '3000')
    import settings
    importlib.reload(settings)
    import processor.tiling_processor
    importlib.reload(processor.tiling_processor)

    from processor.tiling_processor import TilingProcessor
    p = TilingProcessor(min_length=500, max_length=2500, embedder=None)
    data = _make_data(3500)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    # 3500 > 3000、不走 bypass
    assert out['sections'][0]['content'][0].get('tiling_method') != 'bypass'


# ─────────────────── 修正 1 + 修正 2 關鍵驗證 ───────────────────


def test_inline_formula_preserved_with_space_join(tmp_path):
    """修正 1：text + text 用 \\n\\n、text + formula 用空格。"""
    p = _make_processor()
    # 案例 1：純 text+text、用 \n\n
    data1 = {
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': 'para1', 'index': 0},
                {'type': 'text', 'content': 'para2', 'index': 1},
            ]
        }]
    }
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data1, ensure_ascii=False), encoding='utf-8')
    p.process(str(in_path), str(out_path))
    out = json.loads(out_path.read_text(encoding='utf-8'))
    assert '\n\n' in out['sections'][0]['content'][0]['content']

    # 案例 2：text+formula+text、用空格（不應有 \n\n）
    data2 = {
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': 'before', 'index': 0},
                {'type': 'formula', 'content': 'x', 'index': 1},
                {'type': 'text', 'content': 'after', 'index': 2},
            ]
        }]
    }
    in_path.write_text(json.dumps(data2, ensure_ascii=False), encoding='utf-8')
    p.process(str(in_path), str(out_path))
    out = json.loads(out_path.read_text(encoding='utf-8'))
    assert '\n\n' not in out['sections'][0]['content'][0]['content']


def test_bypass_preserves_image_table_original_index(tmp_path):
    """修正 2：原 PDF text[0] / image[1] / text[2] bypass 後 image 仍 index=1。"""
    p = _make_processor()
    data = {
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': 'text before', 'index': 0},
                {'type': 'image', 'content': 'image.jpg', 'index': 1},
                {'type': 'text', 'content': 'text after', 'index': 2},
            ]
        }]
    }
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    image_chunks = [c for c in chunks if c.get('type') == 'image']
    assert len(image_chunks) == 1
    # 修正 2：image 原始 index=1 不被重寫
    assert image_chunks[0]['index'] == 1
