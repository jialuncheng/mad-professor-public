# 提示詞資料庫索引

最後更新：2026-06-02（GOLDEN-BASELINE Tasks 修正）

> 本檔案在每次新增提示詞時必須同步更新。
> 簡化規則：「依時間排序」僅保留最新 15 筆;超過則僅在「依任務分類」內保留。

## 依任務分類

### API-PERF 系列
- 🟡 **API-PERF API 技術審計與效能優化（2026-06-03 Tasks）**
  - `2026-06-03_API-PERF_Tasks_提示詞.md` — Tasks（07:01 修正版：Commit 拆分 C1-C5 實作 + **單一收官 Checkout C6**；對齊已落地 PIPE-CORE/SCAFFOLD：U1 Semaphore 守 Orchestrator.run+雙軌派發點 / U3 LRU 配 ai_core+rag_retriever / U7 計時埋點對齊 PhaseEnum (phase,stage) 二維鍵；產出 _v3）
  - `2026-06-03_API-PERF_C1_run_提示詞.md` — C1 Run（U6 SQLite 連接池：db.py busy_timeout 30s + QueuePool + pool_pre_ping，`=== [API-PERF C1 START/END] ===` 包裹 + 建 tests/test_api_performance_and_robustness.py）
  - `2026-06-03_API-PERF_C2_run_提示詞.md` — C2 Run（U4 upload_paper 1MB 分塊流式寫 + %PDF/415/413 + U5 login X-Forwarded-For 真實 IP，`=== [API-PERF C2 START/END] ===` 包裹 + 追加 streaming/forwarded 測試）
  - `2026-06-03_API-PERF_C3_run_提示詞.md` — C3 Run（U3 廢 lifespan preload + ai_core/rag_retriever 快取改 OrderedDict + 上限 5 + Lazy Load + LRU popitem/gc.collect；retrieve_* 演算法不動，`=== [API-PERF C3 START/END] ===` 包裹 + 追加 lru 測試）
  - `2026-06-03_API-PERF_C4_run_提示詞.md` — C4 Run（U1 PIPELINE_SEMAPHORE 守 A 軌 run_pipeline + B 軌 run_pipeline_shadow + queued SSE / U2 pdf_processor 子進程 nice 19 soft-fail，`=== [API-PERF C4 START/END] ===` 包裹 + 追加 semaphore/queue 測試）
  - `2026-06-03_API-PERF_C5_run_提示詞.md` — C5 Run（U7 (phase,stage) 二維鍵 performance_metric 埋點落 pipeline_core(A 軌) + orchestrator(P1-P4 附加式) + pipeline_finished/rag_finished + 新建 scripts/analyze_performance.py CLI；orchestrator DAG 本體不動、pipelines 20 pytest 維持全綠）
  - `2026-06-03_API-PERF_Check_提示詞.md` — Check（C6 收官：Conformance U1-U7/測試/不可動清單驗收 + 一次性 mv plan_v2/tasks_v3/C1-C6 報告至正式目錄 + TODO 結案 + 歷史全量 Hash 自癒）

