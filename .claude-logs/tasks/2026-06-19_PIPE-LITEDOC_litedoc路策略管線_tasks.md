# PIPE-LITEDOC LiteDocPipeline 策略管線 — Tasks

> 本文件為 PIPE-LITEDOC 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-18_PIPE-LITEDOC_litedoc路策略管線_plan_v1.md`（v3、§9 七 OQ 全 🟢）產出，含 8 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `pipelines/litedoc_pipeline.py`（LiteDocPipeline 四 Phase）/ `tests/test_litedoc_pipeline.py` |
| **修改檔案** | 2 個 | `pipelines/section_engine.py`（**純加法** render_meta_header_html）/ `pipelines/__init__.py`（註冊 import 觸發）|
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 8 個 | C1（HTML formatter）→ C2（骨架註冊）→ C3（P1）→ C4（P2）→ C5（P3）→ C6（P4）→ C7（測試）→ C8（Checkout）|
| **baton 歸檔** | 1 次 | C8 收官：`mv` plan→plans/ + tasks→tasks/ + C1-C8 報告→executions/ + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 五路第 3 路 litedoc（news/web/unknown）未落地;其機制骨幹已由 section_engine（第 4 共用真理源）+ 三真理源 + rag_indexer 備齊，本路為 resume 以外首個 consumer。
- **解法**：新建 `LiteDocPipeline` 四 Phase 全消費共用真理源、零造輪;P1 MinerU 文字攝入 + URL publisher 解碼、P2 六步、P3 size-gate + HTML 扉頁、P4 rag_indexer ≥10。
- **影響範圍**：B 軌新增 litedoc_pipeline + 測試;section_engine 純加法 1 函式;零改 rag_indexer/contracts/resume/slide/三真理源/A 軌。
- **Commit 序**：
  - C1 — section_engine HTML 扉頁 formatter（純加法·首發隔離驗證）
  - C2 — LiteDoc 骨架與三 key 註冊（策略分派）
  - C3 — P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）
  - C4 — P2 六步（消費 section_engine + 三真理源）
  - C5 — P3 size-gate 翻譯與 HTML 扉頁還原（含雙語標題鏈）
  - C6 — P4 Async RAG（rag_indexer ≥10 + 雙語標題）
  - C7 — 單元與接縫整合測試（雙鎖）
  - C8 — Checkout 收官
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/factory.py` | `_FALLBACK_DOC_TYPE='litedoc'`、僅 resume/slides 註冊 | litedoc 未建 → unknown 降級回 NullStrategy 哨兵 |
| `pipelines/section_engine.py` | 有 `render_meta_header`（resume 列表）| 缺 academic-family HTML 扉頁 formatter（news/web 須） |
| `pipelines/litedoc_pipeline.py` | 不存在 | 待新建四 Phase 策略 |
| `processor/doc_analyzer.py:53-55` | 未知 doc_type fallback `'academic'` | litedoc/unknown 直傳會吃論文深層 prompt（U2.1 須映射 'web'）|
| `processor/rag_indexer.py:266` | `index(..., title, translated_title)` | litedoc 須補真譯題（非 resume 捷徑同取）|

---

## §3 觀察問題

### 問題 #1：litedoc 路缺策略、unknown 降級回哨兵
- **證據**：`pipelines/factory.py:21,55`（fallback litedoc 但 _registry 無 litedoc）。
- **影響**：news/web/unknown 上傳於 B 軌無策略可分派。

### 問題 #2：HTML 扉頁 formatter 未共用、DocAnalyzer 偏位、譯題缺鏈
- **證據**：`md_restore_processor.py:460-490`（A 軌 news/web HTML 扉頁）/ `doc_analyzer.py:53`（fallback academic）/ `resume_pipeline.py:780`（title 同取捷徑）。
- **影響**：直接套 resume 機制 → 視覺不一致 + 扁平文吃論文 prompt + 中文 chunk 夾英文題破壞召回。

---

## §4 設計方案

