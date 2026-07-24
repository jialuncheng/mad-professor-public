# FITZ-HOTFIX-5 執行報告 — Post-Translation Inline HTML Re-Neutralization（譯後裸 HTML 標籤出口補中和）

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-HOTFIX-5 |
| **工作流類別** | BE-Hotfix |
| **狀態** | Completed (Commit HOTFIX-5)（Git hash 待 baron 回填） |
| **基準 Commit** | `b783824`（FITZ-HOTFIX-4 checkout） |
| **依據 hotfix** | `.claude-logs/baton/2026-07-24_FITZ-HOTFIX-5_譯後裸HTML出口補中和_hotfix.md`（v2） |
| **執行日期** | 2026-07-24 |

---

## §1 基準與完成狀態

- 於基準 `b783824`（FITZ-HOTFIX-4 checkout）之上實作 HOTFIX-5，治 HOTFIX-4 K1 之殘留缺陷：重啟 pipeline（新 code）後 Browsers 仍 46 頁塌 3 頁。
- 程式改動已完成、測試全綠；**尚未 commit**（依 CLAUDE.md §1.3，實體 `git commit`/`push` 由 baron 手動執行）。
- baton 暫存文件（本執行報告、hotfix 設計書）**留在 `baton/`、未 `mv`、未 `git add`**（待 checkout 一次性歸檔）。

## §2 Commit 表格

| Commit 代號 | Subject | 落地 Hash |
|---|---|---|
| HOTFIX-5 | BE-Hotfix: FITZ-HOTFIX-5 — Post-Translation Inline HTML Re-Neutralization（譯後裸 HTML 標籤出口補中和） | 待 baron 回填 |

## §3 變動檔案清單

**實質改動代碼（1 實體檔 + 1 測試檔）**：

| 檔案 | 變動 |
|---|---|
| `pipelines/litedoc_pipeline.py` | `run_phase3` 尾段（`raw_metadata` handoff 後、扉頁 `_render_meta_headers` prepend 前）新增 2 行：`zh_text = _neutralize_inline_html(zh_text)` / `en_text = _neutralize_inline_html(en_text)`（`[FITZ-HOTFIX-5]` 標記塊，+10 行含註解） |
| `tests/test_litedoc_pipeline.py` | 新增 `TestHOTFIX5_PostTranslateNeutralize`（4 測試）+ `_bare_tags` 輔助 |

**備份（2 `.bak`，已置於 `.claude-logs/archive/`）**：

- `.claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_litedoc_pipeline.py.bak`
- `.claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_test_litedoc_pipeline.py.bak`

**diff stat**：

```
 pipelines/litedoc_pipeline.py  | 10 ++++++
 tests/test_litedoc_pipeline.py | 79 ++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 89 insertions(+)
```

> ⚠️ 暫存於 `baton/` 之本執行報告與 hotfix 設計書 **不列入 git add 清單**（見 §8）。

## §4 說明

### 設計考量：為何補做在 P3 出口、如何防 LLM 譯後反引號丟失

**真因（承 hotfix 設計書）**：HOTFIX-4 K1（`_neutralize_inline_html`）在 **P1 ②' 清洗步**把中繼 md 之裸 HTML 標籤 27→0 全包反引號。但 P3 **section 模式**走 `restore_sections_markdown` **逐 tile 呼叫翻譯 LLM**——LLM 翻譯含 `` `<script>` `` 之段落時**不保證保留反引號**（實證 `final_shadow_zh.md` L57「Java`<script>`」為 LLM 拆掉反引號硬接之痕跡），tiling 亦可能把一對 `` ` `` 拆到兩個 tile → **裸標籤在譯後成品復活**。前端 marked 撞 body 首個裸 `<script>` → DOMPurify 連內文移除 → 其後全部蒸發。

**修法**：K1-at-P1 為**必要但不充分**（給 LLM「這是代碼」信號、但無法保證 LLM 譯後輸出仍守反引號）。於 P3 **body 定案後、扉頁注入前**補一道**冪等**中和作**確定性層結構性保證**——不依賴 LLM 是否配合：

- 接線於 `run_phase3` 尾段：`zh_text`/`en_text` 經 `restore_sections_markdown`（section）/`translate_whole`（whole）/`full_text`（is_zh）產出、echo-strip 後 → 各補跑一次 `_neutralize_inline_html`。
- **冪等**（反引號守衛→只包新復活之裸標籤、已包的不動）+ **行數不變**（sidecar 行號/下游零擾動）= 零副作用；覆蓋 whole/section/is_zh 三模式 × zh/en 雙側。
- **扉頁豁免（關鍵時序）**：`paper-header-meta` div（全庫唯一合法 raw HTML）於 body 中和**之後**才由 `_render_meta_headers` prepend（`header_zh + zh_text`）→ 扉頁 div 天然不被反引號包裹。
- K1（P1 源頭給信號）+ HOTFIX-5（P3 出口保證乾淨）成**雙保險**；`_neutralize_inline_html`/`_INLINE_TAG_RE` 本體零改（僅新增 2 行呼叫）。

