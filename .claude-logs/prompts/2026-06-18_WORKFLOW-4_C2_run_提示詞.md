# WORKFLOW-4 C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 01:48 |
| 任務代號 | WORKFLOW-4 C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_WORKFLOW-4_C2_執行.md` |
| 觸發情境 | baron 審 C1 報告並手動 commit 後下達 C2（Execution 側 Conditioning + 雙軸自評）|
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
執行單一 Commit C2（Execution 側 Conditioning + 雙軸自評）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C2）/ template_execution / template_prompt_for_run
- staging：只動模板、嚴禁業務代碼;baton 暫存（plan/tasks/C1/C2 報告）嚴禁 git add、C4 才歸檔（.bak 與模板除外）
- 實作：① 備份 2 模板 .bak（路徑 .claude-logs/templates/、入 C2 git add）② template_prompt_for_run「強制讀檔清單」在 tasks 上方加 `plan.md  # 全局策略 z（StraTA conditioning re-inject）`、`<!-- [WORKFLOW-4 C2 U1] -->` 包裹 ③ template_execution：§1 加「與全局策略對齊」欄（conditioned on plan §2 哪個 U-N）+ §6 後新增 `## §自評（策略對齊自我審查）` 三問（(a)越界? (b)無關/違規? (c)推進哪個 U-N?〔正向軸·做白工自 flag 清理〕）、`<!-- [WORKFLOW-4 C2 U2/U3] -->` 包裹
- 驗收：§6.2 grep + 零業務代碼 + pytest 基線
- 產出：C2 報告 baton（嚴禁 git add）;TODO C2 ✅ / C3 🟡 WIP + hash 自癒
- 停止：報告 + TODO 後立即停;嚴禁 C3/自發 commit/baton git add

## 偏差註記
- 提示詞 cp 路徑 `templates/` 為簡寫 → 實際 `.claude-logs/templates/`（C1 同樣校正過）
- INDEX 補「### WORKFLOW 系列」（既有 taxonomy、非新建 DOC-Refactor 系列）