> 全程消費已落地真理源、零造輪;C1 section_engine 純加法（不碰既有、resume 42 + engine 17 測試鎖死）為首發隔離驗證。四 Phase 鏡像 resume 但 P1 MinerU 文字、P3 size-gate。

### §4.1 C1 — section_engine HTML 扉頁 formatter
section_engine 純加法 `render_meta_header_html(authors, venue, date, doi=None, keywords=None, *, is_zh=False)`，輸出 A 軌等價 `<div class="paper-header-meta">`（對齊 md_restore:460-490、byte 等價 zh/en）;Zero Schema Coupling（收已抽值、零讀 ctx）;不碰既有 render_meta_header。

### §4.2 C2 — LiteDoc 骨架與註冊
`pipelines/litedoc_pipeline.py` 新建 `@PipelineFactory.register('litedoc')`+`('news')`+`('web')` 之 `LiteDocPipeline`（四方法 strict stub）;`pipelines/__init__.py` 補 import 觸發;主幹零 doc_type 分支。

### §4.3 C3 — P1 MinerU 攝入與 metadata 旁路
`run_phase1`：`self.pdf_processor`(MinerU) parse → **強制 md_cleaner** → `DocAnalyzer().analyze(md, analyzer_doc_type)`〔**U2.1 映射**：`doc_type if doc_type in ('news','web') else 'web'`〕→ md2json/json_process/tiling 產 tiles;文字 LLM metadata（title/authors/date/publisher/url + **URL→publisher 解碼**）→ 凍結合約欄（venue 承接 publisher）回填 spec、date/url/organization 經 `meta_normalizer.normalize_fields` 寫 `ctx.raw_metadata` 旁路 → IngestionMetadataSpec。

### §4.4 C4 — P2 六步
`run_phase2`：①全文摘要 ②`normalize_to_lcc(raw_domain, context=abstract)` ③Glossary 級聯（旗標、交易外）④`Translator(DEEP_THINK)` 譯摘要 + `lcc→domain_name` ⑤`section_engine.build_section_summaries`（key=原文標題 path）→ GlossaryReadySpec。

### §4.5 C5 — P3 size-gate 翻譯與 HTML 扉頁還原
`run_phase3`：`InjectionContext(doc_type, domain_name, glossary, constraints)`;**size-gate**（`LITEDOC_WHOLE_TRANSLATE_THRESHOLD` 預設 15k）<15k→`translate_whole`/≥15k→`restore_sections_markdown`;`is_heading_degraded`→fallback;`render_meta_header_html`（呼叫端抽 authors/venue/date/doi/keywords）prepend;`collect_rag_sections`→`ctx.rag_sections`;**U5c translated_title**（is_zh→title / 分段→取頂層 title slot 譯後 / 一鍵→`translate_unit(title,…,"title")`）;zh* edge → BilingualMarkdownSpec。

### §4.6 C6 — P4 Async RAG
`run_phase4`：`rag_indexer.index(ctx.rag_sections, section_summaries, 'litedoc', vectors_dir, paper_db_id, rag_tree_path, title, translated_title)`;門檻走預設 ≥10;四產物;失敗標 rag_status 不阻 reading_ready → RagDbSpec。

### §4.7 C7 — 單元與接縫整合測試
`tests/test_litedoc_pipeline.py`：分派四路 + P1-P4 契約 + §7.2 key-changing 整合。

### §4.8 C8 — Checkout 收官
Conformance 五維度 + §7.2 達標 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C1 動 section_engine（共用引擎）| 🟡 中 | 純加法、不碰既有;C1 後 resume 42 + engine 17 + 新 formatter 測試全綠 |
| DocAnalyzer 偏位（吃論文 prompt）| 🟢 低 | U2.1 呼叫端映射 'web'（C3）|
| 中文 chunk 夾英文題 | 🟡 中 | U5c 雙語標題鏈（C5/C6）|
| 扁平 news 退化 chunks 少 | 🟢 低 | 短文可接受、size-gate <15k 一鍵 + size-cap 子切 |
| 接縫 key 位移 | 🟡 中 | 繼承 section_engine（key 已鎖）+ C7 key-changing 整合 |
| SOP 違規 | 🟢 低 | logger.error 必 exc_info、P4 委 rag_indexer 無裸 commit;§6.9 grep |

