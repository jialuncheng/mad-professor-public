# 提示詞資料庫索引

最後更新：2026-06-06（MODEL-11 Tasks）

> 本檔案在每次新增提示詞時必須同步更新。
> 簡化規則：「依時間排序」僅保留最新 15 筆;超過則僅在「依任務分類」內保留。

## 依任務分類

### META-NORM 系列
- ✅ **META-NORM 封面元數據自癒飛輪與動態欄位登記（2026-06-11 plan → Tasks → C1-C6 → C7 收官·BE-Refactor·解 PIPE-SLIDES C+D）**
  - `2026-06-11_META-NORM_Check_提示詞.md` — Check（C7 收官：Conformance〔U1-U9 / §6 C1-C6 測試 / §7.2 key-changing 整合存在且通過 / 不可動 / 提示詞稽核 / msg〕→ TODO 結案 + baton 一次性歸檔〔plan/tasks/C1-C7 報告→plans//tasks//executions/〕+ hash 全量自癒；PIPE-SPEC 長駐；飛輪 end-to-end 全案結案）
  - `2026-06-11_META-NORM_C6_run_提示詞.md` — C6 Run（Tests·純測試：test_meta_norm 新增 §7.2 key-changing 整合〔P1 自提『課程』→飛輪映 course→消費端 .get('course').get('value') 取值；雙斷言 raw_key≠canonical 仍對位 + 三欄 dict 杜 bare string 退化〕+ test_slide_pipeline assertions 檢查；僅兩測試檔；不自發 commit）
  - `2026-06-11_META-NORM_C5_run_提示詞.md` — C5 Run（Frontend Generic Renderer：web_server +GET /api/meta-fields〔唯讀回 MetaField label/sort_weight〕+ static/index.html CSS .paper-dynamic-meta + window.metaFields 快取〔seed 離線兜底〕+ renderTitleHeader 遍歷非排除集〔BS2〕→ label 顯示 → sort_weight/字母序〔BS7〕渲染標題下方；飛輪產物首次前端顯示；僅兩檔；不自發 commit）
  - `2026-06-11_META-NORM_C4_run_提示詞.md` — C4 Run（Subtitle：`_VISION_PROMPT` schema +subtitle 欄 + run_phase1 units 收 subtitle + page_key/section_summaries fallback〔title 空用 subtitle〕+ `_translate_pages_parallel` 翻 subtitle + `_page_source_md`/`_deliver` 渲染 `### {subtitle}`〔EN/ZH〕；解 D 小標題；2 測試；僅兩檔；不自發 commit）
  - `2026-06-11_META-NORM_C3_run_提示詞.md` — C3 Run（P1 Wire：`_COVER_PROMPT` 追加開放 metadata 抽取〔保留 company/date/authors〕+ run_phase1 旗標 on 呼 MetaNormalizer.normalize_fields → pop reserved〔title/authors/venue/doi〕回填合約 + 其餘 canonical 三欄 dict 寫旁路〔HOTFIX-1b 契約〕、旗標 off 退寫死 + IngestionMetadataSpec 補 venue/doi；2 測試；僅兩檔；不自發 commit）
  - `2026-06-11_META-NORM_C2_run_提示詞.md` — C2 Run（MetaNormalizer Flywheel：新建 `processor/meta_normalizer.py` 繼承 DomainNormalizer 範式；reserved 映射不入庫〔BS1〕+ GENERIC_KEYS 黑名單不快取〔Q9〕+ _cache_lookup/_llm_classify〔temp=0 交易外〕/_register_and_cache〔session.begin on_conflict 註冊+label 提案 BS4〕+ normalize_fields 三路分流 + try/except 降級 + 旗標閘門；4 測試；僅兩檔；不自發 commit）
  - `2026-06-11_META-NORM_C1_run_提示詞.md` — C1 Run（Schema & Flag：models +MetaField/MetaFieldAlias 兩表〔PK/Unique+FK CASCADE+sort_weight、繼承 Domains 範式〕+ settings `LLM_USE_META_NORM`(False) + db.py init_db seed 6 欄〔course/instructor/organization/date/venue/doi、sqlite_insert on_conflict_do_nothing + session.begin 交易安全〕+ 新建 tests/test_meta_norm.py 表結構/種子驗證；僅四檔；3 .bak；不自發 commit）
  - `2026-06-11_META-NORM_Tasks_提示詞.md` — Tasks（依 plan v1〔v1.2 八 OQ+Q9/Q10 全定案、BS1-7〕拆 commit：MetaField/MetaFieldAlias 兩表 + MetaNormalizer 飛輪 + P1 開放抽取/封面放寬接線 + subtitle + 前端通用渲染 + 測試；末 commit checkout 收官；schema 新增 2 表）
  - `2026-06-11_META-NORM_plan_提示詞.md` — plan（baron 構想：LLM 開放抽取封面 meta + 第二次 LLM 比對既有欄位統一＝DOMAIN-NORM 飛輪搬到 metadata 欄名；MetaField/MetaFieldAlias 兩表 + MetaNormalizer 三步飛輪 + P1 開放抽取/封面判定放寬 + subtitle〔D〕併入 + 前端通用 key-value 渲染；§9 八 OQ；A 撤案、B/E/F 歸 HOTFIX-2；不寫碼純規格）

### PIPE-SLIDES 系列
  - `2026-06-12_PIPE-SLIDES-HOTFIX-3d_doc_提示詞.md` — HOTFIX-3d 文件產出（B 軌 vs 原稿比對後修 #2：行內 `**X**`→`<strong>`〔解 CJK 緊貼 `**` 未渲染粗體〕+ 剝除整行裸 URL〔解 p6/18/27/35 破版〕；slide 渲染層、RAG 旁路不碰；baton 暫存待 Run）
  - `2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_run_提示詞.md` — HOTFIX-3b Run（top-level 清單凸排修補執行：HOTFIX-3 二 selector 前置 `#paper-content ul/ol`；備份+grep+pytest 驗收；TODO 標 ✅ + hash 自癒 + baton 移出歸檔）
  - `2026-06-12_PIPE-SLIDES-HOTFIX-3b_doc_提示詞.md` — HOTFIX-3b 文件產出（top-level bullet 凸排：index.html L79 全域 reset 歸零 ul/ol padding、HOTFIX-3 二只修巢狀；base 一處把 list-indent 規則擴含 top-level `#paper-content ul/ol`；不動 themes〔主題 0 命中 list、結構歸主檔〕；baton 暫存待 Run）

  - `2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_run_提示詞.md` — HOTFIX-3 Run（簡報閱讀視圖排版打磨：P3 一-a 圖序+C `_slide_head_html` 標題塊〔解 一-b〕+A/B/C `_promote_subheadings` 升 h3〔\r 相容/不產連續空行〕；base CSS .slide-head/.slide-sub + 巢狀 ul 縮排;rag_sections 原封不動;更新既有斷言+4 新測試;收官 mv hotfixes/+executions/;不自發 commit）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-3_doc_提示詞.md` — HOTFIX-3 文件產出（簡報閱讀視圖排版打磨：一-a 圖在上+C 副標併 .slide-head 標題塊〔順帶解 一-b 夾線〕+A/B/C 升 h3+二 base 巢狀縮排；design/docs 設計對齊、subtitle 對 RAG 零影響已驗；baton 暫存待 Run）

- ✅ **PIPE-SLIDES SlidePipeline 簡報策略管線（2026-06-11 Tasks → C1-C6 → C7 Checkout 收官·BE-Refactor·第 2 路）**
  - `2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_run_提示詞.md` — HOTFIX-2 Run（B _safe_alt 破圖根除 + E _strip_master_date 母片日期洗 + F _normalize_paragraph_breaks list-aware〔修 HOTFIX-1 F4 回歸〕+ 3 測試；單檔兩檔、收官 mv hotfixes/+executions/；不自發 commit）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-2_doc_提示詞.md` — HOTFIX-2 文件產出（B alt 轉義破圖根除 + E 母片日期洗除〔dedup 格式變異漏網〕+ F 修 HOTFIX-1 F4 條列鬆散回歸；單檔三點純渲染/清洗、零 Vision prompt 改動；A 撤案、C/D 留 schema 後話；baton 暫存待 Run）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-1b_run_提示詞.md` — HOTFIX-1b Run（寫入端三欄 dict 化+run_phase4 取 value+2 測試堵盲區；收官 mv hotfixes/+executions/；不自發 commit）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-1b_doc_提示詞.md` — HOTFIX-1b 文件產出（F2 譯題旁路裸 str → upsert_paper/web_server 期望三欄 dict → 影子寫庫 AttributeError 前端不顯示；修寫入端 dict 化+讀取端取 value+堵測試盲區；baton 暫存待 Run）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-1_run_提示詞.md` — HOTFIX-1 Run（依 hotfix.md 落地 F1 去標題回聲/F2 接譯題/F4 段落正規化＋4 回歸測試；收官自動化 mv hotfix→hotfixes/+報告→executions/；兩規格書長駐 baton 嚴禁動；不自發 commit）
  - `2026-06-11_PIPE-SLIDES-HOTFIX-1_doc_提示詞.md` — hotfix 文件產出（四問題拍板 1C 物理去標題回聲/2B 複用 P3 譯題/3C 並列顯式不修/4 移植 _normalize_paragraph_breaks；單檔三點+4 測試+msg；baton 暫存待 Run）
  - `2026-06-11_PIPE-SLIDES_Check_提示詞.md` — Check（C7 Checkout：Conformance 五維度〔plan U1-U11 / tasks §6.1-§6.6 / 不可動〔A 軌/rag_indexer/合約〕/ 提示詞稽核 / msg 完整〕+ **§7.2 整合測試正面合規**〔key-changing 已實作通過〕→ 母 plan v10 同步〔§8.5 PIPE-VISUAL→PIPE-SLIDES 改名+✅+L70/L258 Bypass 句更正、補註⁷〕+ baton 歸檔〔plan/tasks/C1-C7 報告 + **修改後母 plan→plans/ 升格入版控**；PIPE-SPEC 長駐〕+ TODO 結案；不自發 commit；第 2 路全案結案）
  - `2026-06-11_PIPE-SLIDES_C6_run_提示詞.md` — C6 Run（Unit & Integration Tests·純測試：補全 plan §8.1 缺口 + **§7.2 跨 Phase 整合測試**〔P2→P3→P4 串接、FakeTranslator 真改寫頁標題=key-changing transform、斷言下游 chunk 對位取得正確頁摘要·p{N}_ key 同基準不變式〕；嚴禁改業務碼〔發現 bug 暫停回報〕；1 .bak；不自發 commit）
  - `2026-06-11_PIPE-SLIDES_C5_run_提示詞.md` — C5 Run（P4 Wire：`run_phase4` 呼共用 `rag_indexer.index`〔sections=ctx.rag_sections+section_summaries+rag_tree_path+title、resume 同範式〕；四產物、≥3 門檻、異常拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready；**零 A 軌 rag_processor import**；mock 接線測試；C5 包裹+2 .bak；不自發 commit）
  - `2026-06-11_PIPE-SLIDES_C4_run_提示詞.md` — C4 Run（P3 Per-Page Translate & Restore〔最大 commit〕：逐頁 InjectionContext+NORMAL、並行照抄 RESUME-PERF-1〔slot 保序+semaphore+單頁退原文〕；還原 `![alt=description 譯文](images/page-N.jpg)`+譯文、**嚴禁 *圖表：* 段**〔雙 Caption 物理根除〕、不渲染 meta header；_SLIDE_CONSTRAINTS〔Q4 四條〕；ctx.rag_sections 旁路 summary_key=page_key 同基準+同頁合併〔Q3 策略側〕；zh 路跳譯仍建 per-section；fallback Q5；不污染 rag_indexer；C4 包裹+2 .bak；不自發 commit）
  - `2026-06-11_PIPE-SLIDES_C3_run_提示詞.md` — C3 Run（P2 Six-Step：`run_phase2` 統一六步〔①全文摘要同呼叫順產 raw_domain·缺→None 降級 / ②批次每頁摘要同呼叫順產缺失頁標題·**key=`p{頁序}_{原文頁標題}`** 防連續同標題撞 / ③LCC ④Glossary 級聯〔query_cascade→extract→upsert 冪等·LLM 交易外〕 ⑤DEEP_THINK 翻摘要 ⑥批次翻頁摘要→section_summaries〕+ 三安全鎖 + domain_name；C3 包裹+2 .bak；§6.3 pytest+裸 commit grep；不自發 commit）
  - `2026-06-11_PIPE-SLIDES_C2_run_提示詞.md` — C2 Run（P1 Vision Ingestion：`run_phase1`＋私有群〔`_render_pages` fitz 整頁存圖 page-{N}.png 空白跳過·自建零 A 軌 import / `_transcribe_page` Vision temp=settings.LLM_VISION_TEMPERATURE+忠實轉錄 prompt 含 cell 禁 ###+條件滾動 Q1 預設關 / `_detect_cover` 封面→raw_metadata·否→title fallback 檔名 / `_dedupe_headers` Q2 短行≥60% 非封面頁剔除+log〕；每頁=section、tiles=processed JSON、source_lang 啟發式、影子後綴 → IngestionMetadataSpec；C2 包裹+2 .bak；§6.2 grep+pytest；不自發 commit）
  - `2026-06-11_PIPE-SLIDES_C1_run_提示詞.md` — C1 Run（Skeleton & Register：新建 `pipelines/slide_pipeline.py`〔`@register('slides')` + DocumentStrategy 四方法 stub + `rag_char_threshold=3`〕+ `pipelines/__init__.py` 補 import〔`# === [PIPE-SLIDES C1] ===` 包裹、C7-hotfix 教訓〕+ 新建 `tests/test_slide_pipeline.py` 分派測試〔_registry 含 'slides'、get_strategy 非 NullStrategy〕；僅三檔；.bak；msg /tmp、不自發 commit）
  - `2026-06-11_PIPE-SLIDES_Tasks_提示詞.md` — Tasks（依 plan v1〔v1.1 八 OQ 全結清〕拆 commit：新建 `pipelines/slide_pipeline.py`〔P1 每頁存圖+Vision temp=0+封面判定+統計去重 / P2 六步 key=`p{N}_{標題}` / P3 逐頁並行+alt 對齊雙 Caption 根除+rag_sections / P4 rag_indexer 照抄〕+ `__init__` 註冊 + `tests/test_slide_pipeline.py`〔含 §7.2 key-changing 整合測試〕；末 commit Checkout 含母 plan §8.5 PIPE-VISUAL→PIPE-SLIDES 改名同步〔Q6/Q7〕；工作範圍硬限三檔）

