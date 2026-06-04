# PIPE-RESUME ResumePipeline 策略管線 — Tasks

> 本文件為 PIPE-RESUME 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8、四輪對接稽核定稿）產出，含 7 個 Commit（C1-C6 實作 + C7 Checkout 收官）。
> 工作流類別：**BE-Refactor**（強制 logging SOP + database SOP 一致性核查）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `pipelines/resume_pipeline.py`（ResumePipeline 四 Phase 策略插件）/ `tests/test_resume_pipeline.py`（策略分派 + P1-P4 契約單元測試） |
| **修改檔案** | 0 個 | 業務代碼零改動（複用 `ResumeProcessor`/`rag_processor`/三大真理源/Orchestrator 皆為**呼叫**、非改動）；`custom_metadata` 上游合約擴充屬硬前置、**不在本任務**（見 §9） |
| **目錄初始化** | 0 個 | `pipelines/` 已於 PIPE-CORE 落地 |
| **狀態更新** | 2 個 | `TODO.md`（高優先新增 🟡 WIP 條目）/ `prompts/INDEX.md`（PIPE-RESUME Tasks 提示詞歸檔） |
| **Commits** | 7 個 | C1 → C2 → C3 → C4 → C5 → C6 → C7（Checkout） |
| **baton 歸檔** | 1 次 | C7 收官：`mv` baton plan_v1（保留 `_v1` 檔名）+ tasks + C1-C7 執行報告 → `plans/` + `tasks/` + `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 大改版要求 `doc_type` 分流由主幹 `if/elif`（`pipeline_core.py L542-568`）下放為五條高內聚策略插件；ResumePipeline 為縱向絞殺第一路，須將散落的履歷處理（Vision 轉錄、metadata 抽欄、tiling bypass、RAG ≥3 過濾）收斂為一條跨四 Phase 策略管線，交付物對齊 PIPE 四份凍結合約。
- **解法**：於 `pipelines/resume_pipeline.py` 落地 `ResumePipeline(DocumentStrategy)`，以 6 個原子 Commit 漸進實作——`C1 — 策略骨架與工廠註冊（插件註冊與四方法骨架）` → `C2 — P1 Ingestion（Vision 整份解析與元數據）` → `C3 — P2 Glossary & Context Prep（四步循序自癒）` → `C4 — P3 Translation & Restore（100% Bypass 翻譯還原）` → `C5 — P4 Async RAG（門檻 ≥3 技能詞保護）` → `C6 — 單元測試（策略分派與四 Phase 契約）`，最後 `C7 — Checkout（收官歸檔與 TODO 結案）`。
- **影響範圍**：100% 新增檔案（策略插件 + 測試）；複用既有模組皆為呼叫、零業務代碼改動；影子期屬 B 軌，A 軌 `pipeline_core.py` resume branch 保留至 Flip。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/factory.py` | `PipelineFactory.register`/`get_strategy` 已落地（PIPE-CORE）；`resume` 尚未註冊任何策略 | 待 `@register('resume')` 掛入 ResumePipeline |
| `pipelines/base_strategy.py` | `DocumentStrategy` ABC 四抽象方法 `run_phase1..4(ctx)→四合約` 已落地 | 待 ResumePipeline 子類實作 |
| `pipelines/resume_pipeline.py` | **不存在** | 待新建（本任務核心交付物） |
| `processor/resume_processor.py` | `ResumeProcessor` Vision 忠實轉錄 + 黑名單 `RESUME_TITLE_BLACKLIST`（L59）已穩定 | P1 複用、不改 |
| `processor/domain_normalizer.py` | `normalize_to_lcc(raw_domain, context_text=None)` 已落地 | P2 消費 |
| `processor/glossary_extractor.py` | `GlossaryManager.query_cascade/extract_terms/upsert_terms` 已落地 | P2 消費 |
| `processor/translator.py` | `Translator.translate(text,ctx,mode,text_type)` + `InjectionContext` + `TranslateMode` 已落地 | P2/P3 消費 |
| `processor/rag_processor.py` | `_is_chunk_meaningful(doc, doc_type)` + `MIN_CHUNK_RESUME_SLIDES=3` 已落地 | P4 複用、不改 |
| `pipelines/contracts.py` | `IngestionMetadataSpec`（`extra="forbid"`、無 `custom_metadata`）；其餘三合約完整 | `custom_metadata` 履歷專屬欄落點屬上游硬前置（見 §9） |

