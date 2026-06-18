# PIPE-LITEDOC LiteDocPipeline 策略管線 plan

> PIPE 縱向五路第 3 路：news / web / unknown（factory fallback）之 B 軌策略管線。P1 MinerU 文字攝入、P2-P4 全消費已落地之共用真理源（section_engine / DomainNormalizer / Glossary / Translator / rag_indexer），不重造機制。純規格定義、不含設計脈絡。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 五路第 3 路（litedoc＝news/web/unknown）尚未落地;其「遞迴標題樹→摘要/翻譯/還原/rag 旁路/meta header」骨幹已由 PIPE-SECTION-BASE 抽成共用 `section_engine`，本路為其**首個 resume 以外的 consumer**（驗證引擎泛化）。
- **解法**：新建 `pipelines/litedoc_pipeline.py`（`@register('litedoc'/'news'/'web')`、unknown 靠 factory fallback 承接），四 Phase 全消費共用真理源——P1 MinerU+md_cleaner 文字攝入 + 文字 LLM metadata 抽取（含 URL→publisher 解碼、走 raw_metadata 旁路 + META-NORM 飛輪）;P2 section_engine 六步（abstract/LCC/Glossary/section_summaries）;P3 size-gate（<15k 一鍵 `translate_whole` / ≥15k 逐 section `restore_sections_markdown`）+ heading 退化 fallback + meta header 純格式化器;P4 `rag_indexer.index`（門檻走預設 ≥10、零改引擎）。
- **影響**：新增 `pipelines/litedoc_pipeline.py` + `pipelines/__init__.py` 註冊觸發 + `tests/test_litedoc_pipeline.py`;**`section_engine` 純加法補 `render_meta_header_html`**（academic-family 置中 HTML 扉頁 formatter、不碰既有 resume 列表 formatter、見 U5b/Q7）。**零改 rag_indexer / contracts / resume / slide / 三真理源 / A 軌**（全為 consume）。doc_type 額外 metadata（date/publisher/url/org）走 `ctx.raw_metadata` 旁路（INFRA-4 後收合）。

---

## §2 目標規格

- **U1 策略註冊與分派**：`@PipelineFactory.register` 將 `LiteDocPipeline` 註冊於 `'litedoc'` / `'news'` / `'web'` 三 key;`unknown` doc_type 經 factory `_FALLBACK_DOC_TYPE='litedoc'` 自動承接;`pipelines/__init__.py` 補 import 觸發註冊（同 resume/slides 範式）。主幹零 doc_type 分支。
- **U2 P1 攝入（MinerU 文字、非 Vision）**：`run_phase1` 走 `PDFProcessor(MinerU)` + 強制 `md_cleaner` + doc_analyzer + md2json + json_process + tiling → IngestionMetadataSpec（title / authors / source_lang / tiles;**venue 承接 publisher**、無 Abstract/LCC/Glossary、零翻譯）。
  - **U2.1 DocAnalyzer doc_type 映射（防扁平文體誤吃論文 prompt）**：呼叫 `DocAnalyzer().analyze(md, analyzer_doc_type)` 時呼叫端做安全映射——`doc_type in ('news','web')` 原樣傳;`'litedoc'/'unknown'` 等→**統一映射 `'web'`**（扁平文體 structure/heading_fix prompt）。**根因**：`doc_analyzer.py:53-55` 對不在 `HEADING_FIX_PROMPTS` 之 doc_type〔含 `'litedoc'`〕fallback `'academic'`〔深層論文 prompt〕→ 扁平短文結構分析偏位;映射確保 unknown/litedoc 走 `'web'` 扁平 prompt。
