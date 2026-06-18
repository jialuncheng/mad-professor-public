# PIPE-LITEDOC C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:08 |
| 任務代號 | PIPE-LITEDOC C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C2_執行.md` |
| 觸發情境 | baron 確認 C1 後、下達 C2 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C2（LiteDoc 骨架與三 key 註冊·策略分派）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U1）** / tasks（§8 C2）/ logging SOP / database SOP
- 範圍：新建 `pipelines/litedoc_pipeline.py`（`@register('litedoc'/'news'/'web')` 三裝飾器疊加 + 四 run_phase strict stub NotImplementedError + rag_char_threshold）+ 新建 `tests/test_litedoc_pipeline.py`（分派測試 litedoc/news/web/unknown→fallback）+ 改 `pipelines/__init__.py`（僅註冊 import、`# === [PIPE-LITEDOC C2 START/END] ===` 包裹）
- 嚴禁：其餘代碼/合約
- 備份：`__init__.py` .bak（本階段須 git add）
- 驗收：§6.2 grep + `pytest tests/test_litedoc_pipeline.py -q` + 全套件基線 + §6.9 SOP
- TODO：C2 ✅ / C3 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C2_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C2_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 動業務代碼僅 litedoc_pipeline.py（新）+ __init__.py（plan/tasks 明指、CLAUDE.md §3 例外）。
