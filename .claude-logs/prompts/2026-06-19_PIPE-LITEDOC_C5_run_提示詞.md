# PIPE-LITEDOC C5 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 02:33 |
| 任務代號 | PIPE-LITEDOC C5 |
| 觸發 Commit | C5 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C5_執行.md` |
| 觸發情境 | baron 確認 C4 後、下達 C5 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C5（P3 size-gate 翻譯與 HTML 扉頁還原·含雙語標題鏈）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / **plan（全局策略 z·U5/U5b/U5c）** / tasks（§8 C5）/ logging SOP / database SOP
- 範圍：改 `pipelines/litedoc_pipeline.py`（實作 run_phase3）+ `tests/test_litedoc_pipeline.py`（追加 P3 測試）
- 實作（tasks §8 C5）：① InjectionContext(doc_type/domain_name/glossary/constraints) ② **size-gate**（`LITEDOC_WHOLE_TRANSLATE_THRESHOLD` 預設 15k；<15k 或無 section → `translate_whole`、≥15k → `restore_sections_markdown`）③ `is_heading_degraded` 退化 fallback ④ **U5c translated_title 三路**（is_zh→title / 分段→取頂層 title slot 譯後 / 一鍵→`translate_unit(title,…,"title")`）⑤ `render_meta_header_html`（呼叫端抽 authors/venue/date/doi/keywords + lang）prepend final_zh/en ⑥ `collect_rag_sections`/`single_container_sections` → ctx.rag_sections ⑦ zh* edge 不重譯 → BilingualMarkdownSpec（rag_tree_json=None）
- translated_title handoff：存 `ctx.raw_metadata["translated_title"]`（既有旁路、PIPE-SLIDES-HOTFIX-1b 三欄 dict 範式；不動 contracts/context）
- 包裹：`# === [PIPE-LITEDOC C5 START/END] ===`
- 備份：litedoc_pipeline.py + test .bak（本階段須 git add）
- 驗收：§6.5 grep + `pytest tests/test_litedoc_pipeline.py -k run_phase3 -v` + 全套件基線 + §6.9 SOP
- TODO：C5 ✅ / C6 🟡 + hash 自癒（無對應 commit 之佔位維持、不捏造）
- msg → `/tmp/PIPE-LITEDOC_C5_msg.txt`（**簽名校正 Opus 4.8 (1M context)**、非提示詞誤植之 Sonnet）
- 產出：`baton/..._C5_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 提示詞 msg 模板誤植「Claude Sonnet 4.6」→ 校正為 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- translated_title 經 ctx.raw_metadata 旁路傳 P4（既有旁路、不動凍結合約/context.py）。