---

## §3 觀察問題

### 問題 #1：resume 處理散落主幹、無策略邊界
- **證據**：`pipeline_core.py#L546` `elif doc_type == 'resume'` → `L552` `parser = ResumeProcessor()`；`L568`/`L717` 多處 resume 條件硬編碼。
- **影響**：履歷四 Phase 邏輯與其他文體耦合於 God Class，違反 PIPE 三層解耦；無法獨立測試與影子驗證。

### 問題 #2：四 Phase 產物未對齊凍結合約
- **證據**：現行 resume 路徑直接寫 output，無 `IngestionMetadataSpec`/`GlossaryReadySpec`/`BilingualMarkdownSpec`/`RagDbSpec` 交接點。
- **影響**：Phase 間資料流無 Pydantic 驗證，跨 Phase 隱性依賴難以追蹤。

---

## §4 設計方案

按 Commit 漸進落地 `ResumePipeline`，每個實作 Commit 對映一個 `run_phaseN` 方法（或骨架/測試），語意完整、獨立可測、獨立可逆。

### §4.1 C1 — 策略骨架與工廠註冊
新建 `pipelines/resume_pipeline.py`：`class ResumePipeline(DocumentStrategy)` + `@PipelineFactory.register('resume')`；四方法 `run_phase1..4(ctx)` 先以 `raise NotImplementedError` 佔位；定義策略實例暫存欄（interim 穿線 `phone`/`email`/`domain`，見 §9）。

### §4.2 C2 — P1 Ingestion（run_phase1）
實作 `run_phase1`：呼叫 `ResumeProcessor` Vision 核心（複用、不改），輸出 Markdown + Tiles；抽欄 `candidate_name→title`；建 `IngestionMetadataSpec(title, source_lang, tiles)`（零 Abstract/LCC/Glossary）；`phone`/`email`/`domain` 暫存策略實例（interim、待 `custom_metadata` 硬前置，見 §9）。

### §4.3 C3 — P2 Glossary & Context Prep（run_phase2，四步循序）
實作 `run_phase2`：①`normalize_to_lcc(raw_domain=暫存 domain, context_text=履歷全文)`；②做整份履歷摘要→`abstract`；③`GlossaryManager` `query_cascade`→（缺詞）`extract_terms`（將②摘要+①LCC 注入翻譯 prompt context）→`upsert_terms` 冪等回寫→凍結；④`Translator.translate(…,DEEP_THINK)` 翻 `abstract`→`translated_abstract` + `lcc→Domains.name` 唯讀 PK 檢索→`domain_name`；建 `GlossaryReadySpec`。

### §4.4 C4 — P3 Translation & Restore（run_phase3，100% Bypass）
實作 `run_phase3`：建 `InjectionContext(lcc, glossary, zh_summary←translated_abstract, domain_name, doc_type='resume')`；`Translator.translate(text, ctx, mode=NORMAL, text_type="content")` 整份翻（不切 Section/不開 Sliding Window）；`md_restore` 純樣板渲染；建 `BilingualMarkdownSpec(final_zh_path, final_en_path, translated_abstract〔沿用 P2〕)`。

### §4.5 C5 — P4 Async RAG（run_phase4，門檻 ≥3）
實作 `run_phase4`：複用 `_is_chunk_meaningful(doc, doc_type='resume')`（不改演算法）；批量一次 Embedding→FAISS + `PaperChunk` 寫庫；建 `RagDbSpec(vectors_path, paper_chunk_count, index_meta)`；非同步由 Orchestrator 注入 `dispatch_p4` 達成、本體同步。