**修法定位**：改的是 **B 軌 P3（`run_phase3`）尾段之「組裝最終交付 md」步**——非前端、非新階段、非 P1/P2/P4。P3 產出的 `final_zh.md` 即前端閱讀視圖消費之檔；供給端治本、前端 `static/`（marked/DOMPurify 行為正確）零碰。

## §5 測試與 Grep 結果

### pytest（HOTFIX-5 + 全套件）

```
$ venv/bin/python -m pytest tests/test_litedoc_pipeline.py -q -k "HOTFIX5"
....                                                                     [100%]
4 passed, 162 deselected in 0.67s
```

```
$ venv/bin/python -m pytest tests/ -q
...
1025 passed, 3 skipped, 3 warnings in 56.90s
```

- 基線 1021 → **1025 passed**（+4 新測試、零新 fail、零回歸）。

**新增 4 測試涵蓋**：
- `test_section_mode_revived_bare_tags_neutralized`：section 模式 `restore_sections_markdown` 回傳含裸 `<script>`/`<p>`/`<link>` 之 zh body → 出口中和後 body 危險標籤零裸、`` `<script>` `` 已包、`<script>` 後文字面存活（治吞文）。
- `test_header_meta_div_exempt`：扉頁 `<div class="paper-header-meta">` 原封存在、**未**被反引號包裹（zh/en 雙側）。
- `test_whole_mode_both_sides_neutralized`：whole 模式 zh（translate_whole）與 en（=full_text）雙側 body 皆補中和。
- `test_neutralize_idempotent_and_line_invariant`：冪等（重跑相等）+ 行數不變 + 不誤傷 `a < b` 不等式。

### SOP §5 一致性核查（修改檔 `pipelines/litedoc_pipeline.py`）

**§5.1 logging**：

```
$ grep -nE "traceback\.format_exc|logger\.error|logger\.exception" pipelines/litedoc_pipeline.py
無命中（合規）
```

- 本案新增 2 行純函式呼叫、無日誌。合規。

**§5.2 database（裸 commit）**：

```
$ grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py
無 .commit() 命中（合規）
```

- 本案不涉資料庫。合規。

## §6 不可動清單遵守

- [x] `_neutralize_inline_html`／`_INLINE_TAG_RE` 本體（HOTFIX-4 K1）— **零改**（僅新增 2 行呼叫）。
- [x] HOTFIX-4 K1 P1 ②' 源頭接線 / K2 / HOTFIX-3 K3 / FITZ-ANCHOR U1-U6 / FITZ-HOTFIX-1 C3 R8 — **零改**。
- [x] `render_meta_header_html`／扉頁 `paper-header-meta` 結構（body 中和在前、扉頁 prepend 在後）— **零改**。
- [x] `section_engine`／`ingestion_engine`／`image_filter`／`fitz_processor`／`md_cleaner`／`rag_indexer` — **零改**（`git status` 確認）。
- [x] 前端 `static/`（DOMPurify／marked）／A 軌全鏈／resume／slides／既有旗標／DB schema／API 簽名 — **零改**。
- [x] `ctx.rag_sections`（早於本剝定案、RAG 不受影響）— **未觸碰**。
- [x] 本案高度內聚於 `pipelines/litedoc_pipeline.py` `run_phase3` 尾段（2 行接線）+ 測試。

## §7 銜接

- **baton 狀態**：本執行報告 `2026-07-24_FITZ-HOTFIX-5_執行.md`、hotfix 設計書均留 `baton/`（未 mv / 未 git add），待 checkout 一次性歸檔。
- **消化 baton 檔 → commit 映射**（待 Checkout §7 銜接回填實際 hash）：
  - `2026-07-24_FITZ-HOTFIX-5_執行.md` → HOTFIX-5（hash 待 baron 回填）。
- **下一步**：等 baron 確認後另行下達 **checkout 收官歸檔**（Conformance 驗收 K1 出口中和/扉頁豁免/冪等對照 hotfix + baton 一次性 mv〔hotfix→hotfixes/、執行報告→executions/〕+ 白名單 git add + staged-set 自檢 + checkout 執行報告 + TODO 雙層結案 + hash 自癒）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出、2 個 .bak）

# 2. git add 清單（僅本次 HOTFIX-5 實質改動代碼與對應備份；baton/ 目錄下報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-5_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-5_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-5_msg.txt
```
