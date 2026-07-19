# === [PIPE-INGEST C1] ===
"""ingestion_engine 單元測試（PIPE-INGEST C1）。

覆蓋 plan v4 §2.1 引擎硬規格：title 抽取 / 非連續 meta 分離 / soft-fail 三態 /
figure content 重建 + caption 關聯 / table・formula 語意等價 / section 層級樹 /
title 零加工 / 零文體字面量靜態掃描 / TilingProcessor 接口相容。
"""

import inspect
import json

from pipelines import ingestion_engine as ie


# ──────────────────────────────────────────────────────────────────────────
# 測試素材（對映 SpaceX 實證樣本形狀：epigraph 夾於 byline 之前 → 判型行不連續）
# ──────────────────────────────────────────────────────────────────────────
SAMPLE_MD = "\n".join([
    "# Doc Main Title",                     # 0  title
    "",                                     # 1
    "Earth is the cradle of humanity.",     # 2  epigraph（intro_text、非 meta）
    "",                                     # 3
    "AUTHOR ONE AND AUTHOR TWO JUN 15",     # 4  authors
    "",                                     # 5
    "PUBLISHER NEWS",                       # 6  publication_info
    "",                                     # 7
    "Region | Tech | Opinion",              # 8  publication_info
    "",                                     # 9
    "Intro paragraph before sections.",     # 10 內文
    "",                                     # 11
    "## Section Alpha",                     # 12
    "Alpha body line.",                     # 13
    "![fig alt](images/pic1.jpg)",          # 14
    "Figure 1: sample caption",             # 15
    "### Alpha Child",                      # 16
    "Child body line.",                     # 17
    "$$ E=mc^2 $$",                         # 18
    "## Section Beta",                      # 19
    "<html><body><table><tr><td>x</td></tr></table></body></html>",  # 20
    "Beta body line.",                      # 21
])

SAMPLE_STRUCTURE = {
    "structure": [
        {"start": 0, "end": 0, "type": "title"},
        {"start": 2, "end": 2, "type": "intro_text"},
        {"start": 4, "end": 4, "type": "authors"},
        {"start": 6, "end": 6, "type": "publication_info"},
        {"start": 8, "end": 8, "type": "publication_info"},
    ]
}


def _assemble(md=SAMPLE_MD, structure=SAMPLE_STRUCTURE):
    return ie.assemble(md, structure)


def _walk_blocks(sections):
    for sec in sections:
        for item in sec.get("content", []):
            yield sec, item
        yield from _walk_blocks(sec.get("children", []))


def _all_text(sections):
    return "\n".join(
        item.get("content", "")
        for _sec, item in _walk_blocks(sections)
        if item.get("type") == "text"
    )


# ──────────────────────────────────────────────────────────────────────────
# title 抽取
# ──────────────────────────────────────────────────────────────────────────
class TestExtractTitle:
    def test_first_heading_becomes_title(self):
        title, idx = ie.extract_title(SAMPLE_MD.split("\n"))
        assert title == "Doc Main Title"
        assert idx == 0

    def test_no_heading_returns_empty(self):
        title, idx = ie.extract_title(["plain line", "another"])
        assert title == ""
        assert idx is None

    def test_title_not_hidden_in_output(self):
        # plan §2.1「title 不丟」：assemble 頂層欄位交付
        result = _assemble()
        assert result["title"] == "Doc Main Title"


# ──────────────────────────────────────────────────────────────────────────
# meta 分離（非連續判型）
# ──────────────────────────────────────────────────────────────────────────
class TestMetaSeparation:
    def test_noncontiguous_meta_blocks_all_separated(self):
        """epigraph（非 meta）夾於 title 與 authors 之間，不得使後續判型作廢。"""
        result = _assemble()
        meta = result["meta"]
        assert meta["authors"] == ["AUTHOR ONE AND AUTHOR TWO JUN 15"]
        assert meta["publication_info"] == ["PUBLISHER NEWS", "Region | Tech | Opinion"]

    def test_meta_lines_not_in_body(self):
        body = _all_text(_assemble()["sections"])
        assert "AUTHOR ONE" not in body
        assert "PUBLISHER NEWS" not in body
        assert "Region | Tech" not in body

    def test_title_line_not_in_body(self):
        sections = _assemble()["sections"]
        body = _all_text(sections)
        assert "Doc Main Title" not in body
        assert all(sec["title"] != "Doc Main Title" for sec, _ in _walk_blocks(sections))

    def test_non_meta_lines_survive_in_body(self):
        """epigraph 與 intro（未判 meta 型）必須留在內文（孤兒容器）。"""
        body = _all_text(_assemble()["sections"])
        assert "Earth is the cradle of humanity." in body
        assert "Intro paragraph before sections." in body