---

## §6 測試計畫

> 每個中間 Commit 後跑對應 grep + `pytest tests/ -q` 維持基線（657 passed 起點）。

### §6.1 C1 驗收
```bash
grep -nE "def render_meta_header_html\(" pipelines/section_engine.py   # 期望命中
grep -c "paper-header-meta\|header-authors\|header-venue-date" pipelines/section_engine.py  # 期望 ≥3
grep -c "raw_metadata\|PipelineContext" pipelines/section_engine.py    # render_meta_header_html 不新增讀取（維持僅註解）
pytest tests/test_section_engine.py tests/test_resume_pipeline.py -q   # 既有 17+42 全綠（不碰既有）
```

### §6.2 C2 驗收
```bash
grep -nE "@PipelineFactory.register\('litedoc'\)|register\('news'\)|register\('web'\)" pipelines/litedoc_pipeline.py
grep -c "litedoc_pipeline" pipelines/__init__.py        # 註冊 import
# 分派測試：get_strategy('litedoc'/'news'/'web'/'未知') → LiteDocPipeline
```

### §6.3 C3 驗收
```bash
grep -nE "def run_phase1|pdf_processor|md_cleaner|DocAnalyzer|analyzer_doc_type|in \('news', 'web'\)|normalize_fields" pipelines/litedoc_pipeline.py
grep -n "raw_metadata\[" pipelines/litedoc_pipeline.py  # date/url/publisher 旁路
```

### §6.4 C4 驗收
```bash
grep -nE "def run_phase2|build_section_summaries|normalize_to_lcc|GlossaryReadySpec" pipelines/litedoc_pipeline.py
```

### §6.5 C5 驗收
```bash
grep -nE "def run_phase3|WHOLE_TRANSLATE_THRESHOLD|translate_whole|restore_sections_markdown|render_meta_header_html|collect_rag_sections|translated_title|is_heading_degraded" pipelines/litedoc_pipeline.py
```

### §6.6 C6 驗收
```bash
grep -nE "def run_phase4|rag_indexer.index|translated_title=|'litedoc'" pipelines/litedoc_pipeline.py
# 門檻：litedoc 不在 rag_indexer _is_chunk ≥3 tuple、走預設 ≥10（rag_indexer 零改）
grep -c "litedoc" processor/rag_indexer.py              # 期望 0（引擎未被改）
```

### §6.7 C7 驗收
```bash
ls -la tests/test_litedoc_pipeline.py
grep -ciE "key.?chang|summary_key|同基準|dispatch|fallback" tests/test_litedoc_pipeline.py
pytest tests/test_litedoc_pipeline.py -v
pytest tests/ -q                                        # 全套件基線 + 新增
```

### §6.8 C8（Checkout）驗收
```bash
pytest tests/ -q
ls .claude-logs/baton/ | grep -i PIPE-LITEDOC && echo "❌殘留" || echo "✅ baton 清空"
```

### §6.9 §5 SOP 一致性核查（BE-Refactor 強制）
```bash
grep -nE "logger\.error|logger\.exception|traceback\.format_exc" pipelines/litedoc_pipeline.py   # 用 error 必含 exc_info=True
grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py   # 期望無裸 commit（P4 委 rag_indexer）
```
> 各執行報告 §5 必貼 SOP grep 結果（空輸出貼「無命中（合規）」）。

---

## §7 不可動清單

