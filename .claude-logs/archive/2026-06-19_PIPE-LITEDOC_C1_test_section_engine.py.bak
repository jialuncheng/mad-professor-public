"""PIPE-SECTION-BASE C4 — 共用 section 引擎單元測試 + base 層接縫整合測試。

覆蓋 `pipelines/section_engine.py` 之純函式引擎（resume / litedoc / academic / technical /
book 共用）。雙鎖之一：resume 既有 `test_resume_pipeline.py` 驗「resume 路徑不退化」；
本檔驗「引擎本身對任意 doc_type 之接縫 key 不位移」（plan §8 / Q6）。
"""

import threading
import time

import pytest

from pipelines import section_engine as se


# ──────────────────────────────────────────────────────────────────────────
# Fakes
# ──────────────────────────────────────────────────────────────────────────
class _FakeLLM:
    """chat 回 `[i] 摘要i` 逐行（idx 由 user 內 [n] 抽出）；raise_on=True 模擬失敗。"""
    def __init__(self, raise_on=False):
        self.calls = 0
        self._raise = raise_on

    def chat(self, messages=None, **kw):
        self.calls += 1
        if self._raise:
            raise RuntimeError("LLM down")
        import re
        user = (messages or [{}])[-1].get("content", "")
        idxs = sorted({int(m) for m in re.findall(r"\[(\d+)\]", user)})
        return "\n".join(f"[{i}] 摘要{i}" for i in idxs)


class _DetTr:
    """確定性翻譯器：text → ZH::text（改變內容/key，用於 byte 序 + key-changing 驗證）。"""
    def translate(self, text, inj, mode, text_type="content"):
        return f"ZH::{text}"


def _tiles_3():
    def _s(t, c):
        return {"title": t, "content": [{"type": "text", "content": c}], "children": []}
    return [_s("Skills", "Python C++"), _s("Education", "PhD"), _s("Experience", "Lead")]


# ──────────────────────────────────────────────────────────────────────────
# ① 標題樹走訪（collect_summary_targets / node_content_text）
# ──────────────────────────────────────────────────────────────────────────
def test_collect_summary_targets_dfs_keys():
    """DFS pre-order、node_key=原文標題 path（巢狀 path 以 / 串接）。"""
    tiles = [{
        "title": "A", "content": [{"type": "text", "content": "a-body"}],
        "children": [{"title": "A1", "content": [{"type": "text", "content": "a1-body"}], "children": []}],
    }]
    targets = se.collect_summary_targets(tiles)
    keys = [k for k, _t, _c in targets]
    assert keys == ["A", "A/A1"]                    # 父先於子、path 串接
    assert targets[0][2] == "a-body"


def test_collect_summary_targets_accepts_subtree():
    """U3.2：可吃任意子標題樹（非僅 root）→ 供 book rolling 組合。"""
    subtree = [{"title": "Chap3", "content": [{"type": "text", "content": "c3"}], "children": []}]
    targets = se.collect_summary_targets(subtree, path_prefix="Vol1")
    assert targets[0][0] == "Vol1/Chap3"            # 子樹 + prefix 仍正確串接


def test_collect_summary_targets_skips_empty():
    """無 title 或無實質內文之節點不入 targets。"""
    tiles = [
        {"title": "", "content": [{"type": "text", "content": "x"}], "children": []},   # 無 title
        {"title": "T", "content": [], "children": []},                                   # 無內文
    ]
    assert se.collect_summary_targets(tiles) == []


# ──────────────────────────────────────────────────────────────────────────
# ② 批次摘要保序（parse_indexed / build_section_summaries）
# ──────────────────────────────────────────────────────────────────────────
def test_parse_indexed_order_and_bounds():
    out = "[2] c\n[0] a\n[1] b\n[9] x"           # 亂序 + 越界
    parsed = se.parse_indexed(out, n=3)
    assert parsed == {0: "a", 1: "b", 2: "c"}    # 越界 [9] 丟棄、缺漏自然留空


def test_build_section_summaries_batch_not_n():
    """三安全鎖①批次：⑤產 + ⑥翻 各 1 次 LLM（共 2 次）、不隨 section 數 N 增長。"""
    fake = _FakeLLM()
    zh = se.build_section_summaries(
        _tiles_3(), llm=fake, abstract="全文摘要", source_lang="en",
        summary_model="m1", translate_model="m2",
        summary_system_prompt="sp", translate_system_prompt="tp",
        input_chars_cap=2000, max_chars=8000, paper_id="p1",
    )
    assert fake.calls == 2                                       # 3 sections 仍 2 次
    assert set(zh.keys()) == {"Skills", "Education", "Experience"}  # key=原文標題 path
    assert all(v.startswith("摘要") for v in zh.values())


