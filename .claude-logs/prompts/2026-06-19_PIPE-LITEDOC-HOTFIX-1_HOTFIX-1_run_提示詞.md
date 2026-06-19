# PIPE-LITEDOC-HOTFIX-1 HOTFIX-1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 17:40 |
| 任務代號 | PIPE-LITEDOC-HOTFIX-1 HOTFIX-1 |
| 觸發 Commit | HOTFIX-1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_執行.md` |
| 觸發情境 | baron 確認 hotfix 規劃、下達執行指令 |
| 工作流類別 | BE-Hotfix |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit HOTFIX-1（litedoc 雙缺陷落地）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / hotfix doc / logging_SOP / database_SOP
- 三防線：物理（只動 `litedoc_pipeline.py` + `section_engine.py` + 測試、其他不可動）/ 測試（補單測 detect_zh_tw/classify_source_lang/sample_body_text/strip_title_echo + P3 dual-strip、pytest 全綠）/ 文件（不自發 commit）
- 備份：兩受災檔 → `.claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_HOTFIX-1_*.py.bak`
- 實作（hotfix doc 修法）：F1 section_engine 新增 detect_zh_tw/classify_source_lang/sample_body_text/strip_title_echo 純函式 / F2 P1 改用 classify_source_lang（取內文樣本、簡體不給 zh*）/ F3 P3 雙剝（① pre-strip full_text + ② post-strip zh_text）
- TODO：新增 PIPE-LITEDOC-HOTFIX-1 → ✅、頂部完成表 + hash 自癒
- 產出：`baton/..._HOTFIX-1_執行.md`（template_execution、§1 對齊 + §自評 + §5.3 SOP grep）
- 收官（單 commit 即結案）：mv hotfix doc→hotfixes/、執行報告→executions/、提示詞 git add、msg→`/tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt`
- 停止：報告 + 收官移動後立即停、待 baron commit + hash 回填

## 偏差註記
- msg 草稿補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 單一 Commit hotfix：Run 即收官（同 RAG-ASYNC-HOTFIX 先例、baton 一次性歸檔）。
