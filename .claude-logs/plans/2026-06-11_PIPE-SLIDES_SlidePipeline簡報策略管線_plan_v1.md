# PIPE-SLIDES SlidePipeline 簡報策略管線 · plan v1

> 工作流類別：**BE-Refactor**（新建 `pipelines/slide_pipeline.py` + 簡報 Vision 處理；零 A 軌改動）
> 必讀 SOP：logging_SOP + database_SOP
> 任務代號：**PIPE-SLIDES**（baron 拍板、取代母 plan §8.5 原「PIPE-VISUAL」條目名——同步事宜見 §9 Q6）
> 定位：PIPE 縱向五路絞殺**第 2 路**（Resume → **Slides** → Academic → LiteDoc → Book）；同步首落地 **MD-RESTORE 純樣板化之 slides 部分**（圖片 alt 對齊、雙 Caption 根除——母 plan §8.5 綁定）。

---

## §0 改版規則
- 改版觸發：§2 / §4 / §9 任一變動 → 直接改章節 + §99.2 加 Revision
- 多輪 review 累積（§1.9）：v1 初稿（baron 三輪設計討論 + A 軌實件品質模擬收斂）→ **v1.1 review 拍板（八 OQ 全結清）→ 可進 tasks**

---

## §1 TL;DR（概要）

新建 `SlidePipeline`（doc_type=`slides`）四 Phase 策略：**P1 每頁整頁存圖 + Vision 忠實轉錄（temp=0、條件滾動）+ 封面判定 + 跨頁統計去重**；**P2 統一六步（section=頁、摘要順產 raw_domain、頁摘要順產缺失標題）**；**P3 逐頁並行翻譯 + 圖片 alt 對齊（雙 Caption 物理根除）+ rag_sections 旁路**；**P4 完全照抄 rag_indexer 共用真理源（同頁短 items 合併 + ≥3 門檻）**。

**設計基礎**：① 母 plan / SPEC（含 PIPE-SYNC-2 剛凍結之 §1.3.1 Vision 共用規格、key 接縫契約、zh 路）；② Resume 第 1 路全部落地經驗零學費繼承（六步順序／翻譯順序／旁路封存／並行範式／四產物）；③ A 軌實件品質模擬（ST 電源簡報 18 頁列印版）實證 A 軌三病灶——**每頁三層描述疊加（~1/3 冗文、`slides_processor.py:155` 物理產生點）、Vision 零 temperature（每次重跑抖動）、table cell 塞 `###` 畸形**——本管線分別以 alt 對齊、§1.3.1、轉錄 constraints 根除。

**品質判定（模擬結論）**：同質保底（圖文對照物理策略同 A 軌）、四處確定升級（冗文去除／重現性／摘要 toolbar／RAG 頁粒度+摘要增強）、一處需本 plan 顯式規範（表格畸形）。

---

## §2 目標規格

### P1 Ingestion（視覺解析、零衍生語境）

| # | 規格 |
|---|---|
| U1 | **每頁整頁存圖 + Vision 轉錄**：fitz `get_pixmap` 逐頁渲染存 `images/page-N.png`（演算法參照 A 軌 `slides_processor.py` 之渲染/空白頁跳過/橫向 clip、**自建不 import**）；Vision 對頁圖忠實轉錄，遵循 **SPEC §1.3.1 共用規格**（忠實轉錄鐵律 + `LLM_VISION_TEMPERATURE=0` + 非確定性註記）。**條件式滾動**：偵測跨頁延續（判準見 Q1）才注入前頁內容；預設各頁獨立並行解析 |
| U2 | **封面判定**：第 1 頁 LLM 判定——是封面 → Title/公司/日期等入 `IngestionMetadataSpec.title` + 簡報專屬欄走 **`ctx.raw_metadata` 旁路**（resume 先例）；非封面 → **title fallback 檔名**、其餘欄位誠實留空 |
| U3 | **跨頁統計去重**（slides 專屬）：全頁轉錄後統計「出現於多數非封面頁之相同短行」（頁眉頁腳公司名）→ 剔除；**統計排除封面頁**（封面公司名＝metadata）。不用 A 軌 `md_cleaner` |
| U4 | P1 硬約束（凍結合約 ①）：零 Abstract/LCC/Glossary/翻譯/Embedding；**每頁＝一個 section**、processed JSON 直當 tiles（opt-out TextTiling、SPEC U8 先例）；`source_lang` 啟發式判定（沿 resume）；影子 `(測試)` 後綴 + 影子寫庫保真 |