def test_build_section_summaries_llm_fail_non_fatal():
    """三安全鎖②非致命：LLM 失敗 → 留空 dict、不拋。"""
    fake = _FakeLLM(raise_on=True)
    zh = se.build_section_summaries(
        _tiles_3(), llm=fake, abstract="", source_lang="en",
        summary_model="m1", translate_model="m2",
        summary_system_prompt="sp", translate_system_prompt="tp",
        input_chars_cap=2000, max_chars=8000,
    )
    assert zh == {}


def test_translate_section_summaries_zh_source_skips():
    """source_lang zh* → 原文即繁中、不重譯（key=node_key）。"""
    targets = [("K0", "T0", "c0"), ("K1", "T1", "c1")]
    raw = {0: "原文摘要0", 1: "原文摘要1"}
    fake = _FakeLLM()
    out = se.translate_section_summaries(
        raw, targets, abstract="", source_lang="zh-TW",
        llm=fake, model="m", system_prompt="sp", max_chars=8000,
    )
    assert out == {"K0": "原文摘要0", "K1": "原文摘要1"}
    assert fake.calls == 0                                       # zh 不呼 LLM


# ──────────────────────────────────────────────────────────────────────────
# ③ 排版還原（restore_sections_markdown）：byte 序 / 限流 / 異常隔離
# ──────────────────────────────────────────────────────────────────────────
def test_restore_byte_order_preserved():
    """並行翻譯後輸出 byte = 序列預期（保序 + HEADING 層級 + raw passthrough）。"""
    sections = [
        {"title": "S0", "level": 1, "content": [{"type": "text", "content": "t0"}], "children": []},
        {"title": "S1", "level": 1, "content": [{"type": "text", "content": "t1"}], "children": []},
    ]
    md, slots, zh = se.restore_sections_markdown(sections, None, _DetTr(), True, max_workers=4)
    # title slot 亦翻（ZH::S0）、level=2（## ）、content 翻 + 保序
    assert md == "## ZH::S0\n\nZH::t0\n\n## ZH::S1\n\nZH::t1\n"
    assert zh[0] == "ZH::S0"                                # title slot 亦翻


def test_restore_concurrency_capped():
    """受限並行：同時進入翻譯的執行緒峰值 ≤ max_workers（傳 2）。"""
    state = {"cur": 0, "max": 0}
    lock = threading.Lock()

    class _ConcTr:
        def translate(self, text, inj, mode, text_type="content"):
            with lock:
                state["cur"] += 1
                state["max"] = max(state["max"], state["cur"])
            time.sleep(0.02)
            with lock:
                state["cur"] -= 1
            return f"ZH::{text}"

    sections = [
        {"title": f"S{i}", "level": 1, "content": [{"type": "text", "content": f"t{i}"}], "children": []}
        for i in range(6)
    ]
    se.restore_sections_markdown(sections, None, _ConcTr(), True, max_workers=2)
    assert state["max"] >= 1
    assert state["max"] <= 2                                # 受 max_workers 限


def test_restore_unit_error_isolated():
    """單 unit 翻譯拋例外 → 退回原文、其餘正常、不中斷。"""
    class _ErrTr:
        def translate(self, text, inj, mode, text_type="content"):
            if "BOOM" in text:
                raise RuntimeError("unit fail")
            return f"ZH::{text}"

    sections = [
        {"title": "Good", "level": 1, "content": [{"type": "text", "content": "alpha"}], "children": []},
        {"title": "Bad", "level": 1, "content": [{"type": "text", "content": "BOOM-text"}], "children": []},
    ]
    md, slots, zh = se.restore_sections_markdown(sections, None, _ErrTr(), True, max_workers=4)
    assert "ZH::alpha" in md                                # 正常單元已翻
    assert "BOOM-text" in md                                # 失敗單元退回原文
    assert "ZH::BOOM-text" not in md                        # 失敗單元未被翻譯


# ──────────────────────────────────────────────────────────────────────────
# ④ heading 退化偵測
# ──────────────────────────────────────────────────────────────────────────
def test_is_heading_degraded_too_few():
    """heading 數 < min_sections → 退化。"""
    one = [{"title": "Only", "content": [{"type": "text", "content": "x"}], "children": []}]
    assert se.is_heading_degraded(one, min_sections=2) is True


