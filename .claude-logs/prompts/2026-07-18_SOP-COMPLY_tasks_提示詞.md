````markdown
# 2026-07-18 — SOP-COMPLY Tasks 提示詞

> **收到時間**：2026-07-18 05:03（UTC+8）
> **任務代號**：SOP-COMPLY Tasks
> **觸發 commit**：SOP-COMPLY-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md
> **觸發情境**：baron 同意 plan v1.1（execution-ready），下達階段 2 任務拆分指令。
> **⚠️ 工作目錄校正**：提示詞列 `.claude/worktrees/hopeful-yalow-902c50/`（已刪除·GOV-PATH-FIX 已修模板但此提示詞早於其落地）；依主 repo 就地慣例執行。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-18 05:03 | 任務代號 | SOP-COMPLY Tasks | 觸發 Commit | SOP-COMPLY-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先歸檔 → 更新 INDEX → 回覆後續行）

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：SOP-COMPLY / 工作流：BE-Refactor
- Plan：.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / SOP-COMPLY plan / template_tasks / template_execution / database_SOP / logging_SOP

### 🏢 工作目錄硬規則
- 唯一合法工作目錄：.claude/worktrees/hopeful-yalow-902c50/（⚠️ 已刪除·主 repo 就地）
- 嚴禁改業務代碼（此階段僅閱讀分析）；執行中產出先放 baton/。

### 📊 成果盤點約束（§0.5 必置）
### ⚙️ Commit 拆分與執行報告原則
1. 僅限 SOP 清帳範圍（25 處 logger.error 補 exc_info、llm/client 吞例外、paper_manager/web_server + 3 測試 DB 事務改造），不改業務邏輯本體與 DB schema。
2. 各開發 commit 產執行報告暫存 baton/（template_execution）。
3. 最後 Commit 為 Checkout 收官：才准 mv baton plan/tasks/執行報告→ plans/ executions/ tasks/ + 產 checkout_執行.md + git add；中間 commit 嚴禁搬移。
4. 可逆與最小干擾：每 commit 獨立可測最小單元。

### 📋 §8 六維度 Commit 拆分表格（影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作·對齊 SOP + plan OQ）
### 📝 §1 TL;DR 中文括號命名（例 C1 — Logging Hardening（日誌合規補齊））
### 🔄 同步更新 TODO.md（🔴 高優先最前方新增 SOP-COMPLY 🟡 WIP·依賴無）
### 📁 產出規格：baton/2026-07-18_SOP-COMPLY_..._tasks.md·template_tasks·WORKFLOW_SOP §6

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
