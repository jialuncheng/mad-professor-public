# FE-RHYTHM-UNIFY Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 02:21 |
| 任務代號 | FE-RHYTHM-UNIFY Check |
| 觸發 Commit | FE-RHYTHM-UNIFY-Check |
| 相關產出檔案 | C1/C2 執行報告 + 待產 C3 報告 |
| 觸發情境 | 所有 Commit ship 完畢，baron 下達 Conformance 驗收指令 |
| 工作流類別 | FE-Refactor |

## 正文（原文摘要）
對 FE-RHYTHM-UNIFY 執行 Conformance 驗收 + 收官歸檔。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / tasks / C1 / C2 執行報告
- Conformance 五維度：① 目標規格（plan §2 U1-U10）② 驗收條件（tasks §6 grep/pytest）③ 不可動清單（tasks §7）④ 提示詞歸檔稽核（plan/tasks/run/check 實體存在、缺則補建）⑤ msg.txt 草稿完整性
- C3 執行報告（template_execution）：§1-§8，§4 嵌 Conformance 表、§5 git status -s、§7 baton 清空至 README、§8 msg 草稿
- 收官：TODO 移完成表 + 移除 WIP + 索引 + hash 全量自癒；baton mv（plan→plans/、tasks→tasks/、C1-C3 報告→executions/）+ git add；確認 baton 只剩 README.md；INDEX 確認
- 停止：TODO + baton 歸檔後立即停；嚴禁自發 commit/push、嚴禁改已歸檔文件

## 偏差註記（Claude Code）
- 提示詞 §2 C3 msg 草稿簽名為 `Claude Sonnet 4.6 <noreply@anthreply.com>`（型號+網域皆誤）→ C3 報告/草稿更正為當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- baton README.md 規則：依母 plan 慣例，baton 尚有其他在途任務文件（QUEUE-1/INFRA-2/CHAT-STRUCT-1/PIPE-SPEC 等），收官僅 mv 本任務（FE-RHYTHM-UNIFY）文件、不動他人；「只剩 README」應理解為「本任務文件已淨空」