### §4.6 C6 — 單元測試
新建 `tests/test_resume_pipeline.py`：策略分派 / P1 契約 / P2 契約 / P3 Bypass+doc_type / P4 門檻；mock LLM 不實打 API；全套件綠。

### §4.7 C7 — Checkout / 收官歸檔
Conformance 三維度驗收（plan §2 U1-U5 / tasks §6 grep+pytest / 不可動清單 git 證據）+ SOP 一致性核查（logging + database）+ baton 一次性歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `custom_metadata` 硬前置未落地致 P1→P2 `domain` 斷鏈 | 🟡 中 | 採 plan 既決：P1 暫存 `domain` 於策略實例穿線給 P2，不依賴未擴充的凍結合約（§9） |
| 複用 `ResumeProcessor`/`_is_chunk_meaningful` 時誤改演算法 | 🟡 中 | §7 不可動清單明列；C2/C5 僅**呼叫**、grep 證明未改原檔 |
| P2 串接三大真理源 LLM 呼叫落入 DB 交易內致 SQLite 鎖庫 | 🔴 高 | database SOP：LLM 呼叫一律在 `session.begin()` 交易外；`lcc→Domains.name` 唯讀免交易；C3 執行報告貼 §5 核查 grep |
| `BilingualMarkdownSpec.translated_abstract` 必填漏帶致 ValidationError | 🟡 中 | C4 明確沿用 P2 `translated_abstract`；C6 加契約測試 |
| DEEP_THINK 未設 `LLM_THINKING_BUDGET>0` 靜默退化 | 🟢 低 | C3 細節註明前置；C6 測試以 monkeypatch 顯式設 budget |

---

## §6 測試計畫

### §6.0 既有測試底線（每個 Commit 後必跑）
```bash
pytest tests/ -v   # 防 Regression：既有全套件不得因新增策略而轉紅
```

### §6.1 C1 驗收（骨架與註冊）
```bash
grep -nE "class ResumePipeline|@PipelineFactory.register\('resume'\)|def run_phase[1-4]" pipelines/resume_pipeline.py  # 期望：類 + 註冊 + 四方法命中
python -c "from pipelines.factory import PipelineFactory; import pipelines.resume_pipeline; print(type(PipelineFactory.get_strategy('resume')).__name__)"  # 期望：ResumePipeline
grep -nE "doc_type *== *'resume'|if/elif" pipelines/resume_pipeline.py  # 期望：0 命中（策略內無 doc_type 分支）
```

### §6.2 C2 驗收（P1 Ingestion）
```bash
grep -nE "IngestionMetadataSpec|ResumeProcessor|title *=|source_lang" pipelines/resume_pipeline.py  # 期望：建 Spec + 複用 ResumeProcessor
pytest tests/test_resume_pipeline.py -k "phase1 or ingestion" -v  # 期望：title=candidate_name、無 Abstract/LCC/Glossary 斷言通過
```

### §6.3 C3 驗收（P2 四步循序）
```bash
grep -nE "normalize_to_lcc|query_cascade|extract_terms|upsert_terms|TranslateMode.DEEP_THINK|Domains" pipelines/resume_pipeline.py  # 期望：四步真理源呼叫齊全
grep -nE "\.commit\(\)" pipelines/resume_pipeline.py | grep -v "with .*session.*begin\(\)"  # 期望：無命中（database SOP，無裸 commit）
pytest tests/test_resume_pipeline.py -k "phase2 or glossary or lcc" -v
```

### §6.4 C4 驗收（P3 Bypass）
```bash
grep -nE "InjectionContext|doc_type='resume'|TranslateMode.NORMAL|final_zh_path|translated_abstract" pipelines/resume_pipeline.py  # 期望：注入 doc_type='resume' + 沿用 translated_abstract
pytest tests/test_resume_pipeline.py -k "phase3 or bypass" -v
```

