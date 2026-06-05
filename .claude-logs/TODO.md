# Mad Professor — TODO（最後更新 2026-06-02，GOLDEN-BASELINE Check 收官）

> 本文件為 **Single Source of Truth**（依 `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §2.1）。
> **任何規劃 / 執行 / hotfix 前必先 view 框架文件**：`.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`
> 對應 template 位於 `.claude-logs/templates/template_plan.md` / `template_execution.md` / `template_hotfix.md`
>
> **狀態 Emoji**（依框架 §2.2）：⬜ 未開始 / 🔵 plan 中 / 🟡 WIP / ✅ done
> **任務生命週期**（依框架 §2.5）：done 後**必須**從下方 active 列表移除、改寫入頂部 ✅ 已完成表格 + 同步索引。

---

## ✅ 已完成

### BE-Refactor PIPE-RESUME ResumePipeline策略管線（PIPE 大改版縱向五路絞殺第 1 路）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `pipelines/resume_pipeline.py` 骨架 + `@PipelineFactory.register('resume')` 註冊 + `DocumentStrategy` 四方法 stub + `rag_char_threshold=3` + interim `_raw_meta` 穿線容器 | `f3d4e41` |
| C2 | 實作 `run_phase1` 全鏈 P1 Ingestion（`ResumeProcessor` Vision + Metadata Stage A + `DocAnalyzer` + md2json/json_process/tiling 產 Tiles）→ IngestionMetadataSpec〔title=candidate_name / source_lang 啟發式 / 零 Abstract/LCC/Glossary〕；phone/email/domain 暫存 `_raw_meta`；**baron 拍板**擴 `PipelineContext` 加 pdf_path/owner_id + web_server 影子派發傳值 | `d7edcd9` |
| C3 | 實作 `run_phase2` 四步循序自癒：①`normalize_to_lcc(raw_domain, context_text=履歷全文)` ②LLM 生成原文 `abstract` ③`GlossaryManager` 旗標閘門自癒〔query_cascade→缺詞 extract_terms〔注入摘要+LCC〕→upsert 冪等、LLM 交易外〕④`Translator(DEEP_THINK)`→`translated_abstract` + `lcc→Domains.name` PK 唯讀免交易 → GlossaryReadySpec | `48aa5df` |
| C4 | 實作 `run_phase3`：`InjectionContext(doc_type='resume')` 100% Bypass 整份 `Translator.translate(NORMAL,content)`〔不切 Section/不開 Sliding Window〕+ md_restore 純樣板渲染〔廢除 extra_info、嚴禁 AI Questions/Summary〕→ final_zh/final_en → BilingualMarkdownSpec〔translated_abstract 沿用 P2〕 | `8971a19` |
| C5 | 實作 `run_phase4`：複用 `RagProcessor._create_vector_store`〔`_is_chunk_meaningful` 門檻 ≥3 保技能詞/email/phone/url + FAISS + paper_chunks 批量寫庫 + index_meta〕；Embedding 於交易外、paper_db_id None 優雅降級；異常拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready → RagDbSpec | `e8a7429` |
| C6 | 新建 `tests/test_resume_pipeline.py` 15 測試（策略分派 + P1-P4 契約、mock LLM/Embedding 隔離）；全套件 480 passed | `fabb114` |
| C7 | Conformance 三維度驗收（目標規格 U1-U5 / 測試 §6 / 不可動清單）+ baton/ 一次性歸檔（plan_v1〔保留 _v1〕/tasks/C1-C7 報告）+ 歷史全量 Hash 自癒 + 結案 | `a644e48` |
| C7-hotfix | 緊急熱修復：`pipelines/__init__.py` 補 `from pipelines import resume_pipeline` 觸發 `@register('resume')`——修復 runtime 路徑無人 import 策略致 `get_strategy('resume')` 回 NullStrategy、影子上傳 P1 拋 NotImplementedError 阻斷；factory._registry 含 'resume' 驗證通過、全套件 480 passed | `d2e0af2` |
| C8-hotfix | 緊急熱修復：`web_server.py` `run_pipeline_shadow` 影子完成後補 `paper_manager.upsert_paper` 寫 Paper row——修復影子 P1-P4 全綠生實體檔但 `run_pipeline_shadow` 漏寫庫致 Paper row 未建、`list_papers`(讀 DB) 撈不到、前端不顯示 (測試) 列；校正版 str 絕對路徑 + ctx.bilingual 守衛 + doc_type-agnostic 五路通用；test_pipe_scaffold 5 passed、全套件 480 passed | `b0713e7` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8、四輪對接稽核定稿）
> **PIPE 對齊**：PIPE 縱向五路絞殺**第 1 路**；ResumePipeline 四 Phase（P1 Ingestion / P2 Glossary & Context Prep / P3 Translation & Restore / P4 Async RAG）全落地；消費 DomainNormalizer LCC + GlossaryManager 級聯自癒 + 呼叫 Translator 雙模式；對齊 PIPE-CORE 落地 ABC `run_phase1..4` / 四凍結合約 / PIPE-SCAFFOLD 影子機制。
> **baron 拍板（AskUserQuestion）**：① C2 擴 `PipelineContext` 加 pdf_path/owner_id（首落地隨 PIPE-RESUME、五路共用基建）；② P1 全鏈編排（忠實 PIPE-SPEC §1.1①「Tiles 在 P1 產出」）。
> **defer / Flip 阻擋**：`custom_metadata` 履歷專屬欄暫存 `_raw_meta` 穿線（tasks §9 硬前置）；P1 凍結合約未全域擴 `custom_metadata` 前僅影子 B 軌驗證、不得正式 Flip 線上流量。

### BE-Refactor PIPE-RESUME v9 影子整合與規格同步（PIPE 縱向五路第 1 路·影子保真整合）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Sync System Specs：plan_v1 + 母 plan v10 + PIPE-SPEC 三文件就地同步（`raw_metadata` 旁路欄登記 / P3「翻譯策略隔離原則」/ Phase2 摘要先行步序 / C7-C8 hotfix 史 / P1 影子後綴規格 + Flip Cleanup 待辦）；嚴禁動 Python 業務代碼 | `b97958b` |
| C2 | P1 + Context：`pipelines/context.py` 加 `raw_metadata: Dict[str,Any]={}` 狀態欄 + `run_phase1` 寫入整包原始 meta（含 regex phone/email）+ `_shadow` paper_id → title 加綴 `(測試)`（前端列表肉眼可辨、不入內容） | `e64417a` |
| C3 | P2 步序與讀取對齊：`run_phase2` ①摘要先行→②LCC（跨路統一、功能等價）+ `raw_domain` 改讀 `ctx.raw_metadata`（經 `_meta_value`）+ 廢除 `self._raw_meta` 實例暫存（`ctx.raw_metadata` 為唯一穿線載體） | `f239721` |
| C4 | P3 Business Constraints：模組常數 `_RESUME_CONSTRAINTS`〔公司/產品名保留・Email/電話/URL 原樣・技能詞英文・專利/期刊原文+對照〕+ `run_phase3` `InjectionContext(constraints=…)` 逐路注入共用 Translator（PIPE-SPEC §1.2.3.1 翻譯策略隔離） | `9bbad2d` |
| C5 | Shadow DB Fidelity：`web_server.py` `run_pipeline_shadow` C8-hotfix 影子寫庫 `meta_dict` 改優先讀 `ctx.raw_metadata` 組整包 `metadata_json`（對齊 A 軌 `upsert_paper(self._metadata)` 保真）+ title 沿用 `ctx.ingestion.title`〔含 (測試)〕+ 空值防禦 fallback；無裸 commit、A 軌 byte 不動 | `9291c5c` |
| C6 | Unit Tests：`tests/test_resume_pipeline.py` 修復 C3 遺留 2 個 `_raw_meta` 紅燈（改 `ctx.raw_metadata`）+ 追加 4 v9 契約測試（P1 影子後綴 / P2 摘要先行步序 / P3 constraints 注入 / C5 影子寫庫保真）；resume 19 passed、核心 pipelines 25 passed | `4e15905` |
| C7 | Checkout：Conformance 三維度驗收全綠（目標規格 / tasks §6 pytest+grep〔resume 19 / 目標 44 / 全套件 483 passed〕/ 不可動清單 git 證據）+ SOP 核查 + 提示詞 8 份稽核 + msg 完整性 + baton 一次性歸檔（plan_v1/tasks/C1-C7 報告 → plans//tasks//executions/，母 plan v10/PIPE-SPEC 就地 git add） | `36db1cf` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11、六項 + v10 P2 步序 + v11 表格保留）
> **PIPE 對齊**：原 PIPE-RESUME（C1-C7 已收官、四 Phase 落地）後的**影子保真整合批次**——將 raw_metadata 旁路穿線、P1 影子標題後綴、P2 摘要先行、P3 翻譯策略隔離、C5 影子寫庫保真五者整合；消費既有三大真理源 + PIPE-SCAFFOLD 影子。本批次 C1-C7 為 v9 內部序，與原 PIPE-RESUME C1-C7（上方表）區別。
> **流程註**：C7 驗收時 baron 已逐一 commit C1-C6，依框架 §2.2 回填 git log 實證 hash；C7 自身 `36db1cf`（SHADOW-HOTFIX-2 時自癒回填）。
> **Flip 阻擋（延續）**：P1 影子後綴 + 影子寫庫僅供 B 軌驗證；正式 Flip（PIPE-FLIP）待五路全通 + Golden Diff 0% + custom_metadata 凍結合約全域擴充（母 plan v11 Cleanup 含「移除 P1 影子後綴」）。

### BE-Hotfix PIPE-RESUME TILING-HOTFIX-1 — TextTiling Embedding 速率超限 (429) 批次化修復

| Commit | 內容 | Hash |
|---|---|---|
| TILING-HOTFIX-1 | `processor/tiling_processor.py:425` 分塊 embedding 由逐筆 `[embed_query(b) for b in blocks]` 改批次 `embed_documents(blocks)`〔請求 1/32 + 線性退避 15s/30s + 重試耗盡退回逐筆 + 順序保證〕，根治 TextTiling 長文/併發 429 RESOURCE_EXHAUSTED 阻斷與全套件 `test_tiling_paragraph` 併發 flaky；`# === [PIPE-RESUME TILING-HOTFIX-1 START/END] ===` 包裹僅此行；tiling 三套件 15 passed、全套件 484 passed（429 全綠、僅剩 env flake） | `702347a` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_TILING-HOTFIX-1_hotfix.md`
> **⚠️ 行為變更**：`task_type` 由 `RETRIEVAL_QUERY`→`RETRIEVAL_DOCUMENT`（對 Document-Blocks 語意更正確），向量值略異 → TextTiling 分段邊界或微幅位移。**PIPE Flip/結案前 baron 須於 MinerU 重捕五路 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`、容差 D2≥0.95/D3≥0.90），未重捕前既有基準 diff 會全面誤報。
> **flaky 認定修正**：先前 PIPE-RESUME C5–C7 全套件 `test_tiling_paragraph` 偶發失敗的真因即此 429（非純環境性 flaky），本 hotfix 一併根治。

### BE-Hotfix PIPE-RESUME SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復

| Commit | 內容 | Hash |
|---|---|---|
| SHADOW-HOTFIX-2 | B軌三處「移除矛盾、交回母提示詞」：①`web_server.py` 影子寫庫補綴 `translated_title` ` (測試)`〔前端列表優先取 translated_title、防漏顯〕②`processor/translator.py:40` STYLE_HINTS['resume'] 移除「公司名」③`pipelines/resume_pipeline.py:109` `_RESUME_CONSTRAINTS[0]` 改「產品名保留原文」——公司/機構交回母提示詞 `content_translate_prompt.txt` L5 統一「翻譯 (原文)」，消除 ②⑤ 與母提示詞反向覆寫的矛盾（公司沒翻 + doubling 源頭）；不改 `translate_processor.py`（A軌棄修）/母提示詞；`# === [PIPE-RESUME SHADOW-HOTFIX-2 START/END] ===` 包裹 + 補 2 回歸測試；resume 21 / translator 8 / 相關 19 passed、全套件 486 passed（僅 env flake） | `3d2778a` |