### P2 Glossary & Context Prep（統一六步、section=頁）

| # | 規格 |
|---|---|
| U5 | **統一六步**（RAG-ASYNC 凍結、全形照抄）：① 產原文全文摘要（**同呼叫順產 `raw_domain` 一行**——封面常無領域欄、簡報屬性由內容定）→ ② 批次產**每頁摘要**（1 次 LLM；**頁無標題者同呼叫順產標題**）→ ③ `normalize_to_lcc(raw_domain, context=摘要)` → ④ Glossary 級聯自癒（`query_cascade` 先比對 → 缺詞 `extract_terms`〔**對全部提取內容**、注入摘要+LCC〕→ upsert 冪等；LLM 交易外）→ ⑤ 翻全文摘要（DEEP_THINK、`translated_abstract` 一次到位）→ ⑥ 全文摘要引導批次翻頁摘要 → `GlossaryReadySpec.section_summaries`。安全鎖三件（批次有界/非致命/可量測）+ `domain_name` P2 一次解析 |
| U6 | **key 接縫契約（slides 特化、根除 HOTFIX-2 重複標題覆蓋邊界）**：section key＝**`p{頁序}_{原文頁標題}`**——頁序保唯一（物理錨）、標題保可讀（引用顯示）；標題缺由 ② 順產。**P2 產／P3 帶（`summary_key`）／P4 取三方同此基準**（SPEC v6 key 契約之 slides 實例化） |

### P3 Translation & Restore（逐頁翻譯+排版還原；MD-RESTORE slides 部分首落地）

| # | 規格 |
|---|---|
| U7 | **逐頁翻譯**（頁=天然 section）：`InjectionContext(lcc, glossary, zh_summary=P2 譯後摘要, constraints, doc_type='slides')` 注入共用 Translator（NORMAL）；**摘要先翻、內文後翻、譯後摘要餵內文**（對齊 resume）。**並行照抄 RESUME-PERF-1**（ThreadPool + slot index 保序 + 既有 `_api_semaphore` 限流 + 單頁失敗退原文）。退化 fallback：頁結構異常 → 整檔單發兜底（判準 Q5） |
| U8 | **圖片 alt 對齊（雙 Caption 物理根除）**：每頁渲染為 `![{alt}](images/page-N.png)` + 轉錄譯文；**alt＝Vision description（`final_zh` 譯文／`final_en` 原文）**；**嚴禁**輸出 `*圖表：desc*` 獨立段與頁頂總述重複段（A 軌 `slides_processor.py:155` 病灶、實證每頁 ~1/3 冗文）——描述資訊全收斂進 alt、一處呈現 |
| U9 | **Vision 轉錄 constraints**（U1 prompt 級 + P3 譯文級）：表格 **cell 內禁 `###`/多層標題語法**（A 軌實證畸形）；品牌/產品名保留原文；術語 **Glossary 中英並列**；數字/單位原樣。規則由策略擁有、引擎共用執行（§1.2.3.1） |
| U10 | **結構封存（鐵律繼承）**：譯後逐頁旁路封存 `ctx.rag_sections`（`summary_key`=U6 key）；**zh 來源簡報**跳過翻譯仍建 per-section（SPEC U4）；**slides 不渲染 meta header**（封面頁已天然呈現、顯式不繼承 resume META-HOTFIX——防照抄出重複） |

### P4 Async RAG（完全照抄、零自選）

| # | 規格 |
|---|---|
| U11 | `rag_indexer` 共用真理源（零依賴 A 軌）：Strategy B header augment（`#`+Context+**頁摘要**）+ size-cap；**四產物缺一不可**（FAISS+paper_chunks+index_meta+rag_tree.json）；≥3 門檻；Embedding 交易外；失敗 `rag_status='failed'` 不阻 `reading_ready`。**同頁短 items 合併**：於 **P3 構造 rag_sections 時**將同頁短 text items 併單一 chunk（落點見 Q3、`rag_indexer` 不動） |

---

## §3 現況與證據

### §3.1 grep / 實件鋼鐵證據