### PIPE-SYNC-2 系列
- ✅ **PIPE-SYNC-2 resume 路落地經驗回灌母 plan 與 SPEC（2026-06-11 Tasks → C1-C3 → C4 Checkout 收官·DOC-Refactor）**
  - `2026-06-11_PIPE-SYNC-2_Check_提示詞.md` — Check（C4 Checkout：Conformance 五維度〔plan §2 U1-U14 / tasks §6.1 六+§6.2 七+§6.3 五條 grep / 不可動〔業務碼/凍結合約欄位/Slides Bypass〕/ 提示詞稽核 / msg 完整〕+ **§7.2 豁免顯式聲明〔DOC、無 code handoff、Q4〕** → 全綠後 TODO 結案 + baton 歸檔〔plan→plans/ + tasks→tasks/ + C1-C4 報告→executions/；**兩長駐真理源 2026-06-01_PIPE* 嚴禁動**〕；msg /tmp、不自發 commit；PIPE-SYNC-2 全案結案、PIPE-VISUAL 前置完成）
  - `2026-06-11_PIPE-SYNC-2_C3_run_提示詞.md` — C3 Run（SOP Fix & Archive：U11 `model_recommendations` EMBEDDING_MODEL 建議值 -2→**-001**🔴+EXTRA_INFO 已廢註 / U12 `google_latest_models_guide` 頂部勘誤 banner〔embedding-2 與 MODEL-11 實測矛盾、內文不動〕/ U13 `doc_type v3` 適用範圍 banner〔A 軌專用、B 軌見 PIPE-SPEC §1.3〕+ **v1/v2 mv archive/** / U14 `mineru_SOP` §6 補 RELEASE_ON_UPLOAD 配套句；四 .bak；sop 皆 tracked 正常 git add；§6.3 五條 grep；不自發 commit）
  - `2026-06-11_PIPE-SYNC-2_C2_run_提示詞.md` — C2 Run（SPEC Sync：PIPE-SPEC 就地補註〔U3 §1.1②+§1.4.1 key 契約凍結三句·逐字對齊 WORKFLOW_SOP §7.1 / U4 zh 來源五路通用 edge path / U5 新增 §1.3.1 Vision 解析共用規格三原則〔忠實轉錄鐵律/temp=0/非確定性註記〕/ U6 樣例 embedding-2→-001 / U7 rag_tree 由 build_rag_tree 自建 / U8 resume P1 opt-out 註 / U9 受限並行句 / U10 還原三件套註〕；四凍結合約欄位結構不動；HTML 包裹 + §99.2 v6；.bak 入 archive、SPEC 本體不入版控；§6.2 七條 grep；不自發 commit）
  - `2026-06-11_PIPE-SYNC-2_C1_run_提示詞.md` — C1 Run（Master Plan Sync：母 plan v10 就地補註〔U1 resume Bypass 雙處 L71/L257 改逐 section、slides L70/L258 嚴禁動·Q6 / U2 §8.5 RAG-ASYNC ⬜→✅+產出補 rag_indexer·PIPE-RESUME 狀態註 / U3 母句 key=原文標題 path / U8 Tiles 交付形狀措辭 / U5 PIPE-VISUAL 條目尾 §1.3.1 指標〕；HTML 註解包裹 + §99.2 補註⁶；.bak 入 archive 審計、母 plan 本體不入版控〔195e12b 先例〕；§6.1 六條 grep 驗收；執行報告暫存 baton、不自發 commit）
  - `2026-06-11_PIPE-SYNC-2_Tasks_提示詞.md` — Tasks（依 plan v1〔v1.2 OQ 全結清、U1-U14〕拆 commit：兩真理源就地補註〔U1 矛盾/U2 stale/U3 key 契約/U4 zh 路/U5 Vision §1.3.1/U6 樣例 -001/U7 rag_tree 歸屬/U8 Tiles 措辭/U9 並行/U10 還原三件套〕+ sop 四檔〔U11 model_recommendations 🔴/U12 guide 勘誤/U13 doc_type banner+v1v2 歸檔/U14 mineru RELEASE_ON_UPLOAD〕；HTML 註解包裹、不 bump 版本；末 commit Checkout 一次性歸檔；§7.2 豁免）

### LAZYLOAD-MULTI-1 系列
- ✅ **LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放（2026-06-10 Tasks → C1-C4 → C5 Checkout 收官·BE-Refactor）**
  - `2026-06-10_LAZYLOAD-MULTI-1_Check_提示詞.md` — Check（C5 Checkout：Conformance 六維度〔plan v5 U1-U9 / tasks §6 grep+pytest〔10+556 passed〕/ **§7.2 整合測試 test_retrieve_multi_loads_all_tagged〔key=paper_uuid 穩定、key-changing N/A〕** / 不可動〔C3/C4 hunk 不重疊〕/ 提示詞稽核 / msg 完整〕→ 全綠後 TODO 結案〔C1 8893ad1/C2 9849600/C3 c5b0c31/C4-C5 + 全量 hash 自癒〕+ baton 一次性 mv〔plan v1-v5→plans/ + tasks→tasks/ + C1-C4 報告→executions/〕+ C5 報告直寫；YuLun_Wu_CV_chat.md 保持原狀；msg /tmp〔Opus 4.8 1M〕、不自發 commit；LAZYLOAD-MULTI-1 全案結案、根治 API-PERF C3 lazy-load 漏召）
  - `2026-06-10_LAZYLOAD-MULTI-1_C4_run_提示詞.md` — C4 Run（記憶體釋放策略：`settings.py` `RELEASE_ON_UPLOAD`=on + `web_server.py` 模組級 `_owner_current_paper` + helper `_release_caches_except_active`〔全清該 owner cached、唯一豁免 active_streams done==False、快照 keys 再清、gc.collect 騰 MinerU〕+ `/content` 換篇 gate〔F1 語言切換同篇不放〕+ `/upload` 開關釋放 + `ai_core.py` remove_paper docstring 修〔P4〕；靠 C3 ③ 自載兜底；**只動端點段+helper、不碰 C3 啟動接線段**、不動 rag_retriever；4 .bak + 3 釋放測試〔skip_active/only_on_switch/upload_toggle〕；msg /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-10_LAZYLOAD-MULTI-1_C3_run_提示詞.md` — C3 Run（啟動接線與容量·核心 LIVE：`settings.py` `RAG_MAX_CACHE` 5→100〔env 可覆寫〕+ `web_server.py` 啟動 lifespan 接線一行 `ai_core.retriever.set_loader(λ o,p: load_paper_resources(OUTPUT_DIR,o,p,ai_core))`〔API-PERF C3 區附近、retriever 就緒後 yield 前〕→ retrieve_multi 對未載 tagged 篇經 ③ 自載、跨文件 #cv 不再只召當前篇；純加法 2-3 行；**只動啟動段不碰端點〔C4〕**、不動 rag_retriever/ai_core〔C1/C2〕；3 .bak + test_cap_100_default；msg /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-10_LAZYLOAD-MULTI-1_C2_run_提示詞.md` — C2 Run（in-memory cache 併發鎖純硬化·**單一共享 RLock**：`rag_retriever.py` import threading + `self._lock=RLock()` + `with self._lock` 包 add_paper/_evict/remove_paper/set_rag_tree/_get_vector_store dict mutation〔🔴 鐵則 loader 呼叫在鎖外防 AB-BA re-enter〕；`ai_core.py` 共用 `self.retriever._lock` 包 load_paper_cache/remove_paper〔修正 tasks §4.2 兩鎖 load_paper_cache↔_get_vector_store 相反鎖序死鎖隱患〕；純加鎖行為不變〔既有全套件全綠=回歸網〕+ 追加 `test_concurrent_lazyload_no_corruption`〔≥8 thread、不死鎖 timeout〕；3 .bak；只動 rag_retriever+ai_core+測試、不動 web_server/settings；msg /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-10_LAZYLOAD-MULTI-1_C1_run_提示詞.md` — C1 Run（`rag_retriever.py` loader 接縫：`set_loader` + `_get_vector_store` 兩層後加第三層「完全 miss 呼注入 loader 自載重試」+ `is_ready` 改 `or self._loader is not None`〔U7 防全清繞過〕；保留既有兩層、loader 未設＝現況回 None 向後相容；`# === [LAZYLOAD-MULTI-1 C1] ===` 包裹 + .bak + 新建 `tests/test_lazyload_multi.py` 5 測試〔自載/未設回 None/整合 6 篇只註冊 1/重載 title 非空/is_ready〕；只動 rag_retriever.py+測試、不加 RLock〔C2〕/釋放〔C4〕；msg /tmp〔Opus 4.8 1M〕、baton 不入 git、不自發 commit）
  - `2026-06-10_LAZYLOAD-MULTI-1_Tasks_提示詞.md` — Tasks（依 plan v5 §9 Q6 拆 5 commit〔C1 retriever loader 接縫自載+is_ready / C2 RLock 純硬化+並發 / C3 接線+cap100 核心 LIVE / C4 釋放策略 content 換篇 gate+upload 開關+跳過 active_streams+gc / C5 Checkout〕、忠實轉 §8 六維度不自行增刪、C3/C4 web_server hunk 邊界、對齊 U1-U9/§4 接縫五條；plan v1-v5 留 baton 待 C5 歸檔；各 Run 各產執行報告）

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
  - `2026-06-04_TRANSLATOR_C2_run_提示詞.md` — C2 Run（Prompt Engine：translator.py 補 Translator 類 + 系統提示詞五步〔text_type 路由含 caption / doc_type Style Hints / LCC 注入讀 ctx.domain_name 零 DB / Glossary 強約束含大小寫不敏感 / constraints〕+ 用戶提示詞；新建 prompt/translate/caption_translate_prompt.txt，C2 標記包裹 + 改前 .bak）
  - `2026-06-04_TRANSLATOR_C3_run_提示詞.md` — C3 Run（Dual-Mode Routing & Thinking：settings.py +LLM_THINKING_BUDGET〔+TRANSLATE_MODEL 預設改 gemini-3.5-flash〕+ llm/client.py chat() 補 thinking_config 受控擴充〔§4 唯一例外、gated budget>0+思考世代、前向相容〕+ translator.py Translator.translate() 雙模式 chat 路由；C3 標記包裹 + 三檔 .bak）
  - `2026-06-04_TRANSLATOR_C4_run_提示詞.md` — C4 Run（Formatting Fallback & Tests：translator.py translate() 末加 U4 多行 re.sub 分行兜底；新建 tests/test_translator.py 8 測試〔normal/deep_think/style_hints/prompt_file_routing/lcc_domain_injection/glossary_injection/formatting_fallback/user_prompt_references〕；C4 標記包裹 + 改前 .bak）
  - `2026-06-04_TRANSLATOR_Check_提示詞.md` — Check（C5 收官：三維度 Conformance 驗收 U1-U4/測試 §6.1-§6.4/不可動清單 + 一次性 mv plan_v10/tasks_v1/C1-C5 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒；不給 commit 建議、msg 寫 /tmp/）

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

### WORKFLOW 系列（流程治理）
- ✅ **WORKFLOW-3（2026-06-08 plan v3 → Tasks → C1-C3 → C4 Checkout 收官·DOC-Refactor·補流程治本）**
  - `2026-06-08_WORKFLOW-3_Check_提示詞.md` — Check（C4 Checkout 收官：Conformance 五維度驗收〔目標規格 plan_v3 U1-U5 / tasks §6 grep / 不可動清單 / 提示詞稽核 / 整合測試豁免聲明〕→ 全綠後 TODO 結案〔C1-C4 完成表 + 全量 hash 自癒〕+ baton 一次性 mv 歸檔〔plan v1/v2/v3→plans/ + tasks→tasks/ + C1-C3 報告→executions/〕+ C4 報告直寫 executions/；整合測試豁免〔DOC-Refactor 無 code handoff、§7.2 + plan Q2-Q3〕明載；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit；WORKFLOW-3 全案結案）
  - `2026-06-08_WORKFLOW-3_C3_run_提示詞.md` — C3 Run（framework §4.1 計畫檔結構契約 自列八章節 → 改引用 template_plan.md 為 plan 結構 SSOT〔保留「不寫程式碼純分析」哲學句 + 模板含哪些章 + 跨 Phase 接縫契約唯一源引用 WORKFLOW_SOP §7〕；不刪 §4.2 執行報告契約及其他章；§99.2 v4；改前 .bak + 兩條 grep 驗收；執行報告暫存 baton 嚴禁 mv、C4 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit；C3=最後內容 commit、下一步 C4 Checkout）
  - `2026-06-08_WORKFLOW-3_C2_run_提示詞.md` — C2 Run（template_plan.md 升 plan 結構 SSOT：§3 後插兩新章〔§4 跨 Phase 接縫契約 三欄式範本 + 交叉引用 WORKFLOW_SOP §7 / §5 變動風險與相容性評估 三欄式範本 + 對齊 framework §4.1 #5〕+ 重編號原 §4-§7→§6-§9 + §0 改版觸發 §1–§7→§1–§9 + §99 同步 + Revision；改前 .bak + 四條 grep 驗收〔含 grep -c '^## §' 章節數 +2〕；執行報告暫存 baton 嚴禁 mv、C4 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit；C3 依賴本 C2 SSOT 先確立）
  - `2026-06-08_WORKFLOW-3_C1_run_提示詞.md` — C1 Run（WORKFLOW_SOP.md 新增 §7 跨 Phase 接縫契約〔§7.1 producer/consumer/key 同基準 + worked example 修正版 #1 + 反例 / §7.2 收官前整合測試 + key-changing transform + Checkout 必驗 + 顯式豁免〕+ §3 強制規則整合測試前置一行 + §4.2 A6〔6 項〕+ §99.1 重複防護 + §99.2 v4；改前 .bak + 六條 grep 驗收〔含 A5 無動態內容〕；執行報告暫存 baton 嚴禁 mv、C4 才歸檔；msg 寫 /tmp〔Opus 4.8 1M 署名〕、不自發 commit）
  - `2026-06-08_WORKFLOW-3_Tasks_提示詞.md` — Tasks（依 plan v3〔§8 Q6/Q8 定案〕拆 DOC-Refactor commit：WORKFLOW_SOP §7 跨 Phase 接縫契約〔producer/consumer/key 同基準 + worked example 修正版 #1〕+ 收官前跨 Phase 整合測試〔含 key-changing transform、Checkout Conformance 必驗〕+ §4.2 A6 + template_plan 升 plan 結構 SSOT〔接縫契約 + 變動風險章〕+ framework §4.1 改引用 template〔根治 drift〕；各 Commit 各產執行報告暫存 baton、最後 Checkout 一次性歸檔；純文件 grep 驗收無 pytest；不預設 commit 數/名、自行規劃；含 §0.5 成果盤點 + §8 六維度表）
  - `2026-06-08_WORKFLOW-3_plan_提示詞.md` — plan（RAG-ASYNC #1 接縫缺陷治本：WORKFLOW_SOP 加「跨 Phase 接縫契約」〔plan 必凍結 handoff producer/consumer/key 同基準〕+「收官前跨 Phase 整合測試」強制條款〔真 transform、Checkout Conformance 必驗〕+ §4.2 A6 + framework §4.1 同步；純規格含 Open Questions、不給 commit、存 baton）

### RAG-ASYNC 系列（P4 共用真理源）
- 🔵 **CHAT-STRUCT-1（2026-06-08 plan·#5 選 C·結構化欄位確定性回答·待 baron 過目）**
  - `2026-06-08_CHAT-STRUCT-1_plan_提示詞.md` — plan（#5 履歷聯絡資訊 name/phone/email 不入向量、RAG 撈不到；選 C：chat router 偵測結構化意圖→DB metadata 確定性回答、繞過 RAG；純規格含 Open Questions、不給 commit、存 baton 待 tasks）
- 🟡 **RAG-ASYNC-HOTFIX-3（2026-06-08 BE-Hotfix·#4 zh 履歷 per-section·選 B·Run 落地）**
  - `2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_run_提示詞.md` — HOTFIX-3 Run（落地：`pipelines/resume_pipeline.py` `run_phase3` is_zh 分支 `_single_container_sections`→有 section 時走 `ctx.ingestion.tiles` 不翻譯、複用 `_collect_render_slots`+`_collect_rag_sections(translate=False)` 建 per-section rag_sections〔summary_key=原文 zh path、與 P2/#1 chunk node_key 天然對齊、無跨譯落差〕、無 section 退單一容器兜底；不改 zh_text=full_text〔final_zh byte 不變〕/en 主路/degraded；`# === [RAG-ASYNC-HOTFIX-3 HOTFIX-3 START/END] ===` 包裹 + 2 .bak + 補 3 測試〔zh per-section / zh 無 section 兜底 / 接 #1 摘要對位〕；單一 commit 一次性歸檔；msg 寫 /tmp、嚴禁自發 commit；⚠️ zh 來源 golden 須重捕、en 不需）
  - `2026-06-08_RAG-ASYNC-HOTFIX-3_doc_提示詞.md` — Hotfix doc（#4 is_zh 路單一容器→zh 履歷無 per-section chunk、size-cap 切任意窗；選 B：is_zh 有 section 走 ctx.ingestion.tiles 不翻譯、複用 `_collect_render_slots`+`_collect_rag_sections(translate=False)` 建 per-section rag_sections〔summary_key=原文 zh path、與 P2/#1 天然對齊〕；依賴 #1 slot key；doc-only 程式碼 diff 寫文件、實檔未動、含 commit 草稿、存 baton 待 Run）
- 🟡 **RAG-ASYNC-HOTFIX-2（2026-06-08 BE-Hotfix·#2 補產 rag_tree·選 B 完整版·Run 落地）**
  - `2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_run_提示詞.md` — HOTFIX-2 Run（落地：`processor/rag_indexer.py` 新增 `build_rag_tree`〔依 ctx.rag_sections 自建完整 rag_tree：key_map key=B 軌 chunk Header(=node_key)→`/sections/{i}/content/0` + 巢狀節點帶 translated_content/translated_title〕+ `index()` 加 `rag_tree_path` 參數寫 `final_{paper}_rag_tree.json`〔IO 失敗優雅降級〕；`pipelines/resume_pipeline.py` `run_phase4` 傳 `paper_manager.rag_tree_path` + ingestion title；零改 rag_retriever/ai_core；`# === [RAG-ASYNC-HOTFIX-2 HOTFIX-2 START/END] ===` 包裹 + 4 .bak + 補 4 測試〔key_map 對位 chunk Header / 節點含 translated_content / run_phase4 寫 rag_tree / retriever 章節引用整合〕；單一 commit 一次性歸檔；msg 寫 /tmp、嚴禁自發 commit）
  - `2026-06-08_RAG-ASYNC-HOTFIX-2_doc_提示詞.md` — Hotfix doc（#2 B 軌不產 rag_tree.json→檢索端章節引用/paper_title/公式相鄰降級；baron 選 B 完整產：rag_indexer 依 ctx.rag_sections 自建完整 rag_tree〔key_map+巢狀+translated_title+公式〕對等 A 軌；doc-only：程式碼 diff 寫進文件、不動實檔、含 commit 草稿、存 baton 待 Run）
- 🟡 **RAG-ASYNC-HOTFIX-1（2026-06-08 BE-Hotfix·#1 key 穿線 + #3 dead code·Run 落地）**
  - `2026-06-08_RAG-ASYNC-HOTFIX-1_HOTFIX-1_run_提示詞.md` — HOTFIX-1 Run（落地：`pipelines/resume_pipeline.py` `_collect_render_slots` title slot 帶原文標題 path `key` 穿線 + `_collect_rag_sections` 存 `summary_key`〔原文 path〕；`processor/rag_indexer.py` `_walk` 以 `summary_key` 首選查節點摘要〔無則 fallback node_key/title 向後相容〕；移除 dead `_load_index_meta`〔#3〕；`# === [RAG-ASYNC-HOTFIX-1 HOTFIX-1 START/END] ===` 包裹 + 4 .bak；補 3 測試〔`test_summary_key_lookup_crosslang`/`test_summary_key_absent_falls_back`/`test_seam_p3_to_p4_section_summary_attaches`〕；單一 commit 一次性歸檔 mv hotfix.md→hotfixes/+執行.md→executions/；msg 寫 /tmp、嚴禁自發 commit；改 B軌召回須重捕 resume golden）
  - `2026-06-08_RAG-ASYNC-HOTFIX-1_提示詞.md` — Hotfix doc（第一性原理體檢發現 #1 section_summaries 原文 key vs 譯文 key 對不上→Chapter Summary 永遠進不了 chunk、C5 白做〔doc 階段 live repro 證〕；修法：`_collect_render_slots` title slot 帶原文標題 path key、`_collect_rag_sections` 存 `summary_key`、`rag_indexer._walk` 以 summary_key 首選查〔向後相容 fallback〕+ 移除 dead `_load_index_meta`〔#3〕+ 補接縫整合測試；**baron 選 doc-only：碼已還原、hotfix.md 留 baton 待過目後下 Run**；#2/#4/#5 分流 backlog）
- ✅ **RAG-ASYNC P4 RAG 索引共用真理源（2026-06-07 plan → 2026-06-08 Tasks → C1-C6 + C7 收官）**
  - `2026-06-08_RAG-ASYNC_Check_提示詞.md` — C7 Check（Conformance 五維度驗收〔plan_v2 §2 U1-U6 / tasks §6 grep+pytest / 不可動清單 git 證據 / 提示詞稽核 / msg 完整性〕→ 全合規後 TODO 結案〔C1-C7 完成表 + hash 全量自癒〕+ baton 一次性 mv 歸檔〔plan_v2→plans//tasks→tasks//C1-C7 報告→executions/〕+ baton 乾淨度；嚴禁自發 commit、msg 寫 /tmp；RAG-ASYNC 全案結案、chunks=1 修復、B 軌零 A 軌依賴）
  - `2026-06-08_RAG-ASYNC_C6_run_提示詞.md` — C6 Run（BE-Refactor Wire P4：`run_phase3` 附加封存譯後 section 結構〔title/level/content/children〕至旁路 `ctx.rag_sections`〔is_zh/degraded 容器降級、不改 final_zh/en 輸出〕；`run_phase4` 移除 `from processor.rag_processor import RagProcessor`〔L73〕改呼 `rag_indexer.index(譯後結構 + section_summaries + doc_type)`、不再餵 final_zh_path；交付 RagDbSpec 不變、paper_db_id None 降級；test P4 改 mock 驗 indexer 呼叫/chunks 量級/零 LLM；`# === [RAG-ASYNC C6 START/END] ===` + 改前 .bak；B 軌全鏈零 rag_processor 依賴、chunks=1 退化修復）
  - `2026-06-08_RAG-ASYNC_C5_run_提示詞.md` — C5 Run（BE-Refactor P2 統一六步：`resume_pipeline.run_phase2` 四步→六步——② 產章節摘要〔原文、非 book 1 次批次、可併①〕+ ⑥ 以全文摘要引導一次性批次翻全部章節摘要→繁中 section_summaries〔超 token 拆批〕；三安全鎖〔批次非 N / 非致命 logger.warning exc_info+extra_fields 不阻 reading_ready / 可量測 performance_metric phase=P2〕；交付 GlossaryReadySpec.section_summaries；test 加 3 測試〔key 對位/批次次數/異常 fallback〕；`# === [RAG-ASYNC C5 START/END] ===` + 改前 .bak）
  - `2026-06-08_RAG-ASYNC_C4_run_提示詞.md` — C4 Run（BE-Refactor 向量落庫 + ④ conformance：`rag_indexer.py` 加 `index()`——build_chunk_markdown → MarkdownHeaderTextSplitter 切 # → is_chunk_meaningful 過濾 → EmbeddingModel 批量 → FAISS.from_documents(MAX_INNER_PRODUCT) save_local → paper_chunks 批量〔embedding 交易外、極短交易、paper_db_id None 降級僅 FAISS+meta〕→ 自寫 index_meta.json → RagDbSpec；禁 import rag_processor〔write_index_meta_json 自實作〕；test 加 conformance〔B 軌 vector store → rag_retriever.load_vector_store 讀回召回〕；`# === [RAG-ASYNC C4 START/END] ===` + 改前 .bak）
  - `2026-06-08_RAG-ASYNC_C3_run_提示詞.md` — C3 Run（BE-Refactor 新模組：新建 `processor/rag_indexer.py`〔禁 import rag_processor〕——`build_chunk_markdown` DFS 走訪 section 樹 Stage 1 Strategy B header augment〔# + Context + Chapter Summary〔缺則略降級〕+ 內文〕+ Stage 2 size-cap 遞迴子切〔超 EMBEDDING_MAX_TOKENS_PER_ITEM、子塊重貼前綴〕+ 自實作 _is_chunk_meaningful〔≥3 + email/phone/url 保留〕；本 commit 僅產 chunk 文件清單不嵌入；新增 `tests/test_rag_indexer.py`〔多塊/格式降級/size-cap/門檻〕；檔頂 `# === [RAG-ASYNC] ===`）
  - `2026-06-08_RAG-ASYNC_C2_run_提示詞.md` — C2 Run（BE-Refactor 合約欄位：`contracts.py` GlossaryReadySpec 移除 Book 專用 chapter_summaries、新增 `section_summaries: Optional[Dict[str,str]]=None`〔五路通用節點摘要、key 對位巢狀樹、繁中、frozen/extra=forbid 不破〕+ 全庫對齊引用〔resume_pipeline/test_pipe_core〕+ pytest 全綠；`# === [RAG-ASYNC C2 START/END] ===` 包裹 + 改前 .bak）
  - `2026-06-08_RAG-ASYNC_C1_run_提示詞.md` — C1 Run（DOC-Refactor 規格文件同步：母 plan v10 §U2/§U6 + PIPE-SPEC §1.1②/§1.4/§1.3〔含修 resume P3「100% Bypass」doc-drift〕+ 兩檔 §99.2 Revision；HTML 註解包裹 + 改前 .bak；零 Python；baton 暫存不 git add、僅 .bak 入庫）
  - `2026-06-08_RAG-ASYNC_Tasks_提示詞.md` — Tasks（BE-Refactor 依 plan_v2 七定案 D1-D7 拆 commit；C1 規格同步〔母 plan v10 + PIPE-SPEC、含修 §1.3 P3 doc-drift〕不含 Python；代碼段 processor/rag_indexer.py 全重寫零 import rag_processor + GlossaryReadySpec section_summaries 取代 chapter_summaries + run_phase2 統一六步 section_summaries + run_phase4 改呼自有模組 + Strategy B/size-cap 子切 + ④ conformance 測試；最後 Checkout 一次性 baton 歸檔；§0.5 成果盤點 + §8 六維度表）
  - `2026-06-07_RAG-ASYNC_plan_提示詞.md` — plan（針對 B 軌 P4 chunks=1 退化 + 偏離 SPEC §1.4/R4.3 之根因，建 P4 共用真理源：新模組自生 Strategy B chunk-md〔# + Context + Chapter Summary + content〕、不 import rag_processor、吐凍結 RagDbSpec；section_summaries 全 P2 同步產〔並行/非致命/可量測三鎖〕；含母 plan v10 §U2/§U6 + PIPE-SPEC §1.1②/§1.4/§1.3〔順手修 resume P3「100% Bypass」doc-drift〕同步；不含 commit 拆分；依 template_plan 產 baton/）

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

- 🟡 **PIPE-RESUME ResumePipeline 策略管線（2026-06-04 Tasks + C1 WIP）**
  - `2026-06-04_PIPE-RESUME_Tasks_提示詞.md` — Tasks（BE-Refactor Commit 拆分含最後 Checkout 收官；plan_v1〔§99.2 內部 v8、四輪對接稽核定稿〕ResumePipeline 四 Phase 策略：P1 Vision 整份解析+去浮水印+四欄 / P2 4 步循序〔LCC→做摘要→Glossary 自癒→DEEP_THINK 翻摘要〕/ P3 100% Bypass+doc_type='resume' / P4 非同步 RAG ≥3 技能詞保護；對齊 PIPE-CORE 落地 ABC run_phase1..4/四凍結合約/三大真理源/PIPE-SCAFFOLD 影子；custom_metadata 列硬前置不自落地；中間 Commit 留 baton、唯 Checkout 一次性歸檔保留 _v1）
  - `2026-06-04_PIPE-RESUME_C1_run_提示詞.md` — C1 Run（策略骨架與工廠註冊：新建 pipelines/resume_pipeline.py `@PipelineFactory.register('resume')` class ResumePipeline(DocumentStrategy) + run_phase1..4 NotImplementedError stub + self._raw_meta interim 暫存欄，`=== [PIPE-RESUME C1 START/END] ===` 包裹；純新建檔零既有改動）
  - `2026-06-04_PIPE-RESUME_C2_run_提示詞.md` — C2 Run（P1 Ingestion：實作 run_phase1 複用 ResumeProcessor Vision 核心整份解析+去浮水印、抽 candidate_name→title 建 IngestionMetadataSpec〔零 Abstract/LCC/Glossary〕、phone/email/domain 暫存 self._raw_meta interim 穿線，`=== [PIPE-RESUME C2 START/END] ===` 包裹 + 改前 .bak；baron AskUserQuestion 拍板擴 context.py 加 pdf_path/owner_id + web_server 影子派發傳值 + P1 全鏈編排）
  - `2026-06-04_PIPE-RESUME_C3_run_提示詞.md` — C3 Run（P2 Glossary & Context Prep 四步自癒：run_phase2 ①normalize_to_lcc(raw_domain+context_text) ②做履歷摘要 ③GlossaryManager 自癒〔摘要+LCC 注入 prompt context、LLM 交易外〕④Translator(DEEP_THINK)→translated_abstract + lcc→Domains.name 唯讀免交易→domain_name；交付 GlossaryReadySpec，`=== [PIPE-RESUME C3 START/END] ===` 包裹 + 改前 .bak）
  - `2026-06-04_PIPE-RESUME_C4_run_提示詞.md` — C4 Run（P3 Translation & Restore 100% Bypass：run_phase3 建 InjectionContext〔lcc/glossary/zh_summary←P2 translated_abstract/domain_name/doc_type='resume'〕→ 正文整份 Translator.translate(NORMAL,content) 不切 Section/不開 Sliding Window → md_restore 純樣板渲染 → final_zh_path/final_en_path → BilingualMarkdownSpec〔translated_abstract 沿用 P2、必填〕；嚴禁 AI Questions/Summary，`=== [PIPE-RESUME C4 START/END] ===` 包裹 + 改前 .bak）
  - `2026-06-04_PIPE-RESUME_C5_run_提示詞.md` — C5 Run（P4 Async RAG ≥3：run_phase4 讀 ctx.bilingual.final_zh_path → RagProcessor()._create_vector_store〔vectors_path + paper_db_id〕→ _is_chunk_meaningful(doc_type=resume ≥3 保 email/phone/url) → replace_paper_chunks 批量寫庫〔DB 交易不含 LLM/Embedding、paper_db_id None 優雅降級〕→ 讀 index_meta.json + chunks_total → RagDbSpec；錯誤 logger.warning(exc_info)+拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready，`=== [PIPE-RESUME C5 START/END] ===` 包裹 + 改前 .bak；四 Phase 全落地）
  - `2026-06-04_PIPE-RESUME_C6_run_提示詞.md` — C6 Run（單元測試：新建 tests/test_resume_pipeline.py mock LLM/Embedding 隔離；策略分派 get_strategy('resume')→ResumePipeline 無 doc_type 分支 / P1 IngestionMetadataSpec 無 Abstract/LCC/Glossary / P2 normalize_to_lcc cache+fallback general+GlossaryReadySpec abstract/translated_abstract/domain_name+缺詞自癒+凍結 / P3 100% Bypass+doc_type='resume'+translated_abstract 沿用 / P4 _is_chunk_meaningful ≥3 保 email/phone/url+RAG 失敗不阻 reading_ready，`# === [PIPE-RESUME C6 START/END] ===` 包裹、純新增檔）
  - `2026-06-04_PIPE-RESUME_C7_check_提示詞.md` — Check（C7 收官：Conformance 三維度驗收〔目標規格 U1-U5 / 測試 §6 / 不可動清單〕+ 提示詞歸檔稽核 + msg 草稿完整性 → 全合規後一次性 mv plan_v1〔保留 _v1〕/tasks/C1-C7 報告至正式目錄 + TODO 結案〔C1-C7 完成表 + 索引 ✅〕+ 歷史全量 Hash 自癒；不自發 commit、msg 寫 /tmp；PIPE 縱向五路第 1 路全案結案）
  - `2026-06-04_PIPE-RESUME_C7-hotfix_run_提示詞.md` — C7-hotfix Run（BE-Hotfix 策略註冊缺失：影子測試上傳履歷觸發 NullStrategy→P1 NotImplementedError 阻斷；根因 runtime 路徑無人 import resume_pipeline→@register('resume') 不觸發；修法 pipelines/__init__.py 補 `from pipelines import resume_pipeline`〔`# === [PIPE-RESUME C7-hotfix START/END] ===` 包裹〕+ .bak 備份 + factory._registry 驗證；移出 baton→hotfixes/）
  - `2026-06-04_PIPE-RESUME_C8-hotfix_run_提示詞.md` — C8-hotfix Run（BE-Hotfix 影子論文 DB 寫入缺失：影子 P1-P4 全綠+生實體檔但前端不顯示；根因 run_pipeline_shadow 漏 paper_manager.upsert_paper→Paper row 未建→list_papers 讀 DB 撈不到；修法 web_server.py 影子派發尾端補 upsert_paper〔校正版 str 絕對路徑+ctx.bilingual 守衛+'high'+doc_type-agnostic 五路通用，`# === [PIPE-RESUME C8-hotfix START/END] ===` 包裹〕+ web_server .bak；移出 baton→hotfixes/；Run 提示詞 §2 為校正前舊版、以規劃文件校正版為準）
### VISION-HOTFIX 系列
- 🟡 **VISION-HOTFIX-1 Vision 轉錄 temperature 確定化（2026-06-06 文件 + Run）**
  - `2026-06-06_VISION-HOTFIX-1_run_提示詞.md` — Run（落地：`settings.py` 加 `LLM_VISION_TEMPERATURE`(0.0) + `llm/client.py` `chat_with_images` 加可選 `temperature` 參數〔預設 None 向後相容、非 None 才注入 GenerateContentConfig〕+ `processor/resume_processor.py` `_analyze_resume` 傳 `temperature=settings.LLM_VISION_TEMPERATURE`；`tests/test_resume_processor.py` 追加 test_vision_passes_temperature_zero + test_chat_with_images_wires_temperature；`# === [VISION-HOTFIX-1 START/END] ===` 包裹 + 4 .bak；pytest+grep+SOP；收官 mv hotfix.md+執行.md→hotfixes/；⚠️ 共用 A軌 pdf2md+B軌 P1、Vision 輸出變→清 _capture_work 後重捕 resume golden）
  - `2026-06-06_VISION-HOTFIX-1_doc_提示詞.md` — Hotfix 文件撰寫（BE-Hotfix plan：Vision pdf2md 每次輸出抖動 13126/13233/13281；真因＝`llm/client.py:308` `chat_with_images` `GenerateContentConfig` 未設 temperature→吃 Gemini 預設 ~1.0 高溫採樣、忠實轉錄卻隨機；唯一呼叫者 `resume_processor.py:157`；修法＝settings 加 `LLM_VISION_TEMPERATURE`(0.0)+`chat_with_images` 加可選 `temperature` 參數〔預設 None 向後相容〕注入 config+ResumeProcessor 傳值；切頁救不了〔temp 才是槓桿〕；依 template_hotfix 產 `baton/2026-06-06_VISION-HOTFIX-1_..._hotfix.md` 含 3 檔 diff+測試+commit；⚠️ 共用 A軌 pdf2md+B軌 P1、Vision 輸出變→須重捕 resume golden〔自此可重現〕；不動 .py、Run 待 baron）

### RESUME-PERF 系列
- ✅ **RESUME-PERF-1 run_phase3 逐 section 翻譯並行化（2026-06-06 收官）**
  - `2026-06-06_RESUME-PERF-1_Check_提示詞.md` — C4 Check（Conformance 三維度驗收〔plan §2 U1-U7 / tasks §6 grep+pytest〔含 C3 4 並行測試〕/ 不可動清單 git 證據〕+ SOP 核查 + 提示詞稽核 + msg 完整性 → 全合規後 TODO 結案〔C1-C4 完成表 + hash 自癒〕+ baton 一次性 mv 歸檔〔plan_v1→plans//tasks→tasks//C1-C4 報告→executions/〕；嚴禁自發 commit、msg 寫 /tmp；RESUME-PERF-1 全案結案）
  - `2026-06-06_RESUME-PERF-1_C3_run_提示詞.md` — C3 Run（Unit Tests：`tests/test_resume_pipeline.py` 追加 4 並行專屬測試〔mock 確定化 `f"ZH::{text}"`〕——`test_p3_parallel_order_byte_equal`〔多層 section byte 等拍保序+層級+段落〕/ `test_p3_parallel_concurrency_capped`〔patch `LLM_MAX_CONCURRENT=2`+lock 計數驗峰值 ≤ 2〕/ `test_p3_parallel_unit_error_isolated`〔單 unit 拋例外退原文、其餘正常、spec 交付〕/ `test_p3_parallel_degraded_single_call`〔heading 退化→`_translate_whole` 單呼叫不並行〕；`# === [RESUME-PERF-1 C3 START/END] ===` 包裹 + .bak；grep+pytest 全綠；報告暫存 baton 不 git add）
  - `2026-06-06_RESUME-PERF-1_C2_run_提示詞.md` — C2 Run（ThreadPool 並行翻譯：`pipelines/resume_pipeline.py` 檔頭 import `concurrent.futures.ThreadPoolExecutor` + `settings.LLM_MAX_CONCURRENT`；`_restore_sections_markdown` 逐 slot 序列翻譯→`ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)` 並行、`{index:future}` 保序回填〔實際 API 併發受既有 `LLMClient._api_semaphore` 限〕；單 unit future 拋例外→退原文 `slot["text"]`+`logger.warning(event=resume_translate_unit_fallback)` 異常隔離保交付；組裝段/退化/zh* 不動；`# === [RESUME-PERF-1 C2 START/END] ===` 包裹 + .bak；grep+SOP+pytest 既有 29 全綠〔行為等價〕；報告暫存 baton 不 git add）
  - `2026-06-06_RESUME-PERF-1_C1_run_提示詞.md` — C1 Run（Collect/Assemble 重構：`pipelines/resume_pipeline.py` 新增 `_collect_render_slots`〔遞迴鏡像走訪、不翻譯、append title/content/raw slot、title 記 level=min(2+depth,6)〕+ 重構 `_restore_sections_markdown`〔collect→**序列**翻譯→按序組裝：title→`#*level`+zh、content→`_normalize_paragraph_breaks`、raw→原文〕；**仍序列、輸出 byte 等價**〔既有 resume 測試全綠為基本盤〕；HEADING/PARA/META 邏輯原值搬移不改；`# === [RESUME-PERF-1 C1 START/END] ===` 包裹 + .bak；報告暫存 baton 不 git add）
  - `2026-06-06_RESUME-PERF-1_Tasks_提示詞.md` — Tasks（依 plan v2〔§7 OQ Q1-Q7 核准〕拆 4 commit：C1 Collect/Assemble 重構〔收集-組裝解耦、仍序列、行為等價〕→ C2 ThreadPool 並行翻譯〔序列→受限並行、受既有 `LLMClient._api_semaphore`/`LLM_MAX_CONCURRENT=6` 限流、單 unit 失敗退原文+warning〕→ C3 單元測試〔mock 確定化 byte 等拍/併發峰值≤上限/異常隔離/退化路徑〕→ C4 Checkout；baron 拍板「不必等五路、現在做」〔plan Q5 原 Flip 前屬優先序非依賴〕；含 §0.5 成果盤點/§8 六維度/末尾 Checkout 一次性歸檔，中間報告留 baton）
  - `2026-06-06_RESUME-PERF-1_plan_提示詞.md` — plan 撰寫（perf 候選：A軌 golden translate 序列 331.85s/77%、grep 確認 B軌 `_restore_one_section` 同樣序列 `_t`〔無 async/gather/ThreadPool〕；解法＝`run_phase3` 兩段式受限並行〔序列收集→ThreadPool 並行翻譯〔受既有 `LLMClient._api_semaphore`/`LLM_MAX_CONCURRENT=6` 限流〕→保序組裝〕、行為等價只改執行方式、HEADING/PARA/META/合約不動；依 template_plan 產 `baton/2026-06-06_RESUME-PERF-1_..._plan_v1.md`〔§2 U1-U7 / §3 grep / §4 不可動 / §6 驗證 / §7 OQ Q1-Q7〕；不含 commit 建議；實施時機＝resume 上線前、A軌不動）

### RESUME-P3 系列
- 🟡 **RESUME-P3 META-HOTFIX-1 P1 Meta 渲染進文件 header（2026-06-06 文件 + Run）**
  - `2026-06-06_RESUME-P3_META-HOTFIX-1_run_提示詞.md` — Run（落地：`pipelines/resume_pipeline.py` 新增 `_render_meta_header`〔讀 ctx.raw_metadata domain/organization/phone/email + ctx.ingestion.title 姓名含 (測試) + en domain 優先 gspec.domain_name、組 `# 姓名`+領域/機構/電話/Email **無序列表**、缺項省略、整包空回 ''〕+ `run_phase3` 寫出前 prepend zh/en；`tests/test_resume_pipeline.py` 追加 `test_p3_meta_header_rendered`〔# 王小明 (測試) 開頭 + 四欄值 + 各欄獨立 list item〕；`# === [RESUME-P3 META-HOTFIX-1 START/END] ===` 包裹 + 2 .bak；grep+pytest+SOP；收官 mv hotfix.md+執行.md→hotfixes/；改 B軌輸出須重捕 resume golden）
  - `2026-06-06_RESUME-P3_META-HOTFIX-1_doc_提示詞.md` — Hotfix 文件撰寫（BE-Hotfix plan 階段：P1 抽的 meta〔姓名/電話/email/領域/機構〕只到 DB〔raw_metadata 旁路終點＝web_server 寫庫〕、`run_phase3` 渲染端從不讀 → final 無 header；治標＝在 run_phase3 加 pipelines/ 私有 `_render_meta_header` 讀現有 `ctx.raw_metadata` 旁路 + `ctx.ingestion.title` 組 `# 姓名`+領域/機構/電話/Email **無序列表**〔缺項省略、list 規範保證一欄一行防 RAG-10 軟換行、(測試) 保留〕prepend final_zh/en；不動凍結合約〔轉正屬 INFRA-4 遠期〕；依 template_hotfix 產 `baton/2026-06-06_RESUME-P3_META-HOTFIX-1_hotfix.md` 含詳細真因 + 完整 helper + diff + commit msg + 設計待確認表；代號由 HEADER 改 META 避免與 HEADING 混淆；不動 .py、Run 待 baron；改 B軌輸出須重捕 resume golden）
- 🟡 **RESUME-P3 PARA-HOTFIX-1 B軌正文段落邊界正規化（2026-06-06 文件 + Run）**
  - `2026-06-06_RESUME-P3_PARA-HOTFIX-1_run_提示詞.md` — Run（落地：`pipelines/resume_pipeline.py` 新增 `_normalize_paragraph_breaks`〔移植 A軌 `_preserve_pipe_table` pipe-table-safe 單 `\n`→`\n\n`、不耦合 A軌 class〕+ `_restore_one_section` text item/字串 fallback 套用；`tests/test_resume_pipeline.py` 追加 `test_p3_text_paragraph_blank_line_normalized`〔兩段升 `\n\n` + pipe table rows 保單 `\n`〕；`# === [RESUME-P3 PARA-HOTFIX-1 START/END] ===` 包裹 + 2 .bak；grep+pytest+SOP；收官 mv hotfix.md+執行.md→hotfixes/；改 B軌輸出須重捕 resume golden）
  - `2026-06-06_RESUME-P3_PARA-HOTFIX-1_doc_提示詞.md` — Hotfix 文件撰寫（BE-Hotfix plan 階段：B軌正文兩段黏一起、A軌有留白；真因＝CommonMark 單 `\n`=soft break，A軌靠 `_write_to_md` 補 `\n\n` + `_preserve_pipe_table:629` 單 `\n`→`\n\n`，B軌 `_restore_one_section` 兩者皆無 + C2 停用 U4；baron 拍板「移植 `_preserve_pipe_table` 邏輯進 pipelines/、不耦合 A軌 class」；依 template_hotfix 產 `baton/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md` 含詳細真因 + 完整 helper `_normalize_paragraph_breaks` + diff + commit msg；不動 .py、Run 待 baron；改 B軌輸出須重捕 resume golden）
- 🟡 **RESUME-P3 HEADING-HOTFIX-1 B軌標題層級遞迴深度修復（2026-06-06 文件 + Run）**
  - `2026-06-06_RESUME-P3_HEADING-HOTFIX-1_run_提示詞.md` — Run（落地：`pipelines/resume_pipeline.py` `_restore_sections_markdown` 傳 depth=0 + `_restore_one_section` 簽名加 depth、移除 `sec.get("level")` 恆=1 短路改 `level=min(2+depth,6)`、children 遞迴 depth+1；`tests/test_resume_pipeline.py` 追加 `test_p3_heading_level_by_recursion_depth`〔3 層巢狀全 level=1 仍還原 ##/###/####〕；`# === [RESUME-P3 HEADING-HOTFIX-1 START/END] ===` 包裹 + 2 .bak；grep+pytest+SOP；收官 mv hotfix.md+執行.md→hotfixes/；改 B軌輸出須重捕 resume golden）
  - `2026-06-06_RESUME-P3_HEADING-HOTFIX-1_doc_提示詞.md` — Hotfix 文件撰寫（BE-Hotfix plan 階段：B軌履歷標題塌成全 h1、無階層；真因＝`_restore_one_section:562` `sec.get("level") or sec.get("heading_level")` 因 level 欄恆=1 短路永取 1；baron 拍板「直接用遞迴深度 depth 推算」`level=min(2+depth,6)`〔頂層 h2、children +1、上限 h6、等價 heading_level 但不依賴資料欄〕；依 template_hotfix 產 `baton/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md` 含詳細真因 + 完整 diff；不動 .py、Run 待 baron；改 B軌輸出須重捕 resume golden）
- 🟡 **RESUME-P3 B軌履歷翻譯品質重構（2026-06-05 Tasks）**
  - `2026-06-06_RESUME-P3_Check_提示詞.md` — Check（C6 收官：Conformance 三維度驗收〔目標規格 plan §2 U1-U8 / tasks §6 pytest+grep / 不可動清單〕+ 提示詞稽核 + msg 完整性 → 全合規後建 C6 執行報告 + TODO 結案〔C1-C6 完成表 + hash 全量自癒〕+ 一次性 mv plan/tasks/C1-C6 報告 → plans//tasks//executions/ + git add；嚴禁自發 commit、msg 寫 /tmp；末尾提醒 baron 重捕 Golden Baseline；RESUME-P3 全案結案）
  - `2026-06-05_RESUME-P3_C5_run_提示詞.md` — C5 Run（Unit Tests：`tests/test_resume_pipeline.py` 修 C1 carryover `test_run_phase1_contract`（FakeMd 寫含 section JSON、對齊 C1 opt-out 直讀 processed）+ 追加 C1 opt-out（不呼叫 TilingProcessor）/ C3 逐 section 標題正文分流翻譯+無整行英文標題殘留 / 無 doubling / C4 退化 fallback（單一巨 section→整檔）/ 契約 BilingualMarkdownSpec 完備；`# === [RESUME-P3 C5 START/END] ===` 包裹 + .bak；全套件除 env flake 全綠）
  - `2026-06-05_RESUME-P3_C4_run_提示詞.md` — C4 Run（heading 退化 Fallback：`run_phase3` 逐 section 前加退化偵測，section 數 < 2 或單一 section 文字佔比 > 85%（heading 抓取失敗）→ warning + 降級走 C3 的 `_translate_whole` 整檔翻譯 fallback、保證極限情況仍交付 BilingualMarkdownSpec；`# === [RESUME-P3 C4 START/END] ===` 包裹 + .bak；退化單元測試歸 C5）
  - `2026-06-05_RESUME-P3_C3_run_提示詞.md` — C3 Run（P3 逐 heading 重寫：重寫 `pipelines/resume_pipeline.py::run_phase3`，讀 tiles section 結構遞迴分流翻譯標題與正文並重組，替代 100% Bypass 整檔單發以解標題漏譯/原文中文重複；pipelines 內重建不耦合 A 軌 translate_processor；`# === [RESUME-P3 C3 START/END] ===` 包裹 + .bak；預期 `test_run_phase3_bypass_doctype_and_carryforward` 失敗待 C5 修）
  - `2026-06-05_RESUME-P3_C2_run_提示詞.md` — C2 Run（Translator U4 resume 停用：`processor/translator.py` translate U4 區塊加閘門 `if (ctx.doc_type or '') != 'resume':`、resume 停用 `。！？` 重切以保全條列/日期/地點原行結構；其他文體不變；`# === [RESUME-P3 C2 START/END] ===` 包裹 + .bak；grep + test_translator 不退化 + SOP；報告暫存 baton 不入 Git）
  - `2026-06-05_RESUME-P3_C1_run_提示詞.md` — C1 Run（P1 履歷 Tiling Opt-out：重構 `resume_pipeline.py::_build_tiles`，履歷強制繞過 TilingProcessor 向量計算、直接把 JsonProcessor 的 processed JSON 當 tiled JSON 加載；保全 ### heading 結構、P1 不跑 TextTiling embedding、滅 429；`# === [RESUME-P3 C1 START/END] ===` 包裹 + .bak；grep + test_resume_pipeline 不退化 + SOP；報告暫存 baton 不入 Git）
  - `2026-06-05_RESUME-P3_Tasks_提示詞.md` — Tasks（依 plan v3〔OQ Q1/Q2/Q3/Q4/Q9/Q10 核准〕拆 commit：P1 履歷 tiling bypass → P3 廢 100% Bypass 改逐 heading section 翻譯+還原〔pipelines/ 內重建、不耦合 A 軌 translate_processor〕+ resume 停用 translator U4 重切 + heading 退化 fallback → 單元測試 → Checkout；改 B軌輸出須與 TILING/SHADOW 合併重捕 Golden；通用化 chunking 歸 INFRA-3；含 §0.5 成果盤點 / §8 六維度 / 末尾 Checkout，中間報告留 baton）

### MODEL-11 系列
- ✅ **MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次（2026-06-06 收官）**
  - `2026-06-06_MODEL-11_C4_run_提示詞.md` — C4 Checkout（收官驗收與一次性歸檔：三維度 Conformance〔目標規格 U1-U7、U6 遷移/U7 Golden 屬 baron 運維 / tasks §6 grep+全套件 499 passed / 不可動清單 git 證據〕+ TODO 結案〔C1-C4 完成表 + hash 回填 + 索引 ✅〕+ baton 一次性 mv 歸檔〔plan_v1→plans//tasks→tasks//C1-C4 報告→executions/〕；§7 運維命令 regen_rag --all + capture resume --force；無業務代碼變動、msg 寫 /tmp）
  - `2026-06-06_MODEL-11_C3_run_提示詞.md` — C3 Run（Unit Tests：`tests/test_embedding_retry.py` 既有 `_make_instance_with_mock_client` model 對齊 gemini-embedding-001 + 追加 4 mock 測試〔real_batch_no_fallback 真批次 N→N spy _embed_one 0 呼叫保序 / auto_split_preserves_order monkeypatch EMBEDDING_BATCH_MAX_ITEMS=2 拆批 embed_content 2 次保序 / task_type_document_vs_query 攔 config.task_type DOCUMENT vs QUERY / embed_batch_429_falls_back_to_one patch _embed_batch 拋 429 退 _embed_one 保序〕；完全 mock embed_content 不打真 API；`# === [MODEL-11 C3 START/END] ===` 包裹 + .bak；pytest 全綠 + 全套件不退化 + SOP grep）
  - `2026-06-06_MODEL-11_C2_run_提示詞.md` — C2 Run（EmbeddingModel 真批次與 task_type：`config.py` embed_documents 廢 BATCH_SIZE=32 固定切分 → token-aware 貪婪封批〔cur_batch/cur_tokens、est=max(1,len(text)) 字元上界、封批臨界 len≥EMBEDDING_BATCH_MAX_ITEMS 或 cur_tokens+est>EMBEDDING_BATCH_MAX_TOKENS、殘留 flush〕+ 單段超 EMBEDDING_MAX_TOKENS_PER_ITEM 發 embedding_oversized_item warning 不截斷 + log 正名 embedding_429→embedding_batch_fallback+reason；_embed_batch 校驗/`_embed_one`/embed_query/embed_image 不動；MODEL-9-OPT C2 頂部過時註解更新〔換 -001 向量改變須 regen_rag --all + Golden 重捕〕；`# === [MODEL-11 C2 START/END] ===` 包裹 + .bak；grep+pytest+SOP）
  - `2026-06-06_MODEL-11_C1_run_提示詞.md` — C1 Run（Settings Config：`settings.py` 將 `EMBEDDING_MODEL_NAME` 預設換用 `gemini-embedding-001` + 追加 `EMBEDDING_BATCH_MAX_ITEMS`(100)/`EMBEDDING_BATCH_MAX_TOKENS`(18000)/`EMBEDDING_MAX_TOKENS_PER_ITEM`(2048) 三批次/Token 約束常數；`# === [MODEL-11 C1 START/END] ===` 包裹 + .bak；純常數新增 C2 才消費、行為等價〔除預設模型名〕；grep+import 印值+pytest 不退化）
  - `2026-06-06_MODEL-11_Tasks_提示詞.md` — Tasks（依 plan v2〔§7 OQ Q1-Q8 核准〕拆 4 commit：C1 settings 換 gemini-embedding-001 預設 + 批次段數/請求 token/單段 token 三常數 → C2 config.py embed_documents token-aware 貪婪拆批〔≤100 段且累計 token 守 20,000、字元保守上界估值〕+ log 正名 embedding_429→embedding_batch_fallback+reason + 過時註解更新〔task_type/_embed_one/embed_image 不動〕→ C3 test_embedding_retry.py 追加 4 測試〔真批次 N→N 不退逐筆 / 超量自動拆批保序 / task_type DOCUMENT+QUERY 斷言 / 真 429 fallback〕→ C4 Checkout；向量值改變、各環境 regen_rag --all + resume 單路 Golden 重捕屬 baron 運維非 commit；含 §0.5 成果盤點 / §8 六維度 / 末尾 Checkout，中間報告留 baton）

### MODEL-9-OPT 系列
- 🟡 **MODEL-9-OPT Embedding 連線與限流框架優化（2026-06-05 Tasks）**
  - `2026-06-05_MODEL-9-OPT_Check_提示詞.md` — Check（C4 收官：Conformance 三維度驗收〔目標規格 plan §2 / tasks §6 pytest+grep / 不可動清單 tasks §7〕+ 提示詞稽核 + msg 完整性 → 全合規後 TODO 結案〔C1-C4 完成表 + hash 全量自癒〕+ 一次性 mv plan→plans//tasks→tasks//C1-C3 報告→executions/ + git add；嚴禁自發 commit、msg 寫 /tmp；MODEL-9-OPT 全案結案）
  - `2026-06-05_MODEL-9-OPT_C3_run_提示詞.md` — C3 Run（Unit Tests：新建 `tests/test_embedding_retry.py` 4 測試〔A embed_query 429 退避 / B embed_image 503 重試 / C embed_documents 批次降級逐筆保序+warning / D Semaphore 併發上限〕、mock client.models.embed_content 不實打 API；`# === [MODEL-9-OPT C3 START/END] ===` 包裹；4 passed + embedding_normalize/llm_retry/tiling 不退化；報告暫存 baton 不入 Git）
  - `2026-06-05_MODEL-9-OPT_C2_run_提示詞.md` — C2 Run（Embedding Resilience Core：config.py EmbeddingModel 引入 `_api_semaphore=threading.Semaphore(EMBEDDING_MAX_CONCURRENT)` + embed_query/embed_image/_embed_batch〔新〕/_embed_one 套 `@retry_call`+`with semaphore` + embed_documents 改批次呼 _embed_batch 失敗降級 _embed_one 移除手動 time.sleep linear + 429 觀測 log；同步 tiling_processor.py 過時退避註解；`# === [MODEL-9-OPT C2 START/END] ===` 包裹 + 二檔 .bak；grep〔time.sleep/for attempt 0 命中〕+ test_embedding_normalize/llm_retry/tiling_paragraph + SOP；報告暫存 baton 不入 Git）
  - `2026-06-05_MODEL-9-OPT_C1_run_提示詞.md` — C1 Run（Settings Knob：settings.py 新增 `EMBEDDING_MAX_CONCURRENT=int(os.getenv(...,"5"))` 緊鄰 LLM_MAX_CONCURRENT、`# === [MODEL-9-OPT C1 START/END] ===` 包裹；純新增常數、C2 才消費、行為等價；改前 .bak、grep+test_embedding_normalize 驗收、SOP 無命中；執行報告暫存 baton 不入 Git）
  - `2026-06-05_MODEL-9-OPT_Tasks_提示詞.md` — Tasks（依 plan v3 拆 commit：config.py EmbeddingModel 引入 EMBEDDING_MAX_CONCURRENT Semaphore + embed_query/image/_embed_batch/_embed_one 套 @retry_call + 重構 embed_documents 降級 + 新建 test_embedding_retry.py；含 §0.5 成果盤點 / §8 六維度 / 末尾 Checkout commit；不改向量值不碰 Golden、可獨立先做；中間報告留 baton、唯 Checkout 一次性歸檔）

### PIPE-RESUME 系列（hotfix 區）
- `2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_run_提示詞.md` — SHADOW-HOTFIX-2 Run（🛑 **HALTED 未落地**：提示詞 §2 改 `translate_processor.py`〔A 軌、對 B 軌無效〕+ 採「加翻譯規則」v1 舊法，與現行已核准 hotfix.md〔3 處：web_server + `translator.py:40` + `resume_pipeline.py:109`、採「移除矛盾交回母提示詞」v2〕相矛盾；已停下呈報 baron 待裁示、未動業務代碼）
  - `2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_run_提示詞.md` — TILING-HOTFIX-1 Run（BE-Hotfix：TextTiling Embedding 429 速率超限批次化修復；先就地 bump hotfix.md 4 點〔task_type RETRIEVAL_QUERY→DOCUMENT 行為變更+邊界位移 / Golden Baseline 重捕防線 / 指數→線性退避修正 / 根治 C5-C7 test_tiling_paragraph 併發 429 flaky〕→ 改 `processor/tiling_processor.py:425` 逐筆 `[embed_query(b) for b in blocks]`→批次 `embed_documents(blocks)`〔1/32 請求+線性退避+順序保證、`# === [PIPE-RESUME TILING-HOTFIX-1 START/END] ===` 包裹僅此行〕+ .bak → tiling 三套件+全套件驗證 429 轉綠 → 收官 mv hotfix.md/執行.md→hotfixes/+git add + TODO ✅；msg 寫 /tmp、baron 手動 commit）
  - `2026-06-05_PIPE-RESUME_C7_check_提示詞.md` — C7 Check（Conformance 三維度驗收〔目標規格 plan_v1 §2 / tasks §6 pytest+grep / 不可動清單 tasks §7〕+ 提示詞歸檔稽核 + msg 完整性 → 全合規後 TODO 結案〔C1-C7 完成表 + 移除 active + 索引 ✅〕+ 一次性 mv plan_v1〔保留 _v1〕→plans//tasks→tasks//C1-C7 報告→executions/ + 母 plan v10/PIPE-SPEC 就地 git add 不 mv；嚴禁自發 commit、msg 寫 /tmp；v9 影子整合批次全案結案）
  - `2026-06-05_PIPE-RESUME_C6_run_提示詞.md` — C6 Run（Unit Tests：tests/test_resume_pipeline.py 修復 C3 遺留 _raw_meta 紅燈〔test_run_phase1_contract/test_run_phase2_flag_off 改對 ctx.raw_metadata〕+ 追加 v9 契約測試〔P1 raw_metadata 寫入+影子後綴 (測試) / P2 摘要先行步序+LCC 讀 raw_metadata fallback general / P3 constraints 注入 / C5 影子寫庫 meta_dict 含完整 raw_metadata+繼承 (測試)〕，`# === [PIPE-RESUME v9 C6 START/END] ===` 包裹 + .bak；恢復核心 pipelines/resume 測試全綠；執行報告不入 Git）
  - `2026-06-05_PIPE-RESUME_C5_run_提示詞.md` — C5 Run（Shadow DB Fidelity：web_server.py run_pipeline_shadow C8-hotfix 影子寫庫改由 ctx.raw_metadata 組整包 metadata_json〔對齊 A 軌保真〕+ title 沿用 ctx.ingestion.title〔已自帶 (測試)〕+ ctx.raw_metadata 空時防禦性 fallback 最小 meta_dict；僅呼叫既有 upsert_paper〔無裸 commit〕，`# === [PIPE-RESUME v9 C5 START/END] ===` 包裹 + .bak；執行報告不入 Git）
  - `2026-06-05_PIPE-RESUME_C4_run_提示詞.md` — C4 Run（P3 Business Constraints：新增模組常數 _RESUME_CONSTRAINTS〔公司/產品名保留、Email/電話/URL 原樣、技能詞英文、專利/期刊原文+對照〕+ run_phase3 InjectionContext 加 constraints=_RESUME_CONSTRAINTS〔共用 Translator _build_system_prompt ⑤ 自動貼「【額外譯文約束】」〕，`# === [PIPE-RESUME v9 C4 START/END] ===` 包裹 + .bak；執行報告不入 Git）
  - `2026-06-05_PIPE-RESUME_C3_run_提示詞.md` — C3 Run（P2 步序與讀取對齊：run_phase2 ①做摘要→②LCC 互換〔摘要先行、功能等價〕+ raw_domain 改讀 ctx.raw_metadata.get("domain") + 廢除 self._raw_meta〔__init__ + run_phase1 雙寫一併移除、ctx.raw_metadata 為唯一載體〕，`# === [PIPE-RESUME v9 C3 START/END] ===` 包裹 + .bak；執行報告不入 Git）
  - `2026-06-05_PIPE-RESUME_C2_run_提示詞.md` — C2 Run（P1 + Context：pipelines/context.py 加 `raw_metadata: Dict[str,Any]={}` 欄 + resume_pipeline.py run_phase1 寫 ctx.raw_metadata〔整包 meta〕+ 過渡期雙寫 self._raw_meta〔P2 仍可讀〕+ `_shadow` 時 title 加綴 (測試)，`# === [PIPE-RESUME v9 C2 START/END] ===` 包裹 + 二檔 .bak；執行報告不入 Git）
  - `2026-06-05_PIPE-RESUME_C1_run_提示詞.md` — C1 Run（Sync System Specs：就地同步 baton/ 三份 Markdown〔PIPE-RESUME plan_v1 + 母 plan v10 + PIPE-SPEC〕寫入 C7/C8-hotfix 史/raw_metadata 穿線/P3 翻譯隔離/P2 摘要先行/Revision+§7.1 Cleanup；純文件、baton/ 主文件不入 Git〔僅 .bak+報告+TODO+prompts git add〕、三份 .bak）
  - `2026-06-05_PIPE-RESUME_Tasks_提示詞.md` — Tasks（v9 整合、03:35 精修版取代 03:15：plan §99.2 v11 後拆分；C1 同步**三檔**〔PIPE-RESUME plan_v1 + 母 plan v10 + PIPE-SPEC〕寫入 raw_metadata 穿線/P3 翻譯隔離/Phase2 摘要先行/C7-C8 hotfix 史/Flip Cleanup → C2 P1+Context〔raw_metadata 欄+影子後綴〕→ C3 P2〔步序①②互換+讀 raw_metadata〕→ C4 P3 constraints → C5 影子寫庫保真 → C6 測試 → C7 Checkout；commit 代號本批次內部序、與原 C1-C7 區別）

### CHAT-EXPORT 系列（前端對話下載）
- 🟡 **CHAT-EXPORT-HOTFIX-1（2026-06-09 FE-Hotfix·Run 落地）**
  - `2026-06-08_CHAT-EXPORT-HOTFIX-1_run_提示詞.md` — HOTFIX-1 Run（落地：`static/index.html` `export-btn` handler `onclick=()=>`→`async()=>` + 移除 `window.location.href` 導覽式下載 → fetch→blob→`<a download>`〔含 !res.ok/404/catch 錯誤處理、`a.download={paper_id}_chat.md`〕、`// === [CHAT-EXPORT-HOTFIX-1 START/END] ===` 包裹、保留空對話防護；改前 .bak + 三條靜態 grep〔location.href.*chat/export 無命中 / createObjectURL 命中 / START/END 各 1〕；FE-Hotfix 一次性歸檔 mv hotfix.md→hotfixes/ + 執行報告直寫 executions/；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-08_CHAT-EXPORT-HOTFIX-1_doc_提示詞.md` — Hotfix doc（對話下載在 Dia 瀏覽器卡 8/8 不結束、Safari 正常；真因＝`static/index.html:2812` `window.location.href` 導覽式下載去 attachment URL，Dia 對「主框架導覽去 attachment」收尾異常〔配常駐 SSE〕；後端已證正確〔真 uvicorn+curl content-length 8004/無 chunked/Safari 正常〕；修法＝fetch→blob→`<a download>` 不依賴導覽語意、瀏覽器無關；doc-only 程式碼 diff 寫文件、實檔未動、含 commit 草稿、存 baton 待 Run）

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
  - `2026-06-13_RAG-12_C3_run_提示詞.md` — RAG-12 C3 Run（接線六處 marked.parse → renderMarkdownWithMath：paper L2806 + chat 5 處；保留函式內步驟6 marked.parse；grep 驗 renderMarkdownWithMath=7/marked.parse=1；TODO C3✅/C4 WIP）
  - `2026-06-13_RAG-12_C2_run_提示詞.md` — RAG-12 C2 Run（核心渲染管線 renderMarkdownWithMath：三階段順序佔位 + 無 lookbehind texmath 正則 + 步驟7 ESC 還原 + .katex-display CSS；僅定義不接線；grep+備份；TODO C2✅/C3 WIP）
  - `2026-06-13_RAG-12_C1_run_提示詞.md` — RAG-12 C1 Run（引入自託管 KaTeX 0.16.47 資產：vendor/katex css/js/字型 + fetch 腳本 + vendor README + index.html head 載入；備份+grep+pytest；TODO C1✅/C2 WIP + hash 自癒；baton 報告暫存）
  - `2026-06-13_RAG-12_Tasks_提示詞.md` — RAG-12 Tasks 拆分（依 plan_v7 拆 Commit：自託管 KaTeX 資產/正則核心/視圖+Chat 注入/驗證；§0.5 成果盤點 + §8 六維度表 + TODO 同步；baton 暫存待 Run）
  - `2026-06-12_RAG-12_plan_提示詞.md` — RAG-12 plan 產出（前端 KaTeX 數學渲染：marked-katex-extension + 自託管 KaTeX；解 `$$`/`$` loose inline 跨行真二維公式；FE-Refactor、含套件安裝檔與文件更新；baton 暫存待 plan review）
  - `2026-06-12_RAG-12_plan_提示詞.md` — RAG-12 plan（前端 KaTeX 數學渲染：marked-katex-extension + 自託管 KaTeX；勘查確認 delimiter＝loose inline `$$` 跨軟換行 + inline `$`、token 怪空格無害；附帶發現含數學段落 zh 未翻譯另立任務）
- ✅ **RAG-MULTI-1 跨文件多篇檢索覆蓋與引用修正（2026-06-09 plan v3 → Tasks → C1-C4 → C5 Checkout 收官·BE-Refactor）**
  - `2026-06-09_RAG-MULTI-1_Check_提示詞.md` — Check（C5 Checkout 收官：Conformance 三維度〔plan v3 §2 U1-U7 / tasks §6 grep+pytest〔C4 11 測試、全套件 546 passed〕/ 不可動清單〕+ 提示詞稽核 + msg 完整性 → 全綠後 TODO 結案〔C1 `5b9477a`/C2 `82b95b1`/C3 `b5f9ce4`/C4-C5 + 全量 hash 自癒〕+ baton 一次性 mv 歸檔〔plan v1/v2/v3→plans/ + tasks→tasks/ + C1-C4 報告→executions/〕+ C5 報告直寫 executions/；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit；RAG-MULTI-1 全案結案、根治全域 top-k 飢餓）
  - `2026-06-09_RAG-MULTI-1_C4_run_提示詞.md` — C4 Run（新建 `tests/test_rag_multi.py`〔檔頭 `# === [RAG-MULTI-1 C4] ===`〕mock vector store 確定化分數、**不 mock retrieve_multi 本體**、11 測試：per_paper_floor / 不足全拿 / 小 N 不暴漲〔floor=2 非 5〕/ cap 不超 / N>cap 最高分截斷 / 補位排除已保底 / 0 候選跳過 / cap override / 混型 book 100 chunk 不壓 resume / 單篇路徑不變 / 提示詞禁 [N]；純新建無 .bak；**嚴禁為過測試改業務碼〔測不符停下回報〕**；SOP+pytest 11 全綠+全套件；執行報告暫存 baton 不入 git、C5 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-09_RAG-MULTI-1_C3_run_提示詞.md` — C3 Run（`prompt/ai/ai_character_prompt.txt`「3. 引用源頭」段加禁令「只用《文件名》「章節」、嚴禁輸出 [1][2] 等純數字引用標記〔context 無編號清單、指向虛空〕」、`# === [RAG-MULTI-1 C3] ===` 標、保留既有引用語意；共載檢查 `grep ai_explain_prompt.txt` 無反向 [N] 則不動〔plan §8.1 點3〕；改前 .bak + §6.3 grep；C3 純提示詞無 .py → SOP 跳過合規；執行報告暫存 baton 不入 git、C5 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-09_RAG-MULTI-1_C2_run_提示詞.md` — C2 Run（`rag_retriever.py` `retrieve_multi_with_context` 廢全域 top-k、改每篇保底覆蓋演算法〔`N=len(paper_ids)`；`effective_floor=min(RAG_MULTI_FLOOR_K,max(1,cap//N))`；分組各取前 floor〔不足全拿〕→ floored；N>cap 按各篇最高分取前 cap 篇各 1；全域補位 pool=候選−已選、score 降序補到 cap；最終 score 降序〕+ `top_k`→cap override + import 去 RAG_MULTI_TOP_K；`settings.py` 移除 RAG_MULTI_TOP_K；`# === [RAG-MULTI-1 C2 START/END] ===` 包裹 + 2 .bak + 更新既有 hashtag 路由測試〔若斷言舊 top-k=7〕；不動單篇/threshold/context 格式/shadow；SOP+§6.2 grep+pytest；執行報告暫存 baton 不入 git、C5 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-09_RAG-MULTI-1_C1_run_提示詞.md` — C1 Run（`settings.py` 新增 `RAG_MULTI_FLOOR_K`(2)+`RAG_MULTI_MAX_CHUNKS`(15)、`# === [RAG-MULTI-1 C1 START/END] ===` 包裹；保留 `RAG_MULTI_TOP_K`〔C2 才廢、防中途 import 斷裂〕、不動 `RAG_SCORE_THRESHOLD`；純常數 C2 才消費、行為等價；改前 .bak + SOP 核查〔logging/database 無命中合規〕+ §6.1 grep+import 2/15+pytest；執行報告暫存 baton 嚴禁 mv/git add、C5 才歸檔；msg 寫 /tmp〔Opus 4.8 1M〕、不自發 commit）
  - `2026-06-09_RAG-MULTI-1_Tasks_提示詞.md` — Tasks（依 plan v3〔§9 五項 OQ 全定案〕拆 BE-Refactor commit：`retrieve_multi` 每篇保底覆蓋〔`effective_floor=min(floor_k,max(1,cap//N))`、不足全拿、補位排除已選、N>cap 按最高分截斷〕+ settings 廢 RAG_MULTI_TOP_K/立 FLOOR_K=2·MAX_CHUNKS=15 + 函式 top_k 改 cap override + ai_character_prompt 禁 bare [N]；**不給 commit 建議·自行拆分、末為 Checkout**；各 Commit 各產執行報告暫存 baton、Checkout 一次性 mv plan v1/v2/v3+tasks+報告歸檔；BE SOP 核查+pytest；含 §0.5 成果盤點 + §8 六維度表）
  - `2026-06-09_RAG-MULTI-1_plan_提示詞.md` — plan（`retrieve_multi_with_context` 全域 top-k=7 飢餓〔log 證 6 篇被擠成 2 人、李宗原 A+B軌 佔 5/7、吳焴倫碩士漏召〕→ 修法 A 每篇保底覆蓋 + 防爆 cap；問題 2 提示詞禁 bare [N] 引用、留《title》「章節」；**不做影子過濾〔維 B軌可見性〕**；retrieve_multi 無 doc_type 參數 = 五路通用；純規格含 Open Questions〔保底策略/top_k/citation/同人去重/五路驗證〕、不給 commit、存 baton 待 tasks）

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
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-2_doc_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-1b_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-1b_doc_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-1_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES-HOTFIX-1_doc_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_Check_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C6_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C5_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C4_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C3_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C2_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_C1_run_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SLIDES_Tasks_提示詞.md`
- 2026-06-11 — `2026-06-11_PIPE-SYNC-2_Check_提示詞.md`