> **修法依據**：`.claude-logs/hotfixes/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_hotfix.md`（v2 三處「移除矛盾」版）
> **根因**：B軌履歷翻譯指令三層打架——母提示詞 L5「機構翻譯附原文」vs ②STYLE_HINTS / ⑤constraints「公司保留原文」；②為 A軌 STYLE_HINTS 逐字複製殘渣。移除 ②⑤ 矛盾後公司由 L5 統一翻譯。
> **⚠️ 行為變更 + 重捕**：B軌譯文內容改變 → 衝擊 D2/chunk；**Flip/結案前須與 TILING-HOTFIX-1 合併一次重捕 Golden Baseline**（`venv/bin/python tools/golden_baseline.py capture --all`）。
> **保留意見**：學歷地點行錯亂 / doubling 殘留（U4 + 100% Bypass 整檔單發）屬 B軌 P3 架構問題，已立 `RESUME-P3` plan 另開任務、不在本 hotfix 硬修。

### BE-Refactor MODEL-9-OPT Embedding連線與限流框架優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `settings.py` 新增 `EMBEDDING_MAX_CONCURRENT`（預設 5、env 可調）；純新增常數、C2 才消費、行為等價 | `8feaa12` |
| C2 | `config.py` EmbeddingModel 引入 class-level `_api_semaphore=threading.Semaphore(EMBEDDING_MAX_CONCURRENT)` + `embed_query/embed_image/_embed_batch〔新〕/_embed_one` 套 `@retry_call`〔Full Jitter 指數退避〕+ `with semaphore` + 重構 `embed_documents` 批次降級逐筆〔移除手動 time.sleep linear〕+ 429 extra_fields 觀測 log；`_embed_one` fallback retries=2；同步 `tiling_processor.py` 過時退避註解；embed_content 參數/_l2_normalize 不變→向量值不變→不觸發 Golden 重捕 | `9a44d41` |
| C3 | 新建 `tests/test_embedding_retry.py` 4 測試（embed_query 429 退避 / embed_image 503 重試 / embed_documents 批次降級保序+warning / Semaphore 併發上限）；4 passed、全套件 490 passed | `e86ced9` |
| C4 | Checkout：Conformance 三維度驗收全綠（目標規格 / tasks §6 grep+pytest / 不可動清單 git 證據）+ SOP 核查 + 提示詞 5 份稽核 + msg 完整性 + baton 一次性歸檔（plan/tasks/C1-C3 報告 → plans//tasks//executions/）+ hash 全量自癒 | `待 baron 回填` |

> **修法依據**：`.claude-logs/plans/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_plan.md`（§99.2 v3、review 5 點補強定稿）
> **PIPE 對齊**：基建韌性層——EmbeddingModel 接入 `llm/retry.py` 統一彈性框架（與 LLMClient 機制一致、各自獨立 Semaphore 避免跨模組死鎖）；根治高頻 Embedding 削爆全域配額連帶拖垮 LLM。**不改向量值、不觸發 Golden Baseline 重捕、可獨立先做**（排序 hotfix → MODEL-9-OPT → RESUME-P3）。
> **OQ3 上線觀察項**：併發鎖 ≠ RPM 限流；預設 5+env 可調+429 log 觀測，撞不過才上 token bucket（非本任務）。

### BE-Refactor TRANSLATOR 雙模式原子翻譯器（PIPE 大改版三大共用真理源之三）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `processor/translator.py` 定義 `InjectionContext`（7 欄 frozen+forbid、逐字對齊 PIPE-SPEC §1.2.3 v3）+ `TranslateMode`（NORMAL/DEEP_THINK）；`pipelines/contracts.py` GlossaryReadySpec 補 `domain_name`（P2→P3 載體、向後相容） | `1558f79` |
| C2 | `Translator` 系統提示詞五步拼接（text_type 路由含 caption / doc_type Style Hints / LCC 注入讀 ctx.domain_name 零 DB / Glossary 強約束含大小寫不敏感 / constraints）+ 用戶提示詞；新建 `prompt/translate/caption_translate_prompt.txt`（保留 Figure/Table 編號） | `27db830` |
| C3 | `settings.LLM_THINKING_BUDGET`（預設 0）+ `TRANSLATE_MODEL` 預設改 `gemini-3.5-flash`；`llm/client.py::chat()` 受控擴充 `thinking_config` 注入（**§4 唯一例外**、前向相容 gating 涵蓋 2.5/3.5/4.0 + try/except 降級、budget=0 byte 等價）；`Translator.translate()` NORMAL/DEEP_THINK 雙模式路由 | `11ea52a` |
| C4 | `Translator.translate()` 末加 U4 多行 `re.sub` 分行容錯；新建 `tests/test_translator.py` 8 pytest（雙模式/style/路由/LCC/glossary/兜底/用戶提示詞）；全套件 465 passed | `2ebda03` |
| C5 | Conformance 三維度驗收（U1-U4 / 測試 §6.1-§6.4 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v10/tasks_v1/C1-C5 報告）+ 結案 | `b55219b` |

> **修法依據**：`.claude-logs/plans/2026-06-01_TRANSLATOR_雙模式原子翻譯器_plan_v10.md`（八輪嚴格交叉 review 定稿）
> **PIPE 對齊**：消費 DomainNormalizer LCC（`Domains.name` 英文領域名）+ GlossaryManager 凍結 Glossary；`InjectionContext`/`TranslateMode` 落 `processor/translator.py`（非 contracts.py）；`thinking_config` 列 §4 唯一受控例外（依 model_recommendations.md §1.1）；旗標 `LLM_USE_GLOSSARY_ALIGN`=False + `LLM_THINKING_BUDGET`=0 時行為等同舊狀、線上 0 風險。
> **三大共用真理源全數就緒**：DOMAIN-NORM / GLOSSARY-CORE / TRANSLATOR。

### BE-Refactor GLOSSARY-CORE 中央領域術語庫與跨語系一致性（PIPE 大改版三大共用真理源之二）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 新增 `GlobalGlossary` 表（`(source_lang,target_lang,term_key,domain)` 聯合唯一約束 + 級聯查詢輔助索引 + source auto_extract/manual_edit）；`Paper` 等既有表 byte 不動 | `03d85c8` |
| C2 | 新建 `processor/glossary_extractor.py` GlossaryManager：`query_cascade`（專屬 LCC 覆寫 general）+ LLM `extract_terms`（**交易外**）+ `upsert_terms`（on_conflict_do_nothing 冪等）；全程 try/except 降級不阻斷 | `9af971f` |
| C3 | `translate_processor.py:237-239` 旗標閘門注入級聯術語表 + `pipeline_core._stage_translate` 尾端**非阻塞**背景回填 hook；旗標 OFF byte 等價舊行為；書籍 ParallelChapterTranslator 融合延後 | `fd0e84f` |
| C4 | `AI_professor_chat.py:329-335` 旗標閘門按 `_domain` LCC `query_cascade` 注入「不可違背 System constraint」；前台崩潰防護 graceful degradation；只 stage C4 hunks 隔離既存 RAG-14 改動 | `06bf3df` |
| C5 | 新建 `tools/manage_glossary.py` 自癒 CLI（`--init` / `--test-pipeline --pdf` 離線閉環 / `--backfill-existing-papers` 歷史 domain→LCC 批次升級）；setup_logging + 批次極短交易防鎖 | `7da39bd` |
| C6 | 新建 `tests/test_glossary_core.py` 5 pytest（唯一約束 / 級聯專屬覆寫 / 書籍融合優先 / Chat 注入 / CLI 回填）；全套件 457 passed | `ae705d5` |
| C7 | Conformance 三維度驗收（U1-U5 / 測試 §6.1-§6.6 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v2/tasks/C1-C7 報告）+ C5 交付物補正 + 結案 | `d4c34d5` |

> **修法依據**：`.claude-logs/plans/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md`
> **PIPE 對齊**：消費上游 DomainNormalizer `normalize_to_lcc` LCC（DOMAIN-NORM 已收官）；translate/chat 跨文獻術語一致性注入 + 知識飛輪自癒回填；旗標 `LLM_USE_GLOSSARY_ALIGN` 預設 False、線上 0 風險。
> **延後項**：書籍並行 `ParallelChapterTranslator` 雙層融合（plan U3 後半）待 TRANSLATE-BOOK 落地後整合（tasks §9）。
> **流程註**：C4 發現既存未提交 RAG-14 多標籤後端改動 → baron 拍板「只 stage C4 hunks」隔離、RAG-14 獨立 commit `595e3d8`。

