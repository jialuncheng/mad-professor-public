# FE-RHYTHM-1 FE-RHYTHM-1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 19:18 |
| 任務代號 | FE-RHYTHM-1 |
| 觸發 Commit | FE-RHYTHM-1 |
| 依據 | .claude-logs/baton/2026-06-13_FE-RHYTHM-1_hotfix.md（§3 修法 / §5 測試）|
| 觸發情境 | baron 下達本次執行指令（HOTFIX-4 後） |
| 工作流類別 | FE-Hotfix |

## 正文（原文）

執行單一 Commit FE-RHYTHM-1（FE-Hotfix）。

強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md。

註解包裹硬規則：`/* === [FE-RHYTHM-1 FE-RHYTHM-1 START/END] === */`。

執行命令：依 hotfix.md §3，三防線——
1. 物理防線（§4 不可動）：僅在 static/index.html base CSS #paper-content 區新增 2 條 :has() 交界規則；嚴禁改 themes/*.css、後端、pipeline、RAG、chat 樣式。
2. 測試防線（§5）：grep（定義+包裹存在、themes 0 碰）+ 全套件 pytest 綠。
3. 文件防線（CLAUDE §1.3）：commit/push baron 手動、嚴禁自發。

備份：cp static/index.html → .claude-logs/archive/2026-06-13_FE-RHYTHM-1_FE-RHYTHM-1_index.html.bak

TODO：✅ 已完成區追加 FE-RHYTHM-1 表（hash 待回填）+ git log hash 自癒。

產出：執行報告 → baton/2026-06-13_FE-RHYTHM-1_執行.md；hotfix 不設 Check、立即 mv 移出：hotfix.md→hotfixes/、執行.md→executions/。

§8 baron 執行命令：git add（index.html / .bak / hotfix.md〔移出後〕/ 執行.md〔移出後〕/ run 提示詞 / TODO / INDEX）+ msg 寫 /tmp/FE-RHYTHM-1_msg.txt（簽名 Fable 5、anthropic.com）+ baron 手動 commit。

停止指令：產出報告 + TODO + baton 移出 + git add 後立即停止。嚴禁自發 commit/push。
