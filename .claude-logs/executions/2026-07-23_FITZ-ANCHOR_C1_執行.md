# FITZ-ANCHOR C1 執行報告 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-ANCHOR C1 |
| **工作流類別** | BE-Refactor |
| **狀態** | Completed (Commit C1)（Git hash 待 baron 回填） |
| **基準 Commit** | `5b5f160`（FITZ-HOTFIX-3 checkout） |
| **依據 plan** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`（v2） |
| **依據 tasks** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`（§8 C1） |
| **執行日期** | 2026-07-23 |

---

## §1 基準與完成狀態

- 於基準 `5b5f160`（FITZ-HOTFIX-3 checkout）之上實作 C1「Fitz Geometry Refinement」。
- 程式改動已完成、測試全綠；**尚未 commit**（依 CLAUDE.md §1.3，實體 `git commit`/`push` 由 baron 手動執行）。
- baton 暫存文件（本執行報告、plan、tasks）**留在 `baton/`、未 `mv`、未 `git add`**（待 Checkout 一次性歸檔）。

## §2 Commit 表格

| Commit 代號 | Subject | 落地 Hash |
|---|---|---|
| C1 | BE-Refactor: FITZ-ANCHOR C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重） | 待 baron 回填 |

## §3 變動檔案清單

**實質改動代碼（4 檔）**：

| 檔案 | 變動 |
|---|---|
| `settings.py` | 新增 `FITZ_DEDUP_EPSILON = float(os.getenv("FITZ_DEDUP_EPSILON", "3.0"))` 常數（`[FITZ-ANCHOR C1]` 標記塊） |
| `.env.example` | 新增 `# FITZ_DEDUP_EPSILON=3.0` 註解說明（±0.84pt 描邊副本容差） |
| `processor/fitz_processor.py` | ① 檔頂 `import math`；② `_collect_page` U4 ε 容差同位去重（廢 HOTFIX-3 K1 精確 `dedup_key`）；③ `_repeated_band_keys` U5 比例門檻 |
| `tests/test_fitz_processor.py` | 新增 3 測試類（`TestOverlapDedupEpsilon` / `TestBandRatioThreshold` / `TestSimulationFixtureNhk`）共 6 測試 |

**備份（2 `.bak`，已置於 `.claude-logs/archive/`）**：

- `.claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_fitz_processor.py.bak`
- `.claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_test_fitz_processor.py.bak`

**diff stat**：

```
 .env.example                 |   3 +
 processor/fitz_processor.py  |  40 ++++++++----
 settings.py                  |   7 ++
 tests/test_fitz_processor.py | 152 +++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 188 insertions(+), 14 deletions(-)
```

> ⚠️ 暫存於 `baton/` 之本執行報告與 plan/tasks **不列入 git add 清單**（見 §8）。

## §4 說明

### U4 — ε 容差同位去重（坐標聚類實現）

**真因**：瀏覽器列印 PDF 的 text-stroke／shadow 描邊效果，會將同一行文字在**近乎**同座標重繪多份（NHK 標題實測 ×4，彼此偏移 ±0.84pt 亞像素）。HOTFIX-3 K1 以**精確座標** `dedup_key=(text, round(y0,1), round(x0,1), round(size,1))` 比對——`round(…,1)` 對 0.84pt 偏移仍落不同 bucket、**漏抓亞像素副本**，致 4 份標題全數流入下游、觸發 `md_cleaner` 浮水印規則（同 heading ≥3 全殺）誤殺真標題。

**修法**（`_collect_page`，每頁獨立初始化）：

- 廢精確 `dedup_key`／`seen_lines: set`，改**容差群組** `seen_groups: Dict[Tuple[str, float], List[Tuple[float, float]]]`。
- 群組 key＝`(text, round(size, 1))`；值＝群內**已保留**之 `(x0, y0)` 座標清單。
- 對每行：取所屬群組已保留座標，逐一比 `abs(dx) <= eps and abs(dy) <= eps`（`eps = settings.FITZ_DEDUP_EPSILON`，**函式內 `import settings` 讀取**避免模組級耦合，沿用 `metadata_extractor` 既有 in-function import 範式）——命中即判描邊副本、`continue`（debug log 沿用 K1「同位重繪去重」訊息格式）；未命中則 append 座標並收行。
- **合法重複**（同文同字級但座標差 > ε）→ 不命中、全保留；**每頁獨立**故不干涉跨頁 chrome（歸 R2 管轄）。

### U5 — 跨頁 chrome 剝除改比例門檻