### DOMAIN-NORM 系列
- 🟡 **DOMAIN-NORM 領域標準化對齊器（2026-06-03 Tasks + C1 WIP）**
  - `2026-06-03_DOMAIN-NORM_Tasks_提示詞.md` — Tasks（Commit 拆分含最後 Check/Checkout 驗收；plan v2 動態 LCC 生成 + Domains/DomainMapping 表 + context_text + LLM_USE_GLOSSARY_ALIGN 旗標；中間 Commit 留 baton、唯 Check 一次性歸檔；對齊 PIPE master v10/PIPE-SPEC v2）
  - `2026-06-03_DOMAIN-NORM_C1_run_提示詞.md` — C1 Run（Database Schema：models.py 新增 Domains（lcc_code PK + name 動態註冊）+ DomainMapping（raw→lcc 快取）兩表，`=== [DOMAIN-NORM C1 START/END] ===` 包裹 + 改前 .bak；Paper 表不動）
  - `2026-06-03_DOMAIN-NORM_C2_run_提示詞.md` — C2 Run（Normalizer Core：新建 processor/domain_normalizer.py 快取查→LLM 收斂 Temp=0.0→動態註冊 INSERT OR IGNORE→寫回；LLM 呼叫在 DB 交易外 + try/except 降級 general + logging SOP）
  - `2026-06-03_DOMAIN-NORM_C3_run_提示詞.md` — C3 Run（Entry & Feature Flag：domain_normalizer.py 暴露 normalize_to_lcc(raw_domain, context_text=None)->LCCCode 對齊 PIPE-SPEC/master v10 + settings.LLM_USE_GLOSSARY_ALIGN 預設 False 走舊 raw 直注；`=== [DOMAIN-NORM C3 START/END] ===` 包裹 + settings.py 改前 .bak）
  - `2026-06-03_DOMAIN-NORM_Check_提示詞.md` — Check（C5 收官：三維度 Conformance 驗收 U1-U4/測試 §6.1-§6.4/不可動清單 + 一次性 mv plan_v2/tasks/C1-C5 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒；前置 18:46 Check 經 baron 拍板「先補 C4 Unit Tests」重導為 C5 收官）

### TRANSLATOR 系列
- 🟡 **TRANSLATOR 雙模式原子翻譯器（2026-06-04 Tasks）**
  - `2026-06-04_TRANSLATOR_Tasks_提示詞.md` — Tasks（Commit 拆分含最後 Checkout 收官；plan v10 八輪 review 定稿：InjectionContext/TranslateMode 落 processor/translator.py + caption 專屬提示詞 + thinking_config 受控擴充〔§4 唯一例外〕+ GlossaryReadySpec.domain_name 載體；對齊 PIPE-SPEC §1.2.3 v3/DOMAIN-NORM/GLOSSARY-CORE/PIPE-CORE/model_recommendations §1.1）
  - `2026-06-04_TRANSLATOR_C1_run_提示詞.md` — C1 Run（Contract & Context：新建 processor/translator.py 定義 InjectionContext〔7 欄 frozen+forbid〕+ TranslateMode〔NORMAL/DEEP_THINK〕；pipelines/contracts.py GlossaryReadySpec 補 domain_name，`=== [TRANSLATOR C1 START/END] ===` 包裹 + 改前 .bak）

