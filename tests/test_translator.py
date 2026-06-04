"""TRANSLATOR C4: Translator 雙模式原子翻譯器單元測試。

依據:
- plan v10 §6.1（8 測試）+ tasks §8 C4
- mock LLM（不實打 API）；旗標 LLM_USE_GLOSSARY_ALIGN 以 monkeypatch 控制
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import settings  # noqa: E402
from processor.translator import (  # noqa: E402
    InjectionContext,
    TranslateMode,
    Translator,
)


class _MockLLM:
    """記錄 chat 呼叫參數的 mock LLM。"""

    def __init__(self, response: str = "譯文"):
        self.response = response
        self.calls = []

    def chat(self, messages, stream=True, model=None, thinking_budget=0):
        self.calls.append(
            {"messages": messages, "model": model, "thinking_budget": thinking_budget}
        )
        return self.response


def _ctx(**kw):
    base = dict(lcc="QA", glossary={})
    base.update(kw)
    return InjectionContext(**base)


# ─────────────────── 測試 ───────────────────


def test_translator_normal_mode(monkeypatch):
    """① NORMAL 模式路由到 TRANSLATE_MODEL 且 thinking_budget=0（不啟用思考）。"""
    monkeypatch.setattr(settings, "TRANSLATE_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(settings, "LLM_THINKING_BUDGET", 2048)
    mock = _MockLLM()
    tr = Translator(llm=mock)
    tr.translate("hello", _ctx(), TranslateMode.NORMAL, "content")
    assert mock.calls[0]["model"] == "gemini-3.5-flash"
    assert mock.calls[0]["thinking_budget"] == 0


def test_translator_deep_think_mode(monkeypatch):
    """② DEEP_THINK 模式注入 thinking_budget=LLM_THINKING_BUDGET（>0）。

    顯式設 LLM_THINKING_BUDGET=2048（plan §2 U3：預設 0 會使 DEEP_THINK 退化）。
    """
    monkeypatch.setattr(settings, "TRANSLATE_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(settings, "LLM_THINKING_BUDGET", 2048)
    mock = _MockLLM()
    tr = Translator(llm=mock)
    tr.translate("Title", _ctx(), TranslateMode.DEEP_THINK, "title")
    assert mock.calls[0]["thinking_budget"] == 2048


def test_translator_style_hints(monkeypatch):
    """③ 依 ctx.doc_type 附加正確文體風格提示。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    tr = Translator(llm=_MockLLM())
    sp_book = tr._build_system_prompt(_ctx(doc_type="book"), "content")
    sp_resume = tr._build_system_prompt(_ctx(doc_type="resume"), "content")
    assert "流暢自然的書面語" in sp_book
    assert "正式商務中文" in sp_resume
    # doc_type 未提供時預設 academic
    sp_default = tr._build_system_prompt(_ctx(), "content")
    assert "正式學術用語" in sp_default


def test_translator_prompt_file_routing():
    """④ text_type 路由正確載入底層提示詞檔（title/caption/content 相異）。"""
    tr = Translator(llm=_MockLLM())
    sp_title = tr._build_system_prompt(_ctx(), "title")
    sp_caption = tr._build_system_prompt(_ctx(), "caption")
    sp_content = tr._build_system_prompt(_ctx(), "content")
    # caption 提示詞含 Figure/Table 編號保留硬規則
    assert "Figure" in sp_caption or "圖表編號" in sp_caption
    # 三者底層提示詞不同（doc_type 預設 academic 的尾段相同、但檔頭相異）
    assert sp_title != sp_content
    assert sp_caption != sp_content


def test_translator_lcc_domain_injection(monkeypatch):
    """⑤ LCC 領域注入：讀 ctx.domain_name；空則 fallback ctx.lcc；零 DB。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)
    tr = Translator(llm=_MockLLM())
    sp = tr._build_system_prompt(_ctx(domain_name="Electronics Engineering"), "content")
    assert "本文件主題領域：Electronics Engineering" in sp
    # domain_name=None → fallback lcc 代碼
    sp_fb = tr._build_system_prompt(_ctx(lcc="TK", domain_name=None), "content")
    assert "本文件主題領域：TK" in sp_fb
    # 旗標 OFF → 不注入
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    sp_off = tr._build_system_prompt(_ctx(domain_name="Mathematics"), "content")
    assert "本文件主題領域" not in sp_off


def test_translator_glossary_injection(monkeypatch):
    """⑥ Glossary 強約束塊（含大小寫不敏感指令）；旗標 off 不注入。"""
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)
    tr = Translator(llm=_MockLLM())
    sp = tr._build_system_prompt(_ctx(glossary={"riesling": "雷司令"}), "content")
    assert "術語強約束 System constraint" in sp
    assert "大小寫不敏感" in sp
    assert "riesling → 雷司令" in sp
    # 旗標 OFF → 不注入
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    sp_off = tr._build_system_prompt(_ctx(glossary={"riesling": "雷司令"}), "content")
    assert "術語強約束" not in sp_off


def test_translator_formatting_fallback(monkeypatch):
    """⑦ 多行重分行容錯：原文三行、譯文單行（無換行）→ 按句號重分行。"""
    monkeypatch.setattr(settings, "TRANSLATE_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(settings, "LLM_THINKING_BUDGET", 0)
    # mock 回傳無換行的單行譯文（含三句末標點）
    mock = _MockLLM("第一句。第二句。第三句。")
    tr = Translator(llm=mock)
    src = "line1\nline2\nline3"
    out = tr.translate(src, _ctx(), TranslateMode.NORMAL, "content")
    assert out.count("\n") >= 2  # 已按句號重分行為多行


def test_translator_user_prompt_references():
    """⑧ 用戶提示詞：zh_summary / preceding 生成對應參考區塊。"""
    tr = Translator(llm=_MockLLM())
    up_zh = tr._build_user_prompt("段落", _ctx(zh_summary="摘要X"), "content")
    up_pre = tr._build_user_prompt("段落", _ctx(preceding="前文Y"), "content")
    up_plain = tr._build_user_prompt("段落", _ctx(), "content")
    assert "摘要翻译参考" in up_zh and "摘要X" in up_zh
    assert "前文翻译参考" in up_pre and "前文Y" in up_pre
    assert "摘要翻译参考" not in up_plain and "前文翻译参考" not in up_plain