### BE-Refactor DOMAIN-NORM 領域標準化對齊器（PIPE 大改版三大共用真理源之一）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 新增 `Domains`（lcc_code PK String(3) + name 動態註冊）+ `DomainMapping`（raw_key PK→lcc 快取 + FK）兩表；`Paper` 等既有表 byte 不動 + create_all 自動建表 | `8d4f75f` |
| C2 | 新建 `processor/domain_normalizer.py` DomainNormalizer：快取查→LLM 內容判定（cheap model Temp=0.0、履歷按技能）→動態註冊 Domains（on_conflict_do_nothing 不塞單字）→寫回；**LLM 呼叫在 session.begin() 交易外** + try/except 降級 general | `125af97` |
| C3 | 暴露模組級單一入口 `normalize_to_lcc(raw_domain, context_text=None)->LCCCode`（逐字對齊 PIPE-SPEC §1.2.1 / master v10 L69）+ `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False 走舊 raw 直注、零風險）；惰性單例 | `7e7f2a1` |
| C4 | 新建 `tests/test_domain_normalizer.py` 4 pytest（內容分類 HF/QA + temp=0.0 / 冷門動態註冊 QE 不塞單字 / 快取命中 0 API / 旗標 off 保舊行為）；全套件 452 passed | `aeb4fc2` |
| C5 | Conformance 三維度驗收（U1-U4 / 測試 §6.1-§6.4 / 不可動清單 git 全量證據）+ baton/ 一次性歸檔（plan_v2/tasks/C1-C5 報告）+ 結案 | `1559b08` |

> **修法依據**：`.claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md`
> **流程校正**：原 18:46 Check 提示詞欲收斂為 4-commit（C4=Check），經 baron 拍板「先補 C4 Unit Tests 再收官」→ 回歸 5-commit（C4=Unit Tests / C5=Check）。
> **PIPE 對齊**：DomainNormalizer 為 GLOSSARY-CORE / Translator 共同上游真理源；簽名凍結對齊 PIPE-SPEC §1.2.1。旗標預設 False、線上 0 風險（接線 translate 屬後續路次 plan）。

### BE-Refactor API-PERF API 技術審計與效能防呆優化（PIPE 大改版基建前置）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `db.py` U6 SQLite 連接池（busy_timeout 5s→30s + QueuePool pool_size=5/max_overflow=10/pool_pre_ping）+ 2 pytest | `5326437` |
| C2 | `web_server.py` U4 1MB 分塊流式上傳（%PDF/415/413/清理 partial）+ U5 login X-Forwarded-For 真實 IP + 3 pytest | `e20054d` |
| C3 | U3 廢 lifespan preload + chat 端點按需 Lazy Load + `ai_core`/`rag_retriever` OrderedDict LRU(上限 5)+gc；`retrieve_*` 演算法 byte 不動 + 2 pytest | `76e47ed` |
| C4 | U1 `PIPELINE_SEMAPHORE`(上限 1) 守 A 軌 run_pipeline + B 軌 run_pipeline_shadow + queued SSE；U2 pdf_processor 子進程 nice 19 soft-fail + 2 pytest | `aad3737` |
| C5 | U7 (phase,stage) 二維鍵 performance_metric 埋點（pipeline_core A 軌映射 + orchestrator P1-P4 附加式）+ pipeline_finished/rag_finished + `scripts/analyze_performance.py` + 2 pytest | `59e1c56` |
| C6 | Conformance 驗收（U1-U7 / 測試 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan_v2/tasks_v3/六報告）+ 結案 | `703cfaa` |

> **修法依據**：`.claude-logs/plans/2026-06-01_API-PERF_API技術審計與效能優化_plan_v2.md`
> **PIPE 對齊**：基建前置——U1 PIPELINE_SEMAPHORE 為 PIPE 廢除 QUEUE-1 Thread-level 避讓並發底座；U7 (phase,stage) 埋點介面前向相容 PIPE Orchestrator P1-P4。C3 另有後續微調 commit `beb8f8a`。

### BE-Refactor PIPE-SCAFFOLD web_server 雙軌派發 scaffolding（PIPE 大改版階段 1·建）

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `settings.SHADOW_LAUNCH_ENABLED`（預設 false）+ `web_server.run_pipeline_shadow` 附加影子單元（`_shadow` 四重隔離 + ` (測試)` 標題 + 委派 Orchestrator）+ upload_paper 派發點一閘門；A 軌 `run_pipeline` 本體 byte-for-byte 不動 | `13c1dcb` |
| OP-2 | confirm_type 派發點二閘門納管 + OP-1/OP-2 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解標記（Flip 下線錨點）+ `tests/test_pipe_scaffold.py`（5 pytest 全綠） | `6807a7f` |
| OP-3 | Conformance 三維度驗收（目標規格 U1-U9 / 測試 5 項 / 不可動清單 A 軌 byte diff）+ baton/ 全量歸檔（plan_v3/tasks_v3/三報告）+ 結案 | `58e1b89` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md`
> **範圍**：僅階段一（建）——影子期雙軌派發 scaffolding 注入（旗標預設 false 惰性插入點、線上 0 風險）；**階段二（移／Flip）屬 PIPE-FLIP plan**（觸發＝五路全通 + Golden Diff 0%）。OP-1 commit `13c1dcb` 同時夾帶 PIPE-CORE Check archival。

### BE-Refactor PIPE-CORE 三層解耦調度骨架（PIPE 大改版階段 1）

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | `pipelines/contracts.py` 四凍結合約（IngestionMetadataSpec extra=forbid 保證 R1.1）+ `pipelines/context.py` PipelineContext/PhaseEnum + `tests/test_pipe_core.py`（8 pytest） | `aa786a1` |
| OP-2 | `pipelines/base_strategy.py`（DocumentStrategy ABC + NullStrategy 哨兵）+ `pipelines/factory.py`（註冊/LiteDoc 降級）+ 測試追加（14 pytest） | `effb155` |
| OP-3 | `pipelines/orchestrator.py` 四 Phase DAG 指揮層（宣告式 _PHASES + 交接點驗證 + P4 容錯 + shadow 貫穿）+ 測試追加（20 pytest）+ grep doc_type== 0 命中 | `84b9b30` |
| OP-4 | Conformance 五維度驗收（目標規格 U1-U7 / 測試 20 項 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan_v2/tasks_v2/四報告）+ 結案 | `13c1dcb` |

> **修法依據**：`.claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md`
> **三層解耦**：合約層（contracts）/ 狀態層（context）/ 策略層（base_strategy+factory）/ 指揮層（orchestrator）；與舊 `pipeline_core.py` 物理共存、零業務代碼改動；五路具體策略屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK；P4 BackgroundTasks 屬 RAG-ASYNC（已留 injectable dispatch_p4）

### GOLDEN-BASELINE 黃金基準存盤與退化比對

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | 新建旁路 CLI `tools/golden_baseline.py` capture 子命令 + `tests/golden_baseline/queries.json` 固定 query set + 五路代表性 fixtures PDF；baron 端 MinerU 實跑 `capture --all` 物理存盤五路三維度黃金快照（D1 雙語 md / D2 rag_tree.json / D3 召回 + SHA-256 manifest） | `3be0b0d` |
| OP-2 | `tools/golden_baseline.py` 新增 `diff` 三維度比對引擎（D1 結構樹 / D2 譯文相似度 0.95 / D3 RAG Jaccard 0.90）+ checksum 防竄改 + 影子雜訊正規化 + 紅綠燈裁決 + 雙格式報告 + `tests/test_golden_baseline.py`（18 pytest 全綠）+ 五路自比對歸零 PASS + 負向竄改 FAIL | `74d34e8` |
| Check | Conformance 三維度驗收（目標規格 U1-U7 / 測試計畫 / 不可動清單 git 驗證）+ baton/ 全量歸檔（plan/tasks/OP-1/OP-2/OP-3 報告）+ 結案 | `c0c64e9` |

> **修法依據**：`.claude-logs/plans/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
> **時序修正**：tasks v1 Checkout 誤置 OP-1 → v2 更正為 OP-1 存盤 / OP-2 Diff 腳本 / OP-3 Checkout 收官（WORKFLOW_SOP §3 baton 暫存鐵律）

### RAG-14-HOTFIX-1 — 緊急熱修復：對話置頂氣泡頂部穿透漏出修復

| Commit | 內容 | Hash |
|---|---|---|
| Hotfix | `static/index.html` 移除 `#chat-messages` padding-top，新增 `.qa-group:first-child` margin-top 完美防置頂穿透 | `a5b193f` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-30_RAG-14_hotfix.md`

### RAG-14 多標籤寬鬆格式跨文章 RAG 檢索與對話體驗升級

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `static/index.html` CSS 4 項（gap / msg-user 滿寬 sticky / msg-ai 滿寬 / qa-group）+ sendMessage × 過濾 + `tests/test_rag14_c1_css_and_filter.py` 新增（4 pytest）| `6593962` |
| C2 | `static/index.html` loadChatHistory forEach qa-group 包裝 + in_progress currentGroup + sendMessage qaGroup 包裝 + `tests/test_rag14_c2_dom_structure.py` 新增（3 pytest）| `b8e8770` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `ebf1b9c` |
| Fix (補) | 補交遺漏的 `AI_professor_chat.py` 後端多標籤分流路由與解析邏輯 | `595e3d8` |

> **修法依據**：`.claude-logs/plans/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_plan_v3.md`

### FE-AESTHETICS HOTFIX-1 — 前端學術扉頁自癒與排版靠左優化

| Commit | 內容 | Hash |
|---|---|---|
| C2-hotfix | Frontend Academic Header Self-Healing（CSS 靠左 + normalizeAcademicHeader JS + test_bug_f1 自癒 + 新建 test_fe_aesthetics_c2_hotfix.py）| `bf3c14b` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `452c652` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-29_FE-AESTHETICS-HOTFIX-1_學術扉頁自癒與靠左排版_hotfix_v1.2.md`

### RAG-13-HOTFIX-1 — 緊急熱修復：自訂主題下拉選單捲軸無作用修復

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `static/index.html` scroll handler ctx-popup 過濾 + `tests/test_rag13_hotfix1_scroll_intercept.py` 新增 | `6598d2d` |
| Check | Conformance 驗收與 baton/ 全量歸檔 | `75ab18a` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_hotfix_v1.0.md`

### RAG-13 自訂主題動態清單與選單優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `web_server.py` 新增 `GET /api/themes` + `tests/test_themes_upload.py` fixture GET 掛載 + `test_list_themes_endpoint` | `9e041ed` |
| C2 | `static/index.html` 四項前端變更（setThemes / 分隔線 / loadThemesFromServer / upload handler await）+ `tests/test_bug_f2_theme_dropdown_esc.py` test 更新 | `d842008` |
| Check | Conformance 驗收與 baton/ 全量歸檔收官 | `690b04a` |

> **修法依據**：`.claude-logs/plans/2026-05-29_RAG-13_自訂主題動態清單與選單優化_plan_v3.md`

### FE-AESTHETICS 摘要工具列重構與正文扉頁美化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 後端 `_render_header_en/zh` academic path：dash-list → 階梯式 HTML div 置中對稱排版 + 測試 assertions 更新（59 pytest 全綠） | `3cf8acf` |
| C2 | 前端全棧重構：`#abstract-toolbar` 滿寬摘要容器 + `.paper-header-meta { display:flex }` 螢幕扉頁解鎖 + `renderTitleHeader` JS 重寫 + CSS word-wrap 防禦 + 測試更新（67 pytest 全綠） | `b735a94` |
| Check | Conformance 驗收 + baton/ tasks/C1/C2 全量歸檔 + TODO.md 結案 | `6947098` |

> **修法依據**：`.claude-logs/plans/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md`（v1.3）

### INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pdf_processor.py` backend=pipeline comment lock + `test_backend_parameter_is_pipeline` Case D + `.env.example` VRAM 禁用警告 | `264dadc` |
| C2 | `sop/2026-05-27_mineru_SOP_手冊.md` §1 VRAM 禁用列 + §2.3 CPU 後端紅線規格 + §6.2 VRAM OOM 自愈步驟 + §99.2 v2 Revision | `9e05466` |
| Check | Conformance 驗收 + baton/ 4 份全量 mv 歸檔 + TODO.md 結案 | `878c7a2` |

> **修法依據**：`.claude-logs/plans/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md`

### MODEL-10 MinerU 連線優化與運作維護 SOP

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `pdf_processor.py` MINERU_TIMEOUT 防禦性載入 + L76 timeout 動態化 + Priority 2 廢棄 warning + `.env.example` + 3 pytest | `19ddac8` |
| C2 | 新建 `sop/2026-05-27_mineru_SOP_手冊.md`（193 行，§0/§99 治理結構，6 大運維主軸：env 配置 / 超時對策 / SSH Keep-Alive / Priority 2 SCP 備援規格 / cron 清檔 / 容器重啟） | `991258d` |
| Check | Conformance 驗收 + baton/ 六份全量 mv 歸檔（含 SOP → sop/）+ TODO.md 結案 | `17d187b` |

> **修法依據**：`.claude-logs/plans/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md`

### OPTIMIZE-1 PDF上傳自動無損優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `utils/pdf_optimizer.py`（Atomic Overwrite + Logging SOP）+ `tests/test_pdf_optimize.py`（2 tests） | `b8892be` |
| C2 | 後端 is_slides_pdf 刪除 + optimize_pdf_lossless 整合 + doc_type Form 直通 + 前端 Phase-Shift 翻轉 + 3 tests | `28f098e` |
| C3 | Final Archiving and TODO Sync（baton/ 全量 mv 歸檔 + TODO.md 結案） | `93ab716` |

> **修法依據**：`.claude-logs/plans/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md`（v2）

### WORKFLOW-2 流程模板重構與提示詞自動歸檔

| Commit | 內容 | Hash |
|---|---|---|
| WORKFLOW-2-Tasks | Tasks 拆分（baton 暫存，C5 歸檔） | `7a3332f` |
| C1 | R1 五大提示詞模板自愈歸檔防線 | `b3e22c7` |
| C2 | R2 Check Conformance 維度四+五 | `5d7bdda` |
| C3 | R3+R4 SOP 備份暫存鐵律 + §8 重構 | `5a55939` |
| C4 | R5a 歷史 9 份提示詞物理補建 | `10f9561` |
| C5 | R5b INDEX 幽靈自癒 + 全案收官歸檔 | `7a3332f` |

> **修法依據**：`.claude-logs/plans/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`

### TODO-HOTFIX-1 TODO.md 緊急狀態與殘留修復

| Commit | 內容 | Hash |
|---|---|---|
| TODO-HOTFIX-1 | RAG 狀態整理與 RAG-11/12 抽離（RAG 狀態修復） | `a0d1951` |
| TODO-HOTFIX-1b | MODEL-8 進行中殘留清理（MODEL-8 狀態清理） | `2c78f9e` |
| TODO-HOTFIX-1 Check | Conformance 驗收與歸檔收官（第三階段驗收） | `5f3ef01` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md`

### WORKFLOW-1 流程簡化與文件治理

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Bootstrap Core（自動載入核心文件治理基礎） | `1a0394c` |
| C1.5 | Core Spec Align & TODO Bootstrap（核心規格與 TODO 自舉） | `e0c7a17` |
| C2 & C3 | Templates & Overview + Prompt Templates（模板與引導 / 提示詞模板） | `365aa5d` |
| C4 | SOP & Diagnostics（領域 SOP 與診斷目錄） | `ad0be4e` |
| C5 | 收官 (Closure) | `8965725` |

> **修法依據**：`.claude-logs/plans/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`（v11）

### Phase 4.7d Chat 改造（17 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 17-1 | 後端寫 DB + 廢前端 saveChatHistory POST | `8a1a0ec` |
| 17-1b | 切 paper 立即清 chat + SSE 改 asyncio.to_thread | `7452067` |
| 17-2 | stream broker + /chat/attach + /chat/history 加 in_progress | `5394365` |
| 17-3 | 前端 loadChatHistory + EventSource attach | `aed989c` |
| 17-4 | 移除 POST /chat/history endpoint | `a1adfbc` |

### Phase 4.7d RAG 改造（15 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 15-1 | chunk 優化（空 chunk / Context 前綴 / 短文合併） | `d6cb3df` |
| 15-2 | retriever 加 paper_title 引用 + score logging | `b6622a1` |

### Phase 4.7d RAG-7 doc_analyzer / md_cleaner 切 section 修正（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-7a | md_cleaner 偵測 + 移除重複 heading 行（浮水印自動偵測） | `e2ed0e4` |
| RAG-7b | heading_fix_resume.txt prompt + HEADING_FIX_PROMPTS['resume'] 改指 | `5c182cf` |

### Phase 4.7? MODEL-9 連線彈性防禦（1 commit）

| Commit | 內容 | Hash |
|---|---|---|
| MODEL-9 | 新增 `llm/_http_client.py` 共享 httpx.Client 工廠（timeout 5/60/30/60 + Keep-Alive pool）+ LLMClient / EmbeddingModel 注入 + `llm/retry.py` 升級為 Full Jitter (`random(0, min(MAX, base*2^attempt))`) + 7 個 factory pytest + 2 個 retry pytest；R1 graceful shutdown + R2 環境變數 override（`GEMINI_*_TIMEOUT` / `LLM_RETRY_MAX_BACKOFF`） | `dd18922` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-9_連線彈性防禦_plan.md` §4 + baron R1/R2 補充
> **環境變數**：`GEMINI_CONNECT_TIMEOUT=5` / `GEMINI_READ_TIMEOUT=60` / `GEMINI_WRITE_TIMEOUT=30` / `GEMINI_POOL_TIMEOUT=60` / `GEMINI_MAX_KEEPALIVE=20` / `GEMINI_MAX_CONNECTIONS=100` / `GEMINI_KEEPALIVE_EXPIRY=30` / `LLM_RETRY_MAX_BACKOFF=60`

### Phase 4.7? MODEL-3 tiling 三合一優化（3 commits、B1 + B2 + B3）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | 短文 Fast-path Bypass + `_join_content` helper（修正 1 防排版災難）+ `_bypass_content` 保留 index（修正 2 防 md_restore 對齊破裂）+ `TILING_MAX_LENGTH` env（修正 5）+ pipeline_core 傳 doc_type；新增 10 個 pytest | e97ddd2 |
| B2 | `_merge_small_text_blocks` 改寫：`SOFT_TYPES`/`HARD_BOUNDARY` 常數 + 公式穿透合併 + formula 永不 flush（修正 3）；新增 6 個 pytest | abed78d |
| B3 | `_process_content` long_doc_mode + `_PARAGRAPH_SPLIT_RE` regex（修正 4 容錯 `\r\n` / 多餘空白）+ `TILING_PARAGRAPH_THRESHOLD` env + `tiling_method` 標籤完整化（bypass / paragraph / delimiter / sentence / passthrough）；新增 7 個 pytest | 9177930 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-3_短文Bypass_公式穿透_段落滑動_plan.md`（§4.0 + §4.1 + §4.2 + §4.3 + §4.6 + §3.5/3.6/3.7/3.8/3.9 修正 1-5）
> **環境變數**：`TILING_BYPASS_CHAR_LIMIT=5000` / `TILING_MAX_LENGTH=2500` / `TILING_PARAGRAPH_THRESHOLD=30000`（皆預設）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/{vector_store,*_tiled.json}` → 重啟）執行；觀察 `[tiling bypass]` + `tiling_method` 標籤為書籍場景 / RAG-3 校準鋪路。

