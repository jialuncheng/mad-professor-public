`````markdown
# 2026-06-02 — PIPE-CORE Tasks 提示詞

> **收到時間**：2026-06-02 18:05（UTC+8）
> **任務代號**：PIPE-CORE Tasks
> **觸發 commit**：PIPE-CORE-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md
> **觸發情境**：baron 同意 PIPE-CORE plan v2 規格後，下達 tasks 拆分指令——以 OP-N 執行階段（不拆 Git commit）推進三層解耦空骨架（pipelines/），最後 OP 為 Checkout 收官歸檔（保留 _v2 版號）。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-02 18:05 |
| **任務代號** | PIPE-CORE Tasks |
| **觸發 Commit** | PIPE-CORE-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_PIPE-CORE_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_PIPE-CORE_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 OP 階段清單。

### 📋 任務資訊

- **任務編碼**：PIPE-CORE
- **工作流類別**：BE-Refactor
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/TODO.md                                           # 任務狀態真理源（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md         # 專案進度管控框架
.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md # 本次拆分的依據 plan
.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v9.md # 大改版關聯 plan
.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md # 架構 spec
.claude-logs/templates/template_tasks.md                       # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md                   # 執行報告模板
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
- **嚴禁讀寫主 repo 目錄**（worktree 父目錄）
- **嚴禁改動業務代碼**（此階段 `pipeline_core.py` 舊單體、`web_server.py`、`models.py` 等皆在不可動清單中）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，Checkout 收官時才一次性 mv + git add 歸檔）

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
| **執行階段** | N 個 | OP-1（名稱）→ OP-2（名稱）→ ... → OP-Last（Checkout / 收官歸檔） |
| **執行報告** | N 個 | `baton/2026-06-02_PIPE-CORE_OP-1_執行.md` 等暫存報告（套用 template_execution.md） |
| **baton 歸檔** | 1 次 | **僅在最後 Checkout 階段**一次性 mv 歸檔至正式目錄並執行 git add |
```

### ⚙️ OP 執行階段拆分原則

- **不拆分 Git Commit**：本任務不推薦任何 Git commit 建議，亦不把代碼落地細分為 git commit。改以「**OP-N 執行階段**」推進。
- **階段獨立可測**：每個 OP 階段應為獨立可測試的最小功能單元。
- **最後 Checkout 階段**：必須規劃最後一個階段為 `OP-Last — Checkout / 收官歸檔`。
- **各階段必產報告**：除 Checkout 外，其餘每個 OP 執行階段在執行時，皆須產生一份對應的 `OP-N_執行.md` 報告（暫存於 `baton/`，套用 `template_execution.md`）。
- **暫存與歸檔鐵律**：
  - 在執行 OP-1、OP-2 等期間，所有產出的執行報告、任務 tasks 檔、計畫 plan 檔，**嚴禁在執行中 mv 移動或 git add**，必須原封不動留在 `baton/` 暫存。
  - **唯一且必須在最後的 Checkout 階段**，才能一次性將 plan（保留 `_v2`）、tasks（保留 `_v2`）、以及所有 `OP-*_執行.md` 搬移歸檔至正式目錄並 `git add`。

### 📋 §8 六維度 OP 拆分表格（每個 OP 必填）

tasks.md 的 `## §8 推薦執行階段拆分` 章節，每個 OP 階段必須包含以下六維度表格：

```markdown
### OP-<序號> — <階段名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep/執行 條件** | <具體驗收指令與預期輸出，如 pytest 或 grep 指令> |
| **依賴關係** | <前置 OP 階段或「無前置」> |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-CORE_OP-<序號>_執行.md`（套用 template_execution.md，暫存 baton/、不移動） |
| **具體實作細節** | <逐步說明本階段具體修改邏輯與關鍵代碼，包含目標模組的骨架實作細節> |
```

#### 📦 Checkout 階段特定實作細節要求

在最後一個 `OP-Last — Checkout / 收官歸檔` 的「具體實作細節」中，必須寫明以下指令：

1. 產出 `OP-Last_執行.md` 暫存於 `baton/`。

2. 執行歸檔搬移指令：

   ```bash
   mv .claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md .claude-logs/plans/
   mv .claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md .claude-logs/tasks/
   mv .claude-logs/baton/2026-06-02_PIPE-CORE_OP-*_執行.md .claude-logs/executions/
   ```

3. 執行版控逃逸追蹤：

   ```bash
   git add .claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md
   git add .claude-logs/tasks/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md
   git add .claude-logs/executions/2026-06-02_PIPE-CORE_OP-*_執行.md
   ```

4. 更新 `TODO.md` 對應項目為 ✅。

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 -> ### 🔴 高優先` 最前方，新增本任務條目（維持 tasks 檔與 plan 檔的 `_v2` 版號）：

```markdown
- 🟡 **PIPE-CORE_v2 三層解耦調度骨架**（`.claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`）
  - [/] 🟡 WIP: OP-1 — <OP-1名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: OP-2 — <OP-2名稱>（<中文括號命名>）
  - ...
  - [ ] ⬜ 未開始: OP-Last — Checkout / 收官歸檔（一次性歸檔與 TODO ✅）
  - 工時：N 個 OP
  - 依賴：無
```

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md`（暫存於 `baton/`，**加上版號 `_v2`**）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：

- ❌ 繼續產出 `_執行.md`（執行階段由 baron 下達獨立提示詞觸發）
- ❌ 改動任何業務代碼（tasks 階段只能 view / grep / 文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（tasks 拆分階段，無代碼變動）
- 改動檔案數：新增 tasks_v2.md + 提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 PIPE-CORE plan v2（`baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`）。OP 執行階段由 baron 後續獨立提示詞觸發。
`````
