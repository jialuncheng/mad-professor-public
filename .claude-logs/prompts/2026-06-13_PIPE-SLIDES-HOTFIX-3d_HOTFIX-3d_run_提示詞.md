# PIPE-SLIDES-HOTFIX-3d HOTFIX-3d Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 06:31 |
| 任務代號 | PIPE-SLIDES-HOTFIX-3d HOTFIX-3d |
| 觸發 Commit | HOTFIX-3d |
| 依據 | .claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md（§3 修法 / §5 測試）|
| 觸發情境 | baron 確認 HOTFIX-3c 後，下達本次執行指令 |
| 工作流類別 | BE-Hotfix |

## 正文（原文）

執行單一 Commit HOTFIX-3d（BE-Hotfix）。

強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP。

註解包裹硬規則：`# === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d START/END] ===` + 注入點 `# === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d] ===`。

執行命令：依 hotfix.md §3，三防線——
1. 物理防線（§4 不可動）：只修渲染 body、嚴禁碰 ctx.rag_sections/merged/web_server/四路；保留圖片行與行內 URL。
2. 測試防線（§5）：grep + SOP 核查 + ≥8 pytest（行內粗體/CJK 緊貼/整行 ** 升標題/剝整行 URL/行內 URL 保留/圖片行保留/rag_sections 隔離/p27 端到端）；全套件綠。
3. 文件防線（CLAUDE §1.3）：commit/push baron 手動、嚴禁自發。

備份：cp slide_pipeline.py / test_slide_pipeline.py → .claude-logs/archive/2026-06-13_PIPE-SLIDES-HOTFIX-3d_*.bak

TODO：✅ 已完成區追加 HOTFIX-3d 表（hash 待回填）+ git log hash 自癒。

產出：執行報告 → baton/2026-06-13_PIPE-SLIDES-HOTFIX-3d_執行.md；hotfix 不設 Check、立即 mv 移出：hotfix.md→hotfixes/、執行.md→executions/。

§8 baron 執行命令：git add（slide_pipeline.py / test / 2 .bak / hotfix.md〔移出後〕/ 執行.md〔移出後〕）+ msg 寫 /tmp/PIPE-SLIDES-HOTFIX-3d_msg.txt（簽名 Fable 5）+ baron 手動 commit。

停止指令：產出報告 + TODO + baton 移出 + git add 後立即停止。嚴禁自發 commit/push。
