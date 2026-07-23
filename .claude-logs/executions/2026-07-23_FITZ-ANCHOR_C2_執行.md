# FITZ-ANCHOR C2 執行報告 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場）

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-ANCHOR C2 |
| **工作流類別** | BE-Refactor |
| **狀態** | Completed (Commit C2)（Git hash 待 baron 回填） |
| **基準 Commit** | `b48961a`（FITZ-ANCHOR C1） |
| **依據 plan** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`（v2） |
| **依據 tasks** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`（§8 C2） |
| **執行日期** | 2026-07-23 |

---

## §1 基準與完成狀態

- 於基準 `b48961a`（FITZ-ANCHOR C1）之上實作 C2「Meta Anchor & Title Reinjection」。
- 程式改動已完成、測試全綠；**尚未 commit**（依 CLAUDE.md §1.3，實體 `git commit`/`push` 由 baron 手動執行）。
- baton 暫存文件（本執行報告、C1 報告、plan、tasks）**留在 `baton/`、未 `mv`、未 `git add`**（待 Checkout 一次性歸檔）。

## §2 Commit 表格

| Commit 代號 | Subject | 落地 Hash |
|---|---|---|
| C2 | BE-Refactor: FITZ-ANCHOR C2 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場） | 待 baron 回填 |

## §3 變動檔案清單

**實質改動代碼（3 實體檔 + 3 測試檔 + settings 常數 + .env.example）**：

| 檔案 | 變動 |
|---|---|
| `settings.py` | 新增 `LITEDOC_ANCHOR_MAX_PAGES = int(os.getenv("LITEDOC_ANCHOR_MAX_PAGES", "2"))`（`[FITZ-ANCHOR C2]` 標記塊） |
| `.env.example` | 新增 `# LITEDOC_ANCHOR_MAX_PAGES=2` 註解 |
| `pipelines/litedoc_pipeline.py` | **U1** `_read_anchor_text` + P1 錨定接點 + `_extract_litedoc_metadata` 恢復單參；**U2** `_reinject_title` + analyze 前接線；**U3** `_load_source_hints` 全函式刪除、`hints=` 接線刪除 |
| `processor/fitz_processor.py` | **U3** 生產端退場：`_URL_RE` 常數、sidecar JSON 寫檔塊、`_assemble` URL 捕捉與 `chrome_urls` 收集全刪；`_assemble` 回傳改 `List[str]`；`import json` 清除（now-unused） |
| `pipelines/section_engine.py` | **U6** `_title_echo_match` 子字串分支加 `min/max >= 0.5` 長度比守衛（一行 + 註） |
| `tests/test_fitz_processor.py` | K2 `TestK2ChromeUrlHint`（2）→ `TestU3SidecarRetired`（2·sidecar 不產出 + `_URL_RE` 移除）；`import json as _json` 清除 |
| `tests/test_litedoc_pipeline.py` | K2 `TestK2HintLoading`（4）刪除；新增 `TestC2AnchorText`（3）+ `TestC2ReinjectTitle`（5）+ `TestC2SidecarRetired`（3）+ §7.2 整合（1）；R6 timing spy 對齊單參簽名 |
| `tests/test_section_engine.py` | 新增 U6 三測試（短標題非回聲 / lede 不誤剝 / 真回聲照剝） |

**備份（6 `.bak`，已置於 `.claude-logs/archive/`）**：

- `2026-07-23_FITZ-ANCHOR_C2_litedoc_pipeline.py.bak`
- `2026-07-23_FITZ-ANCHOR_C2_fitz_processor.py.bak`
- `2026-07-23_FITZ-ANCHOR_C2_section_engine.py.bak`
- `2026-07-23_FITZ-ANCHOR_C2_test_litedoc_pipeline.py.bak`
- `2026-07-23_FITZ-ANCHOR_C2_test_fitz_processor.py.bak`
- `2026-07-23_FITZ-ANCHOR_C2_test_section_engine.py.bak`

**diff stat**：

```
 .env.example                   |   3 +
 pipelines/litedoc_pipeline.py  | 116 +++++++++++++------
 pipelines/section_engine.py    |   8 +-
 processor/fitz_processor.py    |  44 +++----
 settings.py                    |   7 ++
 tests/test_fitz_processor.py   |  37 +++---
 tests/test_litedoc_pipeline.py | 253 +++++++++++++++++++++++++++++++----------
 tests/test_section_engine.py   |  26 +++++
 8 files changed, 346 insertions(+), 148 deletions(-)
```

> ⚠️ 暫存於 `baton/` 之本執行報告與 C1 報告、plan/tasks **不列入 git add 清單**（見 §8）。

## §4 說明

### U1 — meta 錨定前移（重要性判斷交 LLM、零新增呼叫）

**真因**：litedoc P1 原本讓 cover-prompt 吃**已被幾何刀切割過的 md**——fitz 三輪 hotfix 的失手全屬「幾何啟發式猜錯重要性」（標題被當浮水印/頁首、lede 被當回聲），受損 md 進 LLM 使 meta 抽取先天不利。

