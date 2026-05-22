"""Phase 4.7? RAG-8: pipe table 經 md_restore 後保留 row 之間原 \\n、不注入空行。

真因：md_restore_processor.py L683-684 原 regex 把 pipe table rows 之間
\\n 改 \\n\\n、破壞 markdown table 渲染。修法用 _preserve_pipe_table()
helper、保留 pipe table 區塊不動。

樣本依據：baron OrcStack 端跑出的 DeHunt_CTO_Tzung-Yuan_Lee _translated.json
顯示 type=text content 內含 pipe table 字串、type 不是 table。
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.md_restore_processor import RestoreProcessor  # noqa: E402


@pytest.fixture
def processor():
    return RestoreProcessor()


def test_pipe_table_rows_preserved(processor):
    """pipe table rows 之間單 \\n 不被改為 \\n\\n。"""
    text = (
        "| col1 | col2 | col3 |\n"
        "| --- | --- | --- |\n"
        "| a | b | c |\n"
        "| d | e | f |"
    )
    result = processor._preserve_pipe_table(text)
    lines = result.split('\n')
    pipe_lines = [i for i, ln in enumerate(lines) if ln.startswith('|')]
    # 連續的 pipe rows 中間不該插入空行（相鄰行索引差 = 1）
    for i in range(len(pipe_lines) - 1):
        assert pipe_lines[i + 1] - pipe_lines[i] == 1, (
            f"pipe rows 之間多插空行：{lines[pipe_lines[i]:pipe_lines[i+1]+1]}"
        )


def test_pipe_table_with_surrounding_paragraph(processor):
    """pipe table 區塊與前後段落之間應該有空行分隔。"""
    text = (
        "前面段落文字。\n"
        "| col1 | col2 |\n"
        "| --- | --- |\n"
        "| a | b |\n"
        "後面段落文字。"
    )
    result = processor._preserve_pipe_table(text)
    # table 前該有空行
    assert '前面段落文字。\n\n|' in result, f"table 前缺空行：{result!r}"
    # table 後該有空行
    assert '| a | b |\n\n後面段落文字。' in result, f"table 後缺空行：{result!r}"


def test_paragraph_single_newline_still_converted(processor):
    """一般段落內單 \\n 仍應該轉 \\n\\n（保留原 regex 對 prose 的作用）。"""
    text = "第一段。\n第二段。"
    result = processor._preserve_pipe_table(text)
    assert '第一段。\n\n第二段。' in result, \
        f"一般段落 \\n 未轉 \\n\\n：{result!r}"


def test_already_double_newline_unchanged(processor):
    """已有 \\n\\n 的不該被改成 \\n\\n\\n。"""
    text = "第一段。\n\n第二段。"
    result = processor._preserve_pipe_table(text)
    assert '\n\n\n' not in result, f"出現三連 \\n：{result!r}"


def test_dehunt_education_table_real_case(processor):
    """真實案例：DeHunt 學歷 pipe table（baron OrcStack 跑出的 _translated 內容）。"""
    text = (
        "| | | |\n"
        "| :--- | :--- | :--- |\n"
        "| 2003/09 - 2008/06 | 國立交通大學 | 新竹, 台灣 |\n"
        "| | 電機與控制工程學系 | 博士候選人 |"
    )
    result = processor._preserve_pipe_table(text)
    # 4 行 pipe table 連續、沒有空行插入
    lines = [ln for ln in result.split('\n') if ln]
    pipe_lines = [ln for ln in lines if ln.startswith('|')]
    assert len(pipe_lines) == 4, f"預期 4 個 pipe rows、實際 {len(pipe_lines)}"


def test_no_table_no_change_to_prose(processor):
    """無 table 的純 prose、行為與原 regex 一致（單 \\n 轉 \\n\\n）。"""
    text = "段落 A。\n段落 B。\n段落 C。"
    result = processor._preserve_pipe_table(text)
    paragraphs = [p for p in result.split('\n\n') if p.strip()]
    assert len(paragraphs) == 3, f"預期 3 個段落、實際 {len(paragraphs)}：{result!r}"
