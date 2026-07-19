# PIPE-INGEST C1 — Ingestion Engine（攝入引擎本體）執行報告

---

**任務代號**：PIPE-INGEST C1
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md`（v4）
**次級參考**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md`（§8 C1）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `c258af2`（BRAINSTORM-1 checkout）。litedoc P1 仍走 A 軌組裝借用鏈（`md_processor`→`json_processor`→`TilingProcessor`）；figure block 無 `content` 鍵致圖片全滅、title 遭 `_load_tiles` 丟棄、meta 判型被連續性假設作廢——引擎不存在。
- **完成狀態**：新增 `pipelines/ingestion_engine.py`（B 軌自有攝入組裝引擎、269 行）+ `tests/test_ingestion_engine.py`（23 測試全綠）。**純加法、零接線**（`grep -rn "ingestion_engine" pipelines/litedoc_pipeline.py` → 0 命中）、零 runtime 行為變化；全套件 771 passed（基線 748 + 新增 23、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v4 §2.1（ingestion_engine 硬規格六項）；無偏離——title 不丟／meta 非連續分離／figure `content` 重建／table・formula 語意等價／零文體字面量／TilingProcessor 相容全數落地並經測試斷言。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新增 B 軌自有攝入組裝引擎 `pipelines/ingestion_engine.py` + `tests/test_ingestion_engine.py`（23 測試、含零文體字面量靜態掃描與 tiling 相容） | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `pipelines/ingestion_engine.py` | —（全新檔、無需備份） | 攝入組裝引擎：`extract_title` / `mark_meta_lines` / `split_blocks` / `build_sections` / `assemble` 五純函式 |
| 新建 | `tests/test_ingestion_engine.py` | —（全新檔、無需備份） | 23 測試：title 抽取 ×3 / 非連續 meta 分離 ×4 / soft-fail ×4 / 分塊 ×5 / 層級樹 ×4 / 引擎紀律 ×2 / tiling 相容 ×1 |

> baton/ 暫存之 plan / tasks / 本執行報告依鐵律**不在** git add 清單（Checkout 一次性歸檔）。

---

## §4 實作說明

### §4.1 `pipelines/ingestion_engine.py` — 引擎本體（tasks §8 C1 細節逐項落地）

- **`extract_title(lines)`**：首個 `#` heading 行 → `(title 文字, 行號)`；無則 `('', None)`。
- **`mark_meta_lines(lines, structure, meta_types, title_idx)`**：判型 blocks **逐塊獨立標記**（廢除連續性假設——非 meta 行夾雜不使後續判型作廢）；`type=="title"` blocks 與 title 行一律標 meta；先整批驗證行號、**任一越界／格式不符 → 整體 soft-fail**（`meta={}`、僅 title 行仍不入內文，回現況行為不阻斷）：

```python
# 先整批驗證行號（任一越界 → 整體 soft-fail，不做半套分離）
for block in blocks:
    start, end = int(block["start"]), int(block["end"])
    if start < 0 or end < start or end >= len(lines):
        logger.warning("[PIPE-INGEST] 判型行號越界（…）、跳過 meta 分離（soft-fail）")
        return fallback
```

- **`split_blocks(lines)`**：單次保序掃描、語意對齊既有分塊器（formula `$$ body $$`／table 原行 `content`／figure caption 上下行查找同語意 regex）；**figure 必帶 `content`（缺陷② 病根規格）**：

```python
fig_block = {"type": "figure", "src": src, "alt": alt,
             "content": f"![{alt}]({src})"}
```

- **`build_sections(lines, meta_flags)`**：heading 層級棧組裝父子；首 heading 前孤立內容 → 無標題容器 section；**section title＝heading 原文零加工**（P2/P4「原文標題 path」基準零位移、接縫契約）。
- **`assemble(markdown_text, structure, *, meta_types=DEFAULT_META_TYPES)`**：頂層入口 → `{"title", "meta", "sections"}`；sections 為 processed 相容 schema（`index`/`part` 由 tiling 自補、引擎不產）。
- **引擎紀律**：全模組零文體字面量（`grep -c "doc_type"` → 0）、零 import 任何 A 軌 processor、`meta_types` 由呼叫端注入（預設值為判型 schema 型別 token、非文體名）。
- **logging SOP**：模組級 logger、異常路徑一律 `logger.warning(..., exc_info=True)`、無 `logger.error`、無 `basicConfig`；**零 DB 操作**。