### GLOSSARY-CORE 系列
- 🟡 **GLOSSARY-CORE 中央領域術語庫與跨語系一致性（2026-06-03 Tasks）**
  - `2026-06-03_GLOSSARY-CORE_Tasks_提示詞.md` — Tasks（Commit 拆分含最後 Checkout 收官；plan v2 中央術語庫 + 級聯查詢自癒 + 跨語系一致性；上游真理源 DomainNormalizer LCCCode 已凍結；中間 Commit 留 baton、唯 Checkout 一次性歸檔；對齊 PIPE master v10/PIPE-SPEC/PIPE-CORE/DOMAIN-NORM）
  - `2026-06-03_GLOSSARY-CORE_C1_run_提示詞.md` — C1 Run（Database Schema：models.py 新增 GlobalGlossary 表（source_lang/target_lang/term_key/original_term/translation/domain/source）+ (source_lang,target_lang,term_key,domain) 聯合唯一約束 + 級聯查詢輔助索引，`=== [GLOSSARY-CORE C1 START/END] ===` 包裹 + 改前 .bak；Paper 表不動）
  - `2026-06-03_GLOSSARY-CORE_C2_run_提示詞.md` — C2 Run（Glossary Core & Cascading Retrieval：新建 processor/glossary_extractor.py GlossaryManager——query_cascade 級聯查詢（專屬覆寫 general）+ LLM extract_terms（交易外）+ upsert_terms（on_conflict_do_nothing 冪等）；database SOP 交易邊界鐵律）
  - `2026-06-03_GLOSSARY-CORE_C3_run_提示詞.md` — C3 Run（Translate Integration & Backfill：translate_processor.py:237-239 旗標閘門注入級聯術語表 + pipeline_core.py translate 後背景回填 hook；全 `if settings.LLM_USE_GLOSSARY_ALIGN:` 閘門 + 回填 try/except 非阻塞 + `=== [GLOSSARY-CORE C3 START/END] ===` 包裹 + 改前 .bak；旗標 OFF byte 等價；書籍融合延後）
  - `2026-06-03_GLOSSARY-CORE_C4_run_提示詞.md` — C4 Run（Chat Injection：AI_professor_chat.py:329-335 旗標閘門按 _domain LCC query_cascade 取術語組「不可違背 System constraint」注入 character/explain prompt；前台崩潰防護 try/except graceful degradation + `=== [GLOSSARY-CORE C4 START/END] ===` 包裹 + 改前 .bak；旗標 OFF byte 等價；發現既存 RAG-14 改動→只 stage C4 hunks 隔離）
  - `2026-06-03_GLOSSARY-CORE_C5_run_提示詞.md` — C5 Run（Hot-Pluggable CLI：新建 tools/manage_glossary.py 自癒 CLI——--init / --test-pipeline --pdf 離線閉環 / --backfill-existing-papers 歷史 LCC 批次升級；logging SOP setup_logging 嚴禁 basicConfig + 批次極短交易防 SQLite locked）
  - `2026-06-03_GLOSSARY-CORE_C6_run_提示詞.md` — C6 Run（Unit Tests：新建 tests/test_glossary_core.py 5 測試——聯合唯一約束/級聯優先覆寫/書籍融合優先/Chat 注入/CLI 回填；mock LLM 不實打 API + file-based SQLite FK ON fixture）
  - `2026-06-04_GLOSSARY-CORE_Check_提示詞.md` — Check（C7 收官：三維度 Conformance 驗收 U1-U5/測試 §6.1-§6.6/不可動清單 + 一次性 mv plan_v2/tasks/C1-C7 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒；不給 commit 建議、msg 寫 tmp/）

### PIPE 大改版系列
- 🟡 **GOLDEN-BASELINE 黃金基準存盤與退化比對（2026-06-02 Tasks）**
  - `2026-06-02_GOLDEN-BASELINE_Tasks_提示詞.md` — Tasks（OP-N 執行階段拆分、不給 commit；OP-1 Checkout plan baton→plans 保留 _v2、OP-2 五路黃金基準物理存盤、OP-3 自動化 Regression Diff 比對腳本 + 同步 TODO.md）
  - `2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md` — Tasks 修正（baron 指出 Checkout 時序悖論；重編 OP-1 五路存盤 / OP-2 Diff 腳本 / OP-3 Checkout 收官一次性歸檔 plan+tasks+三報告）
  - `2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md` — OP-1 Run（五路黃金基準物理存盤：新建 tools/golden_baseline.py capture 子命令 + 五路 fixtures + golden 三維度凍結 + manifest）
  - `2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md` — OP-2 Run（自動化 Regression Diff 比對腳本：diff 子命令 + 三維度引擎 + checksum 驗證 + 正規化 + 紅綠燈裁決 + 雙格式報告 + tests/test_golden_baseline.py）
  - `2026-06-02_GOLDEN-BASELINE_Check_提示詞.md` — Check（Conformance 三維度驗收 + OP-3 收官：一次性 mv plan/tasks/OP-1/OP-2/OP-3 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒）