**修法**：新增靜態 `_read_anchor_text(pdf_path)`——`fitz.open` 逐頁 `get_text("text")` 取前 `settings.LITEDOC_ANCHOR_MAX_PAGES`（=2）頁**原始文字層**、`"\n".join`；任何異常 `logger.warning(exc_info=True)` 回 `""`。P1 接點（R7 之後）改：

```python
anchor = self._read_anchor_text(pdf_path)
meta = self._extract_litedoc_metadata(anchor if anchor.strip() else markdown_text)
```

- 錨定裸文字**零過濾**、含完整版面線索（含 chrome URL）→ LLM 判 title/authors/date/publisher/language 遠比受損 md 準；**同一次 cover-prompt、換更好的輸入**（零新增呼叫）。
- 錨定空（掃描件/加密/壞檔）→ fail-open 退回現行 md 文首，**不成新 SPOF**。
- 與 design spec F6 一致：讀正文文字層、零檔案屬性依賴（不讀 `/Title`）。
- 時序：meta 抽取隨 U2 回注需求前移至 ③ analyze 之前（仍在 `_build_tiles` 之前，R6 值注入不變）；`_extract_litedoc_metadata` 恢復單參數、`[:_META_INPUT_CHARS]` 截斷窗語意不變。

### U2 — 標題回注 promote-else-inject（整類標題誤殺的最終保底）

**真因**：無論哪把幾何刀誤殺標題（浮水印規則、頁首 band、字級判定），下游 md 就是缺 title heading。逐刀補丁是打地鼠。

**修法**：新增靜態 `_reinject_title(md_path, title)`，接線於 R7 之後、③ `DocAnalyzer().analyze` 之前、`markdown_text` 重讀之前（回注行進 sidecar 行號基準、下游行界同基準）。正規化（`re.sub(r"\s+","",…).casefold()`）比對三分支：

- **(a) heading 已在**：存在 `#` 開頭且正規化相等之行 → `return`（不重複注入）。
- **(b) promote**：存在正文行正規化相等 → 就地改寫為 `# {原行}` + `logger.warning(case=promote)`。
- **(c) inject**：全文缺席 → 頂部 `# {title}\n\n` + `logger.warning(case=inject)`。
- **空 title**（錨定失敗）→ 直接 `return`，現行 `_resolve_title` 兜底鏈原樣運作。

呼叫端傳 `str(meta.get("title") or "").strip()`（錨定 title）；warning 供版式觀測（哪個網站版式又騙過幾何層、不必等 E2E）。與哪把刀誤殺無關、單點終局保底。

### U3 — HOTFIX-3 K2 sidecar 管線退場（被 U1 吸收、生產/消費端同刀移除）

**真因**：HOTFIX-3 K2 為補 publisher 而建 `_source_hints.json` sidecar（fitz 生產、litedoc 消費）——U1 錨定改吃前 N 頁裸文字後，**chrome URL 天然在錨定輸入內**，sidecar 職能被完整吸收、屬冗餘管線。

**修法**（防半殘管線、同案同刀）：
- **生產端**（`fitz_processor.py`）：刪 `_URL_RE` 常數、`parse` 之 sidecar JSON 寫檔塊、`_assemble` 之 URL 捕捉與 `chrome_urls` 收集；`_assemble` 回傳簽名 `Tuple[List[str], set]` → `List[str]`；連帶清除 now-unused `import json`。
- **消費端**（`litedoc_pipeline.py`）：刪 `_load_source_hints` 全函式、P1 之 `hints=self._load_source_hints(...)` 接線；`_extract_litedoc_metadata` 恢復單參數。
- **測試**：移除 sidecar 產出/加載/截斷窗注入測試，改立退場斷言（`_URL_RE`/`_load_source_hints` 移除、單參簽名、publisher 經錨定輸入仍可解）。

### U6 — echo 守衛（相似度長度比、防禦性一行）

**真因**：`section_engine._title_echo_match` 之子字串分支 `sa in sb or sb in sa` 無長度守衛——「大谷翔平」(4 字) ⊂ lede 導語 (88 字) 被判回聲、整行剝除（NHK 診斷實證）。

**修法**：子字串分支加 `min(len(sa),len(sb)) / max(len(sa),len(sb)) >= 0.5` 長度比守衛——短標題 ⊂ 長 lede（ratio 0.045）不再誤中；真回聲（整行 ≈ 標題、長度相近）照剝。`sa == sb` 短路保雙空零除安全。U2 落地後屬雙保險、成本一行。

## §5 測試與 Grep 結果

### pytest（C2 三測試檔 + 全套件）

```
$ venv/bin/python -m pytest tests/test_fitz_processor.py tests/test_litedoc_pipeline.py tests/test_section_engine.py -q
...............................................................................  [100%]
231 passed in 1.24s
```

```
$ venv/bin/python -m pytest tests/ -q
...
1010 passed, 3 skipped, 3 warnings in 65.14s (0:01:05)
```

