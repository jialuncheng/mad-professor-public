````markdown
# 2026-07-01 — RESCUE-1 Tasks 提示詞

> **收到時間**：2026-07-01 12:34（UTC+8）
> **任務代號**：RESCUE-1 Tasks
> **觸發 commit**：RESCUE-1-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-01_RESCUE-1_遺失治理文件挽救_tasks.md
> **觸發情境**：baron 同意 plan 規格（`2026-06-28_RESCUE-1_遺失治理文件挽救_plan_v1.md`），下達任務拆分指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-01 12:34 |
| 任務代號 | RESCUE-1 Tasks |
| 觸發 Commit | RESCUE-1-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-07-01_RESCUE-1_遺失治理文件挽救_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-07-01_RESCUE-1_Tasks_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請依指令將 plan 拆分為可執行 Commit 清單。

### 任務資訊
- 任務編碼 RESCUE-1 / 工作流 DOC-Refactor
- Plan：.claude-logs/baton/2026-06-28_RESCUE-1_遺失治理文件挽救_plan_v1.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / 本次 plan / template_tasks.md / template_execution.md

### 工作目錄硬規則
唯一合法 .claude/worktrees/hopeful-yalow-902c50/；嚴禁讀寫主 repo/業務代碼；產出先放 baton/、Checkout 才歸檔。

### Commit 拆分與報告鐵律
1. 動態合理拆分（依 plan U1~U6，例 還原 QUEUE-1 v2 / 重建 PIPE-SPEC v8 / 清理 MODEL-10 / 修正 TODO）
2. 最後 Commit 必為 Checkout（收官）
3. Checkout 階段才 mv + git add 歸檔（plan/tasks/執行報告，之前留 baton 不入版控）
4. 各階段皆需產執行報告（template_execution）

### 成果盤點約束（§0.5 必置文件開頭）
§0.5 列全量產出：新增/修改/目錄/狀態更新/Commits/baton 歸檔。

### §8 六維度 Commit 拆分表格（每 Commit 必填）
影響範圍 / 安全性 / 可逆性 / 驗收 grep / 依賴 / 具體實作細節（含該 Commit 暫存 baton 的執行報告檔名）。

### §1 TL;DR 中文括號命名要求
每 Commit 引用含中文括號命名（例 C1 — Restore Queue v2（還原雙實例排程計畫））。

### 同步更新 TODO.md（必做、即時）
於 ## 🟡 進行中 → ### 🔴 高優先 最前方新增 RESCUE-1 條目（含各 Commit 中文括號命名）。

### 產出規格
- 產出：.claude-logs/baton/2026-07-01_RESCUE-1_遺失治理文件挽救_tasks.md（暫存 baton/）
- 模板：template_tasks.md；命名依 WORKFLOW_SOP §6

### 停止指令
產出 tasks.md 並更新 TODO.md 後立即停止。嚴禁：續產 _執行.md / 動業務代碼 / 自發 git commit|push。
```

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO.md 同步 + INDEX.md 同步
- pytest baseline → final：N/A（DOC-Refactor 文件挽救）
- 改動檔案數：新增 tasks.md（baton 暫存）；修改 TODO.md、prompts/INDEX.md、本歸檔檔
- 是否 commit / push：否（依 §1.3，commit 由 baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
