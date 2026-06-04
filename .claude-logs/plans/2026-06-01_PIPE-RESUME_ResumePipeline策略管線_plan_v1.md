# PIPE-RESUME ResumePipeline 策略管線 plan

> 定義 PIPE 大改版五條策略管線之 **ResumePipeline（`doc_type='resume'`）** 的四 Phase 目標規格、程式流程與判斷、Phase 交接資料流程。作為 PIPE 縱向五路絞殺第一路（Resume）的落地基準。本 plan 為純規格定義，重構戰略總綱見 §5 所列 PIPE plan §2 U7／U10。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 大改版要求 `doc_type` 分流由主幹 `if/elif`（`pipeline_core.py L542-568`）下放為五條高內聚策略插件。ResumePipeline 為縱向絞殺第一路，須將現行散落的履歷處理（Vision 轉錄 `ResumeProcessor`、metadata 抽欄、短文 tiling bypass、RAG ≥3 過濾）收斂為一條跨完整四 Phase（P1→P4）的策略管線，且交付物對齊 PIPE 四份凍結接口合約。
- **解法**：以 `PipelineFactory.get_strategy('resume')` 取得 ResumePipeline 策略插件，於新核心 `pipelines/` 目錄落地（複用既有 `ResumeProcessor` Vision 忠實轉錄核心，不重寫其 Vision 哲學）。四 Phase 規格：**P1** 以 Vision LLM 整份解析且輸出 Markdown 並保留原本格式，透過提示詞去除 Hunter 或人力公司的重複浮水印，並抽姓名／電話／Email／領域等 Metadata；**P2**（4 步循序）①依據領域做 LLC (LCC) 分類（因不同領域同字可能有不同翻法）→ ②做整份履歷摘要（原文 `abstract`、置於 Glossary 前）→ ③針對全文提取 GLOSSARY 並與資料庫比對（無資料則翻譯、**將②原文摘要與①LCC 組入翻譯 prompt context**回寫資料庫，有資料則採級聯術語表，Glossary 此點凍結）→ ④以 `Translator.translate(…,DEEP_THINK)` 將②原文摘要翻為中文寫入 `translated_abstract` 交付；**P3** 翻譯全部內文（附上 `LCC` + `全文摘要` + `GLOSSARY`）且 100% Bypass（不切分 Section/不開 Sliding Window）；**P4** RAG 字元門檻 ≥3 + 技能詞與結構化資訊保護。
- **影響**：新增 `pipelines/resume_pipeline.py`（策略插件）；`candidate_name` 映射 `IngestionMetadataSpec.title`、`phone`/`email`/`domain` 入 **`IngestionMetadataSpec.custom_metadata`**（自定義屬性容器、避免 Schema Bloat）；複用 `processor/resume_processor.py` / `processor/rag_processor.py` 既有過濾。影子期屬 B 軌，A 軌 `pipeline_core.py` resume branch 保留至 Flip。**Flip 前置**：`IngestionMetadataSpec.custom_metadata` 屬上游凍結合約變更，未全域擴充前本管線僅能於影子 B 軌驗證、不得正式 Flip 線上流量（見 §7 硬前置）。對既有 list/get/delete API、前端讀取路徑零改動。
  > ⚠️ **上游合約硬前置（本計畫不自行落地）**：本路次依賴 `IngestionMetadataSpec` 補入 `custom_metadata: Dict[str, Any] = {}` 欄位（同步 PIPE-SPEC §1.1 ① + `pipelines/contracts.py`），以容納履歷專屬非標準欄位；此屬上游凍結合約擴充，須先授權落地後本路次方可整合（見 §7）。`GlossaryReadySpec.abstract`／`domain_name` 已於落地合約存在（TRANSLATOR C1）、本路次直接消費。

---

## §2 目標規格

> 以下為 ResumePipeline 必須達到的「最終狀態」規格（What it should be），可量化檢驗。實作細節（如何寫）屬 tasks 階段。

### U1. 策略插件歸位
- ResumePipeline 為 `DocumentStrategy` 子類插件，以 `@PipelineFactory.register('resume')` 裝飾器註冊（`factory.py:30`），主幹僅以 `PipelineFactory.get_strategy('resume')` 取得，**主幹不含任何 resume 專屬 `if/elif` 解析邏輯**。
- **實作落地 ABC 四抽象方法**（`base_strategy.py:35-47`）：`run_phase1(ctx)→IngestionMetadataSpec`（=P1）／`run_phase2(ctx)→GlossaryReadySpec`（=P2）／`run_phase3(ctx)→BilingualMarkdownSpec`（=P3）／`run_phase4(ctx)→RagDbSpec`（=P4）。
- 全程跨四 Phase（P1→P4），各 Phase 產物對齊 PIPE 四份凍結接口合約（`IngestionMetadataSpec`／`GlossaryReadySpec`／`BilingualMarkdownSpec`／`RagDbSpec`）。

