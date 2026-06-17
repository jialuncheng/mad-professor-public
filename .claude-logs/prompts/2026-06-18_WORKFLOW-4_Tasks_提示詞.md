# WORKFLOW-4 Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 01:25 |
| 任務代號 | WORKFLOW-4 Tasks |
| 觸發 Commit | WORKFLOW-4-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_WORKFLOW-4_StraTA原理移植文件治理模板_tasks.md` |
| 觸發情境 | baron 拍板 WORKFLOW-4 plan v2（六 OQ 全定案），下達拆 commit + TODO 登記 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
依 plan v2 自主拆 commit 產 tasks。
- 任務 WORKFLOW-4 / DOC-Refactor / plan：baton/2026-06-14_WORKFLOW-4_..._plan_v1.md（v2）
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / framework / plan / template_tasks / template_execution
- 工作目錄硬規則：只動模板文件、嚴禁業務代碼(.py/.html/.css/.js)、產出留 baton/
- 執行報告硬規則：每 C-N 產 _執行.md 暫存 baton；唯最後 checkout 才一次性 mv 歸檔 + git add；前面階段嚴禁 mv/git add baton 檔
- §0.5 成果盤點 + §1 中文括號命名 + §8 六維度表（含 .bak）
- 自主拆分（不給建議）、Bootstrap First、最後 commit 必為 checkout
- 同步更新 TODO（高優先區最前、🟡 WIP）
- 產出 tasks + TODO 後立即停；嚴禁產執行.md/動代碼/提前 mv/commit/push

## 拆分要點（依 plan §2 U1-U6）
- 5 模板輕量加法：prompt_for_run(U1 讀 plan)/execution(U2 對齊欄+U3 雙軸自評)/plan(U4 §2.5 候選)/prompt_for_plan(U4+Q5 stale 校正)/prompt_for_check(U5 減負前移)
- 依賴：U5(check)依 U3(自評)先定義 → check commit 在 execution commit 後
- 六階段骨架不動、不重寫 Conformance 維度定義、StraTA 原理非演算法
