# PIPE-LITEDOC C7 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:49 |
| 任務代號 | PIPE-LITEDOC C7 |
| 觸發 Commit | C7 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C7_執行.md` |
| 觸發情境 | baron 確認 C6 後、下達 C7 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C7（單元與接縫整合測試·雙鎖）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U8）** / tasks（§8 C7）/ logging SOP / database SOP
- 範圍：僅改 `tests/test_litedoc_pipeline.py`（補強 + **§7.2 P2→P3→P4 key-changing 整合測試**）
- 實作（tasks §8 C7）：① 分派四路〔litedoc/news/web/unknown→fallback〕已有 ② P1-P4 契約已隨各 commit ③ **§7.2 整合**：FakeTranslator 真改 title、斷言 P2 section_summaries key 與 P3 rag_sections summary_key 譯後仍同取「原文標題 path」不變〔鎖 RAG-ASYNC-HOTFIX-1 接縫不變式〕、同時驗 size-gate 兩路 translated_title 正確
- 包裹：`# === [PIPE-LITEDOC C7 START/END] ===`
- 備份：test .bak（本階段須 git add）
- 驗收：`pytest tests/test_litedoc_pipeline.py -v` + 全套件 `pytest tests/ -q` 全綠 + §6.9 SOP
- TODO：C7 ✅ / C8 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C7_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C7_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- C7 純測試、零業務代碼改動（不可動清單天然守住）。