### §6.5 C5 驗收（P4 RAG）
```bash
grep -nE "_is_chunk_meaningful|RagDbSpec|PaperChunk|vectors_path" pipelines/resume_pipeline.py  # 期望：複用過濾 + 建 RagDbSpec
pytest tests/test_resume_pipeline.py -k "phase4 or rag or chunk" -v
```

### §6.6 C6 驗收（測試套件）
```bash
pytest tests/test_resume_pipeline.py -v  # 期望：全綠（策略分派 + P1-P4 契約）
pytest tests/ -v 2>&1 | tail -3        # 期望：全套件綠（除既存環境性 test_settings_log_format_default_auto）
```

### §6.7 SOP 一致性核查（C2-C5 落地前強制、貼執行報告）
```bash
grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/resume_pipeline.py  # logging：error 必含 exc_info=True
grep -nE "\.commit\(\)" pipelines/resume_pipeline.py | grep -v "with .*session.*begin\(\)"      # database：無裸 commit
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本任務中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py`（A 軌 resume branch L542-568 影子期保留）/ `web_server.py` / `paper_manager.py` — 100% 不動
- [ ] `processor/resume_processor.py` `ResumeProcessor` Vision 核心與 `RESUME_TITLE_BLACKLIST`（`process L92`/`_validate_vision_output L217`/`L59`）— P1 僅**呼叫**、不改解析哲學或黑名單
- [ ] `processor/rag_processor.py` `_is_chunk_meaningful`（L41-87）+ `MIN_CHUNK_RESUME_SLIDES=3`（L27）+ 結構化 regex（L33-37）— P4 僅**複用**、不改過濾演算法
- [ ] `processor/domain_normalizer.py` / `glossary_extractor.py` / `translator.py` 三大真理源落地簽名 — 僅**消費**、不改
- [ ] `pipelines/contracts.py` `IngestionMetadataSpec` `extra="forbid"` 凍結合約 — **不擴 `custom_metadata`**（屬上游硬前置、本任務不動，見 §9）
- [ ] `pipelines/orchestrator.py` / `context.py` / `base_strategy.py` / `factory.py` — 僅**繼承/呼叫/註冊**、不改本體
- [ ] 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端讀取路徑 — 零改動
- [ ] **主 repo 目錄** — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — 策略骨架與工廠註冊（插件註冊與四方法骨架）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `pipelines/resume_pipeline.py`（骨架）；無 `.bak`（純新建檔） |
| **安全性** | 🟢 高 — 純新增檔案、僅註冊插件，未實作任何 Phase 邏輯、零 runtime 行為改變（旗標未動、A 軌不受影響） |
| **可逆性** | 🟢 高 — `git revert C1` 刪檔即完全回滾、無連鎖 |
| **驗收 grep 條件** | §6.1（類定義 + `@register('resume')` + 四方法 + `get_strategy('resume')` 回 ResumePipeline + 0 `doc_type==` 分支） |
| **依賴關係** | 無前置（PIPE-CORE 已落地 `DocumentStrategy`/`PipelineFactory`） |
| **具體實作細節** | 1) 新建 `pipelines/resume_pipeline.py`，`from pipelines.base_strategy import DocumentStrategy`、`from pipelines.factory import PipelineFactory`、`from pipelines.context import PipelineContext`、`from pipelines.contracts import IngestionMetadataSpec, GlossaryReadySpec, BilingualMarkdownSpec, RagDbSpec`。2) `@PipelineFactory.register('resume')` 裝飾 `class ResumePipeline(DocumentStrategy)`。3) `__init__` 定義 interim 暫存欄 `self._raw_meta: dict = {}`（穿線 phone/email/domain，§9）。4) 四方法 `run_phase1..4(self, ctx) -> 對應 Spec` 先 `raise NotImplementedError("PIPE-RESUME C2-C5")` 佔位。5) 全檔以 `# === [PIPE-RESUME C1 START] ===` / `# === [PIPE-RESUME C1 END] ===` 包裹（Flip/審計錨點）。6) 模組頂 `logger = logging.getLogger(__name__)`（logging SOP，不呼叫 basicConfig）。 |