**① A 軌雙 Caption 物理產生點**：`processor/slides_processor.py:155` `lines.append(f"\n*圖表：{figure_desc}*")`；prompt L33-35 要求 description 另放 `figure_description` 欄、但渲染時又吐獨立段。實件（ST 簡報列印版 18 頁、`baton/現代 AI 資料中心的全方位電源傳輸解決方案.pdf`）每頁可見「此圖展示了…」總述 + 「圖表：…」段雙重複（p3 該段 200+ 字）。
**② A 軌 Vision 零 temperature**：`grep 'chat_with_images\|temperature' processor/slides_processor.py` → **0 命中**（VISION-HOTFIX-1 只修 resume_processor）→ A 軌 slides 每次重跑抖動、golden 無固定靶。
**③ A 軌表格畸形**：實件 p6 `| ### 關鍵產品 | 1.…`——cell 塞 `###`+多行 list。
**④ A 軌整頁存圖既有演算法**：`slides_processor.py` L89 `images_dir` / L114 `get_pixmap` / L137 存檔 / L149 `![slide_NN](images/...)` / L167 `_is_empty` 空白跳過——B 軌 U1 參照重建。
**⑤ B 軌可繼承資產**（全部已落地）：統一六步（RAG-ASYNC C5）/ rag_sections 旁路 + key 契約（HOTFIX-1、SPEC v6）/ rag_tree 四產物（HOTFIX-2、SPEC v6）/ zh 路（HOTFIX-3、SPEC U4）/ §1.3.1 Vision 共用規格（PIPE-SYNC-2 C2）/ 並行範式（RESUME-PERF-1）/ raw_metadata 旁路與影子保真（v9）/ `PipelineFactory.register` + `pipelines/__init__` import（C7-hotfix 教訓）。
**⑥ 品質模擬結論**（A 軌實件 vs 本管線、2026-06-11）：同質保底（圖文對照同物理）、四升級（冗文/重現性/摘要 toolbar/RAG）、一需規範（U9 表格）。

### §3.2 三缺口已拍板解（baron 定案）
- 圖片實體鏈：**整頁當一張圖**（同 A 軌物理、grep ④ 證）。
- 頁 key：**`p{N}_{標題}`**、無標題由頁摘要呼叫順產。
- raw_domain：**全文摘要同呼叫順產**、餵 `normalize_to_lcc`。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| **頁摘要 section_summaries** | P2 ②⑥ 產（key=`p{N}_{原文頁標題}`、缺標題同呼叫順產） | P4 `rag_indexer._walk` 以 `summary_key` 查 | key＝**`p{頁序}_{原文頁標題}`**（頁序物理唯一、根除重複標題覆蓋）；P2 產／P3 帶／P4 取**同此基準**；譯後頁標題僅顯示不作 key |
| **rag_sections 旁路** | P3 譯後逐頁封存（text=譯文、`summary_key`=同上、譯後 title 另存） | P4 `rag_indexer.index` 消費 | 同 key；zh 來源跳譯仍建 per-section（SPEC U4） |
| **raw_metadata 旁路** | P1 封面判定產（公司/日期等簡報欄） | web_server 影子寫庫 `metadata_json` 保真 | 鍵名沿 resume 先例自由欄；title 走凍結合約 `IngestionMetadataSpec.title`（fallback 檔名、不得空） |
| **頁圖 ↔ alt ↔ description** | P1 存 `images/page-N.png` + Vision description | P3 還原 `![alt](images/page-N.png)`（alt=description 譯/原文） | 圖檔名＝`page-{頁序}`、與 section key 之頁序**同一序基準**；嚴禁另吐 `*圖表：*` 段（單一呈現點） |
| **raw_domain** | P2 ① 摘要同呼叫順產 | P2 ③ `normalize_to_lcc(raw_domain, context=摘要)` | 同一次 LLM 輸出、無跨呼叫對位問題；缺值 → None → DomainNormalizer 內容判定/general 降級兜底 |

> 反例錨點：① key 用「標題」不含頁序 → 連續同標題頁覆蓋（HOTFIX-2 邊界簡報高發）。② 描述同時進 alt 與獨立段 → 雙 Caption 復發。③ 去重統計含封面 → 封面公司名被誤殺、metadata 失源。**凍結：key 含頁序、描述單點呈現、去重排除封面。**

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| Golden D1 故意差異（刪 `*圖表：*` 段 + alt 改寫） | 結構差異大、機械比對必紅 | **改善型差異**走 GOLDEN-BASELINE 既有改善豁免條款裁決；plan 預載聲明 |
| 滾動式解析序列化成本 | 誤開＝13 頁串行、慢數倍 | Q1 觸發判準保守、預設關、各頁並行 |
| 表格畸形復發 | 同 Vision 同模型預設同病 | U9 prompt constraints + §8 畸形 grep 驗收 |
| 去重誤殺正文 | 短行重複可能是真內容（如每頁口號式結論） | Q2 門檻 + 僅限「短行」+ 白名單留 OQ |
| P2 順產欄位（raw_domain/頁標題）解析失敗 | JSON 欄缺 | 非致命降級（domain→None→內容判定；標題→`p{N}` 裸序）、不阻鏈 |
| 新路註冊漏 import | C7-hotfix 同型 | `pipelines/__init__` import + factory 註冊測試 |
| 影子併發擠壓 | PIPELINE_SEMAPHORE 既有（上限 1）兜底 | 沿用、不另設 |

