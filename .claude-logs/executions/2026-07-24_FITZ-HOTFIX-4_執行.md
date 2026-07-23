# FITZ-HOTFIX-4 執行報告 — Inline HTML Neutralization & Header-Srcs Basis Fix（裸 HTML 中和與報頭集行號基準修正）

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-HOTFIX-4 |
| **工作流類別** | BE-Hotfix |
| **狀態** | Completed (Commit HOTFIX-4)（Git hash 待 baron 回填） |
| **基準 Commit** | `505ce1e`（FITZ-ANCHOR checkout） |
| **依據 hotfix** | `.claude-logs/baton/2026-07-23_FITZ-HOTFIX-4_裸HTML中和與報頭集基準修正_hotfix.md`（v3） |
| **執行日期** | 2026-07-24 |

---

## §1 基準與完成狀態

- 於基準 `505ce1e`（FITZ-ANCHOR checkout）之上實作 HOTFIX-4，治 FITZ-ANCHOR 落地後兩樣本 E2E 缺陷：Medium 技術文 95% 內容前端蒸發（K1）＋ NHK 樣本 en/zh 側首圖誤殺（K2）。
- 程式改動已完成、測試全綠；**尚未 commit**（依 CLAUDE.md §1.3，實體 `git commit`/`push` 由 baron 手動執行）。
- baton 暫存文件（本執行報告、hotfix 設計書）**留在 `baton/`、未 `mv`、未 `git add`**（待 Checkout 一次性歸檔）。

## §2 Commit 表格

| Commit 代號 | Subject | 落地 Hash |
|---|---|---|
| HOTFIX-4 | BE-Hotfix: FITZ-HOTFIX-4 — Inline HTML Neutralization & Header-Srcs Basis Fix（裸 HTML 中和與報頭集行號基準修正） | 待 baron 回填 |

## §3 變動檔案清單

**實質改動代碼（1 實體檔 + 1 測試檔）**：

| 檔案 | 變動 |
|---|---|
| `pipelines/litedoc_pipeline.py` | **K1** 模組層新增 `_INLINE_TAG_RE` + `_neutralize_inline_html`；P1 ②' 清洗步接線（R7 後、markdown_text 重讀前、DocAnalyzer 判型前）。**K2** `run_phase3` 於 K3 刪行前預算 `_pristine_header_srcs` 並傳 `_filter_source_figures`；`_filter_source_figures` 簽名加 `header_srcs: Optional[set] = None`（None 退回自算兜底） |
| `tests/test_litedoc_pipeline.py` | 新增 `TestHOTFIX4_K1_InlineHtmlNeutralize`(6) + `TestHOTFIX4_K2_HeaderSrcsBasis`(3) + `TestHOTFIX4_K2_BilingualSymmetryE2E`(2)；K3 order 測試 spy 對齊 `_filter_source_figures` 新簽名 |

**備份（2 `.bak`，已置於 `.claude-logs/archive/`）**：

- `.claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_litedoc_pipeline.py.bak`
- `.claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_test_litedoc_pipeline.py.bak`

**diff stat**：

```
 pipelines/litedoc_pipeline.py  |  62 ++++++++++++++-
 tests/test_litedoc_pipeline.py | 176 ++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 234 insertions(+), 4 deletions(-)
```

> ⚠️ 暫存於 `baton/` 之本執行報告與 hotfix 設計書 **不列入 git add 清單**（見 §8）。

## §4 說明

### K1 — 裸 HTML 中和（防 DOMPurify 吞文）

**真因**：Medium「How modern browsers work」正文滿佈字面 `<script>`／`<link>`／`<img>`（原文排為 inline code）；fitz 文字層抽取使 code 樣式蒸發、僅剩裸角括號。前端渲染時 `marked` 把裸 `<script>` 解析為真 script 元素（無閉合 → 其後全部內容當 script 內文），DOMPurify（SEC-XSS、行為正確）移除整個 script 連同內文 → 31,000 字蒸發。**屬輸入面契約缺失**——PDF 抽出的角括號標籤未宣告為字面文字。

**修法**（baron 設計定調：「PDF 專案、HTML 標籤＝一般文字」）：