- 🟡 **PIPE-CORE 三層解耦調度骨架（2026-06-02 Tasks）**
  - `2026-06-02_PIPE-CORE_Tasks_提示詞.md` — Tasks（OP-N 執行階段拆分、不拆 commit；pipelines/ 三層解耦空骨架 + 四合約 Pydantic + NullStrategy + tests/test_pipe_core.py，最後 OP Checkout 收官保留 _v2）
  - `2026-06-02_PIPE-CORE_OP-1_run_提示詞.md` — OP-1 Run（合約與狀態層：pipelines/contracts.py 四份凍結 Pydantic + pipelines/context.py PipelineContext + tests/test_pipe_core.py 建檔）
  - `2026-06-02_PIPE-CORE_OP-2_run_提示詞.md` — OP-2 Run（工廠與策略基類：pipelines/base_strategy.py DocumentStrategy ABC + NullStrategy 哨兵 + pipelines/factory.py PipelineFactory 註冊/LiteDoc 降級 + tests 追加）
  - `2026-06-02_PIPE-CORE_OP-3_run_提示詞.md` — OP-3 Run（Orchestrator 四 Phase DAG：pipelines/orchestrator.py 宣告式 P1→P4 + 交接點驗證 + reading_ready/rag_status + P4 非阻塞容錯 + shadow 貫穿；grep doc_type== 0 命中）
  - `2026-06-02_PIPE-CORE_Check_提示詞.md` — Check（Conformance 三維度驗收 + OP-4 收官：一次性 mv plan_v2/tasks_v2/OP-1~OP-4 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒）
- 🟡 **PIPE-SCAFFOLD web_server 雙軌派發 scaffolding（2026-06-02 Tasks）**
  - `2026-06-02_PIPE-SCAFFOLD_Tasks_提示詞.md` — Tasks（OP-N 執行階段拆分、不拆 commit；web_server.py 影子期雙軌派發 scaffolding：SHADOW_LAUNCH_ENABLED 旗標閘門 + run_pipeline_shadow 附加單元 + 兩派發點納管，A 軌 byte 不動，最後 OP Checkout 收官保留 _v3）
  - `2026-06-03_PIPE-SCAFFOLD_OP-1_run_提示詞.md` — OP-1 Run（settings.SHADOW_LAUNCH_ENABLED 預設 false + web_server.run_pipeline_shadow 附加單元 + upload_paper 派發點一旗標閘門；A 軌 run_pipeline 本體 byte 不動）
  - `2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md` — OP-2 Run（retry/confirm 派發點二旗標閘門納管 + 補標 OP-1/OP-2 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解包裹 + 新建 tests/test_pipe_scaffold.py 雙軌測試）
  - `2026-06-03_PIPE-SCAFFOLD_Check_提示詞.md` — Check（Conformance 三維度驗收 + OP-3 收官：一次性 mv plan_v3/tasks_v3/OP-1~OP-3 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒；階段二 Flip 屬 PIPE-FLIP）

### 一般 / 工具
- `2026-05-23_general_建立提示詞資料庫.md` — 建立 prompts/ 資料庫骨架 + 規範

### WORKFLOW 系列
- `2026-05-24_WORKFLOW-1_v3規劃書可行性評估.md` — WORKFLOW-1 改版規劃書 v3 可行性評估（七大子改動 A-G + 五壓力測試 + Q1-Q10 拍板 + Prompt Caching 子題 7.1-7.6 + 執行計畫骨架 10 commits）
- `2026-05-25_WORKFLOW-1_v4第二輪評估.md` — WORKFLOW-1 v4 第二輪評估（§8 S1-S5 五方案選擇 + §10.1-10.5 可行性判定 + A-F 六壓力測試 + v4 新盲點 4 個、採 §2 拆分式結構試點）
- ✅ **WORKFLOW-1 C1~C5 落地全鏈路（2026-05-26 收官）**
  - `2026-05-26_WORKFLOW-1_C1_提示詞.md` — C1 Bootstrap Core（CLAUDE.md / WORKFLOW_SOP.md / framework §0/§9/§99）
  - `2026-05-26_WORKFLOW-1_C1.5_提示詞.md` — C1.5 Core Spec Align + TODO Bootstrap（r11 三核心文件對齊 + TODO.md 自舉）
  - `2026-05-26_WORKFLOW-1_C2+C3_提示詞.md` — C2+C3 Templates & Overview + Prompt Templates（5 模板重構/新建 + 5 提示詞模板 + GOVERNANCE_OVERVIEW.md）
  - `2026-05-26_WORKFLOW-1_C4_提示詞.md` — C4 SOP & Diagnostics（CACHE_OPTIMIZATION_SOP.md + report/.gitkeep）
  - `2026-05-26_WORKFLOW-1_C5_提示詞.md` — C5 收官（TODO.md 歸檔 + 設計歷程 + baton 全歸檔 + INDEX 更新）
