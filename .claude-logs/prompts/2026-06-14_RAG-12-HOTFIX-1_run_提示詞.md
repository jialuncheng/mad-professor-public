# RAG-12-HOTFIX-1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 05:59 |
| 任務代號 | RAG-12-HOTFIX-1 |
| 觸發 Commit | RAG-12-HOTFIX-1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_RAG-12-HOTFIX-1_hotfix.md` |
| 觸發情境 | baron 確認後下達 RAG-12-HOTFIX-1 執行指令 |
| 工作流類別 | FE-Hotfix |

## 正文（原文摘要）
執行單一 Commit RAG-12-HOTFIX-1（FE-Hotfix）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / hotfix.md（§3 修法 / §5 測試）
- 註解包裹：`// === [RAG-12-HOTFIX-1 START/END] ===` / 注入點 `// === [RAG-12-HOTFIX-1] ===`
- 三防線：① 物理——僅改 static/index.html renderMarkdownWithMath、嚴禁後端/.py/管線/RAG ② 測試——grep（包裹+imgBlocks）+ 全套件 pytest 綠 ③ 文件——commit/push baron 手動
- 備份：cp index.html → .claude-logs/archive/2026-06-14_RAG-12-HOTFIX-1_index.html.bak
- TODO：✅ 已完成追加 RAG-12-HOTFIX-1 表 + git log hash 自癒
- 產出：執行報告 baton/..._執行.md;hotfix 不設 Check → 立即 mv（hotfix.md→hotfixes/、執行.md→executions/）
- §8 baron 命令：git add（index.html/.bak/hotfix〔移出後〕/執行〔移出後〕/run 提示詞）+ msg→tmp/ + baron 手動 commit
- 停止：報告 + TODO + baton 移出 + git add 後立即停;嚴禁自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 msg 草稿網域 `<noreply@anthreply.com>` 錯 → 更正 `<noreply@anthropic.com>`（型號 Opus 4.8 正確）