- 基線 C1 999 → **1010 passed**（移除 6 K2 sidecar 測試 + 新增 17 C2 測試 = 淨 +11、零新 fail、零回歸）。

**新增/改寫 C2 測試涵蓋**：
- `TestU3SidecarRetired`（fitz）：sidecar 即使有 chrome URL 亦不產出 / `_URL_RE` 已移除。
- `TestC2AnchorText`（litedoc）：裸抽含 chrome URL / MAX_PAGES 截頁 / 壞檔 fail-open 回 ""。
- `TestC2ReinjectTitle`（litedoc）：heading 已在不動 / 正文 promote 不重複 / 缺席 inject 頂部 / 空 title 跳過 / 正規化去空白 casefold。
- `TestC2SidecarRetired`（litedoc）：`_load_source_hints` 移除 / 單參簽名 / publisher 經錨定 chrome URL 可解。
- U6（section_engine）：短標題非回聲 / lede 不誤剝 / 真回聲照剝。
- **§7.2 整合** `test_seam_c2_anchor_reinject_key_changing_integration`：實體 PDF（描邊 ×2 標題/QA·11pt 同正文使幾何層漏判·全頁 chrome URL）→ 真 `FitzProcessor`（C1 U4 去重/U5 chrome 剝除、key-changing PDF→md）→ 真 `MarkdownCleaner` → 錨定裸讀（含 URL）→ U2 回注 promote —— 斷言標題經回注存活入 `# ` heading、14 組 QA 完整成對、chrome URL 已剪未重播。

### SOP §5 一致性核查（修改檔）

**§5.1 logging**：

```
$ grep -nE "traceback\.format_exc|logger\.error|logger\.exception" processor/fitz_processor.py pipelines/litedoc_pipeline.py pipelines/section_engine.py settings.py
processor/fitz_processor.py:168:            self.logger.error(
```

- L168 為既有 `parse` 例外處理，已含 `exc_info=True`（C1 未動、SOP-COMPLY 已清）；C2 新增之 `_read_anchor_text` 例外走 `logger.warning(exc_info=True)`、`_reinject_title` 之 warning 屬觀測性非例外脈絡；**零新增 error/exception**。合規。

**§5.2 database（裸 commit）**：

```
$ grep -nE "\.commit\(\)" <四檔>
無 .commit() 命中（合規）
```

- 本次改動不涉資料庫。合規。

### U3 退場零殘留 grep

```
$ grep -rnE "_load_source_hints|source_hints" pipelines/ processor/ --include="*.py"
✅ 生產碼零殘留
```

## §6 不可動清單遵守

- [x] cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` 六欄 schema 與 Rules — **零改**（U1 只換輸入來源）。
- [x] `processor/md_cleaner.py` 浮水印規則本體／`WATERMARK_HEADING_THRESHOLD` — **零改**。
- [x] HOTFIX-3 **K3**（`_strip_meta_source_lines` 行級歸零、含 echo-strip/R8 前時序）— **零改**（`TestK3MetaSourceLineStripping` 全綠）。
- [x] `pipelines/image_filter.py`／`ingestion_engine.py`／`processor/rag_indexer.py`／`contracts.py` — **零改**。
- [x] `pipelines/section_engine.py` 除 U6 一行守衛外全部（`strip_title_echo` 主體/`classify_source_lang`）— **零改**。
- [x] `PDFParser` ABC 簽名／`pdf_processor.py`／`pipeline_core.py`／A 軌全鏈／resume／slides／book — **零改**。
- [x] `LITEDOC_FITZ_ENABLED` 等既有旗標語意（新常數純加法）— **維持**。

## §7 銜接

- **baton 狀態**：本執行報告 `2026-07-23_FITZ-ANCHOR_C2_執行.md`、C1 報告、plan、tasks 均留 `baton/`（未 mv / 未 git add），待 C_CHECKOUT 一次性歸檔。
- **消化 baton 檔 → commit 映射**（待 Checkout §7 銜接回填實際 hash）：
  - `2026-07-23_FITZ-ANCHOR_C2_執行.md` → C2（hash 待 baron 回填）。
- **下一步**：等 baron 確認後另行下達 **C_CHECKOUT 收官歸檔**（Conformance 驗收 U1-U6 對照 C1/C2 報告 + §7.2 整合測試存在且通過必驗 + baton 3-Phase 自檢 + 一次性 mv + 白名單 git add + staged-set 自檢 + checkout 執行報告 + TODO 雙層結案 + hash 自癒）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出、6 個 .bak）

# 2. git add 清單（僅本次 C2 實質改動代碼與對應備份；baton/ 目錄下報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add .env.example
git add pipelines/litedoc_pipeline.py
git add processor/fitz_processor.py
git add pipelines/section_engine.py
git add tests/test_litedoc_pipeline.py
git add tests/test_fitz_processor.py
git add tests/test_section_engine.py
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_section_engine.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_section_engine.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-ANCHOR_C2_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-ANCHOR_C2_msg.txt
```