- [ ] `pipelines/section_engine.py` — **僅 C1 純加法新增 render_meta_header_html**;嚴禁改既有任何函式（resume 42 + engine 17 測試為憑）。
- [ ] `processor/rag_indexer.py` — litedoc 走預設 ≥10、**零改**（不動 `:69` tuple）。
- [ ] `pipelines/contracts.py` 四凍結合約 — 額外 metadata 走 raw_metadata 旁路、不改欄位。
- [ ] `pipelines/resume_pipeline.py` / `pipelines/slide_pipeline.py` — 零碰。
- [ ] 三大共用真理源（domain_normalizer / glossary_extractor / translator）— consume only。
- [ ] **A 軌全部**（pipeline_core / web_server 非影子段 / processor 非本案 / static）— 零改。
- [ ] `DocumentStrategy` ABC / `PipelineFactory` 機制 — 僅新增註冊。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — section_engine HTML 扉頁 formatter（純加法·首發隔離驗證）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/section_engine.py`（純加法）+ `tests/test_section_engine.py`（追加 formatter 測試）|
| **安全性** | 🟢 高 — 純加法新函式、不碰既有 |
| **可逆性** | 🟢 高 — `git revert C1` |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置（plan U5b 排首 commit、隔離驗證後 route 才消費）|
| **具體實作細節** | ① `section_engine.py` 新增 `render_meta_header_html(authors, venue, date, doi=None, keywords=None, *, is_zh=False) -> str`，產 `<div class="paper-header-meta">` + header-authors〔zh `、`/en `, ` 分隔〕/ header-venue-date〔`·` 分隔〕/ header-doi〔`DOI: `〕/ header-keywords〔zh「關鍵字：」/en「Keywords: 」〕，**byte 對齊 A 軌 `md_restore_processor.py:460-490`**;空欄略過、全空回 ''。② `# === [PIPE-LITEDOC C1 ...] ===` 包裹。③ `tests/test_section_engine.py` 追加 render_meta_header_html 測試〔zh/en 各欄、空略過、全空回 ''、與 A 軌格式比對〕。④ 跑 §6.1：既有 17+42 全綠（不碰既有）。⑤ 產 `baton/..._C1_執行.md`（baton 暫存、嚴禁 git add）。 |

### C2 — LiteDoc 骨架與三 key 註冊（策略分派）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`（新）+ `pipelines/__init__.py` + `tests/test_litedoc_pipeline.py`（分派測試）|
| **安全性** | 🟢 高 — 骨架 stub、不接業務 |
| **可逆性** | 🟢 高 — `git revert C2` |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 依賴 C1（engine formatter 就緒）|
| **具體實作細節** | ① 新建 `pipelines/litedoc_pipeline.py`：`@PipelineFactory.register('litedoc')` + `@register('news')` + `@register('web')` 三裝飾器疊加於 `class LiteDocPipeline(DocumentStrategy)`;四方法 `run_phase1..4` strict stub（`raise NotImplementedError`）+ `rag_char_threshold` 屬性〔對齊 ≥10、僅標記〕。② `pipelines/__init__.py` 補 `from pipelines import litedoc_pipeline`（觸發註冊、同 resume/slides 範式）。③ `tests/test_litedoc_pipeline.py` 建檔 + 分派測試〔`get_strategy('litedoc'/'news'/'web')` 回 LiteDocPipeline、`get_strategy('某未知')` fallback 回 LiteDocPipeline〕。④ §6.2 + `pytest tests/ -q` 基線。⑤ 產 C2 報告（baton）。 |

