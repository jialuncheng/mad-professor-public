````markdown
# 2026-07-12 — SEC-HARDEN Tasks 提示詞

> **收到時間**：2026-07-12 06:43（UTC+8）
> **任務代號**：SEC-HARDEN Tasks
> **觸發 commit**：SEC-HARDEN-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md
> **觸發情境**：baron 同意 plan v1.1（execution-ready），下達階段 2 任務拆分指令，將 SEC-HARDEN plan 拆為可執行 Commit 清單並同步 TODO。
> **⚠️ 工作目錄校正**：提示詞列 `.claude/worktrees/hopeful-yalow-902c50/` 為已刪除 worktree（CLAUDE.md §3 v5）；依主 repo 就地慣例（RESCUE-1 C1 / TEST-GREEN 先例）於 `~/mad-professor-public` 執行。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-12 06:43 |
| 任務代號 | SEC-HARDEN Tasks |
| 觸發 Commit | SEC-HARDEN-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先歸檔 → 更新 INDEX → 回覆後續行）

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：SEC-HARDEN
- 工作流類別：BE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / SEC-HARDEN plan /
template_tasks / template_execution / database_SOP / logging_SOP

### 🏢 工作目錄硬規則
- 唯一合法工作目錄：.claude/worktrees/hopeful-yalow-902c50/（⚠️ 已刪除·實際主 repo 就地）
- 嚴禁改業務代碼（此階段僅閱讀分析）；執行中產出先放 baton/。

### 📊 成果盤點約束（§0.5 必置）
### ⚙️ Commit 拆分與執行報告原則
1. 僅限後端加固範圍（web_server.py + settings.py 5 項）、不影響前端/DB schema/渲染。
2. 各開發 commit 產執行報告暫存 baton/（template_execution）。
3. 最後一個 Commit 必為 Checkout 收官：才准 mv baton plan/tasks/執行報告→ plans/ executions/ tasks/ + 產 checkout_執行.md + git add；中間 commit 嚴禁搬移。
4. 可逆與最小干擾：每 commit 獨立可測最小單元。

### 📋 §8 六維度 Commit 拆分表格（影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作細節·對齊 SOP）
### 📝 §1 TL;DR 中文括號命名（例 C1 — IP Parsing（可信代理解析））
### 🔄 同步更新 TODO.md（🔴 高優先最前方新增 SEC-HARDEN 🟡 WIP·依賴無）
### 📁 產出規格：baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md·template_tasks·WORKFLOW_SOP §6

### 🛑 停止指令：產 tasks + 更新 TODO 後停止。嚴禁：續產 _執行.md / 動業務代碼 / 自發 git commit/push。
```

---

## 執行結果摘要

- ✅ 提示詞歸檔 + INDEX 更新
- ✅ 產出 tasks.md 至 baton/、同步 TODO 🟡 WIP
- 改動檔案（本階段）：2（prompts 歸檔 + INDEX）；tasks.md 暫存 baton/ 不入版控
- commit / push：無（tasks 階段不 commit）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