### C2 — P1 Ingestion（Vision 整份解析與元數據）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/resume_pipeline.py`（實作 `run_phase1`）+ 改前 `.bak` |
| **安全性** | 🟢 高 — 複用既有 `ResumeProcessor`（不改原檔），僅在新策略檔組裝 `IngestionMetadataSpec` |
| **可逆性** | 🟢 高 — `git revert C2` 還原 `run_phase1` 為骨架 |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | C1 |
| **具體實作細節** | 1) `run_phase1(ctx)`：以 `ResumeProcessor`（複用 `process`/Vision 核心）渲染並 Vision 整份解析，得忠實去浮水印 Markdown + 物理分組 Tiles。2) 抽欄：`candidate_name→title`；`source_lang` 取原生語言。3) 建 `IngestionMetadataSpec(title=..., source_lang=..., tiles=[...])`（**零 Abstract/LCC/Glossary/翻譯**、對齊 R1.1）。4) `phone`/`email`/`domain` 抽出後暫存 `self._raw_meta`（interim 穿線、待 `custom_metadata` 硬前置，§9）。5) 主標題黑名單違反 → 拋 `PDFParseError`（複用 `_validate_vision_output`）。6) 回傳 Spec（Orchestrator 自動 `early_emit_hook` 快軌 title、本策略不寫 emit 碼）。7) `# === [PIPE-RESUME C2 START/END] ===` 包裹。 |

### C3 — P2 Glossary & Context Prep（四步循序自癒）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/resume_pipeline.py`（實作 `run_phase2`）+ 改前 `.bak` |
| **安全性** | 🟡 中 — 串接三大真理源 LLM 呼叫，須嚴守 database SOP 交易邊界 |
| **可逆性** | 🟢 高 — `git revert C3` 還原 `run_phase2` 為骨架 |
| **驗收 grep 條件** | §6.3 + §6.7（無裸 commit、LLM 交易外） |
| **依賴關係** | C2（消費 `self._raw_meta.domain` + Tiles 全文） |
| **具體實作細節** | **步驟①**：`normalize_to_lcc(raw_domain=self._raw_meta['domain'], context_text=履歷全文/技能)` 得標準 LCC。**步驟②**：做整份履歷摘要→`abstract`（置於 Glossary 前）。**步驟③**：`gm = GlossaryManager(...)`；`source_lang=ctx.ingestion.source_lang`、`target_lang='zh-tw'`（固定繁中）；`existing = gm.query_cascade(source_lang, target_lang, domain=lcc)`；缺詞分支 `gm.extract_terms(source_text, translated_text, source_lang, target_lang, domain=lcc)`（將②摘要+①LCC 組入翻譯 **prompt context**、非形參）→ `gm.upsert_terms(...)` 冪等回寫；**LLM 呼叫全程在 DB 交易外**；Glossary 凍結。**步驟④**：`Translator.translate(abstract, ctx_for_summary, mode=TranslateMode.DEEP_THINK, text_type="abstract")`→`translated_abstract`（前置：`LLM_THINKING_BUDGET>0` + 思考世代模型，否則退化 NORMAL）；`lcc→Domains.name` 以 LCC 為 PK **唯讀單表檢索**（無 helper、`session` 唯讀免交易）→`domain_name`。**交付**：`GlossaryReadySpec(abstract, lcc, glossary, translated_abstract, domain_name, chapter_summaries=None)`。`# === [PIPE-RESUME C3 START/END] ===` 包裹。 |

