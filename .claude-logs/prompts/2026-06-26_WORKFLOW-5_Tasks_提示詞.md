````markdown
# 2026-06-26 — WORKFLOW-5 Tasks 提示詞

> **收到時間**：2026-06-26 20:32（UTC+8）
> **任務代號**：WORKFLOW-5 Tasks
> **觸發 commit**：WORKFLOW-5-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md
> **觸發情境**：baron 同意 plan v5 規格（含兩 Open Questions 拍板），下達任務拆分指令，要求依 DOC-Refactor 流程將 plan 拆為可執行 Commit 清單並同步 TODO。

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-26 20:32 |
| 任務代號 | WORKFLOW-5 Tasks |
| 觸發 Commit | WORKFLOW-5-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入提示詞歸檔檔 .claude-logs/prompts/2026-06-26_WORKFLOW-5_Tasks_提示詞.md（格式依 prompts/README.md §3）
2. 更新 INDEX.md（對應分類 + 依時間排序首行插入，超過 15 筆刪最舊）
3. 確認完成後回覆「✅ 提示詞已歸檔：<路徑>」，再繼續

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：WORKFLOW-5
- 工作流類別：DOC-Refactor
- Plan 路徑：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_plan.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / TODO.md /
本次 plan / template_tasks.md / template_execution.md

### 🏢 工作目錄硬規則
- 唯一合法工作目錄：.claude/worktrees/hopeful-yalow-902c50/（對齊當前 worktree）
- 嚴禁讀寫主 repo 目錄；嚴禁改動業務代碼
- 執行中產出文件必須先放 baton/（checkout 收官後才 mv + git add）

### 📊 成果盤點約束（§0.5 必置文件開頭）
tasks.md §0.5 成果盤點強制列出：新增檔案 / 修改檔案 / 目錄初始化 / 狀態更新 / Commits / baton 歸檔。

### ⚙️ Commit 拆分原則（本次特別約束）
- 彈性規劃，數量內容由你依最佳工程實務安排，無固定上限。
- 每個 Commit 為獨立可測試最小功能單元。
- 各個 Commit（階段）都必須產生對應執行報告（依 template_execution.md），暫存 baton/。
- 最後一個 Commit 必須明確命名為 Checkout 階段；只有 Checkout 才允許 mv baton → 正式目錄 + git add。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）
影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節。

### 📝 §1 TL;DR 中文括號命名要求
每個 Commit 引用必須含中文括號命名（例 C1 — SessionEnd Dry-Run（阻擋能力實測））。

### 🔄 同步更新 TODO.md（必做、即時）
在 ## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先 最前方新增本任務條目（含各 Commit 中文括號命名）。

### 📁 產出規格
- 產出路徑：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md（暫存 baton/）
- 套用模板：template_tasks.md；命名格式依 WORKFLOW_SOP §6

### 🛑 停止指令
產出 tasks.md 並更新 TODO.md 後必須立即停止。
嚴禁：繼續產 _執行.md / 動業務代碼 / 將 baton 計畫與任務檔歸檔（歸檔限 Checkout）。
```

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO.md 同步 + INDEX.md 同步
- pytest baseline → final：N/A（tasks 階段不跑業務測試；hook 腳本測試屬 Run 階段）
- 改動檔案數：新增 tasks.md（baton 暫存）；修改 TODO.md、prompts/INDEX.md、本歸檔檔
- 是否 commit / push：否（依 §1.3，commit 由 baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
