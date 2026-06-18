# PIPE-LITEDOC C6 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:42 |
| 任務代號 | PIPE-LITEDOC C6 |
| 觸發 Commit | C6 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C6_執行.md` |
| 觸發情境 | baron 確認 C5 後、下達 C6 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C6（P4 Async RAG·rag_indexer ≥10 + 雙語標題）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U6）** / tasks（§8 C6）/ logging SOP / database SOP
- 範圍：改 `pipelines/litedoc_pipeline.py`（實作 run_phase4）+ `tests/test_litedoc_pipeline.py`（追加 P4 測試、驗 rag_indexer.index 傳 'litedoc'、門檻 else ≥10、rag_indexer 未改）
- 實作（tasks §8 C6）：取 paper_db_id（paper_manager、try/except 降級 None）；呼 `rag_indexer.index(ctx.rag_sections, ctx.glossary_ready.section_summaries, 'litedoc', vectors_dir, paper_db_id, rag_tree_path, title=原文標題, translated_title=讀 ctx.raw_metadata["translated_title"]["value"])`；門檻走 is_chunk_meaningful 預設 ≥10（litedoc 不入 ≥3 tuple、rag_indexer 零改）；四產物；異常拋出 Orchestrator 標 rag_status='failed' 不阻 reading_ready → RagDbSpec
- 包裹：`# === [PIPE-LITEDOC C6 START/END] ===`
- 備份：litedoc_pipeline.py + test .bak（本階段須 git add）
- 驗收：§6.6 grep + `pytest tests/test_litedoc_pipeline.py -k run_phase4 -v` + 全套件基線 + §6.9 SOP + `grep litedoc rag_indexer.py`=0（引擎未改）
- TODO：C6 ✅ / C7 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C6_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C6_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- rag_indexer 零改（litedoc 走 else 預設 ≥10、不動 :69 tuple）。
