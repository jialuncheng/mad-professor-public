`````markdown
# 2026-06-03 — API-PERF Tasks 提示詞

> **收到時間**：2026-06-03 07:01（UTC+8，本版；06:48 初版同名草稿經本版覆寫）
> **任務代號**：API-PERF Tasks
> **觸發 commit**：API-PERF-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md
> **觸發情境**：baron 同意 API-PERF plan v2 規格後下達 tasks 拆分指令。**本版（07:01）修正 Checkout 時序**：廢除 06:48 初版的「C1 提前搬 plan」雙 Checkout，改為**單一收官 Checkout（C6）**——實作階段 C1–C5 全部暫存 baton/，唯最後 C6 一次性搬移 plan + tasks + 所有執行報告。對齊已落地 PIPE-CORE（Orchestrator/PhaseEnum）/PIPE-SCAFFOLD（雙軌派發）：U1 Semaphore 守 Orchestrator.run+雙軌派發點、U3 LRU 配 ai_core/rag_retriever、U7 計時埋點對齊 PhaseEnum (phase,stage) 二維鍵。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-03 07:01`                                           |
| **任務代號**     | `API-PERF Tasks`                                             |
| **觸發 Commit**  | `API-PERF-Tasks`                                             |
| **相關產出檔案** | `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md` |
| **觸發情境**     | `baron 同意 plan 規格，下達任務拆分指令`                     |
---
### 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
（同前：寫入 prompts/2026-06-03_API-PERF_Tasks_提示詞.md + 更新 INDEX）
---
你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。
### 📋 任務資訊
- **任務編碼**：`API-PERF` ｜ **工作流類別**：`BE-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_API-PERF_API技術審計與效能優化_plan_v2.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / TODO.md /
plan_v2 / PIPE plan_v9 / PIPE-CORE plan_v2 / PIPE-SCAFFOLD plan_v3 / template_tasks / template_execution
### 🏢 工作目錄與變更限制硬規則
- 唯一合法工作目錄 worktree；嚴禁讀寫主 repo；嚴禁改業務代碼（tasks 階段只 view/grep/編輯 tasks）；產出先放 baton/。
### 📊 成果盤點約束（§0.5 必置文件開頭）
### ⚙️ Commit 拆分原則與關鍵要求（請在拆分時落實）
1. **必須包含 Checkout Commit（收官歸檔階段）**：
   - 實作階段（C1–C5）所有的新建/修改規劃、任務清單與執行報告**均原封不動暫存於 baton/**。
   - **檢出與搬移時機**：必須規劃一個獨立的收官 Checkout Commit（如 `C6 — Checkout`）。只有在這個最後的 checkout 階段，才准一次性將 plan 搬移至 plans/、tasks.md 搬移至 tasks/，以及將所有實作階段的 `_執行.md` 報告搬移至 executions/ 下，並執行 git add 納入版控。
2. **各階段必須產生執行報告**：C1–C5 每個 commit 執行完畢產 `_執行.md`（暫存 baton/，套用 template_execution.md）。
3. **對齊新架構（實作細節指引）**：
   - U1 (Semaphore)：並發信號量需直接守護新架構 `Orchestrator.run(ctx)` 與舊單體雙軌入口的派發點。
   - U3 (LRU Cache)：Lazy Load 與 LRU 淘汰直接配置在 `ai_core.py` 及 `rag_retriever.py` 快取容器，無縫服務新 Strategy 呼叫的 RAG 檢索。
   - U7 (性能計時埋點)：直接對齊已落地 `PhaseEnum`(P1-P4) 與 `Orchestrator` 內部迴圈，(phase, stage) 二維鍵寫結構化 JSON 日誌，省去 plan 過渡期暫映射。
4. **不用給 commit 建議**：tasks.md 不預定義 git commit 行為，僅列六維度拆分與驗收。
5. **加上版號**：產出路徑 `.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`。
### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）
（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）
### 📝 §1 TL;DR 中文括號命名要求（每個 Commit 引用含中文括號命名）
### 🔄 同步更新 TODO.md（必做、即時）
於 TODO.md ### 🔴 高優先 最前方新增 API-PERF 條目（依實際 Commit 數量）。
### 📁 產出規格
產出路徑 baton/2026-06-03_API-PERF_..._tasks_v3.md；套用 template_tasks.md。
---
### 🛑 停止指令
產出 tasks.md 並更新 TODO.md 後立即停止。嚴禁續產 `_執行.md` / 動業務代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（tasks 拆分階段、無代碼變動）
- 改動檔案數：覆寫 tasks_v3.md（C1-C5 實作 + C6 單一收官 Checkout）；修改 TODO.md / INDEX.md / 本提示詞歸檔覆寫
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

本版（07:01）覆寫 06:48 初版同名草稿，修正 Checkout 時序為單一收官 C6（廢除提前搬 plan 的 C1 Checkout）。依據 API-PERF plan v2。
`````
