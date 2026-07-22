# FITZ-HOTFIX-1 C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）執行報告

---

**任務代號**：FITZ-HOTFIX-1 C1
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` §8 C1
**上游 plan**：同名 `_plan.md`（v4、六問拍板）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §1 基準與完成狀態

- 基準 commit：`9ca13aa`（PIPE-SYNC-5 checkout、baron 已 ship）
- 完成狀態：R1/R2/R3/R5 四刀已落地、**未 commit**（依 §1.3 由 baron 手動執行）
- **單檔內聚自檢**：`git status -s`（排除 .claude-logs）＝恰為 `processor/fitz_processor.py` + `tests/test_fitz_processor.py` 兩檔

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Fitz Processor Refinement（Fitz 處理器標題救回與結構修復） | [留空，由 baron 回填] |

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `processor/fitz_processor.py` | 修改 | R1/R2/R3/R5 四刀 + 幾何輔助純函式 + `Optional` import |
| `tests/test_fitz_processor.py` | 修改 | +13 測試（R1 ×2／R2 ×2／R3 ×4／R5 ×5） |
| `.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_fitz_processor.py.bak` | 備份 | 改前快照（隨本 commit git add） |
| `.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_test_fitz_processor.py.bak` | 備份 | 改前快照（隨本 commit git add） |

（baton 暫存之 plan/tasks/本報告依鐵律**不入** git add 清單。）

## §4 說明（真因與修法）

### R1 — 圖框內文字排除（重疊面積比演算法）
`_collect_page` 改為**先備判定素材**（`_collect_images` 一趟同時回「圖項目清單」與「全圖框矩形」；同一 xref 多處放置之 rect 全數納入判定）。逐行取完整 bbox `(x0,y0,x1,y1)`，以模組級 `_max_overlap_ratio(bbox, image_rects)` 計「與任一圖框之最大重疊面積 ÷ 行面積」，`> _FIGURE_OVERLAP_MAX (0.5)` 即剔除（不入 lines）。圖本身仍作 figure 保留、資訊不丟；剔除記 `logger.debug` 供審計。

### R2 — repetition key 複合化（救標題、列印 PDF 通案）
`_repetition_key(text, size)` 由回傳字串改回傳 **`(數字歸一文字, round(size,1))` 元組**；`_repeated_band_keys` 與 `_assemble` 兩呼叫端同步傳 `line["size"]`。**通案根因**：瀏覽器列印必於每頁頁首印 `document.title`（小字級 chrome），其文字與文章真標題完全相同，而真標題必在第一頁頂部（常落頂 band）→ 純文字 key 使**每一份列印網頁 PDF 的真標題都必然撞上自己的頁首 chrome key 被誤殺**。加字級後：chrome（7.0pt）跨頁重複照剝、真標題（25.6pt）全文件唯一故存活。

### R3 — heading 第三級 `###`（含 body 字級判定修正）
`_heading_sizes` 回 `(h1, h2, h3)`＝候選前三級（不足補 `0.0`、於 `_heading_level` 為 falsy 故該級自然停用、兩級文件行為不變）；`_heading_level(line, h1, h2, h3)` 新增 `size >= h3 → 3`，`_assemble` 之 `"#" * level` 天然產出 `###`。R1 先淨化（圖表黏字剔除）→ 候選階梯方為真實三層。

**⚠️ 實作期發現並修正之連帶缺陷（既有回歸測試攔下）**：R3 落地後 `test_paragraphs_separated_by_blank_line` 失敗——正文段落被判成 `###`。追因：`_heading_sizes` 原以**全體行**字元權重定「正文字級」，而列印頁首/頁尾 chrome 於短文件中字元量可壓過真正文（該 fixture：band 內 8pt 長 URL 共 92 字元 > 非 band 11pt 正文 79 字元）→ body 誤判為 8pt → 真正文 11pt 落入候選、被 R3 第三級收編。**修法**：拆兩張權重表——**正文字級只由非 band 行決定**（chrome 屬雜訊、不得定義正文），**候選字級仍由全體行枚舉**（真標題常落頂 band，排除 band 會連 h1 一併殺掉、毀 R2 目的）；全文件皆 band 之極端情況退回全體行權重。已加專屬測試 `test_body_size_from_non_band_lines_only` 鎖死。

