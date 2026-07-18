````markdown
# 2026-07-18 — BRAINSTORM-1 Tasks 提示詞

> **收到時間**：2026-07-18 22:24（UTC+8）
> **任務代號**：BRAINSTORM-1 Tasks
> **觸發 commit**：BRAINSTORM-1-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md
> **觸發情境**：baron 同意 plan v2 規格（三落點拍板 + Q1–Q7 定案 + review 三點併入），下達階段 2 任務拆分指令。

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-07-18 22:24` |
| **任務代號** | `BRAINSTORM-1 Tasks` |
| **觸發 Commit** | `BRAINSTORM-1-Tasks` |
| **相關產出檔案** | `.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md` |
| **觸發情境** | `baron 同意 plan 規格，下達任務拆分指令` |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_BRAINSTORM-1_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的 `## 依時間排序` 首行插入以下新條目，若超過 15 筆則刪除最舊一筆：
   `- 2026-07-18 — `2026-07-18_BRAINSTORM-1_Tasks_提示詞.md`（Tasks·DOC-Refactor：依 plan v2 拆 BRAINSTORM-1 為原子 commits——C1 導入作業 SOP 及視覺伴讀指引 / C2 導入 tools/ 腳本並以環境變數改導 / Checkout 兩階段歸檔；各 commit 執行報告暫存 baton 並套用 template_execution；Checkout 階段一次性歸檔；同步 TODO 🟡 WIP；無 commit 建議）`

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_BRAINSTORM-1_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：`BRAINSTORM-1`
- **工作流類別**：`DOC-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md`

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

​```
CLAUDE.md                                                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                       # 工作流規範（已自動載入）
.claude-logs/TODO.md                                                                   # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md  # 本次拆分的依據 plan
.claude-logs/templates/template_tasks.md                                               # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md                                           # 執行報告模板
​```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）
- **嚴禁讀寫授權範圍外檔案**（授權範圍由各任務 plan / tasks 工作目錄條款定義）
- **嚴禁改動業務代碼**（`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*`）
- **執行中產出文件必須先放 baton/**（非 baton/ 暫存文件不入版控，checkout 收官後才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）

**首先**，在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本任務的全量產出：

​```markdown
## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | N 個 | <檔案 1> / <檔案 2> / ... |
| **修改檔案** | N 個 | <檔案 1>（改動簡述）/ ... |
| **目錄初始化** | N 個 | <目錄>（用途）|
| **狀態更新** | N 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Commit代號> |
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + tasks/ + git add |
​```

### ⚙️ Commit 拆分與歸檔原則

- **最後一個 Commit 必須為 Checkout（收官歸檔）**：你必須規劃最後一個 Commit 作為 Checkout 收官階段。
- **延遲歸檔鐵律**：在本階段（產出 tasks.md）**嚴禁**將目前位於 `baton/` 的 plan 移入 `plans/`。本 plan、新產出的 tasks.md 及後續各階段產出的執行報告，一律暫存於 `.claude-logs/baton/`，**必須且僅能在最後一個 Commit (Checkout) 的執行階段一次性進行移動並歸檔**。
- **Checkout 執行報告**：Checkout 階段必須產出並保存 `.claude-logs/executions/<YYYY-MM-DD>_BRAINSTORM-1_checkout_執行.md`（ Checkout 歸檔時檔名更正為 `.claude-logs/executions/`，但暫存期在 `baton/`）。
- **每階段必須產出執行報告**：除 Checkout 外，每一個中間執行 Commit 都必須在 `.claude-logs/baton/` 下產生一份執行報告（暫存不歸檔），其檔案命名必須依 `.claude-logs/ref/WORKFLOW_SOP.md §6` 命名規則，且必須套用 `.claude-logs/templates/template_execution.md` 模板。
- **可逆設計**：每個 Commit 必須可獨立 revert，且為語意完整的最小功能單元。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit 必須包含以下六維度表格：

​```markdown
### <Commit代號> — <Commit名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep 條件** | <具體驗收指令，如：grep -n "..." <檔案> # 期望：有命中> |
| **依賴關係** | <前置 Commit 或「無前置」> |
| **具體實作細節** | <逐步說明每個檔案的具體改法，含關鍵代碼邏輯> |
​```

### 📝 §1 TL;DR 中文括號命名要求

`## §1 TL;DR（概要）` 章節中，每個 Commit 引用必須含中文括號命名：
- 正確範例：`C1 — Bootstrap Core（自動載入核心）`
- 錯誤範例：`C1 Bootstrap Core`（缺少括號中文子標題）

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目：

​```markdown
- 🟡 **BRAINSTORM-1 brainstorming問答與視覺伴讀**（`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：無
​```

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md`（暫存於 baton/）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：
- ❌ 繼續產出任何 `_執行.md`（執行階段由 baron 下達獨立提示詞觸發）
- ❌ 動任何業務代碼（tasks 階段只能 view / grep / 文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`
```

---

## 執行結果摘要

- ✅ 完成：依 plan v2 產出 tasks.md（暫存 baton/）+ 同步 TODO.md 🟡 WIP
- 拆分：C1 作業 SOP 與視覺伴讀指引 / C2 tools/ 腳本導入與環境變數改導 / Checkout 收官（共 3 commits）
- pytest baseline：748 passed（本任務零 .py 業務邏輯、不影響）
- 改動檔案：本階段僅產 tasks.md + 改 TODO.md（暫存不 commit）
- commit / push：由 baron 手動執行

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