### Phase 4.7? MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI（3 commits、C1 + C2 + C3）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 加 `PaperChunk` ORM + `Paper.chunks` relationship + `paper_manager.py` 加 3 個 DAL helper（不重做 `get_paper_db_id`、修正 5）+ `processor/rag_processor.py` 加 `CHUNK_FILTER_VERSION` 常數 + `settings.py` 加 `OUTPUT_DIR` env（修正 7、依 db_analysis §5.2）+ `web_server.py:77-78` 改 `from settings import OUTPUT_DIR`（2 行、其他 20+ 處引用不動）；新增 7 個 pytest | aeb42cb |
| C2 | `processor/rag_processor.py` 加 module-level `write_index_meta_json`（修正 4、CLI 共用）+ `RagProcessor._write_paper_chunks_to_db` method + `process` / `_create_vector_store` 加 `paper_db_id` 參數 + `pipeline_core.py::_stage_rag` 加 2-3 行 `paper_db_id` 注入（修正 2、不動 web_server）；新增 5 個 pytest | ab40fdc |
| C3 | `tools/regen_rag.py` 新檔（6 子命令：`--check / --paper / --all / --force / --dry-run / --init`、含 cmd_init 修正 6 完整 pseudo-code 反向導入既有 paper）；新增 7 個 pytest | 16f62d4 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md` v3（§3.1 + §3.2 + §3.3 + §3.3.1 + §3.4 + §3.6 + §5.1 + §6 + §7 + Q1-Q18 + 附錄 A/B）+ `.claude-logs/ref/db_analysis_and_future_extension.md`（§1 + §3.1 + §4 + §5.2 + §5.3）
> **8 個修正**：路徑統一 `vectors/` / paper_db_id 內部注入 / 移除 tiling_method / write_index_meta_json 抽 module-level / 不重做 get_paper_db_id / cmd_init pseudo-code 完整 / OUTPUT_DIR env 化 / Pg-Ready 安撫
> **環境變數**：`OUTPUT_DIR=/app/storage/output`（預設 `_BASE_DIR / "output"`、Docker / K8s 部署用）
> **Backfill 一次性 SOP**：baron OrcStack 端 `git pull && venv/bin/python tools/regen_rag.py --init` 從 `vectors/` FAISS docstore 反向導入既有 paper、未來升 embedding 直接 `--all`、< 5 分/書籍。

### Phase 4.X? RAG-1 Phase 2 Hashtag RAG 路由 + 雙語摘要 + Chat Token UI（3 commits、P2-1 + P2-2 + P2-3）

| Commit | 內容 | Hash |
|---|---|---|
| P2-1 | 雙語摘要管道：`processor/metadata_extractor._ALL_FIELDS` 加 `translated_abstract` + `pipeline_core._stage_translate` 完成後同步寫入 `self._metadata["translated_abstract"]`（source=translate_pipeline / confidence=high、try/except 防禦 / 空值不覆寫）；3 個 pytest | 26a4439 |
| P2-2 | 後端 hashtag RAG 路由：`settings.RAG_MULTI_TOP_K=7` env + `paper_manager.list_paper_uuids_by_tag`（owner-scoped、共用 R2 `_normalize_tag`）+ `paper_manager.parse_query_hashtag`（長標籤優先排序防 `#complex` 攔 `#complex_system`）+ `rag_retriever.retrieve_multi_with_context`（跨 paper 全域 Merge-Sort top-k、L2 normalize 後 cosine 可比）+ `AI_professor_chat.process_query_stream` 入口分流（0/1/多/無 4 路徑、繞 router、單篇路徑 100% 不動）；14 個 pytest | 9ee44f3 |
| P2-3 | 前端 chat hashtag token UI：`static/index.html` chat-input `<textarea>` → `<div contenteditable>` + placeholder hint（Q11 完整版）+ `:empty::before` data-placeholder CSS（§3.3.5-#1）+ `contenteditable="false"` 禁用契約（§3.3.5-#2）+ 全域 grep 替換 `.value` / `.disabled` / textarea autosize（§3.3.5-#3）+ autocomplete dropdown 綁 `#chat-input-area` 容器（§3.3.5-#4）+ Claude `/skill` 風格 hashtag-token + 6 個 JS handler（input / keydown / compositionstart-end / blur / mousedown / × remove）+ design/docs/components.md §11.2 Hashtag Token + dom-reference.md / interaction.md 同步註記；9 個 pytest（含 §3.3.5-#1 / #3 兩個 v2 grep test） | f85b830 |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_Phase2_執行計劃.md` v2（8 章節 + §3.3.5 四點防護補強 + 15 Open Questions Q1-Q15）+ `.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md`（後端全部 Proposed Changes）+ baron 新需求（chat hint + Claude `/skill` 風格 token UI）+ `design/docs/components.md §11.2`（新增）
> **計畫累積**：plan v1 → v2（補 §3.3.5 4 點防護：CSS placeholder / disabled 樣式 / 全域 grep / dropdown 錨點）→ 落地 P2-1/P2-2/P2-3、共 **26 個 pytest**（3 P2-1 + 14 P2-2 + 9 P2-3、含 §3.3.5-#1 / #3 兩個 v2 grep test）
> **核心設計亮點**：
> - **零 schema 變動**：讀 Phase 1 `metadata_json.user_tags` 陣列、共用 `_normalize_tag` 真理源
> - **單篇 / 多篇 分流**：多篇 hashtag 走新 `retrieve_multi_with_context` + 繞 router；單篇 / 無 hashtag 走既有 `_get_rag_context` 路徑、零變動
> - **全域 Merge-Sort**：L2 normalize 後 cosine score 跨 paper 可比、防 prompt 爆炸（top_k=7 env override）
> - **長標籤優先排序**：`sorted(tags, key=len, reverse=True)` 防 `#complex` 攔 `#complex_system`
> - **contenteditable 四點防護**（§3.3.5）：CSS `:empty::before` placeholder / `contenteditable="false"` 禁用契約 / 全域 grep 替換 `.value` / dropdown 容器錨點
> - **中文 IME 防護**（Q12）：`compositionstart/end` + `e.isComposing` 雙重防護、組字中不觸發 autocomplete
> - **跟 Phase 1 解耦**：Phase 1 寫入路徑 100% 不動、Phase 2 純讀 user_tags 陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. **P2-1**：上傳英文 paper → 跑完 pipeline → 切中文、toolbar abstract 顯示中文（不再 fallback 英文）
> 2. **P2-2**：建 3 篇 HR 履歷加 `#hr` tag → 輸入 `#hr 比較這幾篇` → AI 回答含 3 個 paper title 引用、後端 log「matched_papers=3」
> 3. **P2-3**：chat-input 顯示「輸入 # 可加入 hashtag 跨文獻搜尋」placeholder → 輸入 `#` autocomplete dropdown 跳出 → `↓` `Enter` 確認、`#hr` 變藍色 token → `×` / `Backspace` 一次刪掉
> 4. **跨文件問答收官**（baron 需求 3）：`#hr 我的學歷區應該怎麼寫？` → AI 跨 3 份履歷比較 + 統一建議
> **影響範圍**：純 user-facing 功能擴充、無 schema 變動、無 backfill 需求；舊 paper 缺 `translated_abstract` 走前端 R1 子項 F fallback

### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）

| Commit | 內容 | Hash |
|---|---|---|
| BUG-F1 | 前端 micro fix 包 — tag fallback / placeholder 斷行 / export-btn / --content-max-w（Bug 1/3/4/5、5 pytest） | `9877e54` |
| BUG-F2 | theme dropdown + ESC + P2-3 latent fix — dropdownAPI IIFE + TDZ-aware 3 段拆分（Bug 2 + Bug 11、6 pytest） | `ae20559` |
| BUG-F3 | .modal-input CSS — ui-fixes-batch B5 廣義 selector + color-mix 跨主題 focus ring（Bug 7、2 pytest） | `57c71c8` |
| BUG-F4 | P1 critical 4 項 — A1 trackProgress / A2 empty-state / A3 customPrompt / A4 closeBizPopups（9 pytest） | `646afe4` |
| BUG-F5 | P2 inconsistencies — B1 廢 token 替換主 scale + B3 demo-bar dead code + B4 no-op（8 pytest） | `e799687` |
| BUG-F6 | P3 polish — C4 ~43 ticket 註解清理 / C5 marked 改寫 / C7 ⋯→SVG；C3+C6 no-op（7 pytest） | `12428aa` |
| BUG-B1 | 後端 abstract fallback — A 側路 translate_text + B regex 擴中日文「摘要/概要/內容提要/要旨」（Bug 8、28 pytest） | `a35a720` |
| BUG-B2 | 後端 blockquote→list + 前端 paper-header-meta CSS — `>` → `-` list + `<div>` wrap + @media screen（Bug 10、7 pytest、全鏈路收官） | `94ed27d` |

> **修法依據**：`.claude-logs/2026-05-24_RAG-1_前端_Bug_Fix_可行性評估.md` v2/v3 + `.claude-logs/2026-05-24_RAG-1_Bug_Fix_可行性評估.md` v4  
> **收官摘要**：6 前端 + 2 後端 = 8 commits、修 9 / 11 bugs、共 72 pytest 全綠、零迴歸；Bug 6 / Bug 9 延後為 RAG-11 / RAG-12

### Phase 4.X? RAG-1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫（3 commits、R1 + R2 + R3）

| Commit | 內容 | Hash |
|---|---|---|
| R1 | UI Fixes 子項 A/C/F/G 部分：`paper_manager.set_paper_tags` 新增 + `web_server.PaperUpdate.tags` Pydantic 擴充 + PATCH `/api/papers/{paper_uuid}` 整合 tags 處理 + `static/index.html` Modal CSS 補 `--radius-md` / `--font-display`（子項 C）+ `renderTitleHeader` 雙語 abstract fallback（子項 F）+ `#lang-toggle` 切語言後重繪 toolbar（子項 F）+ `#current-title padding-right` + `details.title-abstract max-height: 12rem` 防遮擋 / 防破版（子項 G 部分）；3 個 pytest | 9977428 |
| R2 | UI Fixes 子項 B/D/E/G 剩餘/H + v3 強化全域 lowercase：`paper_manager._normalize_tag()` module-level helper（單一真理源、lowercase + strip）+ `set_paper_tags` 整合 `_normalize_tag` + dedup + `web_server.upload_theme` endpoint（5 道安全過濾）+ `static/index.html` 加 `#` 標籤按鈕 + tag-modal + theme upload UI + tag-pill 半透明磨砂玻璃 + 風格選項英文化（Kahn · Kimbell Art Museum / Yoshitomo Nara）+ 移除「⚠ 後端未實作」警語 + `design/docs/theme-guide.md §7` 寫入 + `design/docs/components.md §11 Tag Pill` 新增 + `api_audit #23` 補完；13 個 pytest | f44a7e6 |
| R3 | 資料夾路徑自動標籤：`paper_manager._folder_ancestor_path_names`（遞迴向 root 取 folder name path、防環 + max_depth=32）+ `_apply_folder_path_tags`（共用 R2 ship 的 `_normalize_tag`、append + de-dup 策略、Q6/Q7 不清舊 tag）+ `set_paper_folder` commit 後 hook（try/except 包覆、不阻塞 core move）；7 個 pytest（HR/CV 基本 / 4 層巢狀 / lowercase / dedup / 未分類保留 / corrupt metadata / 中文 folder） | 49fe66a |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md`（§4.1 + §4.2 + §4.3 + §5 + §6 + §7 + §8 Q1-Q18 + §10）+ `.claude-logs/ref/2026-05-23_RAG-1_UI_Fixes_Implementation_Plan.md` v3（8 大子項 A-H + v3 強化段 + 附錄 C 4 點深度評估認證）+ `.claude-logs/ref/api_audit_and_performance_report.md` #22 + #23 + `design/docs/components.md §2 §6 §11` + `design/docs/theme-guide.md §7`
> **4 輪 review 累積**：v0 原始 UI Plan → v2 整合資料夾自動標籤 + Q1-Q10 決策 → v3 全域 lowercase 強化 + 4 點深度評估認證 → 落地 R1/R2/R3 3 個 commit、共 **23 個 pytest**（3 R1 + 13 R2 + 7 R3）
> **核心設計亮點**：
> - **零 schema 變動**：所有 tag 寫進既有 `metadata_json.user_tags` 陣列
> - **後端 Hook 注入**：所有 client（前端拖拽 / 對話框 / 首次上傳 / CLI）統一觸發、前端零負擔
> - **單一真理源**：`_normalize_tag()` 為所有 tag 寫入路徑唯一 normalize 入口
> - **中文友善**：`.lower()` 對中文無效、`#人資` `#工程` 保留原樣
> - **防禦性容錯**：`_apply_folder_path_tags` `try/except` 包覆、不阻塞 core `set_paper_folder` 移動
> - **Backward compat**：既有大寫 tag 不 retroactively 改寫；既有 R1 `set_paper_tags` 3 個 pytest 重構後仍 passed
> - **跟 Phase 2 解耦**：本 RAG-1 ship `metadata_json.user_tags` 寫入路徑、`.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md` Phase 2（hashtag RAG 路由 + parse_query_hashtag + retrieve_multi_with_context）讀此陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. 移動 paper 到資料夾 HR/CV → 重整、tag-pill 顯示 `#hr #cv`
> 2. 在 `#` Modal 輸入 `#HR #plant 工程` → 儲存後顯示 `#hr #plant #工程`（v3 lowercase + 中文保留 + dedup）
> 3. 從 HR/CV 移回未分類 → 自動 tag `#hr #cv` 保留（Q6/Q7）
> 4. 上傳 .css 主題 → 立即套用 + 重整不失效
> **影響範圍**：純 user-facing UI + 後端 helper、無 schema 變動、無 backfill 需求

