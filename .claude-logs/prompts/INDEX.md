# 提示詞資料庫索引

最後更新：2026-05-30（RAG-14 C1 Run）

> 本檔案在每次新增提示詞時必須同步更新。
> 簡化規則：「依時間排序」僅保留最新 15 筆;超過則僅在「依任務分類」內保留。

## 依任務分類

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

- 2026-05-30 — `2026-05-30_RAG-14_C1_run_提示詞.md`
- 2026-05-30 — `2026-05-30_RAG-14_Tasks_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS-HOTFIX-1_Check_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS_C2-hotfix_run_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS_HOTFIX-1_Tasks_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13-HOTFIX-1_C1_run_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13-HOTFIX-1_Tasks_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13_Check_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13_C2_run_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13_C1_run_提示詞.md`
- 2026-05-29 — `2026-05-29_RAG-13_Tasks_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS_Check_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS_C2_run_提示詞.md`
- 2026-05-29 — `2026-05-29_FE-AESTHETICS_C1_run_提示詞.md`