# ──────────────────────────────────────────────────────────────────────────
# soft-fail 容錯
# ──────────────────────────────────────────────────────────────────────────
class TestSoftFail:
    def test_structure_none(self):
        result = _assemble(structure=None)
        assert result["meta"] == {}
        # 無 meta 分離 → authors 行退化留在內文（回現況行為）
        assert "AUTHOR ONE" in _all_text(result["sections"])
        # 但 title 行仍不入內文
        assert "Doc Main Title" not in _all_text(result["sections"])

    def test_structure_empty_dict(self):
        result = _assemble(structure={})
        assert result["meta"] == {}

    def test_structure_line_out_of_range(self):
        bad = {"structure": [{"start": 4, "end": 999, "type": "authors"}]}
        result = _assemble(structure=bad)
        assert result["meta"] == {}
        assert "AUTHOR ONE" in _all_text(result["sections"])

    def test_structure_malformed_block(self):
        bad = {"structure": [{"type": "authors"}]}  # 缺 start/end
        result = _assemble(structure=bad)
        assert result["meta"] == {}


# ──────────────────────────────────────────────────────────────────────────
# figure / table / formula 分塊
# ──────────────────────────────────────────────────────────────────────────
class TestBlocks:
    def test_figure_has_rebuildable_content(self):
        """缺陷② 病根規格：figure 必帶 content=![alt](src)。"""
        figs = [
            item for _sec, item in _walk_blocks(_assemble()["sections"])
            if item.get("type") == "figure"
        ]
        assert len(figs) == 1
        fig = figs[0]
        assert fig["src"] == "images/pic1.jpg"
        assert fig["alt"] == "fig alt"
        assert fig["content"] == "![fig alt](images/pic1.jpg)"

    def test_figure_caption_attached_and_not_text(self):
        result = _assemble()
        figs = [
            item for _sec, item in _walk_blocks(result["sections"])
            if item.get("type") == "figure"
        ]
        assert figs[0].get("caption") == "Figure 1: sample caption"
        assert "sample caption" not in _all_text(result["sections"])

    def test_table_block_semantics(self):
        tables = [
            item for _sec, item in _walk_blocks(_assemble()["sections"])
            if item.get("type") == "table"
        ]
        assert len(tables) == 1
        assert tables[0]["content"].startswith("<html><body><table>")

    def test_formula_block_semantics(self):
        formulas = [
            item for _sec, item in _walk_blocks(_assemble()["sections"])
            if item.get("type") == "formula"
        ]
        assert len(formulas) == 1
        content = formulas[0]["content"]
        assert content.startswith("$$") and content.endswith("$$")
        assert "E=mc^2" in content

    def test_blank_lines_produce_no_empty_text_blocks(self):
        for _sec, item in _walk_blocks(_assemble()["sections"]):
            if item.get("type") == "text":
                assert item["content"].strip() != ""


# ──────────────────────────────────────────────────────────────────────────
# section 層級樹
# ──────────────────────────────────────────────────────────────────────────
class TestSectionTree:
    def test_hierarchy_and_orphan_container(self):
        sections = _assemble()["sections"]
        # 孤兒容器（epigraph + intro）在最前、無標題
        assert sections[0]["title"] == ""
        # 兩個 top-level section
        titles = [s["title"] for s in sections[1:]]
        assert titles == ["Section Alpha", "Section Beta"]

    def test_child_nesting_by_level(self):
        sections = _assemble()["sections"]
        alpha = sections[1]
        assert alpha["level"] == 2
        assert [c["title"] for c in alpha["children"]] == ["Alpha Child"]
        assert alpha["children"][0]["level"] == 3

    def test_section_title_verbatim_no_rework(self):
        """接縫契約：section title＝heading 原文零加工（原文標題 path 基準零位移）。"""
        md = "# T\n\n## 2.1 Alpha-Beta: Gamma (raw)\nbody"
        sections = ie.assemble(md, None)["sections"]
        assert sections[0]["title"] == "2.1 Alpha-Beta: Gamma (raw)"

    def test_content_belongs_to_own_section(self):
        sections = _assemble()["sections"]
        alpha = sections[1]
        alpha_text = "\n".join(
            b["content"] for b in alpha["content"] if b["type"] == "text"
        )
        assert "Alpha body line." in alpha_text
        assert "Beta body line." not in alpha_text


# ──────────────────────────────────────────────────────────────────────────
# 引擎紀律：零文體字面量（靜態掃描、比照 section_engine 慣例）
# ──────────────────────────────────────────────────────────────────────────
class TestEngineDiscipline:
    def test_no_route_literals_in_source(self):
        src = inspect.getsource(ie)
        forbidden = [
            "doc_type", "litedoc", "resume", "slides",
            "academic", "news", "book", "technical",
        ]
        for token in forbidden:
            assert token not in src, f"引擎源碼不得含文體字面量: {token!r}"

    def test_no_a_track_processor_imports(self):
        src = inspect.getsource(ie)
        assert "from processor" not in src and "import processor" not in src


