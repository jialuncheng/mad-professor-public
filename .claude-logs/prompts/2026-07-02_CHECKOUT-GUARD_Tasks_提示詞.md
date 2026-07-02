# 2026-07-02 — CHECKOUT-GUARD Tasks 提示詞

> **收到時間**：2026-07-02 16:32（UTC+8）
> **任務代號**：CHECKOUT-GUARD Tasks
> **觸發 commit**：CHECKOUT-GUARD-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md`
> **觸發情境**：baron review 核准 plan v2（六 OQ + 範圍補強〔納 template_prompt_for_run〕+ Q6〔checkout 必產報告〕全定案）後，下達階段 2 任務拆分指令；最後一顆 commit 為 checkout、過程文件暫存 baton、同步 TODO 🟡 WIP、不含 commit 建議。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-02 16:32 |
| **任務代號** | CHECKOUT-GUARD Tasks |
| **觸發 Commit** | CHECKOUT-GUARD-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-02_CHECKOUT-GUARD_Tasks_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，依指令將 plan 拆為可執行 Commit 清單。

### 📋 任務資訊
- 任務編碼：CHECKOUT-GUARD / 工作流：DOC-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1 / template_tasks.md / template_execution.md

### 🏢 工作目錄硬規則
唯一合法工作目錄 worktree；嚴禁改業務代碼；過程文件先放 baton/、checkout 才 mv+git add。

### 📊 成果盤點約束（§0.5 必置文件開頭）

### ⚙️ Commit 拆分與執行限制原則
- 不給預設 Commit 建議、自設最小可逆原子 commits。
- 最後一顆必為 checkout。
- 各實作階段產執行報告 → `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_<名稱>_<階段>_執行.md`（套 template_execution）。
- checkout 才 mv 過程文件（plan/tasks/exec）→ plans//tasks//executions/ + git add。

### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填）
影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節。

### 📝 §1 TL;DR 中文括號命名要求

### 🔄 同步更新 TODO.md（必做、即時）
於 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方新增 CHECKOUT-GUARD 條目、🟡 WIP。

### 📁 產出規格
- 產出路徑：`.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_tasks.md`（baton）
- 套用模板：template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止指令
產出 tasks.md + 更新 TODO.md 後立即停止。嚴禁：續產 _執行.md / 動業務代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO 🟡 WIP
- 拆分：C1 WORKFLOW_SOP §3 立鐵律 → C2 三模板落地 → checkout（3 commits）
- 改動檔案數：本階段僅新增 tasks.md（baton）+ 更新 TODO/INDEX（純規劃、零業務碼）
- 是否 commit / push：否（baron 手動）

## 後續引用

執行階段 C1/C2/checkout Run 由 baron 另下獨立提示詞觸發。
