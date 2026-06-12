# PIPE-SLIDES-HOTFIX-3c HOTFIX-3c Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 06:28 |
| 任務代號 | PIPE-SLIDES-HOTFIX-3c HOTFIX-3c |
| 觸發 Commit | HOTFIX-3c |
| 依據 | .claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md（§3 修法 / §5 測試）|
| 觸發情境 | baron 確認 HOTFIX-3b 後，下達本次執行指令 |
| 工作流類別 | BE-Hotfix |

## 正文（原文）

執行單一 Commit HOTFIX-3c（BE-Hotfix）。

強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP。

註解包裹硬規則：`# === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c START/END] ===` + 注入點 `# === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c] ===`。

執行命令：依 hotfix.md §3，三防線——
1. 物理防線（§4 不可動）：只修渲染 body、嚴禁碰 ctx.rag_sections/merged/web_server/其餘四路。
2. 測試防線（§5）：grep + SOP 一致性核查 + ≥6 pytest（箭頭硬換行群/行中不碰/孤行不變/loose 收緊/邊界留白/CRLF/RAG 隔離/頁 B 端到端）；全套件綠。
3. 文件防線（CLAUDE §1.3）：commit/push baron 手動、嚴禁自發。

備份：cp slide_pipeline.py / test_slide_pipeline.py → .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3c_*.bak

TODO：✅ 已完成區追加 HOTFIX-3c 表（hash 待回填）+ git log hash 自癒。

產出：執行報告 → baton/2026-06-13_PIPE-SLIDES-HOTFIX-3c_執行.md；hotfix 不設 Check、立即 mv 移出：hotfix.md→hotfixes/、執行.md→executions/。

§8 baron 執行命令：git add（slide_pipeline.py / test / 2 .bak / hotfix.md〔移出後〕/ 執行.md〔移出後〕）+ msg 寫 /tmp/PIPE-SLIDES-HOTFIX-3c_msg.txt（簽名 Fable 5）+ baron 手動 commit。

停止指令：產出報告 + TODO + baton 移出 + git add 後立即停止。嚴禁自發 commit/push。
