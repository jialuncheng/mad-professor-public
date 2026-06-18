# PIPE-LITEDOC C8 Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:59 |
| 任務代號 | PIPE-LITEDOC Check |
| 觸發 Commit | C8 |
| 相關產出檔案 | C1-C7 執行報告（baton/）|
| 觸發情境 | C1-C7 ship 完畢、baron 下達 Conformance 驗收 + C8 收官歸檔 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、對 PIPE-LITEDOC 執行 5 維度 Conformance 驗收、全綠後 C8 Checkout 收官。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / TODO / plan / tasks / C1-C7 執行報告
- **5 維度 Conformance**：① 目標規格（plan §2 U1-U9 + U2.1/U5b/U5c 跨 C1-C7 全覆蓋）② 驗收條件（tasks §6 grep+pytest 686）③ 不可動清單（§7、各報告 §6）④ 提示詞歸檔（plan/Tasks/C1-C7/Check）⑤ msg §8;聚焦 U-coverage + §7.2 整合（C7 正面通過、key=原文標題 path + translated_title 三分流）
- **C8 收官**：① TODO 移除 WIP + 頂端完成表〔C1-C8、hash 自癒回填 C2-C7;5 處未 commit 佔位維持不捏造〕+ 索引 ✅ ② baton 一次性 mv（plan→plans/、tasks→tasks/、C1-C8 報告→executions/）+ git add ③ git add prompts/*PIPE-LITEDOC* + INDEX ④ ls baton 確認清空
- §7.2 不豁免、達標（C7 key-changing 整合）
- 停止：TODO + mv + git add 後立即停;嚴禁自發 commit/push、嚴禁改已歸檔報告

## 偏差註記
- msg 模板誤植「Claude Sonnet 4.6」→ 校正 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- C1 已 commit b1012bc;C2-C7 git log 自癒回填;5 處歷史佔位（PIPE-SECTION-BASE C5/PIPE-SYNC-3 C3 已回填 f9c261b/RESUME-PERF C3/MODEL-9-OPT C4 等）依現況。