- ✅ **TODO-HOTFIX-1 DOC-Hotfix 三階段全鏈路（2026-05-26 收官）**
  - `2026-05-26_TODO-HOTFIX-1_Plan_提示詞.md` — Plan（TODO.md 損毀診斷 + 5 項問題盤點 + 修法 A/B/C/D/E + 六維度 commit 規劃）
  - `2026-05-26_TODO-HOTFIX-1_Run_提示詞.md` — Run（RAG 狀態修復 + Bug Fix 表格補建 + active 殘留清除 + RAG-11/12 獨立抽離 + hash 補填）
  - `2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md` — Tasks / Run-1b（MODEL-8 active 殘留清理 + 修法 E 落地）
  - `2026-05-26_TODO-HOTFIX-1_Check_提示詞.md` — Check（Conformance 8 項驗證 + TODO.md 收官 + baton 全歸檔）
- ✅ **WORKFLOW-2 流程模板重構與提示詞自動歸檔（2026-05-27 收官）**
  - `2026-05-27_WORKFLOW-2_Plan_提示詞.md` — Plan（五大治理漏洞規格 R1~R5 + 歷史 9 份幽靈提示詞補建計畫）
  - `2026-05-27_WORKFLOW-2_Tasks_提示詞.md` — Tasks（5 Commit 拆分：C1 五模板自愈 + C2 Check 維度四五 + C3 SOP 鐵律 + C4 歷史 9 份補建 + C5 INDEX 對齊）
  - `2026-05-27_WORKFLOW-2_C1_run_提示詞.md` — C1 Run（R1 五大提示詞模板自愈歸檔防線 + Tasks 階段補發執行報告）
  - `2026-05-27_WORKFLOW-2_C2_run_提示詞.md` — C2 Run（R2 Check 模板 Conformance 維度四提示詞歸檔 + 維度五 msg.txt 草稿完整性 + TODO.md hash 自癒）
  - `2026-05-27_WORKFLOW-2_C3_run_提示詞.md` — C3 Run（R3+R4 SOP 三鐵律 + execution/tasks/run/check 模板 §8 重構 + TODO 自癒防線物理寫入）
  - `2026-05-27_WORKFLOW-2_C4_run_提示詞.md` — C4 Run（R5a 歷史 9 份提示詞摘要重建物理補建：WORKFLOW-1 C1~C5 + TODO-HOTFIX-1 四階段）
  - `2026-05-27_WORKFLOW-2_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + INDEX 幽靈自癒 + baton 全歸檔收官）

### RAG 系列
- 🟡 **RAG-14 多標籤寬鬆格式跨文章RAG檢索與對話體驗升級（2026-05-30 WIP）**
  - `2026-05-30_RAG-14_Tasks_提示詞.md` — Tasks（C1 後端多標籤解析器 + C2 前端 sendMessage 過濾 + C3 前端 QA-group + CSS + Sticky + C4 測試升級 + Check 收官）
  - `2026-05-30_RAG-14_C1_run_提示詞.md` — C1 Run（CSS 4 項：#chat-messages gap / .msg-user 滿寬 sticky / .msg-ai 滿寬 / .qa-group 新增 + sendMessage × 過濾 + 4 pytest）
  - `2026-05-30_RAG-14_C2_run_提示詞.md` — C2 Run（loadChatHistory history.forEach → qa-group + currentGroup + in_progress currentGroup.appendChild + sendMessage qaGroup 包裝 + 3 pytest）
  - `2026-05-30_RAG-14_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ plan_v3/tasks_v1/C1/C2/Check 全量歸檔 + TODO.md RAG-14 結案）