# ──────────────────────────────────────────────────────────────────────────
# TilingProcessor 接口相容（bypass 路徑、免 embedding）
# ──────────────────────────────────────────────────────────────────────────
class TestTilingCompat:
    def test_assemble_output_feeds_tiling_processor(self, tmp_path):
        """assemble 產物直餵 TilingProcessor（<5000 字走 bypass、零 API）不炸。"""
        from processor.tiling_processor import TilingProcessor

        result = _assemble()
        processed = tmp_path / "processed.json"
        tiled = tmp_path / "tiled.json"
        processed.write_text(
            json.dumps(
                {"title": result["title"], "sections": result["sections"]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        TilingProcessor().process(str(processed), str(tiled))
        data = json.loads(tiled.read_text(encoding="utf-8"))
        assert isinstance(data.get("sections"), list) and data["sections"]
        # figure block 穿透 tiling 且 content 鍵保留（缺陷② 全鏈前半段）
        figs = [
            item for _sec, item in _walk_blocks(data["sections"])
            if item.get("type") == "figure"
        ]
        assert figs and figs[0].get("content") == "![fig alt](images/pic1.jpg)"
        # tiling 自補索引欄（引擎不產）：全 block 補 part、text 合併塊補 index
        assert all("part" in item for _sec, item in _walk_blocks(data["sections"]))
        assert all(
            "index" in item
            for _sec, item in _walk_blocks(data["sections"])
            if item.get("type") == "text"
        )
# === [PIPE-INGEST C1 END] ===


# === [PIPE-INGEST C3 START] §7.2 跨 Phase 整合測試（WORKFLOW_SOP §7.2、Checkout 必驗）===
class TestCrossPhaseIntegration:
    """cleaned md + 判型 → assemble → collect_render_slots → key-changing mock 翻譯 → 組裝。

    key-changing transform（譯文≠原文）為 §7.2 硬要求——純 mock 同 key 兩端不予承認；
    斷言接縫不變式：figure 全穿透 / 標題不入內文 / meta 零重播 / node key 原文基準對位。
    """

    def _run_chain(self):
        from pipelines import section_engine

        result = ie.assemble(SAMPLE_MD, SAMPLE_STRUCTURE)
        slots = section_engine.collect_render_slots(result["sections"], 0, "")
        # key-changing mock 翻譯：譯文＝[譯] 前綴（≠ 原文）
        zh_by_index = {
            i: f"[譯]{s['text']}"
            for i, s in enumerate(slots)
            if s["kind"] in ("title", "content")
        }
        rendered = []
        for i, slot in enumerate(slots):
            if slot["kind"] == "raw":
                rendered.append(slot["text"])
            elif slot["kind"] == "title":
                rendered.append(f"{'#' * slot['level']} {zh_by_index[i]}")
            else:
                rendered.append(zh_by_index[i])
        return result, slots, zh_by_index, "\n\n".join(rendered)

    def test_figures_survive_key_changing_chain(self):
        """缺陷② 接縫不變式：figure content 經 raw slot 穿透至譯後組裝輸出。"""
        _result, _slots, _zh, out = self._run_chain()
        assert "![fig alt](images/pic1.jpg)" in out

    def test_title_and_meta_not_replayed(self):
        """缺陷①③ 接縫不變式：文件標題與 meta 行零重播於譯後內文。"""
        _result, _slots, _zh, out = self._run_chain()
        assert "Doc Main Title" not in out
        assert "AUTHOR ONE" not in out
        assert "PUBLISHER NEWS" not in out
        # 非 meta 內文（epigraph）正常穿透（防過度剔除）
        assert "[譯]Earth is the cradle of humanity." in out

    def test_node_key_alignment_under_translation(self):
        """P2/P4 對位不變式：summary_key＝原文標題 path、譯文改變 key 不動（RAG-ASYNC #1 防回歸）。"""
        from pipelines import section_engine

        _result, slots, zh_by_index, _out = self._run_chain()
        title_slots = [(i, s) for i, s in enumerate(slots) if s["kind"] == "title"]
        keys = [s["key"] for _i, s in title_slots]
        assert "Section Alpha" in keys
        assert "Section Alpha/Alpha Child" in keys
        # 模擬 P2 section_summaries（key＝原文標題 path）→ 譯後仍可對位
        mock_summaries = {k: f"摘要-{k}" for k in keys}
        for i, s in title_slots:
            assert s["key"] in mock_summaries          # key-changing 下 key 零位移
            assert zh_by_index[i] != s["key"]           # 譯文確實已變（非同 key 假整合）
        # collect_rag_sections：summary_key 保原文 path、title 存譯文（雙欄分離）
        sink = []
        section_engine.collect_rag_sections(slots, zh_by_index, True, sink)
        alpha = [x for x in sink if x.get("summary_key") == "Section Alpha"]
        assert alpha and alpha[0]["title"] == "[譯]Section Alpha"
# === [PIPE-INGEST C3 END] ===