---

## §6 不可動清單

- [ ] **A 軌全部**：`pipeline_core.py` / `processor/slides_processor.py`（病灶留 A 軌、Flip 一併下線）/ `md_restore_processor` / `rag_processor`——零改動。
- [ ] **第 1 路**：`pipelines/resume_pipeline.py` / `tests/test_resume_pipeline.py`——零改動。
- [ ] **三大真理源本體**：`translator.py` / `glossary_extractor.py` / `domain_normalizer.py`——只消費不改。
- [ ] **`processor/rag_indexer.py` 核心**：同頁合併落點在 slides 側（Q3 定案 P3 構造時）、rag_indexer 不動。
- [ ] **四凍結合約欄位結構**（contracts.py ①②③④）——slides 專屬欄一律走 `raw_metadata` 旁路。
- [ ] `web_server.py` 影子派發 scaffolding（已支援 doc_type 直通、無需改）；retrieve/lazy-load 層（LAZYLOAD-MULTI-1 已收）。
- [ ] 母 plan / SPEC 本體（本 plan 純引用；§8.5 條目改名與狀態更新屬收官同步、見 Q6）。

---

## §7 規格依據

- 母 plan v10：§8.5 PIPE-VISUAL 條目（L258、本任務前身）/ U3 Tiles 交付形狀（補註⁶）/ U10 五路絞殺序
- PIPE-SPEC（v6）：§1.1-§1.4 四合約 / **§1.3.1 Vision 共用規格** / §1.2.3.1 翻譯策略隔離+受限並行 / §1.4.1 key 契約+四產物 / zh 路（U4）
- 落地先例：RAG-ASYNC C5（六步）/ HOTFIX-1/2/3（key/rag_tree/zh）/ RESUME-PERF-1（並行）/ v9（raw_metadata/影子）/ VISION-HOTFIX-1（temp=0）/ C7-hotfix（register import）
- A 軌證據：`slides_processor.py` L33-35/89/114/137/149/155/167；實件 `baton/現代 AI 資料中心的全方位電源傳輸解決方案.pdf`（18 頁列印版）

---

## §8 驗證計畫

### §8.1 自動化單元測試（新建 `tests/test_slide_pipeline.py`）
1. 策略分派：`get_strategy('slides')` 回 SlidePipeline（含 `__init__` import 註冊測試）。
2. P1：封面判定兩路（metadata 入欄 / fallback 檔名 title 非空）；統計去重（mock 多頁重複短行剔除、封面排除）；每頁存圖檔名=`page-{N}`；空白頁跳過。
3. P2：六步契約（mock LLM）；**key=`p{N}_{標題}`**、無標題順產、**連續同標題頁 key 不撞**；raw_domain 順產缺值降級。
4. P3：逐頁翻譯分流；**alt=description 譯文、全文無 `*圖表：*` 段**（grep 斷言）；表格 cell 無 `###`（U9）；並行保序 byte 等拍 + 單頁失敗退原文（仿 RESUME-PERF-1 C3）；meta header 不渲染。
5. **§7.2 跨 Phase 整合測試（Checkout 必驗、含 key-changing transform）**：P2→P3→P4 串接 + **FakeTranslator 真改寫頁標題**（譯 title≠原文 key）→ 斷言 P4 chunk 含 Chapter Summary（頁摘要對位成功、`p{N}_` key 不受譯文影響）——正面滿足 §7.2 key-changing 要求。
6. P4：mock rag_indexer 消費 rag_sections+section_summaries；同頁短 items 合併後 chunk 數正確；四產物路徑傳遞。
7. zh 來源：跳譯仍建 per-section rag_sections。
- 全套件不退化。

### §8.2 手動 E2E（baron）
1. 影子上傳 ST 簡報（同一實件）→ B 軌 `(測試)` 件：閱讀視圖**圖文對照、無「圖表：」獨立段、無頁頂重複總述**；toolbar 雙語摘要顯示。
2. 對照 A 軌同件：冗文密度、表格渲染、重跑兩次輸出穩定（temp=0）。
3. chat：單篇問答引用顯「《簡報名》> p{N} 頁標題」；`#sst` 跨文件含此件。
4. Golden：`golden_baseline.py capture slides --force` 重捕（B 軌首件）+ diff 改善豁免裁決。

