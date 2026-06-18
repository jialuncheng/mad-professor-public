# PIPE-SECTION-BASE C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 07:03 |
| 任務代號 | PIPE-SECTION-BASE C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C1_執行.md` |
| 觸發情境 | baron 同意 tasks 規格、下達 C1 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C1（section_engine 骨架 + 摘要簇）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / **plan（全局策略 z·U1 conditioning re-inject）** / tasks（§8 C1）/ database SOP / logging SOP
- 三防線：物理（§7 不可動）/ 測試（§6 grep + pytest）/ 文件（不自發 commit）
- 包裹要求：既有原始碼改動用 `# === [PIPE-SECTION-BASE C1 START/END] ===`
- 備份：`cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C1_resume_pipeline.py.bak`
- 實作（tasks §8 C1）：① 新建 `pipelines/section_engine.py`（marker + docstring）② 摘要簇 `_collect_summary_targets`/`_node_content_text`/`_build_section_summaries`/`_generate_section_summaries`/`_translate_section_summaries`/`_parse_indexed` 原值搬入為 module-level 純函式、llm 參數注入、collect 可吃任意子樹（U3.2）③ resume 對應 method 改 delegate ④ resume import section_engine ⑤ key=原文標題 path 保留 ⑥ §6.1 grep + `pytest tests/test_resume_pipeline.py` 全綠（行為等價）⑦ §6.6 SOP grep
- TODO：C1 ✅ / C2 🟡 WIP + hash 自癒
- 產出：`baton/..._C1_執行.md`（套 template_execution、含 §1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 本 Commit 首次動業務代碼——但 `section_engine.py` + `resume_pipeline.py` 為 plan/tasks 明指、屬 CLAUDE.md §3 例外（plan 內指明修改之 pipelines）。