### U2. P1 Ingestion — Vision 整份解析 + 四欄抽取
- 以 Vision LLM 整份渲染解析（**禁 MinerU／md_cleaner**），並讓 LLM 輸出 Markdown 並保留原本格式。
- 透過 LLM 轉錄提示詞直接去除 Hunter 或人力公司的重複浮水印，產出忠實且去噪的原文 Markdown 與物理分組 Tiles。
- 抽取四個結構化欄位交付 `IngestionMetadataSpec`：**姓名（candidate_name）映射原生 `title` 欄；電話（phone）／Email（email）／專業領域（domain，例如行銷、程式設計、IC設計）入 `custom_metadata` 自定義容器**（保 `extra="forbid"` 嚴格性、避免全域合約塞入文體專屬欄；未來 Slides 等亦可複用）。
- 主標題硬約束：必須為人名，違反黑名單（`Resume`／`CV`／`履歷` 等通用詞）即判失敗（複用既有 `ResumeProcessor` 黑名單）。
- **硬約束（對齊 PIPE U3）**：P1 交付**零 Abstract／零 LCC／零 Glossary／零翻譯**——`domain` 為 raw 專業領域短句，非標準 LCC。
- **Early Emit（SPEC R4.1）**：P1 產出的 `title`（即 `candidate_name`）經由 Orchestrator 的 `early_emit_hook` 快軌機制（`orchestrator.py:101-102`、P1 後觸發）優先渲染至前端；此為 orchestrator 基建掛點，策略只需正確交付 `IngestionMetadataSpec.title`。

### U3. P2 Glossary & Context Prep — LCC 分類、摘要生成、術語自癒、摘要翻譯（4 步循序）
- **步驟①依據領域做 LCC (LLC) 分類**：以 P1 的 `domain`（raw 專業領域）為 `raw_domain`，經共用真理源凍結雙參簽名 `DomainNormalizer.normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode` 收斂標準 LCC；**並傳入 `context_text=履歷全文/技能片段`**，發揮 DOMAIN-NORM 內容判定優勢（精準區分「行銷→HF」vs「程式設計→QA」、解同字不同譯歧義；對齊 DOMAIN-NORM U1「履歷按技能判定」）。命中本地快取則 0 API；domain 為空 fallback `general`。
- **步驟②做整份履歷摘要**：在 P2 生成履歷原文摘要，填 `GlossaryReadySpec.abstract`（必填）。**此步置於 Glossary 之前**，使原文摘要可作為步驟③自癒翻譯的 prompt context（消解前向依賴）。
- **步驟③針對全文提取 GLOSSARY 並自癒（消費 GLOSSARY-CORE `GlossaryManager`）**：以 `query_cascade(source_lang, target_lang, domain=LCC)` 級聯拉取歷史術語並比對。**語系參數綁定**：`source_lang` 來自 P1 合約 `IngestionMetadataSpec.source_lang`（動態值、`contracts.py:34`）；`target_lang` 固定為系統目標語「繁體中文」（對應聯合鍵代碼 `"zh-tw"`、落地 prompt 硬寫繁體中文 `glossary_extractor.py:42/130`）。
  - **無資料（缺詞）**：以 `extract_terms(source_text, translated_text, source_lang, target_lang, domain=LCC)` 提取並翻譯——**將步驟②原文摘要與步驟①LCC 組入 LLM 翻譯提示詞的 prompt context**（採 (a) 方案：注入 prompt context、**非** `extract_terms` 形參，零上游合約改動、對齊 GLOSSARY-CORE 落地簽名）；再經 `upsert_terms(...)` 冪等回寫 SQLite。
  - **有資料**：直接採級聯術語表。
  - 自癒完成後 Glossary **一次凍結**。
- **步驟④翻譯摘要 + 交付合約欄**：以 `Translator.translate(…,DEEP_THINK)` 將步驟②原文摘要翻為中文，填 `GlossaryReadySpec.translated_abstract`。**一次性 `lcc → Domains.name` 唯讀解析、將領域英文名寫入 `GlossaryReadySpec.domain_name`**（物理封存供 P3 Translator 直讀、免再查 DB）。**查詢機制**：以 LCC 碼為 PK 直接單表唯讀檢索 `Domains` 表（`models.py:244-245`、無共用 helper），須遵守 database SOP **唯讀免交易**（不開 `session.begin()` 寫交易、非阻塞讀）。
- **硬約束**：Glossary 與已譯摘要於此點一次凍結，P3 不得再提取、自癒或重新翻譯摘要。