### Phase 4.X? LOGGING refactor 統一日誌基建（3 commits、LOGGING-1 + 2 + 3）

| Commit | 內容 | Hash |
|---|---|---|
| LOGGING-1 | `utils/logging_config.py` 新檔（`JSONFormatter` + `ConsoleFormatter` + `setup_logging` + `reset_logging`）+ 補強 1 冪等性 + 補強 2 第三方劫持（`uvicorn` / `uvicorn.access` / `uvicorn.error` / `sqlalchemy.engine`）+ 補強 4 + v3 建議 1 exception 結構化 + v4 建議 1 噪聲分流（SQLAlchemy DEBUG-only / Uvicorn 動態）+ v4 建議 2 ContextVar `default=None` 雙保險 + v4 建議 3 `json.dumps default=str` 降級 + 🔴 v3 陷阱 1 `ConsoleFormatter.asctime` 顯式綁定 + 🔴 v3 陷阱 2 `uvicorn.run(log_config=None)`；`settings.py` 加 5 env（`LOG_LEVEL` / `LOG_DIR` / `LOG_FORMAT` / `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT`）；`web_server.py` 替換 `_setup_logging`；16 個 pytest | 011cc8c |
| LOGGING-2 | `web_server.py` 加 `@app.middleware("http") trace_id_middleware`（在 `auth_guard` decorator 與 `SessionMiddleware add_middleware` 之間、確保 `request.session` 可讀 owner）+ `X-Trace-ID` request/response header + `ContextVar set/reset` 跨 request 隔離（try/finally）+ SSE chat 路徑（`web_server.py:151 asyncio.to_thread`）自動繼承 ContextVar（Python 3.12.3、補強 3 / §4.11）；9 個 pytest | 3e406a1 |
| LOGGING-3 | `tools/regen_rag.py::main` 改用 `from utils.logging_config import setup_logging` 取代 `logging.basicConfig`；CLI 場景對齊 web_server 共用 settings env + Formatter + 噪聲分流 + ContextVar 雙保險；補 1 個 pytest | 6e764ea |

> **修法依據**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md` v4（§4.3 + §4.4 + §4.8-4.19 + §6 + Q1-Q22 + 附錄 v2/v3/v4 對照表）+ `.claude-logs/ref/logging_refactor_proposal.md`
> **4 輪 review 累積**：v0 原始 → v2 補強 4 點 → v3 致命陷阱 2 + 架構優化 2 → v4 生產健壯性 3 點、確保「不缺漏任何已知陷阱」
> **環境變數**：`LOG_LEVEL`（預設 INFO）/ `LOG_DIR`（預設 `_BASE_DIR/logs`）/ `LOG_FORMAT`（預設 `auto`、auto/json/console）/ `LOG_MAX_BYTES`（預設 10MB）/ `LOG_BACKUP_COUNT`（預設 5）/ `ENVIRONMENT`（development / production、控制 auto 切換）
> **Docker 部署**：`docker run -e ENVIRONMENT=production -e LOG_FORMAT=json -e LOG_LEVEL=INFO ...`、web_server + CLI 都自動 JSON output、Loki/ELK 可解析
> **不採納**：第三方 lib `structlog` / `loguru`（Q2）/ background pipeline ContextVar 跨 thread 注入（Q8、用既有 `[MODEL-8] owner=X paper=Y` 串連 90% 場景）

### Phase 4.7? MODEL-1+2 Embedding 升級（2 commits、B1 + B2）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | EmbeddingModel 升級 `gemini-embedding-2` + MRL 768 維 + `_l2_normalize` helper（防禦升級：空值 / 1e-6 / 零向量 → `[0.0]*len`）+ 4 處 embed call 套用 + `EMBEDDING_OUTPUT_DIMENSIONS` env override；新增 10 個 pytest（`tests/test_embedding_normalize.py`）| `f415218` |
| B2 | `rag_processor._is_chunk_meaningful` helper（修正 2 markdown 噪聲 + 修正 4 履歷防誤殺 `resume/slides ≥ 3` + email/phone/url 保留）+ `rag_retriever` raw score logging + `RAG_SCORE_THRESHOLD` env 化（修正 1、預設 0.22）；新增 11 個 pytest（`tests/test_rag_chunk_filter.py`）| `de649cc` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-1+2_Embedding升級_plan.md`（§4.1 + §4.2 + §4.3 + §4.6 + §3.6 修正 1/2/3/4）
> **環境變數**：`EMBEDDING_MODEL_NAME=gemini-embedding-2` / `EMBEDDING_OUTPUT_DIMENSIONS=768` / `RAG_SCORE_THRESHOLD=0.22`（預設）/ `RAG_*_TIMEOUT`（MODEL-9）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/vector_store/` → 重啟）執行；觀察 `[chunk filter]` + `[retrieve raw]` log 為 RAG-3 score 校準鋪路。

### Phase 4.7? RAG-8/9 翻譯保留排版下游 bug（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-9 | `static/index.html` marked.js GFM strikethrough 關閉、避免單 `~` 配對成 `<del>`（履歷 `100~500 人` / `2003/8~ 仍在職` 等 tilde 範圍語法） | `3a0c523` |
| RAG-8 | `processor/md_restore_processor.py` 加 `_preserve_pipe_table()` helper、L683-684 改用 helper 保留 pipe table 結構；+ 6 個 pytest（`tests/test_md_restore_table_preservation.py`） | `230ca13` |

> **修法依據**：`.claude-logs/2026-05-22_RAG-8_RAG-9_合併診斷_plan.md`（§4.1 + §4.2 修法 1）
> **Backfill**：baron OrcStack 端對 < 10 份既有 paper 重跑 md_restore stage、user-facing 驗證可接受（江元杰 `~` 不再撞線 ✅、DeHunt 學歷 table 自然文字流呈現 ✅、HVDC slides table 欄位對齊正確 ✅）。

### Phase 4.7e Resume 獨立 Pipeline（含 1 次 revert+v2 重做）

| Commit | 內容 | Hash |
|---|---|---|
| 7e-1（舊、已 revert） | ResumeProcessor + Vision prompt + chat_with_images（方向走偏：重組摘要） | `ffb3000` |
| 7e-2（舊、已 revert） | resume 走獨立 ResumeProcessor + doc_analyzer 短路 | `fdc2838` |
| Revert 7e-2 | revert 上述 7e-2 | `32563b5` |
| Revert 7e-1 | revert 上述 7e-1 | `ce91665` |
| 7e-1 v2 | ResumeProcessor 重寫、忠實轉錄 + 主標題黑名單對齊手冊 v2 | `1fb2d7b` |
| 7e-1 v2 hotfix | prompt 加投遞元資訊排除 + 主標題抽取優先順序（解黃忠偉 case） | `eb2164c` |
| 7e-2 v2 | pipeline_core 整合 ResumeProcessor + md_cleaner 跳過（保留 doc_analyzer 雙保險 = baron Q6） | `70889aa` |

> **7e-3 v2** 為 baron OrcStack 端到端 backfill 驗證（重新上傳 DeHunt / 黃忠偉 / 江元杰）、無 commit、純驗證活動；驗證滿意後本系列收尾。

---

## 🟡 進行中 / ⬜ 未開始（依優先序）

### 🔴 高優先

- 🟡 **RESUME-P3 B軌履歷翻譯品質重構**（`.claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_plan_v1.md`）
  - [x] ✅ C1 — P1 履歷 Tiling Opt-out（P1 切塊旁路）（待 baron 回填；1 測試 carryover 待 C5 修）
  - [/] 🟡 WIP: C2 — Translator U4 resume 停用（行結構對齊容錯停用）
  - [ ] ⬜ 未開始: C3 — P3 逐 heading section 翻譯與還原（廢 100% Bypass）
  - [ ] ⬜ 未開始: C4 — heading 退化 Fallback（單一巨 section 降級防護）
  - [ ] ⬜ 未開始: C5 — Unit Tests（逐 heading 契約與退化測試）
  - [ ] ⬜ 未開始: C6 — Checkout（收官與 baton 檔案歸檔）
  - 工時：6 個 commits（C1 P1 opt-out + C2 U4 停用 + C3 P3 核心 + C4 fallback + C5 測試 + C6 Checkout）
  - 依賴：plan v3 OQ 已核准（Q1/Q2/Q3/Q4/Q9/Q10）；改 B軌輸出→須與 TILING/SHADOW 合併重捕 Golden；通用化 chunking 歸 INFRA-3
  - 拆分依據：`.claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_tasks.md`

- 🔵 **QUEUE-1 文件優先權協同避讓調度器**（`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）
  - PipelineCore 實作 class-level 執行緒安全任務註冊表
  - 依 doc_type 與檔案大小自動計算優先權（1/2/3）
  - 階段迭代頂端實作 should_yield 協同避讓與 sleep(2) 迴圈
  - 確保 try...finally 結構保證註冊解除，無死鎖
  - 新增 tests/test_priority_scheduler.py 驗證協同暫停與恢復
  - 工時：1-2 個 commits
  - 依賴：無

- 🔵 **INFRA-2 PipelineCore第一階段切分與定規**（`.claude-logs/baton/2026-05-30_INFRA-2_PipelineCore第一階段切分與定規_plan.md`）
  - [ ] ⬜ 未開始: 文件一 — 現有架構分析報告（`2026-05-30_INFRA-2_PipelineCore現有架構分析_report.md`）
  - [ ] ⬜ 未開始: 文件二 — 新流程規劃設計說明書（`2026-05-30_INFRA-2_PipelineCore新流程規劃_design.md`）
  - [ ] ⬜ 未開始: 文件三 — 數據接口合約 SPEC（`2026-05-30_INFRA-2_PipelineCore接口合約_specification.md`）
  - 工時：1 個 commit（大改版前置定規規格凍結，無程式碼變動）
  - 依賴：無

- ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
  - 問題：切換 paper / 重新整理後，SSE chat history reload 功能缺失（API 合約需調整）
  - 工時：待 plan 評估（預估 1-2 commits）
  - 依賴：無

- ⬜ **RAG-12 LaTeX KaTeX 渲染支援**（Bug 9、需獨立 plan 評估）
  - 問題：論文 / 履歷中的 LaTeX 數學公式無法在前端正確渲染（需引入 KaTeX CDN）
  - 工時：待 plan 評估（預估 1 commit）
  - 依賴：無

### 🟡 中優先

- ⬜ **RAG-4 前端引用顯示**（Commit 15 plan Q3）
  - footnote / 「參考章節」清單 / 連結回原文段落
  - 工時：2-3 個 commits（前端 markdown 渲染 + 點擊跳轉）
  - 依賴：15-2 已提供 section_path

