# WORKFLOW-4 C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 01:35 |
| 任務代號 | WORKFLOW-4 C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_WORKFLOW-4_C1_執行.md` |
| 觸發情境 | baron 審 tasks 合規後下達 C1（Plan 側候選方案 + stale 校正）|
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
執行單一 Commit C1（Plan 側 Diverse Rollout）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C1）/ template_execution
- 工作目錄/staging：只動模板、嚴禁業務代碼;baton 暫存檔（plan/tasks/C1 報告）**嚴禁 git add**、C4 才歸檔（.bak 與模板變更除外）
- 實作：① 備份 2 模板 .bak（入 C1 git add）② template_plan §2 後插選用 §2.5 候選方案〔高風險才列 ≥2 語意分散方案+trade-offs+選定理由+否決留痕;低風險寫單案〕、`<!-- [WORKFLOW-4 C1 U4] -->` 包裹 ③ template_prompt_for_plan 撰寫原則加多候選條 + Q5 校正「套用模板結構」表對齊 template_plan 實際章（§4 跨Phase/§5 風險/§6 不可動/§7 規格依據/§8 驗證/§9 OQ + 新 §2.5）、`<!-- [WORKFLOW-4 C1 U4/Q5] -->` 包裹
- 驗收：§6.1 grep + 零業務代碼 + pytest 基線
- 產出：C1 執行報告 baton（嚴禁 git add）;TODO C1 ✅ / C2 🟡 WIP + hash 自癒
- 停止：報告 + TODO 後立即停;嚴禁 C2/自發 commit/baton git add

## 偏差註記
- 提示詞要求 INDEX 補「### DOC-Refactor 系列」;既有 taxonomy 為「### WORKFLOW 系列」→ 沿用 WORKFLOW 系列（WORKFLOW-1/2/3 脈絡一致）
