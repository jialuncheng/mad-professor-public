`````markdown
# 2026-06-04 — PIPE-RESUME Tasks 提示詞

> **收到時間**：2026-06-04 18:04（UTC+8）
> **任務代號**：PIPE-RESUME Tasks
> **觸發 commit**：PIPE-RESUME-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`
> **觸發情境**：baron 同意 plan 規格（plan_v1 §99.2 內部已迭代至 v8、四輪對接稽核收斂），下達階段 2 任務拆分指令，要求依 template_tasks 將 plan 拆為可執行 Commit 清單 + 同步 TODO.md，拆完即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 18:04 |
| **任務代號** | `PIPE-RESUME Tasks` |
| **觸發 Commit** | `PIPE-RESUME-Tasks` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-04_PIPE-RESUME_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-04_PIPE-RESUME_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit/階段清單。

### 📋 任務資訊

- **任務編碼**：`PIPE-RESUME`
- **工作流類別**：`BE-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```

CLAUDE.md                                                                           # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                    # 工作流規範（已自動載入）
.claude-logs/TODO.md                                                                # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md          # 本次拆分的依據 plan
.claude-logs/templates/template_tasks.md                                            # tasks 模板（套用結構）

```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
- **嚴禁讀寫主 repo 目錄**（worktree 父目錄）
- **嚴禁改動業務代碼**（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，Checkout 收官時才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）

**首先**，在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本任務的全量產出：

```markdown
## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | N 個 | <檔案 1> / <檔案 2> / ... |
| **修改檔案** | N 個 | <檔案 1>（改動簡述）/ ... |
| **目錄初始化** | N 個 | <目錄>（用途）|
| **狀態更新** | N 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Commit代號> |
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + tasks/ + git add |
```

### ⚙️ Commit 拆分與報告歸檔原則（硬約束）

- **必須包含獨立的 Checkout 階段**：必須將最後一個階段/Commit 設計為 `OP-Last — Checkout / 收官歸檔`。
- **Checkout 階段才搬 Plan 與報告鐵律**：
  - 只有在最後一個 Checkout 階段，才允許執行 `mv` 指令，將暫存在 `baton/` 的計畫書（維持 `_v1.md` 檔名）、任務書（`2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`）以及所有執行報告移動至正式歸檔目錄（`plans/`、`tasks/`、`executions/`）並執行 `git add`。
  - WIP 執行階段嚴禁提前移動計畫書，所有執行中報告必須在工作區保持 Untracked/Gitignored 狀態。
- **各階段必須產生執行報告**：
  - 除最後一個 Checkout 階段外，其餘每一個實作 Commit/階段在執行時，皆須產生一份對應的 `OP-N_執行.md`（或 `C-N_執行.md`）報告暫存於 `baton/`。
  - 執行報告格式必須嚴格套用 `.claude-logs/templates/template_execution.md` 模板。
- **語意完整與可逆設計**：每個 Commit 應為獨立可測試的最小功能單元，且必須可獨立 revert。

### 📋 §8 六維度 Commit/階段 拆分表格（每個實作 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit/階段 必須包含以下六維度表格：

```markdown
### <Commit代號> — <Commit名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep 條件** | <具體驗收指令，如：grep -n "..." <檔案> # 期望：有命中> |
| **依賴關係** | <前置 Commit 或「無前置」> |
| **具體實作細節** | <逐步說明每個檔案的具體改法，含關鍵代碼邏輯> |
```

### 📝 §1 TL;DR 中文括號命名要求

`## §1 TL;DR（概要）` 章節中，每個 Commit 引用必須含中文括號命名：
- 正確範例：`C1 — Bootstrap Core（自動載入核心）`
- 錯誤範例：`C1 Bootstrap Core`（缺少括號中文子標題）

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目：

```markdown
- 🟡 **PIPE-RESUME ResumePipeline策略管線**（`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - [ ] ⬜ 未開始: <Checkout Commit代號> — Checkout / 收官歸檔（一次性歸檔與 TODO ✅，保留 _v1 檔名與內部 v3 版號）
  - 工時：N 個 commits
  - 依賴：無
```

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`（暫存 baton/）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：
- ❌ 繼續產出 `_執行.md`（執行階段由 baron 下達獨立提示詞觸發）
- ❌ 動任何業務代碼（tasks 階段只能 view / grep / 文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`（六維度 Commit 拆分 + §0.5 成果盤點）
- 同步：TODO.md 高優先新增 PIPE-RESUME 🟡 WIP 條目
- 是否 commit / push：否（tasks 階段只產文件、baron 手動）

## 後續引用

承 plan_v1（§99.2 內部 v8、四輪對接稽核定稿）。本階段 2 拆分 Commit 清單後即停；階段 4 執行由 baron 逐 Commit 獨立提示詞觸發。
`````
