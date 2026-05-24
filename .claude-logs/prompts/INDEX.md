# 提示詞資料庫索引

最後更新：2026-05-24（BUG-F1 落地）

> 本檔案在每次新增提示詞時必須同步更新。
> 簡化規則：「依時間排序」僅保留最新 15 筆;超過則僅在「依任務分類」內保留。

## 依任務分類

### 一般 / 工具
- `2026-05-23_general_建立提示詞資料庫.md` — 建立 prompts/ 資料庫骨架 + 規範

### RAG 系列
- `2026-05-23_RAG-10_中文Header軟換行bug寫入TODO.md` — 中文 Header meta block 軟換行渲染 bug（候選）
- `2026-05-23_RAG-1_可行性評估+資料夾自動標籤.md` — RAG-1 前端 UI Fixes 可行性評估 + 資料夾自動標籤新需求整合
- `2026-05-23_RAG-1_標籤強制小寫+TODO+認證.md` — RAG-1 v3 強化（全域 lowercase + 4 點深度評估認證 + TODO 條目）
- `2026-05-23_RAG-1_R1_提示詞.md` — R1 落地（UI Fixes 子項 A/C/F/G 部分 + set_paper_tags + Modal 主題）
- `2026-05-23_RAG-1_R2_提示詞.md` — R2 落地（theme upload + # 標籤 Modal + tag-pill + v3 全域 lowercase + design 回寫）
- `2026-05-23_RAG-1_R3_提示詞.md` — R3 落地（資料夾自動標籤、RAG-1 完工）
- `2026-05-23_RAG-1_Phase2_plan提示詞.md` — Phase 2 plan（Hashtag Backend + 前端 chat hint + hashtag token UI）
- `2026-05-23_RAG-1_P2-1_提示詞.md` — Phase 2 P2-1 落地（雙語摘要管道：_ALL_FIELDS + _stage_translate 寫入 + 3 pytest）
- `2026-05-23_RAG-1_P2-2_提示詞.md` — Phase 2 P2-2 落地（後端 hashtag RAG 路由：list_paper_uuids_by_tag + parse_query_hashtag + retrieve_multi_with_context + process_query_stream 入口分流 + 14 pytest）
- `2026-05-23_RAG-1_P2-3_提示詞.md` — Phase 2 P2-3 落地（前端 chat hashtag token UI：contenteditable div + autocomplete + token + §3.3.5 4 點防護 + components.md §11.2 + 9 pytest）
- `2026-05-24_BUG-F1_提示詞.md` — BUG-F1 前端 micro fix 包（Bug 1 tag fallback + Bug 3 placeholder 斷行 + Bug 4 export-btn !important + Bug 5 --content-max-w token + 4 主題覆寫 + 5 pytest）

### Logging / 雲原生
- `2026-05-23_logging_refactor_可行性評估.md` — logging_refactor_proposal.md 可行性評估（部分採納）
- `2026-05-23_logging_refactor_可行性評估_補強4點.md` — 補強 4 點（冪等性 / 第三方 logger / asyncio.to_thread / JSON Stacktrace）
- `2026-05-23_logging_refactor_評估更新_2致命陷阱+2優化.md` — v3 更新：2 致命陷阱（asctime / uvicorn log_config）+ 2 優化（exception 安全 / 動態降噪）
- `2026-05-23_logging_refactor_評估更新v4_3生產健壯性.md` — v4 更新：SQLAlchemy 噪聲分流 + ContextVar LookupError 防禦 + JSON 序列化降級

### LOGGING refactor 落地
- `2026-05-23_LOGGING-1_提示詞.md` — LOGGING-1 落地（utils/logging_config + setup + 噪聲分流 + 2 致命陷阱修正）
- `2026-05-23_LOGGING-2_提示詞.md` — LOGGING-2 落地（trace_id middleware + X-Trace-ID header + ContextVar set/reset）
- `2026-05-23_LOGGING-3_提示詞.md` — LOGGING-3 落地（tools/regen_rag.py CLI 統一 setup_logging、LOGGING refactor 完工）

## 依時間排序（最新 15 筆）

- 2026-05-24 — `2026-05-24_BUG-F1_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_P2-3_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_P2-2_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_P2-1_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_Phase2_plan提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_R3_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_R2_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_R1_提示詞.md`
- 2026-05-23 — `2026-05-23_RAG-1_標籤強制小寫+TODO+認證.md`
- 2026-05-23 — `2026-05-23_RAG-1_可行性評估+資料夾自動標籤.md`
- 2026-05-23 — `2026-05-23_LOGGING-3_提示詞.md`
- 2026-05-23 — `2026-05-23_LOGGING-2_提示詞.md`
- 2026-05-23 — `2026-05-23_LOGGING-1_提示詞.md`
- 2026-05-23 — `2026-05-23_logging_refactor_評估更新v4_3生產健壯性.md`
- 2026-05-23 — `2026-05-23_logging_refactor_評估更新_2致命陷阱+2優化.md`
