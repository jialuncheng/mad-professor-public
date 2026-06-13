# PIPE-SLIDES-HOTFIX-5 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 06:04 |
| 任務代號 | PIPE-SLIDES-HOTFIX-5 |
| 觸發 Commit | HOTFIX-5 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md` |
| 觸發情境 | baron 確認 RAG-12-HOTFIX-1 後下達 PIPE-SLIDES-HOTFIX-5 執行指令 |
| 工作流類別 | BE-Hotfix |

## 正文（原文摘要）
執行單一 Commit PIPE-SLIDES-HOTFIX-5（BE-Hotfix）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md（§3 修法 / §5 測試）/ logging_SOP / database_SOP
- 註解包裹：`# === [PIPE-SLIDES-HOTFIX-5 HOTFIX-5 START/END] ===`；prompt 於既有 HOTFIX-4 包裹內改第 5 條
- 三防線：① 物理——僅 P1 _process ④ is_blank 過濾邏輯放寬 + prompt 第5條釐清；RAG 隔離（ctx.rag_sections/merged 不碰）、不碰 web_server/四路、保留三欄全空後盾 ② 測試——grep + SOP §5 核查 + ≥5 新 pytest（過場跳/裝飾跳/真圖保留/有正文保留/舊無欄相容）+ 全套件綠 ③ 文件——commit/push baron 手動
- 備份：cp slide_pipeline.py → .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak
- TODO：✅ 已完成追加 HOTFIX-5 表 + git log hash 自癒
- 產出：執行報告 baton/..._執行.md;hotfix 不設 Check → 立即 mv（hotfix→hotfixes/、執行→executions/）
- §8 baron 命令：git add + msg→tmp/ + baron 手動 commit
- 停止：報告 + TODO + baton 移出 + git add 後立即停;嚴禁自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 msg 草稿網域 `<noreply@anthreply.com>` 錯 → 更正 `<noreply@anthropic.com>`（型號 Opus 4.8 正確）