### C4 — P3 Translation & Restore（100% Bypass 翻譯還原）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/resume_pipeline.py`（實作 `run_phase3`）+ 改前 `.bak` |
| **安全性** | 🟢 高 — 純呼叫 `Translator` + 樣板渲染，無 schema 變動 |
| **可逆性** | 🟢 高 — `git revert C4` 還原 `run_phase3` 為骨架 |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | C3（消費 `GlossaryReadySpec`） |
| **具體實作細節** | 1) 建 `InjectionContext(lcc=spec.lcc, glossary=spec.glossary, zh_summary=spec.translated_abstract, domain_name=spec.domain_name, doc_type='resume')`（**doc_type='resume'** 套「正式商務中文」風格）。2) 正文 **100% Bypass**：不切 Section、不開 Sliding Window，整份 `Translator.translate(text, ctx, mode=TranslateMode.NORMAL, text_type="content")`。3) `md_restore` 純樣板渲染（無 `extra_info`），產 `final_zh.md`/`final_en.md` 實體檔。4) 建 `BilingualMarkdownSpec(final_zh_path=..., final_en_path=..., translated_abstract=spec.translated_abstract〔沿用 P2、必填〕, rag_tree_json=...)`。5) 嚴禁含 AI Questions/章節 Summary（R3.1）。`# === [PIPE-RESUME C4 START/END] ===` 包裹。 |

### C5 — P4 Async RAG（門檻 ≥3 技能詞保護）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/resume_pipeline.py`（實作 `run_phase4`）+ 改前 `.bak` |
| **安全性** | 🟡 中 — 批量 Embedding + `PaperChunk` 寫庫，須守 database SOP（批量 `session.execute(insert(...))`、極短交易） |
| **可逆性** | 🟢 高 — `git revert C5` 還原 `run_phase4` 為骨架；RAG 失敗本就不阻主鏈 |
| **驗收 grep 條件** | §6.5 + §6.7 |
| **依賴關係** | C4（消費 `BilingualMarkdownSpec` 乾淨 translate JSON） |
| **具體實作細節** | 1) `run_phase4(ctx)`：唯一輸入為 P3 乾淨 translate 產物。2) Chunk 過濾複用 `_is_chunk_meaningful(doc, doc_type='resume')`（門檻 ≥3 保技能詞、email/phone/url 不論長度保留、**不改演算法**）。3) 批量一次 Embedding→FAISS + `PaperChunk` 寫庫（database SOP：批量 `session.execute(insert(PaperChunk), [...])`、交易內不含 LLM/Embedding 計算）。4) 建 `RagDbSpec(vectors_path, paper_chunk_count, index_meta)`。5) 失敗僅 `logger.warning(..., exc_info=True)` + 由 Orchestrator 標 `rag_status='failed'`（不阻 `reading_ready`）；非同步派發歸 Orchestrator `dispatch_p4`、本體同步。`# === [PIPE-RESUME C5 START/END] ===` 包裹。 |

### C6 — 單元測試（策略分派與四 Phase 契約）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `tests/test_resume_pipeline.py`；無 `.bak`（純新建檔） |
| **安全性** | 🟢 高 — 純測試檔、mock LLM 不實打 API |
| **可逆性** | 🟢 高 — `git revert C6` 刪測試檔 |
| **驗收 grep 條件** | §6.6 |
| **依賴關係** | C1-C5（測試完整四 Phase） |
| **具體實作細節** | 新建 `tests/test_resume_pipeline.py`（mock LLM/Embedding、monkeypatch 旗標與 `LLM_THINKING_BUDGET`）：1) **策略分派**：`PipelineFactory.get_strategy('resume')` 回 `ResumePipeline`、無 `doc_type==` 分支。2) **P1 契約**：`run_phase1` 回 `IngestionMetadataSpec`、`title==candidate_name`、斷言**不含** Abstract/LCC/Glossary。3) **P2 契約**：`normalize_to_lcc` cache 命中 0 API、`GlossaryReadySpec.abstract` 必填、缺詞翻譯注入摘要+LCC prompt context、`domain_name` 由 `Domains.name` 解析、Glossary 凍結。4) **P3 Bypass**：100% Bypass、`InjectionContext.doc_type=='resume'`、`BilingualMarkdownSpec` 含 `final_zh_path`/`final_en_path`/`translated_abstract`(沿用)。5) **P4 門檻**：`_is_chunk_meaningful` resume `Python` 保留、`john@x.com` 保留、純數字過濾；RAG 失敗主鏈 `reading_ready` 不受影響。`# === [PIPE-RESUME C6 START/END] ===` 包裹。 |

