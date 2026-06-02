`````markdown
# 2026-06-02 — GOLDEN-BASELINE Tasks 修正 提示詞

> **收到時間**：2026-06-02 02:15（UTC+8）
> **任務代號**：GOLDEN-BASELINE Tasks 修正
> **觸發 commit**：GOLDEN-BASELINE-Tasks-Fix
> **相關產出檔案**：.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md（更新）
> **觸發情境**：baron 審查 tasks.md 時指出 Checkout 時序悖論——將收官歸檔放在 OP-1，導致 OP-2/OP-3 尚未產出的執行報告無從搬移，且違反「執行中產物嚴禁移動、收官才一次性歸檔」鐵律。下達重拆修正指令：Checkout 移至最尾端 OP-3，重編 OP-1=存盤 / OP-2=Diff 腳本 / OP-3=收官歸檔。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-02 02:15 |
| **任務代號** | GOLDEN-BASELINE Tasks 修正 |
| **觸發 Commit** | GOLDEN-BASELINE-Tasks-Fix |
| **相關產出檔案** | .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md (更新) |
| **觸發情境** | baron 指出 Checkout 時序問題，下達任務重拆修正指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**。baron 在審查你產出的 tasks.md 時，指出了一個嚴重的**時序悖論與工作流違規**：
你將 Checkout（收官歸檔）規劃在 `OP-1`，這導致後續 `OP-2` 與 `OP-3` 還沒產出的執行報告根本無從被搬移，且違反了「執行中產物嚴禁移動、收官階段才一次性歸檔」的工作流鐵律。

請你立即**重新閱讀所有依據，並徹底改寫/覆寫**：
`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`
並同步更新 `.claude-logs/TODO.md` 中的任務項目。

### 📖 強制讀檔清單

請在開始改寫前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md         # 進度管控框架
.claude-logs/TODO.md                                           # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md   # 本次拆分的依據 plan
baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v9.md    # 大改版總綱 plan
baron/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md             # 大改版技術 SPEC
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md   # 目前有 Bug 的待修正 tasks 檔
.claude-logs/templates/template_tasks.md                       # tasks 模板
```

### ⚙️ 任務重新拆分與修正硬性約束（必須 100% 遵守）

1. **Checkout 階段強制移至最尾端（最後一個 OP）**：
   * 廢除將 Checkout 放在 `OP-1` 的錯誤規劃。
   * 將 **`OP-3`**（或最後一個 OP 階段）定義為唯一的 **Checkout / 收官階段**。
   * 在 `OP-1` 與 `OP-2` 執行期間，所有的計畫、任務、執行報告一律**暫存留在 `baton/` 中，不移動、不入版控**。
   * 只有在最後的 **`OP-3`（收官階段）**，才執行一次性搬移與 `git add` 追蹤，完成 Traceability：
     * **計畫檔歸檔**：`.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md` ➜ `.claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`（**強制保留 `_v2` 版號**）
     * **任務檔歸檔**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` ➜ `.claude-logs/tasks/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`
     * **所有執行報告歸檔**：將 `OP-1`、`OP-2` 以及 `OP-3` 本身產出的執行報告一次性自 `baton/` 移動至 `.claude-logs/executions/` 目錄。
     * 對上述所有搬移後的正式檔案執行 `git add` 追蹤。

2. **重新編排的 3 大執行階段**：
   * **OP-1**：五路黃金基準物理存盤（建立 Golden Baseline capture）。產出報告為 `baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md`。
   * **OP-2**：自動化 Regression Diff 比對腳本開發（建立質量防線與比對測試）。產出報告為 `baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md`。
   * **OP-3**：Checkout / 收官階段（收官歸檔與最終 Traceability 交接）。產出報告為 `OP-3_執行.md`（並在最後移動歸檔）。

3. **嚴禁給予 Git Commit 建議**：
   * 延續無 commit 建議規格，本 tasks 檔中**不得**包含任何 commit message 草稿、C1/C2 編號或 commit 建議區塊，完全以「OP-N 執行階段」為單元。

4. **同步更新 TODO.md**：
   * 立即更新根目錄 `TODO.md`，將 WIP 清單中的子任務順序更正為最新的 OP 順序：
     ```markdown
     - 🟡 **GOLDEN-BASELINE 黃金基準存盤與退化比對**（`.claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`）
       - [ ] ⬜ 未開始: OP-1 — 五路黃金基準物理存盤（建立 Golden Baseline）
       - [ ] ⬜ 未開始: OP-2 — 自動化 Regression Diff 比對腳本開發（建立質量防線）
       - [ ] ⬜ 未開始: OP-3 — Checkout / 收官階段（一次性歸檔計畫/任務/三份報告，保留 _v2 版號）
       - 工時：3 個 OP 階段
       - 依賴：無
     ```

### 📁 產出與覆寫規格

- **覆寫目標**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`（直接以正確的新結構完全覆寫此暫存檔）
- **同步修改**：`.claude-logs/TODO.md`
- **套用模板**：`.claude-logs/templates/template_tasks.md`（將其中關於 Git commit 的表述更換為本計畫的 OP-N 執行階段與收官歸檔表述）

---

### 🛑 停止指令

**覆寫 tasks.md 並更新 TODO.md 後必須立即停止。**
嚴禁繼續產出各階段的 `_執行.md` 報告。完成後回覆你修正後完整的 tasks.md 全文！
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（DOC-Refactor，無代碼變動）
- 改動檔案數：覆寫 tasks.md + 修改 TODO.md + 提示詞歸檔 + INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

修正前版本見 `2026-06-02_GOLDEN-BASELINE_Tasks_提示詞.md`（初版拆分，Checkout 誤置 OP-1）。
`````