- 模組層 `_INLINE_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>`\n]*?)?/?>")`——`<` 緊跟字母才成標籤族（`a < b`／`3 < 5 > 2` 不中；屬性段禁含 `<>`、反引號、換行防跨行貪婪）。
- `_neutralize_inline_html`：逐行以 `` ` `` 切段、僅對**偶數段**（code span 之外）做 `_INLINE_TAG_RE.sub(lambda m: f"`{m.group(0)}`", …)`——**反引號守衛**使已在 code span 內者不重包。
- 包反引號＝還原源文 inline-code 樣貌：讀者可見、marked 渲染 `<code>`、DOMPurify 零觸發、翻譯 LLM 獲「這是代碼」信號。**行數不變式**（sidecar 行號零擾動）。
- 接線於 P1 ②' 清洗鏈（連字/R7 同段、③ DocAnalyzer 之前）；無旗標（設計定調之確定性行為、回退＝git revert）；扉頁豁免天然成立（`paper-header-meta` div 為 P3 下游注入、P1 本步不可見）。

### K2 — R8 報頭集「原封行序」基準（行號位移陷阱關閉）

**真因**：`_filter_source_figures`（R8、`full_text` 通道）內呼 `_load_header_srcs` 以 **sidecar 原封行號**（hdr_end）掃**當下傳入的 text**；但 R8 執行時 text 已經過 **K3 刪行**（剝 meta 行）——NHK v3：K3 刪 title 堆疊+date → **界外圖（第 8 行）上移進 `[:hdr_end+1]` 掃描窗** → 被誤收為報頭圖 → 規則③ DROP。tiles 通道掃原封 md（圖界外）→ 保留，兩通道基準不一致。**現象 C**：NHK en 4,424 字 <15k → whole mode，zh/en 共用同一 full_text 素材 → R8 位移一刀殺雙語。**行號基準位移家族第五例**（HOTFIX-3 堵了 K3 自己的輸入端、漏了 R8 的邊界端）。

**修法**：報頭集必須在**原封 md 行序**上計算——

- `run_phase3` 於 `_read_source_text` 剛讀、**K3 之前**呼 `_pristine_header_srcs = self._load_header_srcs(ctx, _p3_output_dir, full_text)`（原封 full_text）。
- `_filter_source_figures` 簽名純加法 `header_srcs: Optional[set] = None`：傳入時直接用（原封基準單一源），`None` 時退回自算（既有語意、相容兜底）。
- `run_phase3` 呼叫改 `_filter_source_figures(ctx, full_text, _pristine_header_srcs)`——與 tiles 路同基準、單次計算雙通道共用；whole mode 下 zh/en 共用 full_text → 一併修 zh 側同圖失蹤（現象 C）。
- `_load_header_srcs`／`_collect_header_srcs` 本體零改——修的是**餵給它的 text 基準**。

## §5 測試與 Grep 結果

### pytest（HOTFIX-4 + 全套件）

```
$ venv/bin/python -m pytest tests/test_litedoc_pipeline.py -q -k "HOTFIX4"
...........                                                              [100%]
11 passed, 151 deselected in 0.63s
```

```
$ venv/bin/python -m pytest tests/ -q
...
1021 passed, 3 skipped, 3 warnings in 54.69s
```

- 基線 1010 → **1021 passed**（+11 新測試、零新 fail、零回歸）。

**新增 11 測試涵蓋**：
- `TestHOTFIX4_K1_InlineHtmlNeutralize`（6）：標籤族包裹 / code span 內不重包 / `a < b` 不等式不誤判 / **行數不變式** / 中文正文零擾動 / **Browsers 實物段落**經 K1 後段外零裸標籤（marked→code span、DOMPurify 不吞）→ 後文字面存活。
- `TestHOTFIX4_K2_HeaderSrcsBasis`（3）：舊路（None → 位移 text 自算）誤 DROP / 新路（原封基準傳入）KEEP / `header_srcs=None` 相容兜底＝既有語意。
- `TestHOTFIX4_K2_BilingualSymmetryE2E`（2）：run_phase3 於 K3 刪行後 whole mode（zh/en 共用 full_text）界外圖雙側同步 KEEP + 對稱 / section mode（en 走原文過濾、zh 走 tiles）圖集對稱。

### SOP §5 一致性核查（修改檔 `pipelines/litedoc_pipeline.py`）

**§5.1 logging**：

```
$ grep -nE "traceback\.format_exc|logger\.error|logger\.exception" pipelines/litedoc_pipeline.py
無命中（合規）
```

- K1/K2 新增碼未引入 error/exception 日誌（既有 `_filter_source_figures` fail-open 為 `logger.warning(exc_info=True)`、未動）。合規。

**§5.2 database（裸 commit）**：

```
$ grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py
無 .commit() 命中（合規）
```

- 本次改動不涉資料庫。合規。

## §6 不可動清單遵守

- [x] `pipelines/image_filter.py` 三規則本體／門檻／`_collect_header_srcs`（tiles 路基準本就原封）— **零改**。
- [x] HOTFIX-3 K3（`_strip_meta_source_lines`）本體與時序 / FITZ-ANCHOR U1-U6 全部語意 — **零改**。
- [x] `processor/fitz_processor.py`／`md_cleaner`／`section_engine`／`ingestion_engine`／`rag_indexer` — **零改**（`git status` 確認）。
- [x] 前端 `static/`（DOMPurify／marked）— **零改**（K1 屬供給端治本、消毒層行為正確不動）。
- [x] A 軌全鏈／resume／slides；既有旗標語意；DB schema／API 簽名 — **零改**。
- [x] 本案高度內聚於 `pipelines/litedoc_pipeline.py` 單檔 + 測試（K1 中和 + K2 接線）。

## §7 銜接

- **baton 狀態**：本執行報告 `2026-07-24_FITZ-HOTFIX-4_執行.md`、hotfix 設計書均留 `baton/`（未 mv / 未 git add），待 checkout 一次性歸檔。
- **消化 baton 檔 → commit 映射**（待 Checkout §7 銜接回填實際 hash）：
  - `2026-07-24_FITZ-HOTFIX-4_執行.md` → HOTFIX-4（hash 待 baron 回填）。
- **下一步**：等 baron 確認後另行下達 **checkout 收官歸檔**（Conformance 驗收 K1/K2 對照 hotfix + baton 一次性 mv〔hotfix→hotfixes/、執行報告→executions/〕 + 白名單 git add + staged-set 自檢 + checkout 執行報告 + TODO 雙層結案 + hash 自癒）。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出、2 個 .bak）

# 2. git add 清單（僅本次 HOTFIX-4 實質改動代碼與對應備份；baton/ 目錄下報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-24_FITZ-HOTFIX-4_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-4_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-4_msg.txt
```
