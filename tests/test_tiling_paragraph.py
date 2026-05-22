"""Phase 4.7? MODEL-3 B3: 段落級滑動驗證。

驗證：
- 短文（total < TILING_PARAGRAPH_THRESHOLD）→ split_mode='sentence' 或 'delimiter'
- 長文（total > TILING_PARAGRAPH_THRESHOLD）→ split_mode='paragraph'
- 修正 4：Windows \\r\\n / 多餘空白容錯
- TILING_PARAGRAPH_THRESHOLD env override
- tiling_method 標籤完整化

依據：plan §4.3 + §3.8 修正 4
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_processor(max_length=2500):
    """繞過 embedder 建構 TilingProcessor。"""
    from processor.tiling_processor import TilingProcessor
    return TilingProcessor(min_length=500, max_length=max_length, embedder=None)


def _make_data_with_long_text(text_content, doc_type='academic'):
    """單一 section、單一 text item、可控長度。"""
    return {
        'doc_type': doc_type,
        'sections': [{
            'type': 'section',
            'content': [
                {'type': 'text', 'content': text_content, 'index': 0}
            ]
        }]
    }


# ─────────────────── 1. 短文 vs 長文模式切換 ───────────────────


def test_sentence_level_when_under_threshold(tmp_path):
    """20000 字 + 含 \\n\\n（< TILING_PARAGRAPH_THRESHOLD 30000）→ split_mode='delimiter'、不是 'paragraph'。"""
    p = _make_processor()
    # ~19600 字 + 含 \n\n 分段、但低於 30000 觸發閾值
    text = ("Sentence one. " * 100 + "\n\n" + "Sentence two. " * 100) * 7  # ~19600 字
    assert 5000 < len(text) < 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path), doc_type='academic')

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    # 應該不是 paragraph 模式
    assert 'paragraph' not in tiling_methods


def test_paragraph_level_when_over_threshold(tmp_path):
    """40000 字（> TILING_PARAGRAPH_THRESHOLD 30000）+ 含 \\n\\n → split_mode='paragraph'。"""
    p = _make_processor()
    paragraph = "This is a paragraph about machine learning. " * 30  # ~1300 字/段
    text = (paragraph + "\n\n") * 30  # ~40000 字、足以觸發 long_doc_mode
    assert len(text) > 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path), doc_type='academic')

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    # 應該有 paragraph 模式 chunk
    assert 'paragraph' in tiling_methods


# ─────────────────── 2. 段落判定從 \\n\\n ───────────────────


def test_paragraph_detection_from_newlines(tmp_path):
    """長 text 含 \\n\\n 分段 → 段落級正確切。"""
    p = _make_processor()
    paragraph_a = "Content A. " * 200  # ~2200 字
    paragraph_b = "Content B. " * 200
    paragraph_c = "Content C. " * 200
    text = (paragraph_a + "\n\n" + paragraph_b + "\n\n" + paragraph_c) * 5  # ~33000+ 字
    assert len(text) > 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    assert len(chunks) >= 1
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    assert 'paragraph' in tiling_methods


# ─────────────────── 3. env override ───────────────────


def test_env_override_paragraph_threshold(tmp_path, monkeypatch):
    """TILING_PARAGRAPH_THRESHOLD=10000 生效（15000 字觸發 paragraph）。"""
    monkeypatch.setenv('TILING_PARAGRAPH_THRESHOLD', '10000')

    import settings
    importlib.reload(settings)
    import processor.tiling_processor
    importlib.reload(processor.tiling_processor)

    from processor.tiling_processor import TilingProcessor
    p = TilingProcessor(min_length=500, max_length=2500, embedder=None)
    paragraph = "Content for testing. " * 150  # ~3150 字
    text = (paragraph + "\n\n") * 5  # ~16000 字
    assert len(text) > 10000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    assert 'paragraph' in tiling_methods


# ─────────────────── 4. 修正 4 關鍵驗證：regex 容錯 ───────────────────


def test_paragraph_split_handles_windows_line_ending(tmp_path):
    """修正 4：Windows \\r\\n\\r\\n 切割成多段、不是當成一整段。"""
    p = _make_processor()
    paragraph_a = "Content A. " * 500
    paragraph_b = "Content B. " * 500
    # 用 Windows-style 換行（且僅有 \r\n\r\n、無 \n\n）
    text = (paragraph_a + "\r\n\r\n" + paragraph_b) * 5
    assert len(text) > 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    assert len(chunks) >= 1
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    # 修正 4：regex 應該正確 split Windows line ending、走 paragraph 模式
    assert 'paragraph' in tiling_methods


def test_paragraph_split_handles_extra_whitespace(tmp_path):
    """修正 4：\\n \\n / \\n\\t\\n 等含空白的換行容錯。"""
    p = _make_processor()
    paragraph_a = "Content A. " * 500
    paragraph_b = "Content B. " * 500
    # 含 tab / 空白的「假段落分隔」（避開 \n\n）
    text = (paragraph_a + "\n \n" + paragraph_b + "\n\t\n" + paragraph_a) * 5
    assert len(text) > 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    assert len(chunks) >= 1
    tiling_methods = [c.get('tiling_method') for c in chunks if c.get('tiling_method')]
    # regex 應該正確切割含空白的段落分隔
    assert 'paragraph' in tiling_methods


# ─────────────────── 5. tiling_method 標籤完整化 ───────────────────


def test_tiling_method_labels_present(tmp_path):
    """所有 chunks 應該有 tiling_method 標籤（bypass / paragraph / delimiter / sentence / passthrough）。"""
    p = _make_processor()
    # 6000 字（> 5000 bypass、< 30000 paragraph）+ 含 \n\n
    text = ("Some sentence. " * 100 + "\n\n" + "Another sentence. " * 100) * 5  # ~6500 字
    assert 5000 < len(text) < 30000

    data = _make_data_with_long_text(text)
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    p.process(str(in_path), str(out_path))

    out = json.loads(out_path.read_text(encoding='utf-8'))
    chunks = out['sections'][0]['content']
    # 每個 chunk 都應該有 tiling_method
    for c in chunks:
        assert 'tiling_method' in c
        assert c['tiling_method'] in (
            'bypass', 'paragraph', 'delimiter', 'sentence', 'passthrough'
        )