- **U3 P1 metadata 抽取 + 旁路**：文字 LLM 抽 title/authors/date/publisher/source 與 **URL→正式組織名解碼**;**凍結合約欄（venue 等）回填 spec、合約無欄者（date/url/organization）走 `ctx.raw_metadata` 旁路**，欄名經 `meta_normalizer.normalize_fields`（旗標 `LLM_USE_META_NORM`）飛輪正規化（同 META-NORM 範式、零新機制）。
- **U4 P2 六步（消費 section_engine + 三真理源）**：`run_phase2` ①全文摘要 ②`normalize_to_lcc(raw_domain, context=abstract)` ③Glossary 級聯自癒（旗標閘門、交易外）④`Translator(DEEP_THINK)` 譯摘要 + `lcc→Domains.name`→domain_name ⑤`section_engine.build_section_summaries`（key=原文標題 path、三安全鎖）→ GlossaryReadySpec。
- **U5 P3 翻譯與還原（size-gate + 消費 section_engine）**：`run_phase3` `InjectionContext(doc_type, domain_name, glossary, constraints)`;**size-gate**：文件字數 `< LITEDOC_WHOLE_TRANSLATE_THRESHOLD`（預設 15k）→ `section_engine.translate_whole`（一鍵）;`≥` 或正常多 section → `section_engine.restore_sections_markdown`（逐 section 並行）;`section_engine.is_heading_degraded` 退化 → `translate_whole` fallback;**meta header 走 `section_engine.render_meta_header_html`**（academic-family 置中 HTML `paper-header-meta`、對齊 A 軌 news/web `md_restore:460-490`、**非 resume 列表 formatter**;呼叫端抽 authors/venue〔publisher〕/date/doi/keywords 後傳入、引擎不讀 ctx）prepend final_zh/en;rag 旁路 `section_engine.collect_rag_sections`（summary_key=原文標題 path）寫 `ctx.rag_sections`;zh* edge path 不重譯。→ BilingualMarkdownSpec（rag_tree_json=None、P4 才建）。
- **U5b section_engine 純加法補 HTML 扉頁 formatter**：`section_engine` 新增 `render_meta_header_html(authors, venue, date, doi=None, keywords=None, *, is_zh=False) -> str`——輸出 A 軌等價之 `<div class="paper-header-meta">`〔header-authors / header-venue-date〔`·` 分隔〕/ header-doi / header-keywords〕HTML;**Zero Schema Coupling 同 U3.1**（收已抽好值、引擎零讀 raw_metadata/ctx）;**須與 A 軌 `md_restore` 之 zh/en 扉頁輸出 byte 等價**〔分隔符/label 依 lang、執行期對齊 A 軌驗證〕;**純加法、不碰既有 `render_meta_header`〔resume 列表〕**;academic/book/technical 後續共用（litedoc 為首個 consumer、消滅未來重造）。tasks 排序為**首個 commit**（engine additive + engine 測試綠、隔離驗證後 route commit 才消費）。
- **U5c 雙語標題 `translated_title` 補全（litedoc 為文章、非 resume 捷徑）**：P3 依路徑產 `translated_title` 供 P4——① `is_zh` → `translated_title = title`;② 正常分段（`restore_sections_markdown`）→ 由回傳 slots+zh_by_index 取頂層 title slot 之譯後文字;③ 一鍵 / 退化 → 對 title 額外單元翻譯一次〔`translate_unit(title, inj, tr, "title")`、成本極低〕。**根因**：`rag_indexer.index` 簽名含 `title`/`translated_title`〔RAG-ASYNC-HOTFIX-2、供 rag_tree 引用/UI〕;resume 因無雙語兩者同取 ingestion.title〔`:780`〕、litedoc 文章須補真譯題——**否則中文 chunk header 夾帶英文原題、破壞 RAG 召回品質**〔不只 UI 呈現〕。
- **U6 P4 Async RAG（消費 rag_indexer、零改引擎）**：`run_phase4` 呼 `rag_indexer.index(ctx.rag_sections, section_summaries, doc_type='litedoc', vectors_dir, paper_db_id, rag_tree_path, title=原文標題, translated_title=U5c 譯題)`;**chunk 門檻走 `is_chunk_meaningful` 預設 ≥10**（litedoc 非 resume/slides 短文型、無需改 `rag_indexer.py:69` tuple）;四產物（FAISS/paper_chunks/index_meta/rag_tree.json）;異常拋出由 Orchestrator 標 `rag_status='failed'`、不阻 reading_ready。→ RagDbSpec。
- **U7 接縫 key 同基準**：section_summaries key（P2 產）＝ rag_sections summary_key（P3 帶）＝ rag_indexer 查（P4 取）＝ **原文標題 path**（繼承 section_engine、RAG-ASYNC-HOTFIX-1）。
- **U8 測試**：`tests/test_litedoc_pipeline.py`——策略分派（litedoc/news/web/unknown fallback 四路）+ P1-P4 契約 + **§7.2 P2→P3→P4 key-changing 整合測試**（真翻譯改 title、斷言接縫不變式）;全套件維持基線。
- **U9 治理**：class/檔名零影子標記（最終正式命名、master plan v10 U10 命名紀律）;旗標預設關時行為等價舊狀、線上零風險。

