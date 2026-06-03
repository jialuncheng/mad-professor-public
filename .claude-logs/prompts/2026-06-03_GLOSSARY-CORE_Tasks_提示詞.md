`````markdown
# 2026-06-03 — GLOSSARY-CORE Tasks 提示詞

> **收到時間**：2026-06-03 19:30（UTC+8）
> **任務代號**：GLOSSARY-CORE Tasks
> **觸發 commit**：GLOSSARY-CORE-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md`
> **觸發情境**：baron 同意 GLOSSARY-CORE plan v2 規格後，下達 tasks 拆分指令——拆 Commit 清單（彈性數量 + 最後 Checkout 收官 Commit），中間 Commit 全留 baton/、唯 Checkout 一次性歸檔；對齊已完成之 DOMAIN-NORM（LCCCode 上游）/ PIPE-SPEC / PIPE master v10 / PIPE-CORE。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 19:30 |
| **任務代號** | GLOSSARY-CORE Tasks |
| **觸發 Commit** | GLOSSARY-CORE-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_GLOSSARY-CORE_Tasks_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，依指令將 plan 拆分為可執行 Commit 清單。
### 📋 任務資訊
- 任務編碼 GLOSSARY-CORE｜工作流 BE-Refactor
- Plan `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TODO / GLOSSARY-CORE plan_v2 / PIPE-SPEC / PIPE master v10 / PIPE-CORE plan_v2 / DOMAIN-NORM plan_v2 / template_tasks / template_execution
### 🏢 工作目錄硬規則
唯一合法 worktree；嚴禁讀寫主 repo；嚴禁改業務代碼（view/grep/文件編輯）；產出先放 baton/。
### 📊 成果盤點約束（§0.5 必置文件開頭）
（新增檔案 / 修改檔案 / 目錄初始化 / 狀態更新 / Commits / baton 歸檔）
### ⚙️ Commit 拆分與執行報告硬規則
1. 不用給 Commit 建議（回答與 tasks.md 內嚴禁 git commit 命令與 message）。
2. 必含 Checkout Commit（最後一個，唯此階段 mv baton→plans//tasks//executions/ + git add）。
3. 各實作/測試 Commit 必產執行報告（template_execution、暫存 baton/）。
4. 語意完整與可逆（每 Commit 獨立可測最小單元、可獨立 revert）。
### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填）
（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）
### 📝 §1 TL;DR 中文括號命名要求（每 Commit 引用含中文括號子標題）
### 🔄 同步更新 TODO.md（必做、即時）
於 ### 🔴 高優先 最前方新增 GLOSSARY-CORE 條目（依實際 Commit 數量）；依賴 DOMAIN-NORM (已完成)。
### 📁 產出規格
產出 baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md；套用 template_tasks.md；命名依 WORKFLOW_SOP §6。
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

依據 GLOSSARY-CORE plan v2。上游真理源 DomainNormalizer（DOMAIN-NORM 已收官、LCCCode 凍結）。Commit 執行階段由 baron 後續獨立提示詞觸發。
`````