- ✅ **RAG-13-HOTFIX-1 自訂主題下拉選單捲軸無作用修復（2026-05-29 收官）**
  - `2026-05-29_RAG-13-HOTFIX-1_Tasks_提示詞.md` — Tasks（FE-Hotfix tasks 拆分：C1 選單捲軸修復 + Check 收官）
  - `2026-05-29_RAG-13-HOTFIX-1_C1_run_提示詞.md` — C1 Run（static/index.html L1622 scroll handler ctx-popup 過濾 + test_rag13_hotfix1_scroll_intercept.py 新增）
  - `2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md` — Check（Conformance 驗收與收官歸檔提示詞）
- ✅ **RAG-13 自訂主題動態清單與選單優化（2026-05-29 收官）**
  - `2026-05-29_RAG-13_Tasks_提示詞.md` — Tasks（C1 後端 GET /api/themes + fixture 修正 + C2 前端 setThemes/loadThemesFromServer/分隔線/upload handler）
  - `2026-05-29_RAG-13_C1_run_提示詞.md` — C1 Run（web_server.py GET /api/themes list_themes + test_themes_upload.py fixture GET 掛載 + test_list_themes_endpoint）
  - `2026-05-29_RAG-13_C2_run_提示詞.md` — C2 Run（static/index.html：setThemes() + setupOne 分組分隔線 + loadThemesFromServer() + upload handler await 重構）
  - `2026-05-29_RAG-13_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ tasks/C1/C2/Check 全量歸檔 + TODO.md RAG-13 結案）
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
- `2026-05-24_BUG-F2_提示詞.md` — BUG-F2 theme dropdown + ESC + P2-3 latent fix（Bug 2 dropdownAPI IIFE + TDZ-aware 3 段拆分 + Bug 11 hashtag-autocomplete `.ctx-popup` 移除 + 6 pytest）
- `2026-05-24_BUG-F3_提示詞.md` — BUG-F3 `.modal-input` CSS（Bug 7、ui-fixes-batch B5 全文 + `input[type="text"]` 廣義 selector + color-mix 跨主題 focus ring + 2 pytest、v2 前端三段全完工）
- `2026-05-24_BUG-F4_提示詞.md` — BUG-F4 P1 critical 4 項（A1 trackProgress renderTitleHeader + A2 empty-state 反轉 + A3 customPrompt 新增 + 全 native dialog 替換 + A4 closeBizPopups 移除統一 closePopups + 9 pytest）
- `2026-05-24_BUG-F5_提示詞.md` — BUG-F5 P2 inconsistencies（B1 廢 token 替換主 scale 5 處 + B3 demo-bar CSS/JS dead code 刪除 + B4 no-op setupTooltip 已 ship docs 對齊驗證 + 8 pytest）
- `2026-05-24_BUG-F6_提示詞.md` — BUG-F6 P3 polish（C3+C6 no-op + C4 ~43 ticket 編號註解清理 + C5 marked strikethrough 註解改寫 + C7 paper-menu-btn/folder menu-btn `⋯`→SVG+data-tip + icon-spec.md §4 註記 + 7 pytest、**v2+v3 前端評估全鏈路完工**）
- `2026-05-24_BUG-B1_提示詞.md` — BUG-B1 後端 abstract fallback（Bug 8 lead、A pipeline_core 側路 translate_text 翻譯 + B md_processor regex 擴中日文「摘要 / 概要 / 內容提要 / 内容提要 / 要旨」+ 28 pytest、後端評估首 commit）
- `2026-05-24_BUG-B2_提示詞.md` — BUG-B2 後端 blockquote → list + 前端 paper-header-meta CSS（Bug 10 lead 混合 bug、md_restore _render_header_en/zh `>` → `-` list + `<div class="paper-header-meta">` wrap + 前端 @media screen class hook hide + principles.md §2 / dom-reference.md §4.3 docs sync + 7 pytest、**RAG-1 Bug Fix 全鏈路收官**）

### Logging / 雲原生
- `2026-05-23_logging_refactor_可行性評估.md` — logging_refactor_proposal.md 可行性評估（部分採納）
- `2026-05-23_logging_refactor_可行性評估_補強4點.md` — 補強 4 點（冪等性 / 第三方 logger / asyncio.to_thread / JSON Stacktrace）
- `2026-05-23_logging_refactor_評估更新_2致命陷阱+2優化.md` — v3 更新：2 致命陷阱（asctime / uvicorn log_config）+ 2 優化（exception 安全 / 動態降噪）
- `2026-05-23_logging_refactor_評估更新v4_3生產健壯性.md` — v4 更新：SQLAlchemy 噪聲分流 + ContextVar LookupError 防禦 + JSON 序列化降級

### LOGGING refactor 落地
- `2026-05-23_LOGGING-1_提示詞.md` — LOGGING-1 落地（utils/logging_config + setup + 噪聲分流 + 2 致命陷阱修正）
- `2026-05-23_LOGGING-2_提示詞.md` — LOGGING-2 落地（trace_id middleware + X-Trace-ID header + ContextVar set/reset）
- `2026-05-23_LOGGING-3_提示詞.md` — LOGGING-3 落地（tools/regen_rag.py CLI 統一 setup_logging、LOGGING refactor 完工）

### MODEL-10 系列
- ✅ **MODEL-10 MinerU 連線優化與運作維護 SOP（2026-05-27 收官）**
  - `2026-05-27_MODEL-10_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ 六份全量歸檔含 SOP → sop/ + TODO.md MODEL-10 結案）
  - `2026-05-27_MODEL-10_C2_run_v1_提示詞.md` — C2 Run（新建 .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md ≤250 行，含 §0/§99 治理結構、6 大運維主軸：env 配置 / 超時對策 / SSH Keep-Alive / Priority 2 SCP 備援 / cron 清檔 / 容器重啟）
  - `2026-05-27_MODEL-10_C1_run_v1_提示詞.md` — C1 Run（pdf_processor.py MINERU_TIMEOUT 防禦性載入 + timeout=300 動態化 + Priority 2 廢棄 warning + .env.example + 3 pytest）
  - `2026-05-27_MODEL-10_Tasks_v1_提示詞.md` — Tasks v1（C1 pdf_processor MINERU_TIMEOUT 防禦性載入 + 廢棄 SCP 警告 + 3 pytest + C2 MinerU SOP 手冊 + Check 結案歸檔）