<!-- === [WORKFLOW-4 C1 U4] === 選用章節：Diverse Rollout 多候選探索 -->
### §2.5 候選方案（Diverse Rollout）（選用）

> **架構級決策**：P1 之 metadata 抽取機制決定本路與 A 軌的耦合度、影響 Flip 後維護;觸發多候選。

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| **方案 A（選定）B 軌原生文字 cover-prompt + META-NORM 飛輪** | litedoc P1 自有文字 metadata prompt（抽 title/authors/date/publisher/url）→ `meta_normalizer.normalize_fields` 飛輪正規化欄名 → raw_metadata 旁路 | 難易：中（新 prompt）/ 衝擊：小（不碰 A 軌）/ 擴充：高——**不耦合即將絞殺的 A 軌**（RESUME-P3「pipelines/ 內重建、不耦合 A 軌」先例）、與 slides META-NORM C3 接線同範式 |
| 方案 B（否決）複用 A 軌 `processor/metadata_extractor.py` | 直接呼 A 軌文字 metadata 抽取器（`_ALL_FIELDS` 已含 publication_date/publisher/organization） | 難易：低（複用現成）/ 衝擊：中（B 軌依賴 A 軌模組）/ 擴充：低——**Flip 下線 A 軌時連帶斷裂**、違「B 軌零依賴 A 軌」（rag_indexer/RAG-ASYNC 先例）;省一次性開發、賠長期解耦 |

- **選定理由**：方案 A 與 B 軌既有共用真理源「零依賴 A 軌」原則一致（rag_indexer 全重寫、resume P3 pipelines 內重建）;Flip 後 A 軌下線本路不受影響。
- **否決留痕**：方案 B 之「複用現成」誘人但製造 B→A 反向依賴、與絞殺戰略矛盾;未來若 A 軌 metadata_extractor 升格為共用真理源再評估、本案不採。
<!-- === [WORKFLOW-4 C1 U4 END] === -->

---

## §3 現況與證據

