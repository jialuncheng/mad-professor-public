`````markdown
# 2026-06-03 — DOMAIN-NORM Tasks 提示詞

> **收到時間**：2026-06-03 17:34（UTC+8）
> **任務代號**：DOMAIN-NORM Tasks
> **觸發 commit**：DOMAIN-NORM-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md
> **觸發情境**：baron 同意 DOMAIN-NORM plan v2 規格（動態 LCC 生成 + Domains/DomainMapping 表 + context_text）後下達 tasks 拆分指令——拆 Commit 清單（彈性數量 + 最後 Check/Checkout 驗收 Commit），中間 Commit 全留 baton/、唯 Check 一次性歸檔；對齊已同步之 PIPE master v10 / PIPE-SPEC v2。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | 2026-06-03 17:34                                             |
| **任務代號**     | DOMAIN-NORM Tasks                                            |
| **觸發 Commit**  | DOMAIN-NORM-Tasks                                            |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` |
| **觸發情境**     | baron 同意 plan 規格，下達任務拆分指令                       |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_Tasks_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。
### 📋 任務資訊
- **任務編碼**：`DOMAIN-NORM` ｜ **工作流類別**：`BE-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / DOMAIN-NORM plan_v2 / PIPE master v10 / PIPE-SPEC / PIPE-CORE plan_v2 / template_tasks / template_execution
### 🏢 工作目錄硬規則
- 唯一合法工作目錄 worktree；嚴禁讀寫主 repo；嚴禁改業務代碼（除計畫規定的附加式代碼與兩張新表外）；產出先放 baton/。
### 📊 成果盤點約束（§0.5 必置文件開頭）
（新增檔案 / 修改檔案 / 目錄初始化 / 狀態更新 / Commits / baton 歸檔）
### ⚙️ Commit 拆分原則
- 彈性規劃（數量無固定上限）；每個中間 Commit 為獨立可測最小單元。
- 每個中間 Commit 必須撰寫對應執行報告（template_execution、暫存 baton/）。
- 最後必須含一個獨立 `Check`/`Checkout` 驗收 Commit（Conformance + baton 歸檔）。
- 歸檔時機：中間階段 plan/tasks/執行報告原封不動留 baton/、嚴禁提前 mv/git add；唯最後 Check 一次性 mv 至正式目錄 + git add。
### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）
（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）
### 📝 §1 TL;DR 中文括號命名要求（每個 Commit 引用含中文括號子標題）
### 🔄 同步更新 TODO.md（必做、即時）
於 TODO.md ### 🔴 高優先 最前方新增 DOMAIN-NORM 條目（依實際 Commit 數量）。
### 📦 歸檔計畫與執行報告（Checkout 驗收階段執行）
plan 留 baton/、tasks 產出後嚴禁立即移動；唯最後 Check 一次性 mv plan→plans/、tasks→tasks/、執行報告→executions/ + git add。
### 📁 產出規格
產出路徑 baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md；套用 template_tasks.md；命名依 WORKFLOW_SOP §6。
---
### 🛑 停止指令
產出 tasks.md 並更新 TODO.md 後立即停止。嚴禁續產 _執行.md / 動業務代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：N/A（tasks 拆分階段、無代碼變動）
- 改動檔案數：新增 tasks.md + 提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 DOMAIN-NORM plan v2（已確認可行 + PIPE master v10 / PIPE-SPEC 已同步）。Commit 執行階段由 baron 後續獨立提示詞觸發。
`````
