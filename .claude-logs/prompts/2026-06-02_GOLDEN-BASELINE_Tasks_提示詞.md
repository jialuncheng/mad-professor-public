`````markdown
# 2026-06-02 — GOLDEN-BASELINE Tasks 提示詞

> **收到時間**：2026-06-02 01:45（UTC+8）
> **任務代號**：GOLDEN-BASELINE Tasks
> **觸發 commit**：GOLDEN-BASELINE-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md
> **觸發情境**：baron 同意 GOLDEN-BASELINE plan v2 規格後，下達 tasks 拆分指令；要求以「OP-N 執行階段」取代 Git commit 拆分，OP-1 強制為 Checkout（plan baton→plans 歸檔保留 _v2），同步更新 TODO.md，產出後立即停止。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-02 01:45 |
| **任務代號** | GOLDEN-BASELINE Tasks |
| **觸發 Commit** | GOLDEN-BASELINE-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的「OP-N 執行階段（不給予 Git Commit 建議）」任務清單。

### 📋 任務資訊

- **任務編碼**：GOLDEN-BASELINE
- **工作流類別**：DOC-Refactor（兼顧測試基建準備）
- **Plan 暫存路徑**：.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md         # 進度管控框架
.claude-logs/TODO.md                                           # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md   # 本次拆分的依據 plan
baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v9.md    # 大改版總綱 plan
baron/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md             # 大改版技術 SPEC
.claude-logs/templates/template_tasks.md                       # tasks 模板（套用結構）
```

### 🏢 工作目錄與不可動硬規則（必遵守）

- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
- **嚴禁改動任何業務代碼**（本階段為 tasks 拆分，只允許文件閱讀、檢索與 tasks.md 生成，嚴禁修改任何 python 代碼或配置）。
- **執行中產出文件必須先放 `baton/`**（暫存於 baton/，收官階段才 mv + git add 歸檔）。

### ⚙️ 任務拆分與執行報告硬性約束

1. **嚴禁給予 Git Commit 建議**：
   * 本任務**不拆分任何 Git commit**，改為拆分為獨立的 **「OP-N 執行階段」**（如 `OP-1`, `OP-2`, `OP-3`）。
   * tasks.md 中嚴禁包含任何 git commit message 草稿、C1/C2 編號或 commit 建議區塊。
2. **強制前置 Checkout 階段（OP-1）**：
   * 必須將 `OP-1` 規劃為 **Checkout Commit 階段**。
   * 在 `OP-1` 中，唯一執行的動作是：將位於 `.claude-logs/baton/` 的計畫檔移動至 `.claude-logs/plans/` 並**強制保留版本號 `_v2`**，隨後執行 `git add` 追蹤：
     ```bash
     mv .claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md \
        .claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md
     git add .claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md
     ```
   * 產出 `OP-1` 階段的執行報告，證明計畫檔已安全落盤歸檔。

3. **各階段強制產生執行報告**：
   * 對於拆分出來的每一個執行階段（`OP-1`、`OP-2`、`OP-3` 等），在執行時都必須產出一份獨立的執行報告。
   * 執行報告暫存路徑命名格式：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_[OP代號]_執行.md`。
   * 執行報告必須嚴格套用 `.claude-logs/templates/template_execution.md` 的檔案結構。

📊 成果盤點約束（§0.5 必置於 tasks.md 開頭）
在 `_tasks.md` 的 `## §0.5 成果盤點` 章節中，強制列出本任務的產出規格：

```
## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | N 個 | .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md 等 |
| **修改檔案** | 2 個 | TODO.md / prompts/INDEX.md |
| **狀態更新** | 2 個 | TODO.md 狀態同步 / prompts/INDEX.md 登記 |
| **執行階段** | N 個 | OP-1 (Checkout) → OP-2 (基準物理存盤) → ... |
| **執行報告** | N 個 | 暫存於 baton/ 的各 OP 執行報告（套用 template_execution 模板） |
| **baton 歸檔** | 1 次 | 收官時一次性將計畫、任務與執行報告 mv 歸檔並 git add |
```

📋 §8 執行階段拆分表格要求
在 tasks.md 的 `## §8 推薦執行階段拆分` 章節中，為每個 `OP-N` 填寫以下結構化規格表（取代舊有的 Commit 拆分）：

```
### OP-N — [階段名稱]（[中文子標題]）

| 維度 | 內容 |
|---|---|
| **執行範圍** | <本階段將新建或修改的檔案路徑> |
| **安全性** | 🟢 高 — 僅涉及基準存檔與腳本編寫，業務代碼零改動 |
| **可逆性** | 🟢 高 — 刪除實體備份檔案與測試腳本即可還原 |
| **驗收 grep/執行 條件** | <本階段結束後可用於驗收的具體 terminal 指令> |
| **依賴關係** | <前置 OP 階段或「無」> |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-N_執行.md`（套用 template_execution 模板） |
| **具體實作細節** | <逐步且詳盡說明本階段的工作內容，如挑選哪些 PDF、如何在舊單體下執行、如何備份物理產物，或如何設計自動化 Diff 比對腳本> |
```

🔄 同步更新 TODO.md（必做、即時）
在產出 tasks.md 的同時，立即於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目（狀態設為 `🟡 WIP`，子任務即為你拆分出來的 `OP-N` 執行階段）：

```
- 🟡 **GOLDEN-BASELINE 黃金基準存盤與退化比對**（`.claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`）
  - [/] 🟡 WIP: OP-1 — Checkout Plan（移動並歸檔計畫檔，保留 _v2 版號）
  - [ ] ⬜ 未開始: OP-2 — 代表性文獻黃金基準物理存盤（建立 Golden Baseline）
  - [ ] ⬜ 未開始: OP-3 — 自動化 Regression Diff 比對腳本開發（建立質量防線）
  - 工時：N 個 OP 階段
  - 依賴：無
```

📁 產出規格

* 產出路徑：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`（暫存於 baton/）
* 套用模板：`.claude-logs/templates/template_tasks.md`（將其中關於 Git commit 的表述自動更換為本 SPEC 的 OP-N 執行階段表述）
* 命名格式：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

🛑 停止指令
產出 tasks.md 並更新 TODO.md 後必須立即停止。
嚴禁繼續產出各階段的 `_執行.md` 報告（每個執行階段由 baron 於後續步驟中下達獨立的執行提示詞觸發）。完成後回覆你產出的 tasks.md 全文！
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（DOC-Refactor，無代碼變動）
- 改動檔案數：新增 tasks.md + 提示詞歸檔；修改 TODO.md + INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

無。
`````
