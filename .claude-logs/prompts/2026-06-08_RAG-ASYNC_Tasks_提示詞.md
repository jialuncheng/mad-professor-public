`````markdown
# 2026-06-08 — RAG-ASYNC Tasks（Commit 拆分·BE-Refactor）提示詞

> **收到時間**：2026-06-08 03:45（UTC+8）
> **任務代號**：RAG-ASYNC Tasks（階段 2 拆 commit）
> **觸發 commit**：RAG-ASYNC-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 同意 plan v2 規格，下達任務拆分指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 03:45 | 任務 RAG-ASYNC Tasks | 觸發 Commit RAG-ASYNC-Tasks | 依據 plan_v2 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_Tasks_提示詞.md + 更新 INDEX。

你扮演 Claude Code，依 plan v2 將 RAG-ASYNC 拆為可執行 Commit 清單（BE-Refactor）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v2 / template_tasks.md

### 工作目錄硬規則
唯一合法 .claude/worktrees/hopeful-yalow-902c50/；嚴禁讀寫主 repo；tasks 階段只 view/grep/編輯文件；產出文件先放 baton/、不提前 git add。

### Commit 拆分硬規則
1. C1 必為規格同步（DOC-Refactor）：依 plan_v2 同步 母 plan v10 + PIPE-SPEC；C1 不含 Python 業務碼。
2. 最後一個 Commit 必為 Checkout 收官（Conformance 三維度 + 文件一次性歸檔）。
3. baton 暫存：plan/tasks/執行報告開發期僅暫存 baton/、嚴禁提前 git add；mv→正式目錄只能在最後 Checkout；本 Tasks 階段嚴禁 mv plan_v2。
4. 除 Checkout 外每個代碼 Commit 規劃對應 _執行.md（template_execution）暫存 baton/。

### 強制章節
- §0.5 成果盤點（文件開頭、全量產出 + 最後 Checkout 一次性歸檔）。
- §8 每 Commit 六維度表格（影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作細節；實作步驟不可寫自發 commit）。
- §1 TL;DR 每 Commit 引用含中文括號命名（C1 — Spec Sync（規格文件同步））。

### 同步 TODO.md（即時）
TODO.md ### 🔴 高優先 最前新增 RAG-ASYNC 條目（Tasks WIP + 各 Commit 未開始 + 最後 Checkout）。

### 產出
baton/2026-06-08_RAG-ASYNC_…_tasks.md（暫存）；套 template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止
產 tasks + 更新 TODO 後立即停止；不續產 _執行.md、不動業務碼、不自發 commit/push、不 mv baton plan_v2。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成（tasks.md 產出 baton/）
- 拆分：C1 規格同步（DOC）→ C2-Cn 代碼（contracts/rag_indexer/run_phase2/run_phase4/tests）→ 最後 Checkout 收官
- 是否動業務代碼：否（tasks 階段純文件）；是否 commit：否
- 待 baron 下 C1 執行提示詞

## 後續引用

RAG-ASYNC tasks：依 plan_v2 七定案（D1-D7）拆 commit；C1 同步母 plan v10 + PIPE-SPEC（含修 §1.3 P3 doc-drift）；代碼段建 processor/rag_indexer.py 全重寫 + GlossaryReadySpec section_summaries + run_phase2 六步 + run_phase4 改呼 + conformance 測試；最後 Checkout 一次性 baton 歸檔。
`````
