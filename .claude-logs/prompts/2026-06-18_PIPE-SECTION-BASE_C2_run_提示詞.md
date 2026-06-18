# PIPE-SECTION-BASE C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 13:11 |
| 任務代號 | PIPE-SECTION-BASE C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C2_執行.md` |
| 觸發情境 | baron 驗收 C1 報告後、下達 C2 執行指令 |
| 工作流類別 | BE-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C2（翻譯與排版還原機制）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / **plan（全局策略 z·U1 re-inject）** / tasks（§8 C2）/ database SOP / logging SOP
- 三防線：物理（§7 不可動）/ 測試（§6.2 grep + pytest 行為等價）/ 文件（不自發 commit）
- 包裹：`# === [PIPE-SECTION-BASE C2 START/END] ===`
- 備份：`cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C2_resume_pipeline.py.bak`
- 實作（tasks §8 C2）：render/restore 簇 `_collect_render_slots`/`_restore_sections_markdown`/`_translate_whole`/`_t`/`_normalize_paragraph_breaks`/`_is_heading_degraded`/`_flatten_sections`/`_own_text_len` 原值搬入 section_engine（Translator/InjectionContext/ThreadPoolExecutor/LLM_MAX_CONCURRENT/_api_semaphore 限流 + 單 unit 失敗退原文異常隔離原樣·RESUME-PERF-1;level=min(2+depth,6) HEADING-HOTFIX-1 保留;translator/inj 注入）;resume 改 delegate
- 驗收：§6.2 grep + `pytest tests/test_resume_pipeline.py` 全綠（行為等價、final byte 等價）+ §6.6 SOP
- TODO：C2 ✅ / C3 🟡 WIP + hash 自癒
- 產出：`baton/..._C2_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 代碼 / 自發 commit

## 偏差註記
- 動業務代碼僅 `section_engine.py` + `resume_pipeline.py`（plan/tasks 明指、CLAUDE.md §3 例外）。
