# WORKFLOW-4 Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 02:00 |
| 任務代號 | WORKFLOW-4 Check |
| 觸發 Commit | WORKFLOW-4-Check |
| 相關產出檔案 | plan / tasks / Tasks 報告 / C1-C4 執行報告（baton/）|
| 觸發情境 | 所有前置原子 Commit（C1-C3）已手動提交，baron 下達 C4 checkout 收官、歷史 Hash 自癒、全案移出 baton/ 歸檔 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、對 WORKFLOW-4 執行 5 維度 Conformance 驗收、全綠後執行 C4 checkout 收官。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / tasks（§6）/ 四份 _執行.md（Tasks/C1/C2/C3）
- **5 維度 Conformance**：① 目標規格（plan §2 U1-U6）② 驗收條件（tasks §6 grep，含 C1-C3）③ 不可動清單（tasks §7、pytest 旁證）④ 提示詞歸檔（`ls prompts/ | grep WORKFLOW-4`，plan/tasks/C1/C2/C3/Check 各階段 .md 實體）⑤ msg.txt 草稿完整性（各 §8）
- **C4 收官自動化**：① 新建 C4 報告（baton、template_execution、狀態 Completed (Commit C4)、§1 對齊欄標「對齊 U5」+ §自評三問〔推進 U5〕）② TODO 移除 WIP + 頂端新增完成表格〔Tasks/C1-C4〕+ git log 全量 hash 自癒補填 ③ INDEX 補登 Check + 連結指正式路徑 + 更新時間行 ④ mv baton 全檔（plan→plans/、tasks→tasks/、5 報告→executions/）+ git add ⑤ git add 相關提示詞（plan/Tasks/C1/C2/C3/Check）+ INDEX + TODO ⑥ ls baton 確認清空
- 停止：TODO + mv + git add 後立即停;嚴禁自發 commit/push、嚴禁改已 staged 歸檔檔

## 偏差註記
- plan/tasks 實際在 baton/（未移）→ §4 mv 來源 baton/ 正確;此前 C1/C2/C3 報告亦在 baton/。
- **SOP §4 已升級為 5 維度**（含維度四提示詞歸檔 + 維度五 msg 完整性）、與本提示詞表格一致。