### FE-AESTHETICS 系列
- ✅ **FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化（2026-05-29 收官）**
  - `2026-05-29_FE-AESTHETICS_HOTFIX-1_Tasks_提示詞.md` — Tasks（FE-Hotfix tasks 拆分：C2-hotfix 學術扉頁自癒 + Check 收官）
  - `2026-05-29_FE-AESTHETICS_C2-hotfix_run_提示詞.md` — C2-hotfix Run（CSS 靠左 + normalizeAcademicHeader JS + fetchContent 呼叫 + test_bug_f1 斷言自癒 + 新建 test_fe_aesthetics_c2_hotfix.py）
  - `2026-05-29_FE-AESTHETICS-HOTFIX-1_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ hotfix/tasks/C2-hotfix/Check 全量歸檔 + TODO.md FE-AESTHETICS HOTFIX-1 結案）
- ✅ **FE-AESTHETICS 摘要工具列重構與正文扉頁美化（2026-05-29 收官）**
  - `2026-05-29_FE-AESTHETICS_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ tasks/C1/C2 全量歸檔 + TODO.md FE-AESTHETICS 結案）
  - `2026-05-29_FE-AESTHETICS_C2_run_提示詞.md` — C2 Run（static/index.html：#abstract-toolbar DOM + .paper-header-meta CSS flex + renderTitleHeader JS 重構 + test_bug_b2 / test_bug_f5 assertions 更新）
  - `2026-05-29_FE-AESTHETICS_C1_run_提示詞.md` — C1 Run（`_render_header_en/zh` dash-list → 階梯式 HTML div + test_bug_b2 + test_md_restore assertions 更新）
  - `2026-05-29_FE-AESTHETICS_Tasks_提示詞.md` — Tasks（2 Commits C1 後端扉頁重塑 + C2 前端全棧重構 + Check 收官）