### §4.2 `tests/test_ingestion_engine.py` — 23 測試

- 素材 `SAMPLE_MD` 對映 SpaceX 實證形狀（**epigraph 夾於 byline 之前** → 判型行不連續之關鍵情境）。
- 關鍵斷言：非連續 meta 全分離且不入 body／title 不入 body 也不成 section／soft-fail 三態（None／空 dict／行號越界／缺欄）退化行為／figure `content=![alt](src)` + caption 關聯且 caption 不重複出現於 text／零文體字面量**靜態掃描**（`inspect.getsource` 掃 `doc_type`/8 路由 token）／**真實 `TilingProcessor().process()` 直餵**（<5000 字 bypass 路徑、零 API）：figure `content` 穿透 tiling、`part` 全補、text 合併塊補 `index`。
- 測試中途修正一處：初版斷言「所有 block 補 `index`」與 tiling bypass 實況不符（bypass 僅 text 合併塊補 `index`、全 block 補 `part`），已依實測輸出修正斷言（引擎代碼零改、屬測試對 tiling 既有行為的認知校準）。
  - **零影響之真正機制（2026-07-19 baron 覆驗修正）**：litedoc 消費 tiles 靠 `collect_render_slots`「原 DFS **pre-order**」之 **list 順序**、**不讀 `(index, part)` 排序**（`section_engine.py:207`）——`(index, part)` 兩欄屬 **A軌 `md_restore`**、litedoc 不碰。故 bypass 圖片**缺 index** 對 litedoc 排序**零影響**。⚠️ 更正：並非「圖片保留原始 index」——實測 `ingestion_engine`/`processed.json` 之 figure **本就無 index 鍵**（19 圖 0 有）；零影響是「litedoc 不用 index」而非「圖片有 index」。⚠️ 隱含依賴：若未來 litedoc 有 consumer 改用 `(index,part)`，此結論即失效。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M .claude-logs/TODO.md
 M .claude-logs/prompts/INDEX.md
?? pipelines/ingestion_engine.py
?? tests/test_ingestion_engine.py
```

### §5.2 新測試（實貼）

```
tests/test_ingestion_engine.py::TestExtractTitle::test_first_heading_becomes_title PASSED
tests/test_ingestion_engine.py::TestExtractTitle::test_no_heading_returns_empty PASSED
tests/test_ingestion_engine.py::TestExtractTitle::test_title_not_hidden_in_output PASSED
tests/test_ingestion_engine.py::TestMetaSeparation::test_noncontiguous_meta_blocks_all_separated PASSED
tests/test_ingestion_engine.py::TestMetaSeparation::test_meta_lines_not_in_body PASSED
tests/test_ingestion_engine.py::TestMetaSeparation::test_title_line_not_in_body PASSED
tests/test_ingestion_engine.py::TestMetaSeparation::test_non_meta_lines_survive_in_body PASSED
tests/test_ingestion_engine.py::TestSoftFail::test_structure_none PASSED
tests/test_ingestion_engine.py::TestSoftFail::test_structure_empty_dict PASSED
tests/test_ingestion_engine.py::TestSoftFail::test_structure_line_out_of_range PASSED
tests/test_ingestion_engine.py::TestSoftFail::test_structure_malformed_block PASSED
tests/test_ingestion_engine.py::TestBlocks::test_figure_has_rebuildable_content PASSED
tests/test_ingestion_engine.py::TestBlocks::test_figure_caption_attached_and_not_text PASSED
tests/test_ingestion_engine.py::TestBlocks::test_table_block_semantics PASSED
tests/test_ingestion_engine.py::TestBlocks::test_formula_block_semantics PASSED
tests/test_ingestion_engine.py::TestBlocks::test_blank_lines_produce_no_empty_text_blocks PASSED
tests/test_ingestion_engine.py::TestSectionTree::test_hierarchy_and_orphan_container PASSED
tests/test_ingestion_engine.py::TestSectionTree::test_child_nesting_by_level PASSED
tests/test_ingestion_engine.py::TestSectionTree::test_section_title_verbatim_no_rework PASSED
tests/test_ingestion_engine.py::TestSectionTree::test_content_belongs_to_own_section PASSED
tests/test_ingestion_engine.py::TestEngineDiscipline::test_no_route_literals_in_source PASSED
tests/test_ingestion_engine.py::TestEngineDiscipline::test_no_a_track_processor_imports PASSED
tests/test_ingestion_engine.py::TestTilingCompat::test_assemble_output_feeds_tiling_processor PASSED