### C3 — P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`（run_phase1）+ `tests/test_litedoc_pipeline.py` |
| **安全性** | 🟡 中 — 攝入鏈 + LLM metadata 抽取 |
| **可逆性** | 🟢 高 — `git revert C3` |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | 依賴 C2 |
| **具體實作細節** | ① `run_phase1`：`self.pdf_processor`(MinerU、惰性 import 同 C7-hotfix 教訓) parse → **強制 `md_cleaner.clean`**（非 resume/slides 跳過）。② `DocAnalyzer().analyze(md_path, analyzer_doc_type)`，**U2.1 映射**：`analyzer_doc_type = doc_type if doc_type in ('news','web') else 'web'`（防 fallback academic、soft-fail try/except）。③ md2json（MarkdownProcessor）→ json_process（JsonProcessor）→ tiling（TilingProcessor）產 tiles。④ 文字 LLM metadata 抽取（B 軌原生 cover-prompt、方案 A）：title/authors/date/publisher/url + **URL→publisher 解碼**;title fallback 檔名。⑤ 凍結合約欄 venue 承接 publisher 回填;`date`/`url`/`organization` 經 `meta_normalizer.normalize_fields`（旗標 `LLM_USE_META_NORM`）寫 `ctx.raw_metadata` 旁路（dict {value,source,confidence}）。⑥ `source_lang` 啟發式;`_shadow` title 綴 (測試)。⑦ → IngestionMetadataSpec（extra=forbid 不破）。⑧ 測試〔MinerU mock + metadata 旁路 + URL 解碼 + DocAnalyzer 映射 'web'〕。⑨ §6.3 + 基線。⑩ 產 C3 報告（baton）。 |

### C4 — P2 六步（消費 section_engine + 三真理源）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`（run_phase2）+ 測試 |
| **安全性** | 🟡 中 — 六步 LLM 鏈 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | 依賴 C3 |
| **具體實作細節** | ① `run_phase2`：①全文摘要（litedoc 自有 `_make_summary` 或共用、LLM 交易外）②`normalize_to_lcc(raw_domain, context_text=abstract)`〔raw_domain 讀 ctx.raw_metadata〕③`GlossaryManager` 級聯自癒〔旗標閘門、LLM 交易外、try/except 降級〕④`Translator(DEEP_THINK)` 譯摘要 + `lcc→Domains.name`→domain_name ⑤`section_engine.build_section_summaries(tiles, llm=…, abstract, source_lang, summary_model, translate_model, prompts, …, paper_id)`〔key=原文標題 path〕。② → GlossaryReadySpec（abstract/lcc/glossary/translated_abstract/domain_name/section_summaries）。③ 測試〔六步產 spec、section_summaries key〕。④ §6.4 + 基線。⑤ 產 C4 報告（baton）。 |

### C5 — P3 size-gate 翻譯與 HTML 扉頁還原（含雙語標題鏈）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`（run_phase3）+ 測試 |
| **安全性** | 🟡 中 — size-gate 分流 + 雙語標題 + meta header |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.5 |
| **依賴關係** | 依賴 C4 + C1（render_meta_header_html）|
| **具體實作細節** | ① `run_phase3`：`InjectionContext(doc_type='litedoc', domain_name, glossary, constraints)`。② **size-gate**：`settings.LITEDOC_WHOLE_TRANSLATE_THRESHOLD`（預設 15000）;full_text 字數 `<` 閾值 或 無 section → `section_engine.translate_whole`;否則 → `section_engine.restore_sections_markdown(sections, inj, tr, True, max_workers=LLM_MAX_CONCURRENT)` 取 (md, slots, zh_by_index)。③ `section_engine.is_heading_degraded(sections)` → 退化走 translate_whole fallback。④ **U5c translated_title**：is_zh → `=title`;分段 → 由 slots+zh_by_index 取頂層（level 最小/第一個 title slot）譯後文字;一鍵/退化 → `section_engine.translate_unit(title, inj, tr, "title")`。⑤ meta header：呼叫端從 ctx.raw_metadata + spec 抽 authors/venue〔publisher〕/date/doi/keywords + 依 lang 組 → `section_engine.render_meta_header_html(...)` prepend final_zh/en。⑥ rag 旁路：`section_engine.collect_rag_sections(slots, zh_by_index, translate, ctx.rag_sections)`〔分段路〕或 `single_container_sections`〔一鍵/zh 兜底〕。⑦ zh* edge：不重譯、建 per-section rag_sections。⑧ → BilingualMarkdownSpec（rag_tree_json=None）。⑨ 測試〔<15k 一鍵 calls 驗 / ≥15k 分段 / heading 退化 / translated_title 三路 / meta header HTML prepend / zh edge〕。⑩ §6.5 + 基線。⑪ 產 C5 報告（baton）。 |