### INFRA 系列
- ✅ **INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新（2026-05-28 收官）**
  - `2026-05-28_INFRA-1_Check_提示詞.md` — Check（5 維度 Conformance 驗收 + baton/ 4 份全量歸檔 + TODO.md INFRA-1 結案）
  - `2026-05-28_INFRA-1_C2_run_v1_提示詞.md` — C2 Run（sop/2026-05-27_mineru_SOP_手冊.md §1 VRAM 禁用條目 + §2.3 CPU 後端紅線規格 + §6.2 VRAM OOM 自愈 + §99.2 v2）
  - `2026-05-28_INFRA-1_C1_run_v1_提示詞.md` — C1 Run（processor/pdf_processor.py backend=pipeline comment lock + test_backend_parameter_is_pipeline Case D + .env.example VRAM 禁用警告）
  - `2026-05-28_INFRA-1_Tasks_v1_提示詞.md` — Tasks v1（3 commits 拆分：C1 pdf_processor backend 鎖定 + C2 SOP CPU 推理規格更新 + Check 收官歸檔）

### OPTIMIZE 系列
- ✅ **OPTIMIZE-1 PDF上傳自動無損優化（2026-05-27 收官）**
  - `2026-05-27_OPTIMIZE-1_C3_run_提示詞.md` — C3 Run（Final Archiving and TODO Sync：baton/ 全量 mv 歸檔 + TODO.md 結案）
  - `2026-05-27_OPTIMIZE-1_C2_run_提示詞.md` — C2 Run（後端 is_slides_pdf 刪除 + optimize_pdf_lossless 整合 + 前端 Phase-Shift 事件控制流翻轉）
  - `2026-05-27_OPTIMIZE-1_C1_run_提示詞.md` — C1 Run（新建 utils/pdf_optimizer.py Atomic Overwrite + tests/test_pdf_optimize.py 2 個單元測試）
  - `2026-05-27_OPTIMIZE-1_Tasks_提示詞.md` — Tasks v3（三大前端合規防線：真實行號鋼鐵定位 L1287/L1291/L3193/L3343 + Modal HTML 微調補取消出口/ESC解鎖 + Phase-Shift 事件控制流翻轉）
  - `2026-05-27_OPTIMIZE-1_Tasks_v2_提示詞.md` — Tasks v2（C1 加 Atomic Overwrite + C2 一字步上傳端點 + 前台 UI 整合）

## 依時間排序（最新 15 筆）

- 2026-06-04 — `2026-06-04_TRANSLATOR_C1_run_提示詞.md`
- 2026-06-04 — `2026-06-04_TRANSLATOR_Tasks_提示詞.md`
- 2026-06-04 — `2026-06-04_GLOSSARY-CORE_Check_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C6_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C5_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C4_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C3_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C2_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_C1_run_提示詞.md`
- 2026-06-03 — `2026-06-03_GLOSSARY-CORE_Tasks_提示詞.md`
- 2026-06-03 — `2026-06-03_DOMAIN-NORM_Check_提示詞.md`
- 2026-06-03 — `2026-06-03_DOMAIN-NORM_C3_run_提示詞.md`
- 2026-06-03 — `2026-06-03_DOMAIN-NORM_C2_run_提示詞.md`
- 2026-06-03 — `2026-06-03_DOMAIN-NORM_C1_run_提示詞.md`
- 2026-06-03 — `2026-06-03_API-PERF_C5_run_提示詞.md`