### C7 — Checkout / 收官歸檔（Conformance 驗收與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（結案）；`mv` baton plan_v1/tasks/C1-C7 報告 → `plans/`+`tasks/`+`executions/`；無業務代碼、無 `.bak` |
| **安全性** | 🟢 高 — 純文件歸檔與狀態更新 |
| **可逆性** | 🟢 高 — `git revert C7` 還原歸檔（檔案 mv 可逆） |
| **驗收 grep 條件** | 三維度：plan §2 U1-U5 逐項 / tasks §6 grep+pytest 全綠 / 各報告 §6 不可動清單 git 證據 + §6.7 SOP 核查無命中（合規） |
| **依賴關係** | C1-C6 全部 ship |
| **具體實作細節** | 1) Conformance 三維度逐項交叉比對（目標規格/驗收條件/不可動清單）+ SOP 一致性核查（logging + database 貼 grep 結果，空輸出貼「無命中（合規）」）。2) 更新 `TODO.md`：✅ 已完成新增 BE-Refactor PIPE-RESUME 表（C1-C7，Hash 待 baron 回填）+ 移除 active 條目 + 索引標 ✅ + 歷史全量 Hash 自癒。3) 一次性 `mv` baton（plan_v1〔**保留 `_v1` 檔名**〕/tasks/C1-C7 執行報告）→ `plans/`/`tasks/`/`executions/` + `git add`。4) 確認 baton/ 僅剩 README.md。5) `ls prompts/` grep PIPE-RESUME 確認各階段 md 齊全。6) 嚴禁自發 commit/push（msg 寫 `/tmp/PIPE-RESUME_C7_msg.txt` 由 baron 手動）。 |

---

## §9 Open Questions

> 原則上 tasks 階段 Open Questions 應已於 plan 審核結案。本任務有 **1 項已拍板、但需執行期遵守的前置約束**，據實記錄（非偽「無」）：

| 開放問題 | 狀態 / 推薦答案 | 理由 |
|---|---|---|
| **`IngestionMetadataSpec.custom_metadata` 硬前置**：履歷 `phone`/`email`/`domain` 落點欄在落地凍結合約（`extra="forbid"`）中不存在，本任務 P1 如何交付？ | **已於 plan §7/§99.2 拍板：本任務不擴充凍結合約**（屬上游共用合約變更、影響五路、待獨立授權）。**interim 機制**：P1 將 `phone`/`email`/`domain` 暫存策略實例 `self._raw_meta`、穿線給 P2 消費 `domain`；`IngestionMetadataSpec` 僅交付落地欄（`title`/`source_lang`/`tiles`）。**Flip 阻擋**：`custom_metadata` 正式入合約前，ResumePipeline 僅能影子 B 軌驗證、不得正式 Flip 線上流量。 | 不在 tasks 階段擅自變更跨五路的凍結合約 + PIPE-SPEC（CLAUDE.md §1.6 schema 變動 / 跨任務影響強制詢問）；interim 暫存使本任務四 Phase 可端到端落地與測試、零上游風險；待 baron 另立上游任務擴 `custom_metadata` 後再接線。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-RESUME 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-RESUME executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼與凍結合約；嚴禁跨 Commit 混合不同 Phase；嚴禁自動 `git commit` / `git push`；BE-Refactor 落地前強制 §6.7 SOP 一致性核查 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全域硬規則；四 Phase 規格唯一源在 plan §2 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：初版拆分完成——7 Commit（C1 策略骨架與工廠註冊 / C2 P1 Ingestion / C3 P2 Glossary & Context Prep 四步 / C4 P3 Translation & Restore Bypass / C5 P4 Async RAG / C6 單元測試 / C7 Checkout 收官）；依 plan_v1（§99.2 內部 v8、四輪對接稽核定稿）；`custom_metadata` 硬前置記入 §9（plan 既決 defer、interim 策略實例暫存穿線）。
