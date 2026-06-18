# PIPE-LITEDOC C4 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:25 |
| 任務代號 | PIPE-LITEDOC C4 |
| 觸發 Commit | C4 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C4_執行.md` |
| 觸發情境 | baron 確認 C3 後、下達 C4 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C4（P2 六步·消費 section_engine + 三真理源）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U4）** / tasks（§8 C4）/ logging SOP / database SOP
- 範圍：改 `pipelines/litedoc_pipeline.py`（實作 run_phase2）+ `tests/test_litedoc_pipeline.py`（追加 P2 契約測試、斷言 section_summaries key=原文標題 path）
- 實作（tasks §8 C4）：①全文摘要 ②`normalize_to_lcc(raw_domain, context=abstract)` ③`GlossaryManager` 級聯自癒〔旗標、交易外、try/except 降級〕④`Translator(DEEP_THINK)` 譯摘要 + `lcc→Domains.name`→domain_name ⑤`section_engine.build_section_summaries`〔key=原文標題 path、llm/prompt/model 注入〕→ GlossaryReadySpec
- 包裹：`# === [PIPE-LITEDOC C4 START/END] ===`
- 備份：litedoc_pipeline.py + test .bak（本階段須 git add）
- 驗收：§6.4 grep + `pytest tests/test_litedoc_pipeline.py -k run_phase2 -v` + 全套件基線 + §6.9 SOP（logger.error 須 exc_info、無裸 commit、LLM 交易外）
- TODO：C4 ✅ / C5 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C4_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C4_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 動業務代碼僅 litedoc_pipeline.py（plan/tasks 明指、CLAUDE.md §3 例外）。