### U4. P3 Translation & Restore — 全文翻譯與還原 (100% Bypass)
- **翻譯全部內文**：正文 **100% Bypass**（不切 Section、不開 Sliding Window）。整份呼叫落地 API `Translator.translate(text, ctx: InjectionContext, mode=TranslateMode.NORMAL, text_type="content")` 一次性翻譯。`InjectionContext` 欄位映射：`lcc`（標準 LCC）+ `glossary`（凍結 Glossary）+ **`zh_summary` ← P2 的 `translated_abstract`（全文摘要中文版）** + `domain_name`（領域英文名，由 P2 GlossaryReadySpec 沿用）+ **`doc_type='resume'`**（使 Translator 套用「正式商務中文」風格、防退化 academic；對齊 `translator.py:71` `InjectionContext.doc_type` 與 `_STYLE_HINTS`）。產出乾淨雙語 Markdown，交付 `BilingualMarkdownSpec`：`final_zh_path` / `final_en_path`（落地欄名）+ **`translated_abstract`（必填、沿用自 P2 `GlossaryReadySpec.translated_abstract`，否則 P3→P4 觸 ValidationError；`contracts.py:68-70`）**。
  > 註：摘要翻譯（P2）走 `mode=DEEP_THINK`；其思考啟用前置＝`settings.TRANSLATE_MODEL` 為思考世代模型（如 `gemini-3.5-flash`）且 `LLM_THINKING_BUDGET > 0`，否則靜默退化 `NORMAL`（TRANSLATOR plan §2 U3 退化警告）。
- `md_restore` 退化為純 Markdown 樣板渲染（廢除 `extra_info` 動態修補）。
- **硬約束**：BilingualMarkdownSpec 嚴禁含 AI Questions／章節 Summary 等非原著文字。

### U5. P4 Async RAG — 門檻 ≥3 + 技能詞保護
- RAG 向量化為非同步背景任務（唯一輸入為 P3 乾淨 translate JSON），主鏈 `md_restore` 完成即 `reading_ready`，RAG 完成才 `rag_status='ready'`。**非同步派發歸屬**：非同步由 Orchestrator 注入的 `dispatch_p4`（對齊 RAG-ASYNC 規格、BackgroundTasks 版；`orchestrator.py:62` 注入點）達成；`ResumePipeline.run_phase4` 本體專注**同步**分塊過濾與批量 Embedding 計算（預設 `_default_dispatch_p4` 為同步呼叫、`orchestrator.py:137`）。
- Chunk 字元門檻 **≥3**（非學術路 ≥10），保護 `Python`／`Docker` 等短技能詞；含 Email／電話／URL 之 chunk 不論長度一律保留（結構化資訊保護）。
- **硬約束**：Embedding 僅 P4 批量一次，P1/P2/P3 零 Embedding 呼叫；RAG 失敗僅標 `rag_status='failed'`，不影響 `reading_ready`。

### §2.6 程式流程與判斷（規格化流程，非實作碼）

```
[Upload doc_type='resume'] → PipelineFactory.get_strategy('resume') → ResumePipeline（@register('resume')）
│
├─ P1 Ingestion〔run_phase1(ctx)→IngestionMetadataSpec〕
│   ├─ 渲染 PDF 每頁為影像 → 單次 Vision 整份解析（輸出 Markdown 並保留原本格式，透過提示詞去除 Hunter 或人力公司浮水印，禁 md_cleaner）
│   ├─ 判斷：Vision 回傳空 / 格式不合法 → FAIL（PDFParseError）
│   ├─ 判斷：首行主標題 ∈ 黑名單通用詞（Resume/CV/履歷…）→ FAIL（須人名）
│   ├─ 抽欄：candidate_name→title / phone,email,domain(raw 專業領域)→custom_metadata
│   ├─ 交付 IngestionMetadataSpec（零 Abstract/LCC/Glossary/翻譯）
│   └─ Early Emit：title(=candidate_name) 經 Orchestrator early_emit_hook 快軌優先渲染前端（orchestrator.py:101-102）
│
├─ P2 Glossary & Context Prep〔run_phase2(ctx)→GlossaryReadySpec〕（4 步循序）
│   ├─ ①LCC 分類：normalize_to_lcc(raw_domain=domain, context_text=履歷全文/技能) 推導標準 LCC（內容判定解同字不同譯）
│   │   └─ 判斷：cache 命中 → 0 API / miss → LLM 收斂 + 寫快取 / domain 為空 → fallback 'general' LCC
│   ├─ ②做整份履歷摘要：生成原文摘要 → abstract（置於 Glossary 前、供③當 prompt context）
│   ├─ ③Glossary（GlossaryManager）：query_cascade(source_lang=P1.source_lang, target_lang='zh-tw'(固定繁中), domain=LCC) 級聯比對
│   │   ├─ 無資料（缺詞） → extract_terms（將②摘要+①LCC 組入翻譯 prompt context、非形參） → upsert_terms 回寫 SQLite
│   │   ├─ 有資料 → 採級聯術語表
│   │   └─ 自癒後 Glossary 一次凍結
│   ├─ ④翻譯摘要：Translator.translate(…,DEEP_THINK) 翻②摘要 → translated_abstract；lcc → Domains 表 PK 唯讀檢索(無 helper、SOP 唯讀免交易) → name → domain_name
│   └─ 交付 GlossaryReadySpec（abstract + LCC + 凍結 Glossary + translated_abstract + domain_name）
│
├─ P3 Translation & Restore〔run_phase3(ctx)→BilingualMarkdownSpec〕
│   ├─ 判斷：doc_type='resume' → 100% Bypass（不切 Section / 不開 Sliding Window）
│   ├─ 內文翻譯：Translator.translate(…,NORMAL) 整份翻（InjectionContext 注入 LCC + zh_summary(全文摘要) + GLOSSARY + doc_type='resume'）
│   ├─ md_restore 純樣板渲染（無 extra_info）
│   └─ 交付 BilingualMarkdownSpec（final_zh_path / final_en_path + translated_abstract〔沿用 P2、必填〕）
│
└─ P4 Async RAG〔run_phase4(ctx)→RagDbSpec〕（背景任務、主鏈不等）
    ├─ 主鏈：md_restore 完成 → reading_ready（閱讀/Print PDF 解鎖）
    ├─ 背景：chunk 過濾 _is_chunk_meaningful(doc_type='resume')
    │        ├─ 含 email/phone/url → 保留（不論長度）
    │        ├─ doc_type='resume' → 門檻 ≥3（保技能詞）
    │        └─ 純數字 / markdown 噪聲 → 過濾
    ├─ Embedding 批量一次 → FAISS + PaperChunk 寫庫
    └─ 判斷：Embedding/DB 失敗 → log warning + rag_status='failed'（reading_ready 不受影響）
                  成功 → rag_status='ready'（AI Chat 解鎖）
```

