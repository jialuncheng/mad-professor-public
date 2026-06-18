# PIPE-LITEDOC C3 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:15 |
| 任務代號 | PIPE-LITEDOC C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C3_執行.md` |
| 觸發情境 | baron 確認 C2 後、下達 C3 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C3（P1 MinerU 攝入與 metadata 旁路·DocAnalyzer 映射 + URL publisher 解碼）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U2/U3）** / tasks（§8 C3）/ logging SOP / database SOP
- 範圍：改 `pipelines/litedoc_pipeline.py`（實作 run_phase1）+ `tests/test_litedoc_pipeline.py`（追加 P1 契約測試）
- 實作（tasks §8 C3）：① MinerU(PDFProcessor) parse → **強制 md_cleaner** ② `DocAnalyzer().analyze(md, analyzer_doc_type)`·**U2.1 映射** `doc_type if doc_type in ('news','web') else 'web'`〔防 fallback academic、soft-fail〕③ md2json/json_process/tiling 產 tiles ④ 文字 LLM metadata〔title/authors/date/publisher/url + **URL→publisher 解碼**〕⑤ venue 承接 publisher 回填、date/url/organization 經 `meta_normalizer.normalize_fields` 寫 `ctx.raw_metadata` 旁路 ⑥ source_lang 啟發式、_shadow title 綴(測試) ⑦ → IngestionMetadataSpec
- 包裹：`# === [PIPE-LITEDOC C3 START/END] ===`
- 備份：litedoc_pipeline.py + test .bak（本階段須 git add）
- 驗收：§6.3 grep + `pytest tests/test_litedoc_pipeline.py -k run_phase1 -v` + 全套件基線 + §6.9 SOP（logger.error 須 exc_info、無裸 commit）
- TODO：C3 ✅ / C4 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C3_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C3_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 動業務代碼僅 litedoc_pipeline.py（plan/tasks 明指、CLAUDE.md §3 例外）。