- **`pipelines/factory.py`**：`_FALLBACK_DOC_TYPE='litedoc'`（L21）、未命中降級 litedoc（L48-54）;`register`/`register_strategy`（L30/40）支援同類多 key 註冊。**現 `_registry` 僅 resume/slides 註冊**（litedoc 未建 → unknown 目前降級會回 NullStrategy 哨兵）。
- **`pipelines/section_engine.py`**（PIPE-SECTION-BASE 已落地、本路 consume）：`build_section_summaries` / `collect_render_slots` / `restore_sections_markdown` / `translate_whole` / `is_heading_degraded` / `render_meta_header`（純格式化器）/ `collect_rag_sections` / `single_container_sections`。
- **`processor/rag_indexer.py:55-74`**：`is_chunk_meaningful(text, doc_type)`——`resume/slides ≥3、其餘 ≥10`;**litedoc 走 else 預設 ≥10、無需改**（對齊 master plan v10 L183「Academic/Book/LiteDoc ≥10」）。
- **`pipelines/resume_pipeline.py`**：P1-P4 骨架（`run_phase1` L154 / `run_phase2` L330 / `run_phase3` L518 / `run_phase4` L745、`@register('resume')` L141）為本路鏡像參考。
- **A 軌 `processor/doc_analyzer.py`**：`structure_news.txt`/`structure_web.txt`/`heading_fix_news.txt`/`heading_fix_web.txt` 已存在（B 軌 P1 sectioning 可餵）;`FLAT_DOC_TYPES=('news','web')` 僅縮分析視窗、不設 `flat_structure=True`（建層級樹）。
- **`processor/translator.py:38-39`**：`_STYLE_HINTS` 已含 news/web（免移）。
- **master plan v10 L72**：「LiteDocPipeline（news/web/**technical**/未知 fallback）」——**與本路範圍分歧**（見 §5 / §9 Q4：baron 2026-06-18 re-eval 將 technical 移至深結構家族）。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "_FALLBACK_DOC_TYPE|def register" pipelines/factory.py    # litedoc fallback + 多註冊能力
grep -nE "resume,slides ≥3、其餘 ≥10|doc_type in \(\"resume\", \"slides\"\)" processor/rag_indexer.py  # litedoc 走預設 ≥10
grep -nE "def run_phase[1-4]" pipelines/resume_pipeline.py          # P1-P4 鏡像骨架
grep -n "LiteDocPipeline" .claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md  # L72 母 plan 定義（含 technical 分歧）
```

---

## §4 跨 Phase 接縫契約

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| P2→P4 節點摘要 | P2 `section_engine.build_section_summaries` 產 `section_summaries`，key＝**原文標題 path** | P4 `rag_indexer._walk` 以 `summary_key` 查 | key＝原文標題 path;P2 產與 P4 取**同為原文標題 path**（繼承 section_engine、RAG-ASYNC-HOTFIX-1） |
| P3→P4 rag section | P3 `section_engine.collect_rag_sections` 產 `ctx.rag_sections`，`summary_key`＝**原文標題 path**（譯後 title 僅顯示） | P4 `rag_indexer.index` 消費 | summary_key＝原文標題 path;與 P2 section_summaries key 同基準 |
| P1→P2 raw metadata | P1 寫 `ctx.raw_metadata`（date/publisher/url/org、經 META-NORM 飛輪欄名） | P2 `raw_domain` 讀 / web_server 寫庫讀 | 旁路欄（非凍結合約、INFRA-4 後收合）;同 resume/slides raw_metadata 範式 |

填寫規範與 worked example 見 `.claude-logs/ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **與母 plan v10 分歧**（L72 列 technical 於 litedoc）| 🟡 中 | 本路顯式排除 technical（§9 Q4、baron re-eval：technical 屬深結構家族、歸 academic/book 路）;分歧待 PIPE-SYNC 回灌母 plan v10、本 plan §3/§9 明載、不靜默 |
| 扁平 news/web 退化 chunks 過少 | 🟢 低 | 短文 1-2 節點可接受;size-gate <15k 一鍵翻 + rag_indexer size-cap 子切;深結構粒度問題屬技術文件路、非本路 |
| 行為退化（新路、影子驗證）| 🟡 中 | 旗標預設關時零線上影響;B 軌影子上傳驗證 + 與 A 軌 golden diff（改善豁免）;消費已測之 section_engine（17 測試）降風險 |
| B→A 軌耦合（metadata）| 🟢 低 | §2.5 選方案 A（B 軌原生）、不依賴 A 軌 metadata_extractor |
| 15k size-gate 門檻未校準 | 🟢 低 | env 可調（`LITEDOC_WHOLE_TRANSLATE_THRESHOLD`）;沿用母 plan v10 預設、實測微調 |
| 接縫 key 位移 | 🟡 中 | 繼承 section_engine（key 基準已鎖）;§7.2 key-changing 整合測試雙驗 |