- ⬜ **RAG-3 score 閾值 0.22 校準**（Commit 15 plan Q4）
  - 跑 1-2 週實際 query、收 B2 `[retrieve raw]` logging 數據
  - 用 `grep '\[retrieve raw\]' logs/*.log` 抽 raw score 分布
  - 依 p10/p50/p90 調整閾值
  - **L2 normalize 後預期區間**：raw score 會顯著拉寬、相關 chunks 落 0.45-0.75、無關 < 0.25
  - **推測閾值升到 0.35-0.45 區間**（B2 預設保留 0.22、待實測決定）
  - 透過 env override 動態調整：`export RAG_SCORE_THRESHOLD=0.40`（不需 commit）
  - 工時：1 個 commit（純調常數預設 + 加註解、本機 env 已可先調）
  - 依賴：等資料累積（不能立刻做）

- ⬜ **CHAT-3b 前端清理 POST /chat/history 殘留**（Commit 17-4 報告新加）
  - 17-1 已刪 saveChatHistory 函式定義、留 marker 註解（`static/index.html` L2422 + L2487 兩個 Phase 4.7d Commit 17-1 marker）
  - 17-4 已移後端 endpoint
  - 前端可清掉 marker 註解 / dead reference
  - 工時：5-10 分鐘、純清理
  - 依賴：無（與 CHAT-5 可一起做）

### 🟢 低優先

- ⬜ **RAG-5 短文合併上限 cap**（Commit 15-1 已知限制 #3）
  - 實測若 chunk 過大（> 20 text items）需加上限
  - 工時：觀察驅動、實際撞到才做
  - 依賴：實測撞到

- ⬜ **RAG-6 `_SHORT_DOC_TYPES` 寫進 HOW_TO_ADD_DOC_TYPE.md**
  - 補說明短文型決策標準
  - 工時：1 個小 commit、純 docs
  - 依賴：無

- ⬜ **CHAT-4 取消進行中對話功能**（Commit 17 plan Q7）
  - 用戶按 Esc / cancel button 中止 stream
  - broker 支援 cancel：`session.cancelled = True` → `_run_stream_background` 檢查
  - 工時：1-2 個 commits
  - 依賴：留 4.7e 之後

- ⬜ **CHAT-5 `paper_manager.save_chat_history` 移除（dead code）**（Commit 17-4 報告盤點發現）
  - 17-4 後 0 業務 caller、變 dead code candidate
  - 工時：5 分鐘、純清理
  - 依賴：無(與 CHAT-3b 可一起做)

### 🔵 候選（待 baron 評估、依 `.claude-logs/model_optimization_blueprint.md`）

- 🔵 **RAG-10 中文 Header Meta Block 軟換行渲染 bug**（user-facing 排版、修法 ~5 行、低風險）

  **問題**：論文 Header 區的「作者 / 日期 / 出處 / DOI / 關鍵字」blockquote 在前端渲染時全擠成一行、無斷行。

  **症狀範例**（Jian Xu et al. 2026-01-26 Wuhan University paper）：
  ```
  > 作者：Jian Xu、Xinxiong Jiang... 日期：2026-01-26 出處：Wuhan University 關鍵字：AI data center...
  ```
  預期：每個欄位獨立一行。

  **根因**：CommonMark / GFM 規範下、blockquote 內連續多行**無空行**時、會被解析為**軟換行（soft break）**、在 HTML `<p>` 內被瀏覽器渲染為**單一空格**。`marked.js` 預設行為符合此規範（已 grep `static/` 確認無 `marked.setOptions({ breaks: true })`）。

  **代碼證據**（grep `processor/md_restore_processor.py` 實測）：
  - `_render_header_en`（L435 簽名、meta_bits L460-L470）：
    ```python
    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **Authors**: {', '.join(...)}")  # ← 行尾無斷行標記
    if date:
        meta_bits.append(f"> **Date**: {date}")
    if venue:
        meta_bits.append(f"> **Venue**: {venue}")
    if doi:
        meta_bits.append(f"> **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")
    ```
  - `_render_header_zh`（L484 簽名、meta_bits L511-L519）：相同 pattern、中文欄位。

  **Markdown 標準斷行語法（三選一）**：
  1. 行尾雙空格 `"  "`（推薦、最低侵入）
  2. 行尾反斜線 `\`
  3. 行之間插入僅有 `>` 的空行

  **修法（推薦從後端產生器修正、不改前端）**：

  在 `_render_header_zh` + `_render_header_en` 兩處 `meta_bits.append(...)` 結尾、每行**字串末尾補兩個半形空格**：

  ```python
  # _render_header_en L460-L470
  meta_bits.append(f"> **Authors**: {', '.join(...)}  ")   # ← 末尾補 "  "
  meta_bits.append(f"> **Date**: {date}  ")
  meta_bits.append(f"> **Venue**: {venue}  ")
  meta_bits.append(f"> **DOI**: {doi}  ")
  meta_bits.append(f"> **Keywords**: {', '.join(keywords)}  ")

  # _render_header_zh L511-L519 同樣處理
  ```

  **為何不用前端 `marked.setOptions({ breaks: true })`**：
  - 全域開啟會把所有 paragraph 內的單換行都變 `<br>`、可能破壞原本應該軟換行的 chunk content 排版（如 PDF 內單句跨行的情況）
  - 從後端修正才是定點打擊、零副作用

  **預估工時**：~30 分鐘（含 pytest）

  **拆 commit**：單一 commit（FIX-1）即可、無依賴

  **新增 pytest**（推薦 2-3 個）：
  - `test_render_header_zh_appends_double_space_for_soft_break`
  - `test_render_header_en_appends_double_space_for_soft_break`
  - `test_rendered_meta_block_has_br_in_html`（mock 過一遍 marked.js 風格的解析、驗證 `<br>` 存在）

  **影響範圍**：
  - 僅影響 `_tiled.json` → 最終 markdown 的 Header 區渲染
  - **不需 backfill**（純前端 markdown 字串差異、既有 paper 重開即生效）
  - 既有 paper 重新前端 load 即修正、無需 vector store 重建

  **依據**：
  - CommonMark §6.7 Blockquote + §6.5 Hard line breaks
  - 修正後 HTML 預期含 `<br>` 而非 inline space

- ⬜ **MODEL-5 Structured Outputs router**（依 model_optimization_blueprint.md §3.2）
  - 升級對話路由器、利用 Gemini SDK Structured Outputs (JSON Schema)
  - Pydantic 聲明 `RouterDecision` 模型、消滅 regex + `json.loads`
  - 改 ai_chat / ai_router 相關檔案
  - 工時：1 commit
  - 依賴：無
  - 解 router 對格式變動的脆弱性

- 🔵 **MODEL-7c Metadata 語意前綴增強**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.3、新增）
  - 在生成 Chunk 文本時、最前端注入全域 Metadata 前綴
    - 範例：`"Candidate: John Doe | DocType: Resume | Section: Employment | [內文]"`
  - 將全域背景與局部細節強制綁定、強化語意特徵、embedding 也吃到 doc-level 語意
  - 工時：0.5 commit
  - 依賴：等 RAG-3 score 校準後評估必要性（可能 MODEL-1+2 已夠用、是否真的需要再評估）
  - **優先度低、純候選**

### 🚫 評估後不做（依 `.claude-logs/model_optimization_blueprint.md` / `.claude-logs/pipeline_decoupling_plan.md`）

以下提案經評估為過早優化 / 失控感 / 場景不符、暫不加入 TODO：

- **Parent-Child Indexing**（雙層檢索）
  - 提案：履歷子經歷小區塊向量化、父區塊回 LLM
  - 不做理由：履歷已切到 ### 公司層級、單份 7-8 chunks、痛點不大；實作複雜（chunk 結構 + retriever 邏輯 + schema 改動）、3-4 commits regression 風險高

- **128 Batching 自適應**（Embedding API 並行）
  - 提案：BATCH_SIZE 32 → 128、聲稱「30-50x 提速」
  - 不做理由：測試機 + < 10 份文件、batch size 增益無感（可能省 10-20 秒）；撞 429 風險上升、效益數字行銷話術不可信（實際提速 2-3x）

- **企業 Proxy（HTTP_PROXY/HTTPS_PROXY）**
  - 提案：受限網絡 / GFW 部署支援
  - 不做理由：個人測試機 + 台灣環境、無 firewall / 翻牆需求；未來若要賣企業客戶再做

- **AUTO Grounding（Gemini 自動聯網）**
  - 提案：Gemini 模型自己判斷何時聯網查 Google
  - 不做理由：論文 / 履歷分析場景需明確控制資料來源；AUTO 模式下 user 不知道答案來自文件還是 Google、UX 失控；應 user 明確 opt-in、不該預設啟用
  - **note**：手動 opt-in 聯網已存在於既有 `#web-search-toggle` 前端 toggle（`static/index.html` + `web_server.py:375 use_web_search` + `llm/client.py:118` Gemini Grounding）、整鏈路已通；不需新增 task 重做

- **Pipeline 解耦重構（pipeline_decoupling_plan.md 全套）**
  - 提案：17+ 檔重寫、`BaseStage` / `Context` / `Observer` / `Strategy` 完整體系
  - 不做理由：過早抽象、Mad Professor 是 2 人 / < 10 文件規模；7e-2 v2 `KNOWN_DOC_TYPES` + `check_doc_type_registry.py` 已解 80% 痛點；重構期 regression 風險巨大、機會成本超過所有收益；候選漸進式小手術（dict lookup parser / 並行 helper / module-level constants）可考慮、但全套重構不做

- **MODEL-6 聯網搜尋自動 Fallback 降級路由**（依 `.claude-logs/ref/model_optimization_blueprint.md` §3.2）
  - 提案：RAG max score < 0.35 時、自動切換 Web Search + Google Grounding
  - 不做理由：跟既有「AUTO Grounding 不做」決策**直接衝突**、本質是 trigger condition 不同的 AUTO Grounding；user 不知道答案來自文件還是 Google、UX 失控；mad-professor 定位是「論文/履歷分析助手」、用戶問問題期望基於文件
  - **未來若要做、改為「手動 opt-in 聯網按鈕」**、用戶按下才聯網 + 回答時明確標 [Google Search]

- **MODEL-7b 中英雙語對齊嵌入**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.2）
  - 提案：中英混雜文件、chunking 前拼接「原文 + 譯文」一起 embed、提高跨語召回
  - 不做理由：**gemini-embedding-2 是多語旗艦模型、跨語對齊本身就比舊 model 強得多**（MODEL-1+2 已內建解決 80%）；拼接後每個 chunk 大小翻倍、API tokens / storage 翻倍、是針對舊 model 的 workaround
  - **未來若 B2 backfill 後跑 1-2 週仍有跨語檢索品質問題、再重新評估**

---

## 索引（依類別）