---

## §9 Open Questions（**全數定案** — 2026-06-11 baron review 拍板、八題 100% 認同）

| # | 問題 | 定案 |
|---|---|---|
| ~~Q1~~ | 條件式滾動觸發判準 | **✅ 預設關、各頁獨立並行**；僅頁標題含延續標記（「(續)」「cont'd」）或前頁表格截斷才對該頁開滾動（注入前頁）——最大化並行效能、極限場景精準觸發 |
| ~~Q2~~ | 統計去重門檻 | **✅ 短行（≤20 字）≥60% 非封面頁 → 剔除**；剔除清單入 log（防誤殺審計、E2E 抽查）；封面排除保 raw_metadata 不失源 |
| ~~Q3~~ | 同頁合併落點 | **✅ P3 構造 rag_sections 時（策略側）**——rag_indexer 為五路共用無狀態 SSOT、嚴禁塞 `doc_type=='slides'` 分支污染；構造期策略對頁結構最內聚 |
| ~~Q4~~ | U9 constraints 清單 | **✅ 品牌/產品原文、術語中英並列（升 BM25 召回）、cell 禁 `###`（Prompt+Translator 雙層約束）、數字/單位原樣**；tasks 前可微調條目 |
| ~~Q5~~ | P3 退化 fallback 判準 | **✅ 頁數=1 或 >50% 頁轉錄空/異常 → 整檔單發兜底**（單頁海報防無謂併發；大面積限流容災、不阻 reading_ready）|
| ~~Q6~~ | 任務代號與條目名 | **✅ PIPE-SLIDES 取代母 plan §8.5「PIPE-VISUAL」**、Checkout 時就地同步（HTML 包裹、沿 PIPE-SYNC-2 範式）；類名 `SlidePipeline`（SPEC 既名零改）——三位一體編碼對齊 |
| ~~Q7~~ | P3 切分 | **✅ 逐頁（非 Bypass）定案**——Bypass ⇒ P4 塌單一巨 chunk、失去按頁定位引用；逐頁使 Strategy B 頁摘要增強完美套用；承接 PIPE-SYNC-2 Q6 保留之決策、母 plan「P3 100% Bypass」句 Checkout 一併更正 |
| ~~Q8~~ | golden 處置 | **✅ B 軌首落地手動 E2E 確認排版升級後另捕 B 軌 golden**；與 A 軌 D1 差異（刪 1/3 雙 Caption 贅文）屬故意良性改善、走改善豁免不硬比 0%；後續修改對 B 軌 golden 守 0% | 

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | PIPE 第 2 路 SlidePipeline 四 Phase 策略規格（含 MD-RESTORE slides 部分首落地） |
| 權威源 | 本檔 §2 / §4；上游凍結 SPEC v6 + 母 plan v10 |
| 引用方 | tasks / executions（待產）；母 plan §8.5 條目（收官同步） |
| 不可動唯一源 | §6 |
| 改版觸發 | §2/§4/§9 變動 |

### §99.2 Revision 歷程
- v1.1 (2026-06-11)：baron review 拍板——**§9 八題全數定案**（Q1 滾動預設關/Q2 去重 ≥60%+log/Q3 合併在 P3 策略側·rag_indexer 禁 doc_type 分支污染/Q4 constraints 四條/Q5 fallback 判準/Q6 **PIPE-SLIDES 定名**+Checkout 同步母 plan 條目/Q7 **逐頁定案**/Q8 B 軌另捕 golden+改善豁免）；review 另確認 key=`p{N}_{標題}` 與 U10 不渲染 meta header 兩設計；**plan 全 OQ 結清、可進 tasks**
- v1 (2026-06-11)：初稿——整合 baron 三輪設計討論（四 Phase 重整＋resume 對齊比對＋資料傳導模擬）+ 三缺口拍板解（整頁存圖／key=`p{N}_{標題}`／raw_domain 摘要順產）+ A 軌實件品質模擬（雙 Caption `slides_processor.py:155`／零 temp／表格畸形三病灶實證）；U1-U11 + §4 五條接縫契約（含 key-changing 整合測試正面滿足 §7.2）+ §9 八 OQ（Q6 任務代號 PIPE-SLIDES 取代 PIPE-VISUAL、Q7 逐頁定案承接 PIPE-SYNC-2 Q6 保留之決策）
