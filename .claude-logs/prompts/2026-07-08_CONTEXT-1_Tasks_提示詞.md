# 2026-07-08 CONTEXT-1 Tasks 提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：Tasks（階段 2 拆 commit）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-08

---

## 原始提示詞（逐字）

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-08 23:22 |
| **任務代號** | CONTEXT-1 Tasks |
| **觸發 Commit** | CONTEXT-1-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令；最後一個 commit 為 checkout，checkout 階段才搬 plan 和執行報告，各階段產生執行報告（套用 template_execution）。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-08_CONTEXT-1_Tasks_提示詞.md`
   格式依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-08_CONTEXT-1_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：CONTEXT-1
- **工作流類別**：DOC-Refactor
- **Plan 路徑**：.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

```

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md # 專案控制框架（已自動載入）
.claude-logs/TODO.md                                   # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md # 本次拆分的依據 plan
.claude-logs/templates/template_tasks.md               # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md           # 執行報告模板（套用結構）

```

### 🏢 工作目錄與授權範圍硬規則（必遵守）

- **唯一合法工作目錄**：`/Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public` (主 repo 目綠就地，依 CLAUDE.md §3 新規定)
- **授權讀寫範圍**：限於 `CLAUDE.md` 及 `.claude-logs/` 下特定的治理與配置檔案，嚴禁讀寫任何後端業務邏輯程式碼或測試目錄。
- **嚴禁改動業務代碼**（`*.py`、`static/`、`tests/`）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，checkout 收官時才 mv + git add 歸檔）

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
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + tasks/ + executions/ + git add |
```

### ⚙️ Commit 拆分與執行限制原則

- **自設最小可逆原子 Commits**：提示詞中不提供預設的 Commit 建議，請自行規劃最合適的最小可逆原子 commits 清單，確保每個 Commit 均為獨立可測試的功能單元。
- **最後一個 Commit 必須為 checkout**：最後一個 commit 必須且僅能命名為 `checkout`（例如：`C4 — Checkout（收官歸檔）`）。
- **各實作階段必須產生執行報告**：除最後 checkout 階段外，前面的每個 commit 執行階段（如 C1, C2, C3）在完成改動與測試後，均必須依據 `.claude-logs/templates/template_execution.md` 模板，在 `baton/` 目錄下產生對應的執行報告（例如 `baton/2026-07-08_CONTEXT-1_C1_執行.md`）。
- **Checkout 階段才進行文件搬移**：在前面的執行 commit 階段，所有的執行報告與暫存文件必須暫存在 `baton/` 目錄中。只有在最後的 `checkout` commit 階段，才執行將 plan 移入 `plans/`、將 tasks 移入 `tasks/`、將所有執行報告移入 `executions/` 的搬移與 `git add` 歸檔操作。
- **語意完整與可逆設計**：每個 Commit 應為獨立可測試的最小功能單元，且必須可獨立 revert。
- **優先順序**：依 `CLAUDE.md §3` 與 plan §1.18 Bootstrap First 原則排序。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit 必須包含以下六維度表格：

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
- 🟡 **CONTEXT-1 session載入鏈瘦身與context治理**（`.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：無
```

### 📦 歸檔 baton plan

本任務為 DOC-Refactor 治理工作，請在 tasks.md 產出後，在 tasks 階段**不要**執行 plan 歸檔。Plan 歸檔必須與執行報告一同留在最後的 `checkout` commit 階段才進行實體搬移。

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md`（暫存 baton/）
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

## 上下文（承接對話）

1. plan v1 已於同 session 產出並經 baron 九 OQ 全數定案升 §99.2 v2（`baton/2026-07-07_CONTEXT-1_..._plan_v1.md`）。
2. 本提示詞：baron 下達階段 2 拆 tasks——自設最小可逆原子 commits、末 commit 必為 checkout、各 Run 產執行報告（template_execution）暫存 baton、checkout 才一次性歸檔；同步 TODO 設 🟡 WIP；產出後即停。

## 產出

- `.claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md`
- `TODO.md` 高優先區新增 CONTEXT-1 🟡 WIP 條目
