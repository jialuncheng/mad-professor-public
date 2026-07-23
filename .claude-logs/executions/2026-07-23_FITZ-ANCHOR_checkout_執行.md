# FITZ-ANCHOR Checkout 執行報告 — 成果收官歸檔

## 📊 元數據塊

| 欄位 | 值 |
|---|---|
| **任務代號** | FITZ-ANCHOR Checkout |
| **工作流類別** | BE-Refactor（收官階段） |
| **狀態** | Completed (Checkout)（Git hash 待 baron 回填） |
| **C1 hash** | `b48961a` |
| **C2 hash** | `38cb68e` |
| **執行日期** | 2026-07-23 |

---

## §1 Conformance 驗收結果（五維度 + 規格逐項）

| 維度 | 規格/要求 | 結果 | 證據 |
|---|---|---|---|
| **U1** meta 錨定前移 | `_read_anchor_text` 前 N 頁裸抽送 cover-prompt·空 fallback·`_extract_litedoc_metadata` 單參 | 🟢 | litedoc L484·`TestC2AnchorText`(3)·截頁/URL/fail-open |
| **U2** 標題回注 | promote-else-inject·analyze 前·空跳過 | 🟢 | `_reinject_title`·`TestC2ReinjectTitle`(5) 三分支+空+正規化 |
| **U3** hints 雙端退場 | fitz `_URL_RE`+寫檔塊、litedoc `_load_source_hints`+hints 全清 | 🟢 | 生產碼 grep 零殘留·`TestU3/C2SidecarRetired`(5) |
| **U4** ε 容差同位去重 | `(text,round(size,1))` 群 `|dx|,|dy|≤ε` | 🟢 | C1·`TestOverlapDedupEpsilon`(3) |
| **U5** 比例重複門檻 | `need=max(2,ceil(len(pages)*0.5))` | 🟢 | C1·`TestBandRatioThreshold`(2) |
| **U6** echo 相似度守衛 | 子字串分支 `min/max>=0.5` | 🟢 | section_engine L622·U6(3) |
| **§7.2 整合測試** | 存在且通過（key-changing PDF→md） | 🟢 | `test_seam_c2_anchor_reinject_key_changing_integration` 實體 PDF 端到端 |
| **測試全綠** | 基線 993+ 零新 fail | 🟢 | **1010 passed, 3 skipped** |
| **不可動清單** | md_cleaner/image_filter/ingestion_engine/rag_indexer/pdf_processor/contracts/pipeline_core | 🟢 | `5b5f160..HEAD` diff 空 |
| **SOP §5** | logging exc_info / 無裸 commit | 🟢 | L168 既有 exc_info·無 `.commit()` |
| **提示詞歸檔** | tasks/C1/C2/Check | 🟢 | 實 5 份（含 plan 階段診斷書）全入版控 |

**驗收結論**：全數 🟢 合規，准予收官。

**§7.2 說明**：FITZ-ANCHOR 屬 litedoc P1 **單一 Phase 內**之錨定→回注→tiles 鏈（非 producer/consumer 跨 Phase 資料 handoff），依 WORKFLOW_SOP §7.2 得申請純後端無跨 Phase handoff 豁免；惟本案仍實作 key-changing 整合測試（實體 PDF → 真 FitzProcessor 幾何 → 錨定裸讀 → U2 回注）**超額達標**。

## §2 提示詞歸檔稽核

```
$ ls .claude-logs/prompts/ | grep "FITZ-ANCHOR"
2026-07-23_FITZ-ANCHOR_C1_run_提示詞.md
2026-07-23_FITZ-ANCHOR_C2_run_提示詞.md
2026-07-23_FITZ-ANCHOR_Check_提示詞.md
2026-07-23_FITZ-ANCHOR_tasks_提示詞.md
2026-07-23_FITZ-ANCHOR_診斷與plan_提示詞.md
```

- 實 **5** 份（提示詞 §稽核要求 4 份 tasks/C1/C2/Check + 額外 plan 階段 `診斷與plan`）全部就位。

## §3 baton 歸檔確認

**mv 搬移（Phase 3 一次性、標準 `mv` 非 `git mv`）**：

| 來源（baton/） | 目的地 |
|---|---|
| `..._plan.md` | `.claude-logs/plans/` |
| `..._tasks.md` | `.claude-logs/tasks/` |
| `..._C1_執行.md` | `.claude-logs/executions/` |
| `..._C2_執行.md` | `.claude-logs/executions/` |

```
$ ls .claude-logs/baton/ | grep FITZ-ANCHOR
（無輸出——本案任務檔已全數歸檔、baton 僅餘長駐 spec 與影子 PDF）
```

