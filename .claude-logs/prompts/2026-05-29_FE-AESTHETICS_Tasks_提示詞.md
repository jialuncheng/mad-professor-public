# 2026-05-29 — FE-AESTHETICS Tasks 提示詞

> **收到時間**：2026-05-29 05:05
> **任務代號**：FE-AESTHETICS Tasks
> **觸發 Commit**：FE-AESTHETICS-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md`
> **觸發情境**：baron 同意 plan 規格 (v1.3)，下達任務拆分指令，要求依 plan 拆分 Commit 清單並同步更新 TODO.md

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-29 05:05 |
| **任務代號** | FE-AESTHETICS Tasks |
| **觸發 Commit** | FE-AESTHETICS-Tasks |
| **當前 Checkout Commit** | ef1c0b33356b684aeb4571430aece042d977a245 |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md |
| **觸發情境** | baron 同意 plan 規格 (v1.3)，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-05-29_FE-AESTHETICS_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-05-29_FE-AESTHETICS_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：FE-AESTHETICS
- **工作流類別**：FE-Refactor
- **Plan 路徑**：.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md (v1.3)

### 📖 強制讀檔清單

請在開始拆分前，必須完整閱讀以下文件：

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md # 進度管控規範（已自動載入）
.claude-logs/TODO.md                                   # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md # 本次拆分的依據 plan
.claude-logs/templates/template_tasks.md               # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md           # 執行報告模板（未來執行參考）

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
- **嚴禁讀寫主 repo 目錄**（worktree 父目錄）
- **嚴禁改動業務代碼**（此為 Tasks 規劃階段，嚴禁觸碰任何業務邏輯，僅可編輯文檔）
- **執行中產出文件必須先放 `baton/`**（非 baton/ 暫存文件不入版控，C5 收官後才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）

**首先**，在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本任務的全量產出：

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | N 個 | <檔案 1> / <檔案 2> / ... |
| **修改檔案** | N 個 | <檔案 1>（改動簡述）/ ... |
| **目錄初始化** | N 個 | <目錄>（用途）|
| **狀態更新** | N 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Commit代號> |
| **baton 歸檔** | N 次 | 收官時 mv → plans/ + tasks/ + git add |

### ⚙️ Commit 拆分原則

- **彈性規劃**：Commit 數量可依計畫書最佳施行方式彈性安排，無固定上限
- **語意完整**：每個 Commit 應為獨立可測試的最小功能單元
- **可逆設計**：每個 Commit 必須可獨立 revert
- **優先順序**：依 `CLAUDE.md §3 工作目錄硬規則` 與 plan §1.18 Bootstrap First 原則排序

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

tasks.md 的 `## §8 推薦 Commit 拆分` 章節，每個 Commit 必須包含以下六維度表格：

### <Commit代號> — <Commit名稱>（<中文括號命名>）

| 維度 | 內容 |
|---|---|
| **影響範圍** | <列出所有改動檔案與新增檔案> |
| **安全性** | 🟢 高 / 🟡 中 / 🔴 低 — <理由> |
| **可逆性** | 🟢 高 / 🟡 中 / 🔴 低 — <回滾方式> |
| **驗收 grep 條件** | <具體驗收指令，如：grep -n "..." <檔案> # 期望：有命中> |
| **依賴關係** | <前置 Commit 或「無前置」> |
| **具體實作細節** | <逐步說明每個檔案的具體改法，含關鍵代碼邏輯，且必須符合 template_execution.md 的產出標準> |

### 📝 §1 TL;DR 中文括號命名要求

`## §1 TL;DR（概要）` 章節中，每個 Commit 引用必須含中文括號命名：

- 正確範例：`C1 — Bootstrap Core（自動載入核心）`
- 錯誤範例：`C1 Bootstrap Core`（缺少括號中文子標題）

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本任務條目：

- 🟡 **FE-AESTHETICS 摘要工具列重構與正文扉頁美化**（`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - [ ] ⬜ 未開始: <Commit代號 2> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：無

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md`（暫存 baton/）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：

- ❌ 繼續產出 `_執行.md`（執行階段由 baron 下達獨立提示詞觸發）
- ❌ 動任何業務代碼（tasks 階段只能 view / grep / 文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`
```

---

## 執行結果摘要

- ✅ 提示詞已歸檔
- 產出 `.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md`（2 Commits + Check，共 3 個 commit）
- TODO.md 已同步更新，FE-AESTHETICS 加入 🟡 WIP 進行中條目

## 後續引用

- 本文件為 FE-AESTHETICS Tasks 提示詞歸檔，記錄 baron 下達 tasks 拆分指令的完整意圖。

> 本文件依 `.claude-logs/prompts/README.md §3 檔案格式` 規範建立。