**真因**：`_repeated_band_keys` 原以**固定 `len(hit) >= 2`** 判定「出現於 ≥2 頁的頂/底 band 行＝列印頁首尾 chrome」。此門檻對長文件過鬆——某內容段落行偶然落入 band 且僅在少數頁（如 10 頁只在 2 頁）重複，即被誤判 chrome 剝除。

**修法**（`_repeated_band_keys`）：

- 檔頂新增 `import math`。
- 回傳判定由固定 `>= 2` 改為 `need = max(2, math.ceil(len(pages) * 0.5))` 之 `len(hit) >= need`。
- 真 chrome 幾乎每頁重印（遠超半數）照剝；少數頁偶然重複之 band 內容行（比例 < 50%）獲救。
- **下限 2** → 2-3 頁極短 PDF（`ceil(2*0.5)=1`、`ceil(3*0.5)=2`）門檻仍為 2，與舊行為**完全等價回歸**。

## §5 測試與 Grep 結果

### pytest（fitz 單元 + 全套件）

```
$ venv/bin/python -m pytest tests/test_fitz_processor.py -q
........................................                                 [100%]
40 passed in 0.29s
```

```
$ venv/bin/python -m pytest tests/ -q
...
999 passed, 3 skipped, 3 warnings in 67.15s (0:01:07)
```

- 基線 993 → **999 passed**（+6 新測試、零新 fail、零回歸）。

**新增 6 測試涵蓋**：
- `TestOverlapDedupEpsilon`：`test_subpixel_stroke_redraw_deduped`（±0.84pt ×4 → 恰一份）／`test_beyond_epsilon_kept`（> ε 兩份保留）／`test_dedup_is_per_page_not_cross_page`（每頁獨立）。
- `TestBandRatioThreshold`：`test_ten_page_chrome_stripped_minority_kept`（10/10 chrome 剝除、2/10 內容保留）／`test_two_page_regression_equivalent`（2 頁 need=2 等價回歸）。
- `TestSimulationFixtureNhk`（§3.1 模擬表轉正式）：`test_stroke_title_and_qa_survive_real_cleaner`（描邊 ×4 標題經 U4 去重×1 + 真 `MarkdownCleaner().clean` 標題存活、14 組 QA 完整成對、`移除浮水印…(N 次)` 告警零觸發）。

### SOP §5 一致性核查（修改檔 `processor/fitz_processor.py` / `settings.py`）

**§5.1 logging**：

```
$ grep -nE "traceback\.format_exc|logger\.error|logger\.exception" processor/fitz_processor.py settings.py
processor/fitz_processor.py:172:            self.logger.error(
```

- L172-174 為既有 `parse` 例外處理，已含 `exc_info=True`（SOP-COMPLY C1 已清）；本次 C1 僅新增 `logger.debug`（U4 去重訊息），**零新增 error/exception**。合規。

**§5.2 database（裸 commit）**：

```
$ grep -nE "\.commit\(\)" processor/fitz_processor.py settings.py
無 .commit() 命中（合規）
```

- 本次改動不涉資料庫。合規。

## §6 不可動清單遵守

- [x] `processor/pdf_processor.py`（MinerU 處理器）— **零改**（git diff 未觸及）。
- [x] `pipelines/section_engine.py` — **零改**。
- [x] `pipelines/litedoc_pipeline.py` — **零改**（U3 sidecar 退場屬 C2，本次不動）。
- [x] `pipelines/ingestion_engine.py` — **零改**。
- [x] `processor/md_cleaner.py`（浮水印規則本體）— **零改**（U4 治本在上游去重、不動 cleaner）。
- [x] C1 高度內聚於 fitz 幾何整形：僅動 `settings.py` 常數 + `.env.example` 註解 + `fitz_processor.py` 兩函式 + 測試。

## §7 銜接

- **baton 狀態**：本執行報告 `2026-07-23_FITZ-ANCHOR_C1_執行.md`、plan、tasks 均留 `baton/`（未 mv / 未 git add），待 C_CHECKOUT 一次性歸檔。
- **消化 baton 檔 → commit 映射**（待 Checkout §7 銜接回填實際 hash）：
  - `2026-07-23_FITZ-ANCHOR_C1_執行.md` → C1（hash 待 baron 回填）。
- **下一步**：等 baron 確認後另行下達 **C2 — Meta Anchor & Title Reinjection**（U1 前 2 頁裸文字錨定〔零新增呼叫〕/ U2 標題回注 promote-else-inject / U3 HOTFIX-3 K2 sidecar 同刀退場 / U6 echo 長度比守衛）提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅本次 C1 實質改動代碼與對應備份；baton/ 目錄下報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add .env.example
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_test_fitz_processor.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-ANCHOR_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/FITZ-ANCHOR_C1_msg.txt
```