### §2.7 資料流程（Phase 交接資料契約）

| 交接點 | 上游 Phase | 資料契約 | Resume 路關鍵欄位 | 硬約束 |
|---|---|---|---|---|
| ① | P1→P2 | `IngestionMetadataSpec` | 原文 JSON 樹 + Tiles + `title`(=candidate_name) + `custom_metadata`{`phone`/`email`/`domain`(raw)} | 不含 Abstract／LCC／Glossary，零翻譯，保留原始 Markdown 格式，去浮水印；履歷專屬欄走 `custom_metadata`（須上游補欄、見 §7） |
| ② | P2→P3 | `GlossaryReadySpec` | `abstract`(原文履歷摘要,必填) + 標準 LCC + 凍結 `Glossary` + `translated_abstract`(已譯中文摘要) + `domain_name`(領域英文名) | P2 循序 **①LCC→②做摘要→③Glossary 自癒→④翻摘要**；Glossary 與已譯摘要此點凍結，P3 不得再提取／自癒；缺詞翻譯時將②原文摘要與①LCC 注入 LLM **prompt context**（採 (a)、非 `extract_terms` 形參、零上游改動）回寫 DB；`domain_name` 供 P3 Translator 直讀免查 DB |
| ③ | P3→P4 | `BilingualMarkdownSpec` | `final_zh_path` / `final_en_path` + `translated_abstract`(必填、沿用 P2) | 嚴禁含 AI Questions／Summary／非原著文字；`translated_abstract` 須沿用 P2 否則 ValidationError（`contracts.py:68-70`）|
| ④ | P4→外部 | `RagDbSpec` | `vectors_path`(FAISS) + `paper_chunk_count` + `index_meta`（對應 `Paper`/`PaperChunk` 寫庫 + `index_meta.json`）| chunk ≥3 過濾後寫庫；Embedding 僅此一次（`contracts.py:82-84`）|

---

## §3 現況與證據

詳細盤點與 ResumePipeline 相關的現有程式碼邏輯與關鍵調用鏈：

- **`pipeline_core.py`**：
  - resume 分流硬編碼 `L542-552`：`elif doc_type == 'resume'` → 走 `heading_fix_resume.txt` prompt → `parser = ResumeProcessor()`（病灶②，本管線將其下放策略插件）。
  - `L566-568`：resume 與 slides 同樣跳過 `md_cleaner`。
  - `L717-730`：resume 套用短文 tiling 合併路徑。
- **`processor/resume_processor.py`**：
  - `class ResumeProcessor(PDFParser) L81`：PyMuPDF 渲染 + Vision LLM 忠實轉錄；`process L92` 渲染每頁 JPEG → 整份單次 Vision（`_analyze_resume L153` / `chat_with_images L157`）。
  - `_validate_vision_output L217-249`：首行須 `#` 人名、主標題黑名單檢查（落地符號 `RESUME_TITLE_BLACKLIST` frozenset，`resume_processor.py:59`，L240 使用；即設計手冊 §3.1 `TITLE_BLACKLIST_EXACT`）。**本管線 P1 複用此核心、不改其 Vision 哲學。**
- **`processor/metadata_extractor.py`**：
  - `_ALL_FIELDS L57-67`：已含 `candidate_name`(姓名)／`domain`(專業領域)／`source_platform`／`is_third_party`（resume 專用）。`phone` / `email` 為新增抽取欄。**契約落點**：`candidate_name`→`IngestionMetadataSpec.title`；`phone`/`email`/`domain`→`IngestionMetadataSpec.custom_metadata`（落地 Spec `extra="forbid"` 無履歷專屬欄、須先擴 Spec＋同步 PIPE-SPEC §1.1①，硬前置見 §7）。
- **`processor/domain_detector.py`**：
  - `detect L39-76`：回傳 10-30 字 raw 領域短句（soft fallback 回空字串）；履歷 raw 領域亦可由 `metadata_resume.txt` 的 `domain` 欄提供。