## §4 對 baron §8 清單之更正（留痕）

Checkout 白名單依實際 git 狀態校正如下（CHECKOUT-GUARD 白名單鐵律：declared == staged）：

1. **檔名更正**：baron §8 之 `幾幾整形` → 實際檔名 `幾何整形`。
2. **路徑更正**：baron §8 之裸 `TODO.md`／`archive/TODO_done_archive.md` → 實為 `.claude-logs/TODO.md`／`.claude-logs/archive/TODO_done_archive.md`。
3. **補列漏檔**：baron §8 漏列 plan 階段 `2026-07-23_FITZ-ANCHOR_診斷與plan_提示詞.md`（本任務未追蹤 prompt、應一併入版控）→ 補入白名單（共 5 提示詞）。
4. **剔除 8 `.bak`**：8 個 `.bak` 已於 **C1(`b48961a`)/C2(`38cb68e`) commit 落地**（`git ls-files` 確認 tracked 且 clean）→ checkout 不再重複 `git add`（否則產生無 staged 條目之空宣告、破壞 declared==staged）；審計存檔已在版控中。
5. **剔除代碼檔**：`settings.py`/`.env.example`/`fitz_processor.py`/`litedoc_pipeline.py`/`section_engine.py`/測試檔 均已於 C1/C2 落地 → 不在 checkout 集。
6. **剔除跨任務髒檔**：`SEC-HARDEN`/`SOP-COMPLY`/`PROJECT-REVIEW` 三提示詞屬他任務未追蹤/修改檔 → 逐檔顯式 add、嚴禁 `git add .claude-logs/prompts/` 掃入。

## §5 staged-set 自檢（`git diff --cached --name-only` 實貼）

（見下方終端輸出——須完全等於 §7 宣告之 13 檔白名單，多一檔／少一檔即停。）

## §6 不可動清單遵守

- [x] `5b5f160..HEAD` 對 md_cleaner/image_filter/ingestion_engine/rag_indexer/pdf_processor/contracts/pipeline_core/context 之 diff 為**空**。
- [x] 收官階段純文件搬移 + TODO/archive/INDEX 治理更新，零業務代碼改動。

## §7 銜接（baton 消化 → commit 映射）

| 歸檔檔 | 對應 commit |
|---|---|
| `plans/..._plan.md` | checkout（待 baron 回填） |
| `tasks/..._tasks.md` | checkout |
| `executions/..._C1_執行.md` | checkout（內容對應 C1 `b48961a`） |
| `executions/..._C2_執行.md` | checkout（內容對應 C2 `38cb68e`） |
| `executions/..._checkout_執行.md` | checkout |

**checkout 宣告白名單（13 檔）**：

```
.claude-logs/plans/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md
.claude-logs/tasks/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md
.claude-logs/executions/2026-07-23_FITZ-ANCHOR_C1_執行.md
.claude-logs/executions/2026-07-23_FITZ-ANCHOR_C2_執行.md
.claude-logs/executions/2026-07-23_FITZ-ANCHOR_checkout_執行.md
.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_tasks_提示詞.md
.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C1_run_提示詞.md
.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C2_run_提示詞.md
.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_Check_提示詞.md
.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_診斷與plan_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
```

## §8 baron 執行命令

```bash
# 1. baton 搬移已完成（報告 §3 已列出）；8 .bak 與代碼已於 C1/C2 落地、checkout 不重複 add

# 2. git add 歸檔清單（13 檔·⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`）
git add .claude-logs/plans/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md
git add .claude-logs/tasks/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md
git add .claude-logs/executions/2026-07-23_FITZ-ANCHOR_C1_執行.md
git add .claude-logs/executions/2026-07-23_FITZ-ANCHOR_C2_執行.md
git add .claude-logs/executions/2026-07-23_FITZ-ANCHOR_checkout_執行.md
git add .claude-logs/prompts/2026-07-23_FITZ-ANCHOR_tasks_提示詞.md
git add .claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C1_run_提示詞.md
git add .claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C2_run_提示詞.md
git add .claude-logs/prompts/2026-07-23_FITZ-ANCHOR_Check_提示詞.md
git add .claude-logs/prompts/2026-07-23_FITZ-ANCHOR_診斷與plan_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/archive/TODO_done_archive.md

# 3. commit message 草稿（已寫入 /tmp/FITZ-ANCHOR_checkout_msg.txt）

# 4. baron 手動執行（先核 git diff --cached --name-only == 13 檔白名單）
git commit -F /tmp/FITZ-ANCHOR_checkout_msg.txt
```