對齊 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] `pipelines/section_engine.py` — **僅限純加法新增 `render_meta_header_html`**（Q7、U5b）;**嚴禁改動既有任何函式**（尤 `render_meta_header` resume 列表 formatter、摘要簇、render/restore 簇）——既有 resume 42 + engine 17 測試須全綠為憑。
- [ ] `processor/rag_indexer.py` — litedoc 走預設 ≥10、**零改引擎**（不動 `:69` tuple）。
- [ ] `pipelines/contracts.py` 四凍結合約 — 額外 metadata 走 raw_metadata 旁路、不新增/改欄位（INFRA-4 才收合）。
- [ ] `pipelines/resume_pipeline.py` / `pipelines/slide_pipeline.py` — 零碰。
- [ ] 三大共用真理源（`domain_normalizer` / `glossary_extractor` / `translator`）— consume only、零改。
- [ ] **A 軌全部**（`pipeline_core.py` / `web_server.py` 非影子派發段 / `processor/*` 非本案 / `static/*`）— 零改。
- [ ] `DocumentStrategy` ABC / `PipelineFactory` 註冊範式 — 僅新增註冊、不改機制。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| 跨 Phase 接縫契約唯一源 | `.claude-logs/ref/WORKFLOW_SOP.md §7` |
| 專案進度框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 母 plan（五路/litedoc 定義 L72、RAG 門檻 L183、命名紀律 U10）| `.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md` |
| 共用 section 引擎（本路 P2/P3 消費）| `pipelines/section_engine.py`（PIPE-SECTION-BASE 已落地）|
| 共用 RAG 索引（本路 P4 消費）| `processor/rag_indexer.py`（RAG-ASYNC）|
| 鏡像骨架 + raw_metadata 旁路範式 | `pipelines/resume_pipeline.py`（§3 grep）|
| metadata 飛輪 | `processor/meta_normalizer.py`（META-NORM）|
| 接縫 key 基準 | RAG-ASYNC-HOTFIX-1（原文標題 path 三方同基準）|

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -q   # 全套件維持基線（657 passed 起點）
  ```
- **預計新增**：`tests/test_litedoc_pipeline.py`——
  - 策略分派：`get_strategy('litedoc'/'news'/'web')` 回 LiteDocPipeline、`get_strategy('未知')` fallback 回 LiteDocPipeline。
  - P1 契約：MinerU 攝入（mock）+ metadata 旁路（date/publisher/url→raw_metadata、URL 解碼）+ IngestionMetadataSpec（extra=forbid 不破）。
  - P2 契約：六步產 GlossaryReadySpec（section_summaries key=原文標題 path）。
  - P3 契約：size-gate（<15k translate_whole calls==1 / ≥15k 逐 section）+ heading 退化 fallback + meta header prepend + zh* edge。
  - P4 契約：呼 rag_indexer.index（mock）、門檻 ≥10、四產物、失敗不阻 reading_ready。
  - **§7.2 P2→P3→P4 key-changing 整合**：FakeTranslator 真改 title、斷言 section_summaries key 與 rag_sections summary_key 同基準＝原文標題 path、下游 match。

### §8.2 手動端到端（E2E）驗證流程（baron 運維、非 commit）

1. `.env` `LLM_USE_META_NORM=true` + 影子上傳一篇新聞/網頁 PDF（doc_type=news/web）。
2. 觀察：final_zh meta header 顯示 publisher/date（URL 解碼為組織名）;chunks 量級合理（≥10 門檻）;section_summaries 入 chunk。
3. unknown doc_type 上傳 → factory fallback litedoc、不崩。
4. 與 A 軌 golden diff（改善豁免、B 軌另驗）。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** metadata 旁路欄名 + `LLM_USE_META_NORM` 本路是否開? | **照 resume/slides 慣例**：publisher→venue（凍結合約現成欄）、date/url/organization→raw_metadata + 開 META-NORM 飛輪 | 同 META-NORM 範式、INFRA-4 統一收合;不動凍結合約 |
| **Q2** doc_type 註冊範圍? | **顯式 multi-register `litedoc`/`news`/`web` 同類 + unknown 靠 fallback** | news/web 為 KNOWN_DOC_TYPES、顯式註冊語意清晰;unknown 才走 fallback（語意正確）|
| **Q3** P3 size-gate 門檻 15k 沿用? | **沿用母 plan v10 15k、env `LITEDOC_WHOLE_TRANSLATE_THRESHOLD` 可調** | 對齊母 plan;實測微調免改碼 |
| **Q4** technical 排除本路（vs 母 plan v10 L72 列入）? | **排除**：本路 news/web/unknown;technical 歸深結構家族（academic/book 路）| A 軌證 technical 非 FLAT/非 SHORT/有 abstract＝深結構族;分歧待 PIPE-SYNC 回灌母 plan v10、本 plan 顯式聲明 |
| **Q5** §2.5 P1 metadata 抽取機制? | **方案 A（B 軌原生 cover-prompt + 飛輪）** | 不耦合即將絞殺之 A 軌（§2.5 否決留痕）|
| **Q6** §7.2 整合測試是否豁免? | **不豁免**：BE-Refactor + 真 P2→P3→P4 handoff、寫 key-changing transform 測試 | 同 PIPE-SECTION-BASE/PIPE-SLIDES;DOC 豁免不適用本路 |
| **Q7** 🟢 meta header 格式（resume 列表 vs A 軌 HTML 扉頁）+ 該 HTML formatter 放哪? | **A 軌 `paper-header-meta` HTML、且 `section_engine` 純加法補 `render_meta_header_html` 共用**（litedoc 首個 consumer、academic/book/technical 後續共用）;**update 本 plan 不另開**（純加法、形狀由 A 軌 md_restore 既定、無抽象風險、規模 ~1 函式;紀律落 commit 層〔engine additive 為首 commit、隔離測綠〕）| grep 證 news/web A 軌走置中 HTML〔md_restore:460-490〕、resume 才列表;litedoc 用列表→與 A 軌視覺不一致+golden diff 噪聲。HTML 扉頁六文體共用→放引擎避免 academic/book/technical 重造〔反 PIPE-SECTION-BASE 使命〕。另開 plan 不成比例〔對比 PIPE-SECTION-BASE 大重構〕。slides B 軌不渲染 header〔無前例可抄〕、litedoc 為首個需 HTML 扉頁者 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-LITEDOC（第 3 路 news/web/unknown）策略管線目標規格，作為 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查 + tasks 拆分引用;Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-LITEDOC tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 拍板過程;嚴禁含 commit 拆分（屬 tasks 階段）;consume 共用真理源、嚴禁改其介面 |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成、經 baron 同意歸檔至 archive/ |
| **重複防護** | 僅定義技術規格;工作目錄/流程規格引用 CLAUDE.md/WORKFLOW_SOP;接縫契約引用 WORKFLOW_SOP §7;共用機制引用 section_engine/rag_indexer 不重寫 |

### §99.2 Revision 歷程

- v3 (2026-06-18)：review 兩發現補強（grep 證實）——① **U2.1 DocAnalyzer doc_type 映射**〔`doc_analyzer:53-55` litedoc/unknown 會 fallback academic 深層 prompt → 呼叫端映射 news/web 原樣、其餘→'web' 扁平 prompt〕② **U5c 雙語標題 translated_title 補全**〔`rag_indexer.index` 簽名含 translated_title、resume 因無雙語捷徑同取 title〔:780〕、litedoc 文章須補真譯題：is_zh→title / 分段→取頂層 title slot 譯後 / 一鍵→title 單元翻一次〕+ U6 P4 傳真譯題;U5b 補 `is_zh` 參數 + 「byte 等價 A 軌 zh/en」註。code 草案屬 tasks/execution 階段、不入 plan。
- v2 (2026-06-18)：baron review 拍板 + 新增 **Q7**（meta header 格式）——grep 證 A 軌 news/web 走置中 HTML 扉頁〔`paper-header-meta`、md_restore:460-490〕非 resume 列表;**section_engine 純加法補共用 `render_meta_header_html`**〔U5b、litedoc 首個 consumer、academic/book/technical 後續共用〕、**update 本 plan 不另開**〔純加法、形狀 A 軌既定、無抽象風險、規模 ~1 函式;對比 PIPE-SECTION-BASE 大重構故另開〕;§1 影響 + U5（改 render_meta_header_html）+ U5b（新）+ §6（section_engine 放寬為僅純加法、嚴禁改既有）同步;Q1-Q6 維持。
- v1 (2026-06-18)：初版（BE-Refactor;第 3 路 litedoc=news/web/unknown;U1-U9;§2.5 P1 metadata 二候選〔A B 軌原生飛輪選定〕;§4 三 handoff 接縫;§9 六 OQ 待 baron 拍板〔Q1 旁路/Q2 註冊/Q3 size-gate/Q4 technical 排除-母 plan 分歧/Q5 §2.5/Q6 §7.2 不豁免〕;全消費已落地 section_engine + 三真理源 + rag_indexer、零改引擎;與母 plan v10 L72 technical 分歧顯式聲明）
