# PIPE-LITEDOC C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 01:15 |
| 任務代號 | PIPE-LITEDOC C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C1_執行.md` |
| 觸發情境 | baron 同意 tasks、下達 C1 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C1（section_engine HTML 扉頁 formatter·純加法首發隔離驗證）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U5b）** / tasks（§8 C1）/ logging SOP / database SOP
- 唯一允許改：`pipelines/section_engine.py`（**僅純加法 render_meta_header_html、嚴禁碰既有**）+ `tests/test_section_engine.py`（追加）
- 包裹：`# === [PIPE-LITEDOC C1 START/END] ===`
- 備份：section_engine.py + test_section_engine.py（.bak **本階段須 git add**）
- 實作（tasks §8 C1）：`render_meta_header_html(authors, venue, date, doi=None, keywords=None, *, is_zh=False)` 產 `<div class="paper-header-meta">`〔header-authors〔zh 、/en , 分隔〕/ header-venue-date〔· 分隔〕/ header-doi〔DOI: 〕/ header-keywords〔zh 關鍵字：/en Keywords: 〕〕**byte 對齊 A 軌 md_restore:460-490**、空欄略過、全空回 ''、Zero Schema Coupling
- 驗收：§6.1 grep + `pytest tests/test_section_engine.py tests/test_resume_pipeline.py -q` 既有 17+42 全綠（不碰既有）+ 全套件 657 基線 + §6.9 SOP
- TODO：C1 ✅ / C2 🟡 + hash 自癒
- msg → `/tmp/PIPE-LITEDOC_C1_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C1_執行.md`（template_execution、§1 對齊欄 + §自評、**嚴禁 git add baton**）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Co-Authored-By: Claude Sonnet 4.6」→ 依專案慣例 + 全域規則校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 動業務代碼僅 section_engine.py（plan/tasks 明指·純加法、CLAUDE.md §3 例外）。
