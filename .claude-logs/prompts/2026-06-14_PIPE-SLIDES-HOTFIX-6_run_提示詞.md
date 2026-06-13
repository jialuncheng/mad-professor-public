# PIPE-SLIDES-HOTFIX-6 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 07:35 |
| 任務代號 | PIPE-SLIDES-HOTFIX-6 |
| 觸發 Commit | HOTFIX-6 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_PIPE-SLIDES-HOTFIX-6_hotfix.md` |
| 觸發情境 | baron 確認 HOTFIX-5 後下達 HOTFIX-6 執行指令 |
| 工作流類別 | BE-Hotfix（+ DOC 回溯更正）|

## 正文（原文摘要）
執行單一 Commit HOTFIX-6（BE-Hotfix）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP
- Part A（程式）：`_strip_master_date` 注入單頁純日期清空（`# === [PIPE-SLIDES-HOTFIX-6 HOTFIX-6 START/END] ===`）+ 4 回歸測試
- Part B（文件）：8 份歷史 hotfix 文件 golden 誤述段前插「統一更正 banner」作廢 + TODO 舊完成表附註尾註
- 三防線：① 物理僅改 Part A/B 檔 ② 測試 grep+SOP+pytest 全綠 ③ commit/push baron 手動
- 備份：cp slide_pipeline.py → .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak
- TODO：✅ 追加 HOTFIX-6 表 + HOTFIX-1~5 golden 附註加「更正 HOTFIX-6」尾註 + git log hash 自癒
- 產出：執行報告 baton/..._執行.md;hotfix 不設 Check → mv（hotfix→hotfixes/、執行→executions/）
- 停止：報告 + TODO + baton 移出 + git add 後立即停;嚴禁自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 msg 草稿網域 `<noreply@anthreply.com>` 錯 → 更正 `<noreply@anthropic.com>`（型號 Opus 4.8 正確）