def test_is_heading_degraded_single_giant():
    """單一 heading 自身文字佔比 > ratio_threshold → 退化。"""
    sections = [
        {"title": "Big", "content": [{"type": "text", "content": "x" * 100}], "children": []},
        {"title": "Tiny", "content": [{"type": "text", "content": "y"}], "children": []},
    ]
    assert se.is_heading_degraded(sections, ratio_threshold=0.85) is True


def test_is_heading_not_degraded():
    """均勻多 section → 不退化。"""
    sections = [
        {"title": "A", "content": [{"type": "text", "content": "x" * 30}], "children": []},
        {"title": "B", "content": [{"type": "text", "content": "y" * 30}], "children": []},
    ]
    assert se.is_heading_degraded(sections) is False


# ──────────────────────────────────────────────────────────────────────────
# ⑤ meta header 純格式化器（Zero Schema Coupling·U3.1）
# ──────────────────────────────────────────────────────────────────────────
def test_render_meta_header_pure_formatter():
    """收 (Label, Value) tuples → `# 標題` + 無序列表；空 value 略過；引擎不碰任何 dict。"""
    out = se.render_meta_header(
        "王小明 (測試)",
        [("領域", "IC 設計"), ("機構", "聯詠科技"), ("電話", ""), ("Email", "")],
        sep="：",
    )
    assert out.startswith("# 王小明 (測試)")
    assert "\n- **領域**：IC 設計" in out
    assert "\n- **機構**：聯詠科技" in out
    assert "電話" not in out                                # 空 value 略過
    assert "Email" not in out


def test_render_meta_header_empty():
    """title 空 + 無欄位 → 回 ''。"""
    assert se.render_meta_header("", [], sep="：") == ""


def test_render_meta_header_en_sep():
    out = se.render_meta_header("John", [("Domain", "EE")], sep=": ")
    assert out.startswith("# John")
    assert "- **Domain**: EE" in out


# ──────────────────────────────────────────────────────────────────────────
# ⑥ base 層 P2→P3→P4 key-changing 整合測試（接縫不變式·堵 RAG-ASYNC-HOTFIX-1）
# ──────────────────────────────────────────────────────────────────────────
def test_seam_key_changing_integration():
    """接縫不變式：真翻譯改變標題文字（key-changing），但 P2 section_summaries 之 key 與
    P3 rag_sections 之 summary_key 仍**同基準＝原文標題 path**（譯文 title 僅供顯示）。

    純 mock 同 key 兩端不足以照出退化（RAG-ASYNC-HOTFIX-1）；此處 _DetTr 真把 "Skills"→"ZH::Skills"，
    斷言 summary_key 仍為原文 "Skills"、與 P2 key 對齊 → 下游可正確 match section_summaries。
    """
    tiles = _tiles_3()
    tr = _DetTr()
    fake = _FakeLLM()

    # P2：產 section_summaries（key=原文標題 path）
    section_summaries = se.build_section_summaries(
        tiles, llm=fake, abstract="全文", source_lang="en",
        summary_model="m1", translate_model="m2",
        summary_system_prompt="sp", translate_system_prompt="tp",
        input_chars_cap=2000, max_chars=8000,
    )
    p2_keys = set(section_summaries.keys())

    # P3：collect_render_slots（翻前收 key=原文 path）→ restore（真翻 title）→ collect_rag_sections
    md, slots, zh_by_index = se.restore_sections_markdown(tiles, None, tr, True, max_workers=4)
    rag_sections = []
    se.collect_rag_sections(slots, zh_by_index, True, rag_sections)
    p3_summary_keys = {s["summary_key"] for s in rag_sections}
    p3_display_titles = {s["title"] for s in rag_sections}

    # 接縫不變式：P2 key == P3 summary_key == 原文標題 path
    assert p2_keys == {"Skills", "Education", "Experience"}
    assert p3_summary_keys == p2_keys                       # 同基準（跨譯零位移）
    # 譯文 title 確實已改變（證 key-changing 真實發生、非自洽同 key 假象）
    assert p3_display_titles == {"ZH::Skills", "ZH::Education", "ZH::Experience"}
    # 下游可用 P2 key 命中 P3 section（match 成功）
    for sec in rag_sections:
        assert sec["summary_key"] in section_summaries