============================== 23 passed in 0.53s ==============================
```

### §5.3 全套件（實貼）

```
771 passed, 3 skipped, 3 warnings in 55.13s
```

基線 748 passed → **771 passed（+23、0 failed、零回歸）**。

### §5.4 §6.1 驗收 grep（實貼）

```
--- doc_type 字面量（期望 0）
0
--- assemble 入口
pipelines/ingestion_engine.py:266:def assemble(
--- figure content 重建
165: f"![{alt}]({src})",
--- litedoc 零接線（期望 0 命中）
（grep 無命中、exit=1）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/ingestion_engine.py tests/test_ingestion_engine.py
無命中（合規）——引擎異常路徑一律 logger.warning(..., exc_info=True)
--- database：grep -nE "\.commit\(\)" pipelines/ingestion_engine.py tests/test_ingestion_engine.py | grep -v "with .*session.*begin()"
無命中（合規）——模組零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `processor/md_processor.py`、`processor/json_processor.py` — 零改（僅讀取對照語意）
- [x] `pipeline_core.py` 及 A 軌鏈全體 — 零改
- [x] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py` — 零改
- [x] `pipelines/section_engine.py` — 零改
- [x] `pipelines/litedoc_pipeline.py` — 零改（C1 零接線、grep 實證 §5.4）
- [x] 母翻譯提示詞 / `pipelines/contracts.py` / `processor/rag_indexer.py` — 零改
- [x] 工具層四檔（pdf_processor / md_cleaner / doc_analyzer / tiling_processor）— 零改
- [x] `settings.py` 旗標預設值 — 零改
- [x] 既有 tests 斷言本體 — 零改（僅新增測試檔）
- [x] 禁 constraints 鷹架 — 未向任何 `InjectionContext.constraints` 注入內容

---

## §7 銜接

- **baton 狀態**：本報告 + plan v4 + tasks + design spec 均暫存 `baton/`、未 mv 未 git add（Checkout 一次性歸檔）；`litedoc_shadow_artifacts/` 證據附件續留。
- **自評（正向）**：本 commit 推進 plan §2.1（引擎六硬規格全數落地）、為 §2.2（C2 P1 切換）鋪平唯一前置；**（負向防錯）**：tiling bypass 索引欄行為與 tasks 預估有一處出入（`index` 僅 text 合併塊），已以實測校準測試、引擎規格零影響，C2 接線無需變更。**零影響之機制（baron 覆驗）**：litedoc 靠 `collect_render_slots` list 順序（DFS pre-order）消費、**不讀 `(index,part)`**〔A軌 md_restore 之欄〕，故 bypass 圖片缺 index 不影響 litedoc 排序（非「圖片保留原始 index」·圖片本無 index 鍵）；⚠️ 若未來 litedoc 改用 (index,part) 則失效（§4.2 詳）。
- **下一步**：C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）；等 baron 確認本 commit 後另行下達 C2 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（本 Commit 僅新增，無需備份）

# 2. git add 清單（僅包含本次 C1 實質新增之模組與測試；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/ingestion_engine.py
git add tests/test_ingestion_engine.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST_C1_msg.txt）
cat > /tmp/PIPE-INGEST_C1_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST C1 — Ingestion Engine（攝入引擎本體）

1. 新增 B 軌自有攝入組裝引擎 pipelines/ingestion_engine.py，支援 title 提取、meta 欄位與正文分離（不受行連續性限制）、figure Markdown content 重建與 caption 關聯，且產出與 TilingProcessor 介面相容之 section 樹。
2. 秉持引擎設計紀律，模組中絕不寫入 doc_type 字面量，一律採用參數注入方式以利 academic/book 繼承。
3. 新增 tests/test_ingestion_engine.py 覆蓋引擎所有邊界與 soft-fail 容錯規格，並包含 doc_type 靜態掃描防護與 tiling 相容性測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST_C1_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C1 執行完成——引擎 + 23 測試、771 passed 零回歸、SOP 雙核查合規、零接線純加法
