# 2026-07-02 — FE-PERF-1 Tasks 提示詞

> **收到時間**：2026-07-02 01:24（UTC+8）
> **任務代號**：FE-PERF-1 Tasks
> **觸發 commit**：FE-PERF-1-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_tasks.md`
> **觸發情境**：baron 於 plan（v2、§9 六 OQ 全 🟢 定案）review 核准後，下達階段 2 任務拆分指令，要求依 plan 拆為原子 Commit 清單、最後一個 commit 為 checkout、過程文件暫存 baton/、同步 TODO.md。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 01:24 |
| **任務代號** | FE-PERF-1 Tasks |
| **觸發 Commit** | FE-PERF-1-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-02_FE-PERF-1_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-02_FE-PERF-1_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：FE-PERF-1
- **工作流類別**：DOC-Refactor
- **Plan 路徑**：.claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_plan_v1.md

### 📖 強制讀檔清單

（CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1 / template_tasks.md / template_execution.md）

### 🏢 工作目錄硬規則（必遵守）

- 唯一合法工作目錄：`.claude/worktrees/hopeful-yalow-902c50/`
- 嚴禁讀寫主 repo 目錄；嚴禁改動業務代碼（pipeline_core.py / web_server.py / paper_manager.py / processor/*.py / static/*）
- 執行中產出文件必須先放 baton/（checkout 收官後才 mv + git add）

### 📊 成果盤點約束（§0.5 必置文件開頭）

（強制列 §0.5 成果盤點：新增/修改檔案、目錄初始化、狀態更新、Commits、baton 歸檔）

### ⚙️ Commit 拆分與執行限制原則

- 不提供預設 Commit 建議，自行設計最小可逆原子 commits。
- 最後一個 commit 必須且僅能命名為 `checkout`。
- 各實作階段須產執行報告，寫入 `.claude-logs/baton/2026-07-02_FE-PERF-1_<名稱>_<執行階段>_執行.md`（套 template_execution）。
- checkout 階段才 mv 過程文件（plan/tasks/exec）→ plans//tasks//executions/ + git add。

### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填）

（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）

### 📝 §1 TL;DR 中文括號命名要求

（每個 Commit 引用須含中文括號命名）

### 🔄 同步更新 TODO.md（必做、即時）

（於 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方新增 FE-PERF-1 條目，🟡 WIP）

### 📁 產出規格

- 產出路徑：`.claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_tasks.md`（暫存 baton/）
- 套用模板：`.claude-logs/templates/template_tasks.md`
- 命名格式：依 `WORKFLOW_SOP.md §6`

### 🛑 停止指令

產出 tasks.md 並更新 TODO.md 後必須立即停止。嚴禁：續產 _執行.md / 動業務代碼 / 自發 git commit / push。
````

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO.md 同步 🟡 WIP
- 拆分：C1 SOP 手冊 → C2 WORKFLOW_SOP 回填 → checkout（3 commits）
- 改動檔案數：本階段僅新增 tasks.md（baton）+ 更新 TODO.md / INDEX.md（純規劃、零業務碼）
- 是否 commit / push：否（baron 手動）

## 後續引用

執行階段（C1/C2/checkout Run）由 baron 另下獨立提示詞觸發。