- **`processor/rag_processor.py`**：
  - `MIN_CHUNK_RESUME_SLIDES = 3 L27` / `_is_chunk_meaningful L41-87`（`L85-86` resume/slides ≥3）/ 結構化 regex `L33-37`（email／phone／url 保留）。**P4 直接複用，不改過濾演算法。**

### §3.1 grep 鋼鐵證據

```bash
grep -nE "resume|ResumeProcessor|doc_type ==" pipeline_core.py | head
# 20:from processor.resume_processor import ResumeProcessor
# 542:        if doc_type == 'slides':
# 546:        elif doc_type == 'resume':
# 552:            parser = ResumeProcessor()
# 568:        if doc_type not in ('slides', 'resume'):
# 717:        if doc_type in ('news', 'web', 'slides', 'resume'):

grep -nE "class ResumeProcessor|def process|chat_with_images|_validate_vision_output" processor/resume_processor.py | head
# 81:class ResumeProcessor(PDFParser):
# 92:    def process(self, pdf_path: str, output_dir: str) -> Path:
# 157:            text = self.llm.chat_with_images(
# 217:    def _validate_vision_output(self, text: str, paper_name: str = "") -> None:

grep -nE "_ALL_FIELDS|candidate_name|domain|phone|email" processor/metadata_extractor.py | head
# 57:_ALL_FIELDS = [
# 64:    "organization", "version", "candidate_name", "domain",
# （phone / email 未出現 → P1 新增契約欄）

grep -nE "MIN_CHUNK_RESUME_SLIDES|_is_chunk_meaningful|email|phone|url" processor/rag_processor.py | head
# 27:MIN_CHUNK_RESUME_SLIDES = 3  # resume/slides 放寬到 3 字元（保 Python/Docker 等）
# 41:def _is_chunk_meaningful(doc, doc_type: str = "") -> bool:
# 85:    if doc_type in ("resume", "slides"):
# 86:        return len(clean_text) >= MIN_CHUNK_RESUME_SLIDES
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本管線落地中嚴禁改動：**

- [ ] `processor/resume_processor.py` `ResumeProcessor` Vision 忠實轉錄核心與主標題黑名單驗證（`process L92` / `_validate_vision_output L217`）——P1 複用，嚴禁改其 Vision 解析哲學或黑名單規則。
- [ ] `processor/rag_processor.py` `_is_chunk_meaningful`（L41-87）與 `MIN_CHUNK_RESUME_SLIDES=3`（L27）、結構化 regex（L33-37）——P4 直接複用，不改過濾演算法。
- [ ] `pipeline_core.py` A 軌 resume branch（L542-568）——影子期保留可運行至 Flip，本管線於 B 軌 `pipelines/` 落地，不刪 A 軌。
- [ ] `processor/domain_detector.py` `detect`（L39-76）多模態核心——只取 raw 輸出餵 `DomainNormalizer`，不改偵測邏輯。
- [ ] 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端讀取路徑——零改動。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 五條策略管線 / 四 Phase 合約 / 三大共用真理源 / 縱向五路絞殺 | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md §2 U2/U7/U8/U10` |
| 三層解耦骨架（已落地，`DocumentStrategy` ABC 四方法 `run_phase1..4`／`PipelineFactory.register`/`get_strategy`／`PipelineContext`／四凍結合約） | `.claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md` |
| P4 RAG 非同步剝離（BackgroundTasks／`reading_ready`+`rag_status` 雙狀態；首落地隨本路、PIPE master §8.5） | `RAG-ASYNC`（⬜ 待建立、PIPE master §8.5 L260） |
| DomainNormalizer 單一入口契約（已落地） | `.claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md` |
| GLOSSARY-CORE 自癒演算法（已落地，`GlossaryManager.query_cascade`/`upsert_terms`） | `.claude-logs/plans/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md` |
| Translator 雙模式原子翻譯器（已落地，`translate(text,ctx,mode,text_type)` + `InjectionContext`） | `.claude-logs/plans/2026-06-01_TRANSLATOR_雙模式原子翻譯器_plan_v10.md` |
| 凍結接口合約（IngestionMetadataSpec/GlossaryReadySpec 欄位） | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md §1.1 §1.2` |
| 影子期 web_server 雙軌派發 scaffolding | `.claude-logs/plans/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| 專案進度治理框架（雙軌制／不可動清單） | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 §4` |
| logging / database 程式碼級 SOP（BE-Refactor 強制） | `.claude-logs/sop/2026-05-23_logging_SOP_手冊.md` / `database_SOP_手冊.md` |
| 現況履歷處理鏈 | `processor/resume_processor.py` / `metadata_extractor.py L57-67` / `rag_processor.py L27-87` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**（防 Regression 底線）：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  - 策略分派：`PipelineFactory.get_strategy('resume')` 回傳 ResumePipeline、主幹無 resume `if/elif`。
  - P1 契約：交付 `IngestionMetadataSpec`，`candidate_name`→`title`、`phone`/`email`/`domain`→`custom_metadata`，**斷言不含 Abstract/LCC/Glossary**，且轉錄提示詞去浮水印效果正確；主標題黑名單觸發 FAIL。
  - P2 契約：`normalize_to_lcc(raw_domain, context_text=履歷全文/技能)` cache 命中 0 API；raw_domain 為空 fallback general；`GlossaryReadySpec` 必填 `abstract`、載 `translated_abstract`＋`domain_name`；摘要由 `Translator.translate(..., TranslateMode.DEEP_THINK)` 生成；Glossary 凍結後 P3 不再自癒之斷言。
  - P3 Bypass：resume 路 100% Bypass（不進 Section/Sliding Window）、內文翻譯確有注入 LCC + zh_summary(全文摘要) + Glossary + `doc_type='resume'`、交付 `BilingualMarkdownSpec`（`final_zh_path`/`final_en_path` + `translated_abstract` 必填沿用）。
  - P4 門檻：`_is_chunk_meaningful` resume `Python` 保留、`john@x.com` 保留、純數字過濾；RAG 失敗主鏈 `reading_ready` 不受影響。

### §6.2 手動端到端（E2E）驗證流程

1. **影子雙軌上傳**：`SHADOW_LAUNCH_ENABLED=true` 上傳履歷 PDF，前端出現「原著」與「原著 (測試)」兩列。
2. **P1 驗證**：B 軌 metadata 正確抽出 姓名／電話／Email／專業領域；主標題為人名（非「Resume」通用詞）。
3. **P2 驗證**：日誌顯示 `normalize_to_lcc` 由專業領域推導 LCC、cache 命中時 0 API。
4. **P3 驗證**：正文 100% Bypass、雙語對照無 AI Questions／Summary 污染。
5. **P4 容錯**：模擬 Embedding 失敗，主閱讀/Print PDF 100% 可用、AI Chat 顯示 `rag_status='failed'`；技能詞（Python/Docker）成功召回。
6. **Golden Baseline Diff**：與舊系統存盤履歷比對排版還原度與雙語品質，要求 0% 退化。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **`phone`/`email`/`domain` 履歷專屬欄落點（vs 凍結 IngestionMetadataSpec `extra="forbid"`）** | **`candidate_name`→`title`；`phone`/`email`/`domain`→新增 `IngestionMetadataSpec.custom_metadata: Dict[str,Any]={}`**（自定義容器） | 落地 `IngestionMetadataSpec`＝`{title,authors,venue,doi,source_lang,tiles}`＋`extra="forbid"`，無履歷專屬欄、直塞會 ValidationError。以 `custom_metadata` 容器保型別安全與嚴格性、避免全域 Schema Bloat、未來文體可複用。**硬前置**：須先擴充 `IngestionMetadataSpec` + 同步 PIPE-SPEC §1.1①（上游凍結合約變更、待授權，本路次不自行落地）。**Flip 阻擋**：P1 合約未全域擴充前，ResumePipeline 可於影子 B 軌實作驗證，但**不得正式 Flip 線上流量**（否則 P1→P2 交接 `custom_metadata` 觸 `extra="forbid"` ValidationError）。 |
| **P2 LCC 的 raw 領域與 context_text 來源** | **`raw_domain`＝P1 `domain` 欄；`context_text`＝履歷全文/技能片段**（雙參簽名） | 凍結簽名為雙參 `normalize_to_lcc(raw_domain, context_text=None)`；以履歷內容為 context_text 發揮 DOMAIN-NORM 內容判定（行銷 HF vs 程式設計 QA），比僅 raw domain 更精準。不另跑 `domain_detector.detect`（多一次 LLM 且語意更弱）。 |
| **P2 交付 `GlossaryReadySpec` 必填/載體欄** | **`abstract`(原文履歷摘要)＋`translated_abstract`(中文)＋`domain_name`(lcc→Domains.name)** 一併交付 | 落地 `abstract` 為必填、缺則 ValidationError；`domain_name`(TRANSLATOR C1 載體)供 P3 Translator 直讀免查 DB。三欄於 P2 一次封存、P3 零 DB。 |
| **履歷無學術 Abstract，`translated_abstract` 如何交付** | **做整份履歷摘要，並用 `Translator.translate(…,DEEP_THINK)` 翻譯後交付** | 已決議：履歷雖然無學術 Abstract 結構，但在 P2 會生成一份履歷整份摘要，並用 `Translator.translate(…,DEEP_THINK)` 翻譯後填入 `GlossaryReadySpec.translated_abstract`，以便下游 Phase 3 消費與展示。 |
| **P2 四步順序與 Glossary 自癒的「全文摘要」注入方式** | **循序 ①LCC→②做摘要→③Glossary 自癒→④翻摘要；摘要採 (a) 注入 prompt context（非 `extract_terms` 形參）** | 已決議：②做摘要前置於③Glossary 之前，使原文摘要可作為③自癒翻譯的背景脈絡（消解前向依賴）。無資料分支翻譯時，將②原文摘要與①LCC **組入 LLM 翻譯提示詞的 prompt context**回寫 DB；採 (a) 而非擴 `extract_terms` 形參，**零上游合約改動**（落地簽名 `extract_terms(source_text, translated_text, source_lang, target_lang, domain)` 不變）。有資料則直採級聯術語表；Glossary 自癒後一次凍結。 |
| **既有 `ResumeProcessor` 複用 vs 重寫進 `pipelines/`** | **複用 Vision 轉錄核心、外包一層 ResumePipeline 策略殼** | 既有 `ResumeProcessor` Vision 忠實轉錄 + 黑名單已穩定（Phase 4.7e v2 落地），重寫風險高；策略殼只負責四 Phase 編排與 Spec 交付，核心轉錄複用即可。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 ResumePipeline 策略管線四 Phase 目標規格、程式流程與判斷、Phase 交接資料流程，作為 PIPE 縱向第一路落地 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用；為 PIPE U7 ResumePipeline 的實作依據 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 PIPE-RESUME tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段）；五路戰略總綱不重寫（唯一源在 PIPE plan §2 U7/U10）；共用真理源契約不重寫（唯一源在 DOMAIN-NORM / GLOSSARY-CORE plan） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義 Resume 路專屬四 Phase 規格與資料流；共用真理源 / 影子戰略 / 四 Phase 合約定義一律引用 PIPE / DOMAIN-NORM / GLOSSARY-CORE plan |

### §99.2 Revision 歷程

- v8 (2026-06-04)：第四輪跨 plan 對接稽核——cosmetic 符號精確化（檔名沿用就地 bump、不改名）：§3 主標題黑名單補真實落地符號 `RESUME_TITLE_BLACKLIST`（frozenset、`resume_processor.py:59`、L240 使用；原僅標設計手冊名 `TITLE_BLACKLIST_EXACT`），便於 tasks grep。已查核對齊無需動作：影子機制（`SHADOW_LAUNCH_ENABLED`/`ctx.shadow`/`_shadow`/「(測試)」標題 ↔ PIPE master U10）、複用模組方法名（`ResumeProcessor`/`_analyze_resume`/`_validate_vision_output`/`_is_chunk_meaningful` 全落地存在）。
- v7 (2026-06-04)：第三輪跨 plan 對接稽核——spec 完備性補強（PIPE-SPEC R1.1–R5.1 全對齊確認、檔名沿用就地 bump、不改名）：① **小項1** U3 步驟③／§2.6 補 **語系參數綁定**：`source_lang`←P1 `IngestionMetadataSpec.source_lang`（`contracts.py:34`）、`target_lang` 固定繁體中文（`"zh-tw"`、`glossary_extractor.py:42/130`）；② **小項2** U3 步驟④／§2.6 補 **`lcc→Domains.name` 查詢機制**：以 LCC 為 PK 直接單表唯讀檢索 `Domains`（`models.py:244-245`、無共用 helper）、遵守 database SOP **唯讀免交易**。已查核對齊無需動作：R4.2 plan 採落地 `rag_status='failed'`（較 PIPE-SPEC prose `rag_failed` 嚴謹）、R1.1/R2.1/R2.2/R3.1/R4.1/R5.1 全符。
- v6 (2026-06-04)：第二輪跨 plan 對接稽核（深掘 Orchestrator／PipelineContext 資料流；檔名沿用就地 bump、不改名）：① **發現1（必改）** 狀態 token 正名 `rag_failed`→`rag_status='failed'`（落地 `PipelineContext.rag_status: Literal["pending","ready","failed"]`、`context.py:24`），同步 U5／§2.6／§6.2 E2E 三處＋`ready` 加引號；② **發現2（補強）** U2／§2.6 P1 補 **Early Emit**：`title`(=candidate_name) 經 Orchestrator `early_emit_hook` 快軌前端（`orchestrator.py:101-102`、SPEC R4.1、屬 orchestrator 基建掛點）；③ **發現3（補強）** U5 補 **P4 非同步歸屬**：非同步由 Orchestrator 注入 `dispatch_p4`（RAG-ASYNC BackgroundTasks 版、`orchestrator.py:62`）達成，`run_phase4` 本體為同步分塊過濾＋批量 Embedding（預設 `_default_dispatch_p4` 同步、`orchestrator.py:137`）。已查核對齊無需動作：`query_cascade(source_lang,target_lang,domain)` 參數逐字符、`run_phase1..4`↔`_PHASES`、reading_ready 於 P3 後設定。
- v5 (2026-06-04)：跨 plan 對接稽核補強（對齊 PIPE-CORE 落地 ABC／合約與 PIPE master §8.5 依賴；檔名沿用就地 bump、不改名）：① **落差1** U1／§2.6 補 `DocumentStrategy` 四抽象方法對映 `run_phase1..4(ctx)→四合約`（`base_strategy.py:35-47`）＋ `@PipelineFactory.register('resume')` 註冊（`factory.py:30`）；② **落差2** U4／§2.6 P3 `InjectionContext` 映射補 **`doc_type='resume'`**（套「正式商務中文」風格、防退化 academic；`translator.py:71`）；③ **落差3** `BilingualMarkdownSpec` 欄名正名 `final_zh.md/final_en.md`→`final_zh_path/final_en_path`＋明寫 **`translated_abstract` 必填沿用 P2**（否則 P3→P4 ValidationError；`contracts.py:68-70`），同步 U4／§2.6／§2.7③；④ **落差4** §5 補列 PIPE-CORE plan_v2 與 RAG-ASYNC（PIPE master §8.5 L250 依賴）；⑤ **cosmetic** 合約名統一 `RAG&DB`／`RAG/DB 合約`→`RagDbSpec`（U1／§2.7④、`contracts.py:74-84`）。
- v4 (2026-06-04)：P2 流程依 baron 拍板重排為 **4 步循序**並定調摘要注入方式（檔名沿用就地 bump 先例、不改名）：① **順序重排** ①LCC 分類 → ②**做整份履歷摘要（前置於 Glossary）** → ③Glossary 提取自癒 → ④`Translator.translate(…,DEEP_THINK)` 翻摘要，將原本「摘要綁翻譯且置於 Glossary 之後」拆分並前移做摘要步驟，**消解前向依賴**（原文摘要先生成、方能作③自癒翻譯背景）；② **(a) 方案定調**：③無資料分支翻譯時，將②原文摘要與①LCC **組入 LLM 翻譯 prompt context、非 `extract_terms` 形參**，零上游合約改動（GLOSSARY-CORE 落地簽名 `extract_terms(source_text, translated_text, source_lang, target_lang, domain)` 不變）。同步更新 §1 TL;DR P2 / U3（4 步）/ §2.6 ASCII flow / §2.7 交接表② / §7 Open Questions。
- v3 (2026-06-04)：對齊三大共用真理源**落地後**凍結合約，修正 v2 描述與真實簽名/欄位的不一致（檔名沿用本檔 v2 之就地 bump 先例、不改名，避免 PIPE master plan §8.5 指向 `_plan_v1.md` 斷鏈）：① **A** `candidate_name`→`IngestionMetadataSpec.title`、`phone`/`email`/`domain`→新增 `custom_metadata: Dict[str,Any]={}`（落地 Spec 為 `{title,authors,venue,doi,source_lang,tiles}`＋`extra="forbid"`、無履歷專屬欄；列為**硬前置**：須先擴 Spec + 同步 PIPE-SPEC §1.1①、本路次不自落地；**Flip 阻擋**：P1 合約未全域擴充前僅能影子 B 軌驗證、不得正式 Flip 線上流量）；② **B** `normalize_to_lcc(raw_domain, context_text=履歷全文/技能)` 雙參簽名（DOMAIN-NORM 凍結簽名）；③ **C** `GlossaryReadySpec.abstract` 為必填、P2 一併交付；④ **D** §5 規格依據版號指標校正（PIPE master→v10 / DOMAIN-NORM→plans v2 / PIPE-SCAFFOLD→plans v3 / GLOSSARY-CORE→plans / 補 TRANSLATOR plan_v10 + PIPE-SPEC）；⑤ **E** P2/P3 翻譯統一走 `Translator.translate(text, ctx: InjectionContext, mode, text_type)`（TRANSLATOR 落地 API）、`zh_summary`←`translated_abstract` 映射、DEEP_THINK 須顯式設 `LLM_THINKING_BUDGET>0`（否則退化 NORMAL）；⑥ **F** Glossary 三方法統一 `GlossaryManager.query_cascade/extract_terms/upsert_terms`（GLOSSARY-CORE 落地簽名、LLM 交易外）。同步更新 §1 影響 / §2.6 ASCII flow / §2.7 交接表 ①② / §6 測試描述 / §7 Open Questions。
- v2 (2026-06-04)：全面調整管線物理特徵與合約以契合大改版架構：① P1 採 Vision LLM 整份解析且輸出 Markdown 並保留原本格式，提示詞去浮水印，抽取包含姓名、電話、email、領域之 metadata；② P2 依據領域進行 LCC 分類以因應同字不同譯法，針對全文提取 GLOSSARY 並與 SQLite 比對，無資料則翻譯（附全文摘要與 LCC 分類）並寫回資料庫再送翻譯摘要，有資料則直送翻譯摘要，並由 Translator.translate(…,DEEP_THINK) 翻譯履歷摘要至 `GlossaryReadySpec.translated_abstract`；③ P3 翻譯全部內文（附上 `LCC` + `全文摘要` + `GLOSSARY`）；④ P4 執行非同步 RAG 處理。
- v1 (2026-06-01)：初版建立，定義 ResumePipeline 四 Phase 規格（P1 Vision 整份解析 + 姓名/電話/Email/專業領域；P2 LCC 由專業領域經 DomainNormalizer 推導；P3 100% Bypass；P4 ≥3 技能詞保護）、§2.6 程式流程與判斷、§2.7 Phase 交接資料流程；對齊 PIPE plan §2 U7/U10 與 DOMAIN-NORM / GLOSSARY-CORE 共用真理源。
