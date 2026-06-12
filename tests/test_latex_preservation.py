"""RAG-12 C4 — Producer 契約測試（academic 路保留 LaTeX 數學原文）。

依據：plan_v7 §4 跨 Phase 接縫契約（producer 側）+ §8.2/§8.3。
目標：鎖死產出 academic 論文 final markdown 之 producer（A-rail
`processor/md_restore_processor.py::RestoreProcessor`）**不截斷、不轉義**
`$$...$$` 區塊式與 `$...$` 行內式數學——前端 RAG-12 KaTeX 渲染依賴此原文完整。

producer 確認（grep 證據）：
- `_process_section` formula item → `_write_to_md(path, item['content'])` 逐字寫（L758-762）。
- `_process_section` text item → `_write_to_md(path, _preserve_pipe_table(zh_content))`（L687-752）。
- `_write_to_md` 僅 append `content + "\\n\\n"`（L584-587）、不轉義。
- `_preserve_pipe_table` 僅做 pipe-table 感知之單 \\n→\\n\\n（L589-630）、不碰 `$`。

實際樣本：`output/1/2601_16502v2/final_*_zh.md`（800VDC 資料中心論文、含式(1)(2) + 行內 $P_base$）。
"""
import os
import tempfile

from processor.md_restore_processor import RestoreProcessor


def _run_section(section):
    """跑 _process_section、回傳 (zh_text, en_text)。"""
    proc = RestoreProcessor()
    d = tempfile.mkdtemp()
    en = os.path.join(d, "en.md")
    zh = os.path.join(d, "zh.md")
    open(en, "w").close()
    open(zh, "w").close()
    proc._process_section(section, en, zh)
    with open(zh, encoding="utf-8") as f:
        zh_text = f.read()
    with open(en, encoding="utf-8") as f:
        en_text = f.read()
    return zh_text, en_text


def test_formula_item_preserves_block_dollars():
    """formula item 之 $$...$$（含怪空格 + \\tag）逐字保留、不轉義。"""
    formula = r"$$ P _ { \mathrm { I T } } ( t ) = P _ { \mathrm { b a s e } } + \alpha \cdot U ( t )\tag{1} $$"
    section = {
        "title": "",
        "content": [{"type": "formula", "content": formula, "index": 0, "part": 0}],
        "children": [],
    }
    zh, en = _run_section(section)
    assert formula in zh, "formula 區塊未逐字保留於 zh"
    assert formula in en, "formula 區塊未逐字保留於 en（公式中英一致）"
    assert r"\tag{1}" in zh
    assert r"\$" not in zh, "$ 不應被轉義為 \\$"
    # 公式中英一致、各含一對 $$
    assert zh.count("$$") == en.count("$$") == 2


def test_text_item_preserves_inline_dollars():
    """text item 譯文之行內 $...$（含 _、{}）逐字保留、不被轉義/吞噬。"""
    zh_in = r"其中 $P _ { \mathrm { b a s e } }$ 為待機功率、$k _ { 1 }$ 為係數。"
    section = {
        "title": "",
        "content": [{
            "type": "text",
            "content": r"where $P_{base}$ is standby power and $k_{1}$ is coefficient.",
            "translated_content": zh_in,
            "index": 0, "part": 0,
        }],
        "children": [],
    }
    zh, en = _run_section(section)
    assert r"$P _ { \mathrm { b a s e } }$" in zh
    assert r"$k _ { 1 }$" in zh
    assert "$P_{base}$" in en
    assert r"\$" not in zh, "$ 不應被轉義"


def test_preserve_pipe_table_does_not_touch_dollars():
    """_preserve_pipe_table 僅插段落空行、不轉義/不刪 $（防破壞數學原文）。"""
    proc = RestoreProcessor()
    out = proc._preserve_pipe_table("foo $x _ 1$ bar\n$$ a = b $$")
    assert r"$x _ 1$" in out
    assert r"$$ a = b $$" in out
    assert r"\$" not in out


def test_write_to_md_writes_dollars_verbatim():
    """_write_to_md（formula/text 共用之最終寫出閘）逐字寫 $、不轉義。"""
    proc = RestoreProcessor()
    d = tempfile.mkdtemp()
    f = os.path.join(d, "x.md")
    open(f, "w").close()
    formula = r"$$ \tau \frac { d Q } { d t } + Q = k _ { 1 } \cdot P _ { I T } $$"
    proc._write_to_md(f, formula)
    with open(f, encoding="utf-8") as fh:
        txt = fh.read()
    assert formula in txt
    assert r"\$" not in txt