### C6 — P4 Async RAG（rag_indexer ≥10 + 雙語標題）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`（run_phase4）+ 測試 |
| **安全性** | 🟢 高 — 委共用 rag_indexer |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.6 |
| **依賴關係** | 依賴 C5 |
| **具體實作細節** | ① `run_phase4`：取 `paper_db_id`（paper_manager、try/except 降級 None）;呼 `rag_indexer.index(ctx.rag_sections, ctx.glossary_ready.section_summaries, 'litedoc', vectors_dir, paper_db_id, rag_tree_path, title=原文標題, translated_title=U5c 譯題)`。② 門檻走 `is_chunk_meaningful` 預設 ≥10（litedoc 不入 ≥3 tuple、**rag_indexer 零改**）。③ 四產物（FAISS/paper_chunks/index_meta/rag_tree.json）;Embedding 交易外、paper_db_id None 降級;異常拋出 Orchestrator 標 rag_status='failed' 不阻 reading_ready。④ → RagDbSpec。⑤ 測試〔mock rag_indexer 驗傳參 doc_type='litedoc'+translated_title、門檻 ≥10、降級〕。⑥ §6.6 + 基線。⑦ 產 C6 報告（baton）。 |

### C7 — 單元與接縫整合測試（雙鎖）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_litedoc_pipeline.py`（補全）|
| **安全性** | 🟢 高 — 純測試 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.7 |
| **依賴關係** | 依賴 C1-C6 |
| **具體實作細節** | 補全 `tests/test_litedoc_pipeline.py`：① 分派四路〔litedoc/news/web/unknown fallback〕。② P1-P4 契約〔C2-C6 已隨各 commit 加、本 commit 補強整合〕。③ **§7.2 P2→P3→P4 key-changing 整合**：FakeTranslator 真改 title、斷言 P2 section_summaries key 與 P3 rag_sections summary_key 同基準＝原文標題 path、下游 match;含 size-gate 兩路徑〔<15k 一鍵 / ≥15k 分段〕之 translated_title 正確性。④ §6.7 全綠。⑤ 產 C7 報告（baton）。 |

### C8 — Checkout 收官

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `prompts/INDEX.md` + baton 歸檔（plan→plans/、tasks→tasks/、C1-C8 報告→executions/）|
| **安全性** | 🟢 高 — 純歸檔/狀態 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.8 |
| **依賴關係** | 依賴 C1-C7 全 ship |
| **具體實作細節** | ① Conformance 五維度（目標規格 U1-U9+U2.1/U5b/U5c / tasks §6 grep+pytest / 不可動 §7 / 提示詞稽核 / msg §8）+ §7.2 整合存在且通過（C7 key-changing、**免豁免**）。② baton 一次性 `mv`+`git add`：plan→plans/、tasks→tasks/、C1-C8 報告→executions/。③ TODO 結案（移 WIP、頂端完成表、索引 ✅）+ 全量 hash 自癒。④ 產 C8 報告隨歸檔。⑤ 嚴禁自發 commit/push。 |

---

## §9 Open Questions

無。（plan v3 §9 七 OQ 已於 baron review 全 🟢 定案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-LITEDOC 原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序執行;Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-LITEDOC executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動 plan 指明外之代碼;Run 階段 baton 暫存嚴禁 git add;嚴禁自動 commit/push;section_engine 僅純加法 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔、經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令、不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-19)：初版拆分（8 Commit：C1 section_engine HTML 扉頁 formatter〔純加法首發隔離〕/ C2 骨架三 key 註冊 / C3 P1 MinerU 攝入+DocAnalyzer 映射 U2.1+URL publisher 解碼+raw_metadata 旁路 / C4 P2 六步消費 section_engine+三真理源 / C5 P3 size-gate+HTML 扉頁+U5c 雙語標題鏈 / C6 P4 rag_indexer ≥10+translated_title / C7 單元+§7.2 key-changing 整合 / C8 Checkout;全消費真理源、rag_indexer/contracts 零改;SOP §6.9 核查;§7.2 不豁免）