### R5 — link-tiling nav 剝除（通則）
`_collect_link_rects` 取 `page.get_links()` 之 `from` 矩形（讀取異常 → warning + 空清單、規則自然停用、不阻斷攝入）。`_link_tiling(bbox, link_rects)` 回 `(覆蓋率, 命中 link 數)`——覆蓋率以 **x 區間聯集**計（nav 為水平平鋪；聯集避免重疊 link 重複計面積致低覆蓋行被灌成高覆蓋而誤殺正文）。閘門：`n_links >= 3` **且** `coverage >= 0.6` → 剔除。雙閾值各擋一種誤殺：links 數擋「帶連結的標題/裸 URL 行」（單 link）；覆蓋率擋「正文句內 inline link」。無 link 註記之 PDF → 空清單 → no-op。

## §5 測試與 Grep 結果

```
tests/test_fitz_processor.py：29 passed（16 既有 + 13 新增）in 0.23s
全套件：933 passed, 3 skipped, 3 warnings in 55.88s   ← 基線 920 + 13、零回歸
```

新增 13 測試：
- **R1**：`test_overlap_ratio_math`（全覆蓋 1.0／30%／不相交 0.0／無圖框）；`test_inside_figure_line_dropped_and_wrapped_line_kept`（實體 PDF：圖框正中黏字剔除、圖外正文保留、圖本身仍在）
- **R2**：`test_key_includes_size`（同文不同字級 → 不同 key）；`test_chrome_stripped_but_same_text_title_survives`（3 頁 7.0pt chrome + 第一頁 25.6pt 同文真標題 → `# TITLE` 存活且全文恰出現 1 次）
- **R3**：`test_three_tier_ladder`（`[25.6, 20.9, 17.1]` → 1/2/3、正文 15.2 不升格）；`test_two_tier_document_regression`（h3=0.0 停用）；`test_body_size_from_non_band_lines_only`（**連帶缺陷守門**）；`test_three_tier_end_to_end`（實體 PDF `#`/`##`/`###` 三級齊出）
- **R5**：`test_tiling_ratio_uses_x_interval_union`（5 links 84%／重疊 link 聯集不重複計 30%／無 link）；`test_nav_row_dropped`（5 link 平鋪整行剝除、標題與正文不受影響）；`test_single_link_row_kept`；`test_inline_link_in_body_kept`；`test_no_link_annotations_is_noop`

驗收 grep（§6.1 全項）：

```
R2：132:def _repetition_key(text: str, size: float) -> Tuple[str, float]  ✅
R3：359 def _heading_sizes(...) -> Tuple[float, float, float] / 392 return (h1, h2, h3)  ✅
R1/R5：46 _FIGURE_OVERLAP_MAX=0.5 / 50 _NAV_MIN_LINKS=3 / 207 _max_overlap_ratio 判定 / 215 nav 閘門  ✅
單檔內聚：git status -s（排除 .claude-logs）＝ fitz_processor.py + test_fitz_processor.py 兩檔  ✅
```

SOP 一致性核查（§6.5）：

```
logging：grep logger.error → 僅既有 L167（解析失敗、含 exc_info=True）；
         新增 2 處 logger.warning 皆含 exc_info=True（grep -c 驗證＝2）；零 traceback.format_exc
database：grep "\.commit()" → 無命中（合規：本案零 DB）
```

## §6 不可動清單遵守狀態

- [x] `processor/pdf_processor.py`（MinerU impl）／`pipeline_core.py`／A 軌處理器鏈 — byte 不動
- [x] `pipelines/section_engine.py`／`pipelines/litedoc_pipeline.py`／`pipelines/ingestion_engine.py`／`pipelines/image_filter.py`／`processor/rag_indexer.py`／`contracts.py`／`web_server.py` — 零改（C1 單檔內聚）
- [x] resume／slides／book／academic 各路 — 零碰
- [x] 同形 .md 硬契約不變（`\n\n` 段落／`![](images/)`／`page_{page_idx}_{xref}` 命名）；R3 新增 `###` 屬既有 markdown 語法
- [x] 旗標語意零改（`LITEDOC_FITZ_ENABLED` 仍為 fitz 路總關回）
- [x] 未執行 git commit / push

## §7 銜接

- baton 狀態：plan / tasks / 本報告均暫存 `baton/`、未 mv 未 git add（Checkout 鐵律）。
- 下一步：**C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）**（R6 `ingestion_engine` `meta_values` 純加法 + `_extract_litedoc_metadata` 時序前移 + R7 數字短行清理）；待 baron ship C1 後另下 C2 提示詞。
- 收官前 §7.2 整合測試（tasks §6.4）於 C3 或 Checkout 前補齊（屆時三刀齊備、可端到端串接驗證）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列、2 .bak）

# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_test_fitz_processor.py.bak

# 3. commit message 草稿（已寫入 /tmp/FITZ-HOTFIX-1_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C1_msg.txt
```