### RAG（11 項 active）
- ✅ ~~RAG-14 多標籤寬鬆格式跨文章RAG檢索與對話體驗升級~~（已落地、C1 `6593962` + C2 `b8e8770` + Check 收官 + 補漏 `595e3d8`）
- ✅ ~~RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI~~（已落地、P2-1 + P2-2 + P2-3 三 commit、見 ✅ 完成區）
- ✅ ~~RAG-1 Phase 1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫~~（已落地、R1 + R2 + R3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
- ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）
- RAG-3 score 校準（中、等數據）
- RAG-4 前端引用顯示（中）
- RAG-5 合併 cap（低）
- RAG-6 docs（低）
- 🔵 RAG-10 中文 Header meta block 軟換行渲染 bug（候選、修法 ~5 行、user-facing 排版）
- ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
- ⬜ RAG-12 LaTeX KaTeX 渲染支援（高、需獨立 plan）
- ⚙️ ~~RAG-2 backfill CLI~~（合併到 MODEL-8、見 MODEL 區）
- ✅ ~~RAG-7 doc_analyzer 切 section~~（已落地、拆 RAG-7a `e2ed0e4` + RAG-7b `5c182cf`）
- ✅ ~~RAG-8 md_restore / translate table 渲染 bug~~ `230ca13`
- ✅ ~~RAG-9 markdown `~` 誤判刪除線~~ `3a0c523`

### Chat（3 項 active）
- CHAT-3b 前端清理（中）
- CHAT-4 取消對話（低、留 4.7e 之後）
- CHAT-5 dead code 清理（低）

### MODEL（0 項中優先 / 2 項候選 / 5 項已落地）
- ✅ ~~MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、合併原 RAG-2）
- ✅ ~~MODEL-1+2 Embedding 2 升級 + L2 正規化 + 短 chunk 過濾~~（已落地、B1 `f415218` + B2 `de649cc`）
- ✅ ~~MODEL-3 短文 Bypass + 公式穿透 + 段落滑動~~（已落地、B1 + B2 + B3 三個 commit、hash 待 push 後回填）
- 🔵 MODEL-5 Structured Outputs router
- 🔵 MODEL-7c Metadata 語意前綴（候選、低優先、等 RAG-3 結果再評估）
- ✅ ~~MODEL-9 連線彈性防禦~~（已落地、`dd18922`）
- ✅ ~~MODEL-9-OPT Embedding連線與限流框架優化~~（已落地、C1 `8feaa12` + C2 `9a44d41` + C3 `e86ced9` + C4 收官；EmbeddingModel Semaphore + retry_call 統一退避 + embed_documents 批次降級；不改向量值/不觸發 Golden 重捕；OQ3 RPM 令牌桶屬上線觀察項）
- ✅ ~~MODEL-10 MinerU 連線優化與運作維護 SOP~~（已落地、C1 `19ddac8` + C2 `991258d` + Check 收官）

### Phase 4.7e Resume Independent Pipeline（全完工）
- ✅ ~~7e-1 v2~~ `1fb2d7b`
- ✅ ~~7e-1 v2 hotfix~~ `eb2164c`
- ✅ ~~7e-2 v2~~ `70889aa`
- 7e-3 v2 端到端驗證（無 commit、純驗證、baron OrcStack 重新上傳 3 份 backfill 後收尾）

### WORKFLOW（✅ 已完成）
- ✅ ~~WORKFLOW-1 流程簡化與文件治理~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-2 流程模板重構與提示詞自動歸檔~~（已落地、C1~C5 六 commits、見 ✅ 完成區）

### FE-AESTHETICS (✅ 已完成 + 🟡 HOTFIX-1 進行中)
- ✅ ~~FE-AESTHETICS 摘要工具列重構與正文扉頁美化~~（已落地、C1 `3cf8acf` + C2 `b735a94` + Check 收官）
- ✅ ~~FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化~~（已落地、C2-hotfix `bf3c14b` + Check 收官）

### RAG-13 (✅ 已完成)
- ✅ ~~RAG-13 自訂主題動態清單與選單優化~~（已落地、C1 `9e041ed` + C2 `d842008` + Check 收官）

### RAG-13-HOTFIX-1 (✅ 已完成)
- ✅ ~~RAG-13-HOTFIX-1 自訂主題下拉選單捲軸無作用修復~~（已落地、C1 `6598d2d` + Check 收官）

### INFRA (1 項 active)
- 🔵 INFRA-2 PipelineCore第一階段切分與定規（高、`.claude-logs/baton/2026-05-30_INFRA-2_PipelineCore第一階段切分與定規_plan.md`）
- ✅ ~~INFRA-1 MinerU Pipeline 推理卡死修復與 SOP 規格更新~~（已落地、C1 `264dadc` + C2 `9e05466` + Check 收官）

### QUEUE (1 項 active)
- 🔵 QUEUE-1 文件優先權協同避讓調度器（高、`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）

### OPTIMIZE (1 項 active)
- ✅ ~~OPTIMIZE-1 PDF 上傳自動無損優化~~（已落地、C1 `b8892be` + C2 `28f098e` + C3 收官）

### GOLDEN-BASELINE (✅ 已完成)
- ✅ ~~GOLDEN-BASELINE 黃金基準存盤與退化比對~~（已落地、OP-1 `3be0b0d` + OP-2 `74d34e8` + Check 收官；PIPE 大改版階段 1 完成）

### PIPE-CORE (✅ 已完成)
- ✅ ~~PIPE-CORE 三層解耦調度骨架~~（已落地、OP-1 `aa786a1` + OP-2 `effb155` + OP-3 `84b9b30` + Check `13c1dcb`；PIPE 大改版階段 1 骨架，`pipelines/` 六模組）

### PIPE-SCAFFOLD (✅ 已完成·階段一建)
- ✅ ~~PIPE-SCAFFOLD web_server 雙軌派發 scaffolding~~（已落地、OP-1 `13c1dcb` + OP-2 `6807a7f` + OP-3 `58e1b89`；旗標惰性插入點 + 影子派發單元 + 兩派發點閘門，A 軌 byte 不動；階段二 Flip 屬 PIPE-FLIP）

### API-PERF (✅ 已完成·PIPE 基建前置)
- ✅ ~~API-PERF API 技術審計與效能防呆優化~~（已落地、C1 `5326437` + C2 `e20054d` + C3 `76e47ed` + C4 `aad3737` + C5 `59e1c56` + C6 收官；U1-U7 並發信號量/nice/LRU/流式上傳/真實 IP/連接池/計時埋點+CLI；PIPE 並發底座就緒）

### DOMAIN-NORM (✅ 已完成·PIPE 共用真理源)
- ✅ ~~DOMAIN-NORM 領域標準化對齊器~~（已落地、C1 `8d4f75f` + C2 `125af97` + C3 `7e7f2a1` + C4 `aeb4fc2` + C5 收官；Domains/DomainMapping 兩表 + DomainNormalizer 內容判定/動態註冊不塞單字/快取防重 + normalize_to_lcc 入口 + LLM_USE_GLOSSARY_ALIGN 旗標預設 False；GLOSSARY-CORE/Translator 共同上游真理源就緒）

### GLOSSARY-CORE (✅ 已完成·PIPE 共用真理源之二)
- ✅ ~~GLOSSARY-CORE 中央領域術語庫與跨語系一致性~~（已落地、C1 `03d85c8` + C2 `9af971f` + C3 `fd0e84f` + C4 `06bf3df` + C5 收官 + C6 `ae705d5` + C7 收官；GlobalGlossary 表聯合唯一約束 + GlossaryManager 級聯查詢/交易外提取/冪等回填 + translate/chat 旗標閘門注入 + manage_glossary CLI；消費 DomainNormalizer LCC；書籍融合待 TRANSLATE-BOOK）

### TRANSLATOR (✅ 已完成·PIPE 共用真理源之三)
- ✅ ~~TRANSLATOR 雙模式原子翻譯器~~（已落地、C1 `1558f79` + C2 `27db830` + C3 `11ea52a` + C4 `2ebda03` + C5 收官；processor/translator.py InjectionContext〔7 欄〕/TranslateMode/Translator〔Prompt Engine 五步 + 雙模式路由 + U4 兜底〕+ contracts GlossaryReadySpec 補 domain_name + client thinking_config 受控擴充〔§4 唯一例外、前向相容〕+ caption 提示詞 + 8 pytest；消費 DomainNormalizer/GlossaryManager；三大真理源全數就緒；plan v10 八輪 review 定稿）

### PIPE-RESUME (✅ 已完成·PIPE 縱向五路絞殺第 1 路)
- ✅ ~~PIPE-RESUME ResumePipeline策略管線~~（已落地、C1 `f3d4e41` + C2 `d7edcd9` + C3 `48aa5df` + C4 `8971a19` + C5 `e8a7429` + C6 `fabb114` + C7 收官；`pipelines/resume_pipeline.py` 四 Phase 策略〔P1 Vision 全鏈/P2 LCC+摘要+Glossary 自癒/P3 100% Bypass/P4 RAG ≥3〕+ tests/test_resume_pipeline.py 15 測試；消費 PIPE-CORE ABC/三大真理源/PIPE-SCAFFOLD 影子；baron 拍板擴 PipelineContext pdf_path/owner_id；custom_metadata 硬前置 defer 僅影子 B 軌、不 Flip）
- ✅ ~~PIPE-RESUME v9 影子整合與規格同步~~（已落地、C1 `b97958b` + C2 `e64417a` + C3 `f239721` + C4 `9bbad2d` + C5 `9291c5c` + C6 `4e15905` + C7 收官；raw_metadata 旁路穿線 + P1 影子標題後綴 (測試) + P2 摘要先行步序 + P3 翻譯策略隔離 constraints + C5 影子寫庫保真〔對齊 A 軌 upsert_paper〕+ 廢 self._raw_meta；resume 19 測試、全套件 483 passed；A 軌 byte 不動）
- ✅ ~~TILING-HOTFIX-1 — 緊急熱修復：TextTiling Embedding 速率超限 (429) 批次化修復~~（已落地、`702347a`；`tiling_processor.py:425` 逐筆 embed_query→批次 embed_documents〔1/32 請求+線性退避+順序保證〕；根治 429 阻斷+test_tiling_paragraph 併發 flaky；全套件 484 passed；⚠️ task_type RETRIEVAL_QUERY→DOCUMENT 行為變更、Flip/結案前須重捕 Golden Baseline）
- ✅ ~~SHADOW-HOTFIX-2 — B軌影子標題 (測試) 後綴與履歷公司名翻譯修復~~（已落地、`3d2778a`；3 處移除矛盾交回母提示詞：web_server translated_title 補 (測試) + translator.py:40 STYLE_HINTS 移除公司名 + resume_pipeline.py:109 constraints 改產品-only；全套件 486 passed；⚠️ B軌譯文改變、與 TILING-HOTFIX-1 合併重捕 Golden Baseline；學歷 doubling 殘留歸 RESUME-P3）

