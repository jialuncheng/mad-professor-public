# PIPE-SLIDES-HOTFIX-4 HOTFIX-4 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 19:10 |
| 任務代號 | PIPE-SLIDES-HOTFIX-4 HOTFIX-4 |
| 觸發 Commit | HOTFIX-4 |
| 依據 | .claude-logs/baton/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md（§3 修法 / §5 測試）|
| 觸發情境 | baron 確認 HOTFIX-3d 後，下達本次執行指令 |
| 工作流類別 | BE-Hotfix |

## 正文（原文）

執行單一 Commit HOTFIX-4（BE-Hotfix）。

強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP。

註解包裹硬規則：`# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4 START/END] ===` + 注入點 `# === [PIPE-SLIDES-HOTFIX-4 HOTFIX-4] ===`。

執行命令：依 hotfix.md §3，三防線——
1. 物理防線（§4 不可動）：僅在 P1 _process ④ 區塊注入 is_blank 過濾 + 雙保險；不碰 ctx.rag_sections/merged/web_server/四路；is_cover/封面不動。
2. 測試防線（§5）：grep + SOP 核查 + ≥4 pytest（空白跳過/雙保險保留有內容/純圖頁保留/舊無欄相容）；全套件綠。
3. 文件防線（CLAUDE §1.3）：commit/push baron 手動、嚴禁自發。

備份：cp slide_pipeline.py / test_slide_pipeline.py → .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-4_*.bak

TODO：✅ 已完成區追加 HOTFIX-4 表（hash 待回填）+ git log hash 自癒。

產出：執行報告 → baton/2026-06-13_PIPE-SLIDES-HOTFIX-4_執行.md；hotfix 不設 Check、立即 mv 移出：hotfix.md→hotfixes/、執行.md→executions/。

§8 baron 執行命令：git add（slide_pipeline.py / test / 2 .bak / hotfix.md〔移出後〕/ 執行.md〔移出後〕/ run 提示詞）+ msg 寫 /tmp/PIPE-SLIDES-HOTFIX-4_msg.txt（簽名 Fable 5、anthropic.com）+ baron 手動 commit。

停止指令：產出報告 + TODO + baton 移出 + git add 後立即停止。嚴禁自發 commit/push。
