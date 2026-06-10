# PIPE-SLIDES SlidePipeline 簡報策略管線 · tasks

> 依據 plan：`.claude-logs/baton/2026-06-11_PIPE-SLIDES_SlidePipeline簡報策略管線_plan_v1.md`（§99.2 v1.1、U1-U11、§9 八 OQ 全結清）
> 工作流類別：**BE-Refactor**（logging_SOP + database_SOP 強制 §5 核查）
> **工作範圍硬限三檔**（baron 提示詞硬規則）：新建 `pipelines/slide_pipeline.py` / 修改 `pipelines/__init__.py`（註冊 import）/ 新建 `tests/test_slide_pipeline.py`——其餘核心調度與 A 軌全列 §7 不可動（Checkout 之母 plan 條目同步為唯一文件例外、Q6 拍板）。

---

## §0 改版規則
- 改版觸發：§8 拆分或 §6 驗收變動 → 改章節 + §99.2 Revision
- plan 續留 baton、唯 C7 Checkout 一次性歸檔

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 | `pipelines/slide_pipeline.py`（四 Phase 策略、Vision/去重/封面/六步/逐頁翻譯/alt 對齊全內聚為私有方法）/ `tests/test_slide_pipeline.py`（§8.1 全清單、含 §7.2 key-changing 整合測試）|
| **修改檔案** | 2 | `pipelines/__init__.py`（import slide_pipeline 觸發註冊、C7-hotfix 教訓）/ 母 plan v10（**僅 C7 Checkout**：§8.5 條目 PIPE-VISUAL→PIPE-SLIDES 改名 + 狀態 + slides「P3 100% Bypass」句更正——Q6/Q7 拍板、沿 PIPE-SYNC-2 範式 .bak+HTML 包裹）|
| **狀態更新** | 2 | TODO.md / prompts/INDEX.md |
| **Commits** | 7 | C1 → C2 → C3 → C4 → C5 → C6 → C7(Checkout) |
| **baton 歸檔** | 1 次 | C7 一次性 mv（plan + tasks + C1-C7 執行報告 → plans//tasks//executions/）+ git add |

---

## §1 TL;DR（概要）

PIPE 第 2 路 SlidePipeline 四 Phase 落地，7 commit：

- **C1 — Skeleton & Register（骨架與註冊）**：`@PipelineFactory.register('slides')` stub + `__init__` import + 分派測試。
- **C2 — P1 Vision Ingestion（每頁存圖與視覺解析）**：整頁存圖 + Vision temp=0 轉錄 + 條件滾動 + 封面判定/fallback + 跨頁統計去重（U1-U4）。
- **C3 — P2 Six-Step（六步與頁 key 契約）**：統一六步、① 順產 raw_domain、② 順產缺失頁標題、key=`p{N}_{標題}`（U5/U6）。
- **C4 — P3 Per-Page Translate & Restore（逐頁翻譯與排版還原）**：並行逐頁翻 + alt 對齊雙 Caption 根除 + constraints + rag_sections 旁路（含同頁合併）+ zh 路 + fallback（U7-U10）。
- **C5 — P4 Wire（RAG 接線）**：`run_phase4` 呼 `rag_indexer.index`（四產物、≥3）（U11）。
- **C6 — Unit & Integration Tests（測試補全）**：§8.1 全清單、含 **key-changing 整合測試**。
- **C7 — Checkout（收官歸檔與母 plan 同步）**：Conformance + 母 plan §8.5 改名/狀態/Bypass 句同步（Q6/Q7）+ baton 一次性歸檔。

---

## §2 現況

- B 軌基建全就緒（§3.1⑤ plan 證據）：PIPE-CORE ABC／三大真理源／rag_indexer／統一六步／rag_sections 旁路 key 契約／§1.3.1 Vision 共用規格／RESUME-PERF-1 並行範式／影子派發（web_server doc_type 直通、零改）。
- A 軌 slides 三病灶（plan §3.1①②③ 碼證+實件）：雙 Caption（`slides_processor.py:155`）／Vision 零 temperature／表格 cell 塞 `###`。
- `get_strategy('slides')` 現回 NullStrategy（未註冊）——影子上傳 slides 現況走 A 軌 only。

## §3 觀察問題

對齊 plan §1：A 軌三病灶 + 簡報無 B 軌路；三缺口已拍板解（整頁存圖／key=`p{N}_{標題}`／raw_domain 摘要順產）。

## §4 設計方案（對齊 plan §2 U1-U11；全邏輯內聚 `slide_pipeline.py` 私有方法）

### §4.1 C1 — Skeleton & Register
`pipelines/slide_pipeline.py`：`@PipelineFactory.register('slides')` + `DocumentStrategy` 四方法 stub（拋 NotImplementedError 以外的最小合約形）+ `rag_char_threshold=3`；`pipelines/__init__.py` 補 `from pipelines import slide_pipeline`（C7-hotfix 教訓）。

### §4.2 C2 — P1 Vision Ingestion（U1-U4）
私有方法群：`_render_pages`（fitz `get_pixmap` 逐頁存 `images/page-{N}.png`、空白頁跳過、參照 A 軌演算法**自建不 import**）→ `_transcribe_page`（Vision、`temperature=settings.LLM_VISION_TEMPERATURE`、忠實轉錄 prompt 含 U9 cell 禁 `###` 約束；**條件滾動**：Q1 判準〔頁標題含「(續)」/「cont'd」或前頁表格截斷〕才注入前頁、否則 ThreadPool 並行）→ `_detect_cover`（第 1 頁判定；是→title+公司/日期入 `ctx.raw_metadata`；否→title=檔名 fallback）→ `_dedupe_headers`（Q2：短行 ≤20 字、≥60% 非封面頁→剔除、清單入 `logger.info`）→ 組 sections（每頁=section）→ tiles=processed JSON（opt-out TextTiling）；`source_lang` 啟發式（沿 resume）；影子 `(測試)` 後綴。產 `IngestionMetadataSpec`。

### §4.3 C3 — P2 Six-Step（U5/U6）
`run_phase2` 六步：① 全文摘要（**prompt 同呼叫要求輸出 `raw_domain` 一行**、解析失敗→None 降級）→ ② 批次每頁摘要（**同呼叫對無標題頁順產標題**；key=**`p{頁序}_{原文頁標題}`**）→ ③ `normalize_to_lcc(raw_domain, context=摘要)` → ④ Glossary 級聯（`query_cascade`→缺詞 `extract_terms`〔對全部提取內容、注入摘要+LCC〕→upsert 冪等；LLM 交易外）→ ⑤ 翻全文摘要（DEEP_THINK）→ ⑥ 批次翻頁摘要 → `GlossaryReadySpec.section_summaries`（key 同 ②）+ `domain_name`。三安全鎖（批次有界/非致命/可量測 performance_metric phase=P2）。

### §4.4 C4 — P3 Per-Page Translate & Restore（U7-U10）
`run_phase3`：逐頁 `InjectionContext(lcc, glossary, zh_summary, constraints=_SLIDE_CONSTRAINTS, doc_type='slides')` → Translator NORMAL；**並行照抄 RESUME-PERF-1**（ThreadPool+slot index 保序+既有 `_api_semaphore`+單頁失敗退原文）。還原：每頁 `![{alt=description 譯文}](images/page-{N}.png)` + 譯文；**嚴禁 `*圖表：*` 獨立段與頁頂重複總述**（U8）；**不渲染 meta header**（U10）。`_SLIDE_CONSTRAINTS`（Q4）：品牌/產品原文、術語中英並列、cell 禁 `###`、數字/單位原樣。**同頁短 items 合併**於構造 `ctx.rag_sections` 時（Q3、rag_indexer 零改）；`summary_key`=C3 同 key；**zh 來源**跳譯仍建 per-section；**退化 fallback**（Q5：頁數=1 或 >50% 頁空/異常→整檔單發）。產 `BilingualMarkdownSpec`。

### §4.5 C5 — P4 Wire（U11）
`run_phase4`：呼 `rag_indexer.index(rag_sections+section_summaries, rag_tree_path, title…)`（四產物、≥3 門檻、embedding 交易外、失敗拋由 Orchestrator 標 `rag_status='failed'` 不阻 reading_ready）——對齊 resume run_phase4 範式。

### §4.6 C6 — Unit & Integration Tests
`tests/test_slide_pipeline.py` 補全 plan §8.1 全清單（mock LLM/Vision/Embedding 隔離）；**§7.2 整合測試**：P2→P3→P4 串接 + FakeTranslator **真改寫頁標題**（譯 title≠原文 key）→ 斷言 P4 chunk 含頁摘要（`p{N}_` key 對位不受譯文影響）。

### §4.7 C7 — Checkout
Conformance（plan §2 U1-U11 / §6 各 commit 驗收 / §7 不可動 / 提示詞稽核 / msg 完整 / **§7.2 整合測試存在且通過**〔本路正面達標、免豁免〕）→ **母 plan §8.5 同步**（Q6/Q7：條目 PIPE-VISUAL→PIPE-SLIDES + 狀態 ✅ + slides「P3 100% Bypass」句更正為逐頁；.bak + HTML 包裹、沿 PIPE-SYNC-2 範式、本體不入版控）→ baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

對齊 plan §5：Golden D1 故意差異→改善豁免（Q8）／滾動誤開→Q1 保守判準／表格畸形→U9 雙層約束+grep 驗收／去重誤殺→Q2 門檻+log／順產欄位解析失敗→非致命降級／註冊漏 import→C1 測試鎖。每 commit 行為界線見 §8。

## §6 測試計畫（逐 Commit；對齊 plan §8.1 + §5 SOP + §8.2 E2E）

### §6.1 C1 驗收
- pytest：`get_strategy('slides')` 回 SlidePipeline、`factory._registry` 含 'slides'（含 `__init__` import 路測試）。
- grep：`grep -n "register('slides')" pipelines/slide_pipeline.py`；`grep -n 'slide_pipeline' pipelines/__init__.py`。

### §6.2 C2 驗收
- pytest：封面兩路（metadata 入欄/title=檔名 fallback 非空）；去重（多頁重複短行剔、封面排除、log 有清單）；存圖檔名 `page-{N}`；空白頁跳過；滾動預設關（mock 各頁獨立、無前頁注入）。
- grep：`grep -n 'LLM_VISION_TEMPERATURE' pipelines/slide_pipeline.py`（temp=0 接線）；`grep -n 'get_pixmap' 同檔`；`grep -cn 'import.*slides_processor' 同檔` → 0（不耦合 A 軌）。

### §6.3 C3 驗收
- pytest：六步序（mock LLM）；**key=`p{N}_{標題}`、連續同標題頁不撞**；無標題順產；raw_domain 順產+缺值降級（None→內容判定路）；section_summaries key 對位。
- SOP：`grep -nE '\.commit\(\)' slide_pipeline.py | grep -v session.begin` → 無裸 commit（LLM 交易外）。

### §6.4 C4 驗收
- pytest：逐頁分流；**全文無 `*圖表：` 段**（grep 斷言）+ alt=description 譯文；cell 無 `###`；並行保序 byte 等拍 + 單頁退原文（仿 RESUME-PERF-1 C3）；同頁合併後 rag_sections 條數正確；zh 路 per-section；fallback 兩判準；meta header 不渲染。
- grep：`grep -n '_SLIDE_CONSTRAINTS' slide_pipeline.py`；`grep -cn '圖表：' slide_pipeline.py 還原段` → 渲染路徑 0。

### §6.5 C5 驗收
- pytest：run_phase4 呼 rag_indexer（mock）傳 rag_sections/section_summaries/rag_tree_path/title；失敗拋不吞。
- grep：`grep -cn 'rag_processor' slide_pipeline.py` → 0（零 A 軌依賴）。

### §6.6 C6 驗收
- `pytest tests/test_slide_pipeline.py -v` 全綠（≥ plan §8.1 七類）+ **整合測試 key-changing 通過** + 全套件不退化。

### §6.7 C7 Checkout 驗收
- Conformance 六維度（含 §7.2 整合測試必驗）；母 plan：`grep -c 'PIPE-VISUAL' 母plan` → 0（僅歷史 Revision 引文可留）、slides「100% Bypass」句已更正；`ls baton/ | grep PIPE-SLIDES` → 0。

### §6.8 全任務 E2E（baron、plan §8.2）
影子上傳 ST 實件 → 圖文對照無雙 Caption／toolbar 摘要／重跑穩定／引用「《簡報名》> p{N} 標題」／`#sst` 跨文件含此件／golden capture slides（B 軌）+ 改善豁免裁決。

## §7 不可動清單（對齊 plan §6）

- [ ] **A 軌全部**（`pipeline_core.py`／`processor/slides_processor.py`〔病灶留 A 軌〕／`md_restore_processor`／`rag_processor`）。
- [ ] 第 1 路 `resume_pipeline.py` + 其測試；三大真理源本體；`processor/rag_indexer.py`（**零改、嚴禁 doc_type 分支污染**——Q3）。
- [ ] 四凍結合約欄位結構（contracts.py）——簡報專屬欄走 `raw_metadata` 旁路。
- [ ] `web_server.py`／`orchestrator.py`／`factory.py`／`context.py`（C1 僅 `__init__.py` 一行 import）。
- [ ] SPEC 本體（純引用）；母 plan **僅 C7 依 Q6/Q7 同步兩處**、其餘條目不動。
- [ ] slides 之 A 軌 golden（留作 A 軌基準、Q8）。

## §8 推薦 Commit 拆分

### C1 — Skeleton & Register（骨架與註冊）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `pipelines/slide_pipeline.py`（stub）；修改 `pipelines/__init__.py`（+1 行 import）；新建 `tests/test_slide_pipeline.py`（分派測試） |
| **安全性** | 🟢 高 — stub 註冊、影子旗標外零行為 |
| **可逆性** | 🟢 高 — 刪檔+revert import |
| **驗收 grep 條件** | §6.1 兩 grep + 分派 pytest |
| **依賴關係** | 無前置 |
| **具體實作細節** | `@PipelineFactory.register('slides')` class SlidePipeline(DocumentStrategy)：四方法 stub（合約最小形）+ `rag_char_threshold=3`；`__init__.py` 補 import（C7-hotfix 教訓、附註解）；測試驗 `_registry['slides']` 與 get_strategy 非 NullStrategy |

### C2 — P1 Vision Ingestion（每頁存圖與視覺解析）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（`run_phase1` + `_render_pages/_transcribe_page/_detect_cover/_dedupe_headers` 私有群）；測試追加 |
| **安全性** | 🟡 中 — P1 邏輯量大；mock 測試鎖行為；僅影子 B 軌 |
| **可逆性** | 🟢 高 — 單檔、revert 即回 stub |
| **驗收 grep 條件** | §6.2 全項（temp 接線/get_pixmap/零 slides_processor import + 5 pytest） |
| **依賴關係** | 前置 C1 |
| **具體實作細節** | 依 §4.2：fitz 渲染存圖（演算法參照 A 軌 L89-167、自建）；Vision 呼叫帶 `temperature=settings.LLM_VISION_TEMPERATURE` + §1.3.1 忠實轉錄 prompt（含 U9 cell 禁 `###`）；Q1 滾動判準（預設關、延續標記/表格截斷才注入前頁、其餘 ThreadPool 並行）；Q2 去重（≤20 字短行 ≥60% 非封面頁、剔除入 log）；封面判定→raw_metadata／title fallback 檔名；每頁=section、tiles=processed JSON；source_lang 啟發式；產 IngestionMetadataSpec |

### C3 — P2 Six-Step（六步與頁 key 契約）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（`run_phase2`）；測試追加 |
| **安全性** | 🟢 高 — 全消費既有真理源、LLM 交易外、非致命降級 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.3（key 不撞/順產/降級 pytest + 裸 commit grep 0） |
| **依賴關係** | 前置 C2（吃 tiles/raw_metadata） |
| **具體實作細節** | 依 §4.3 六步；**key=`p{頁序}_{原文頁標題}`**（§4 接縫契約、HOTFIX-2 根除）；① prompt 末加 `domain:` 一行解析（缺→None→DomainNormalizer 內容判定）；② 對無標題頁同呼叫產標題（缺→`p{N}` 裸序兜底）；④ 對全部提取內容提取、注入摘要+LCC；⑤⑥ DEEP_THINK／批次翻；三安全鎖 + domain_name 一次解析 |

### C4 — P3 Per-Page Translate & Restore（逐頁翻譯與排版還原）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（`run_phase3` + `_SLIDE_CONSTRAINTS` + 還原/合併/fallback 私有群）；測試追加 |
| **安全性** | 🟡 中 — 本任務最大 commit（翻譯+還原+旁路）；測試鎖死無 `*圖表：*`/保序/fallback |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.4 全項（無圖表段 grep+alt+cell+並行+合併+zh+fallback+無 header） |
| **依賴關係** | 前置 C3（吃 GlossaryReadySpec） |
| **具體實作細節** | 依 §4.4：逐頁 InjectionContext+NORMAL；並行照抄 RESUME-PERF-1（slot index 保序、`_api_semaphore`、單頁退原文+`logger.warning` event）；還原 `![alt](images/page-{N}.png)`+譯文、alt=description 譯文（en 版原文）、**單點呈現**；`_SLIDE_CONSTRAINTS`=Q4 四條；同頁短 items 合併於構造 rag_sections（Q3）；summary_key=C3 key；zh 路（SPEC U4）；fallback=Q5 兩判準→`_translate_whole` 式兜底；不渲染 meta header（U10） |

### C5 — P4 Wire（RAG 接線）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（`run_phase4`）；測試追加 |
| **安全性** | 🟢 高 — 純接線 rag_indexer（resume run_phase4 同範式） |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.5（mock 接線 pytest + rag_processor import 0） |
| **依賴關係** | 前置 C4（吃 rag_sections） |
| **具體實作細節** | `rag_indexer.index(sections=ctx.rag_sections, section_summaries=…, rag_tree_path=paper_manager.rag_tree_path(...), title/translated_title…)`；異常拋出由 Orchestrator 標 rag_status='failed'；零 A 軌 import |

### C6 — Unit & Integration Tests（測試補全）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 僅 `tests/test_slide_pipeline.py` |
| **安全性** | 🟢 高 — 純測試；**嚴禁為過測試改業務碼**（不符→停下回報） |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.6（全清單綠 + key-changing 整合 + 全套件不退化） |
| **依賴關係** | 前置 C1-C5 |
| **具體實作細節** | 補全 plan §8.1 七類缺口；**整合測試**：P2→P3→P4 串接、FakeTranslator 真改寫頁標題（key-changing transform）→ 斷言 chunk 含頁摘要、`p{N}_` key 不受譯文影響（§7.2 正面達標） |

### C7 — Checkout（收官歸檔與母 plan 同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 母 plan v10（§8.5 兩處、.bak、Q6/Q7）；歸檔/TODO/hash；零業務碼 |
| **安全性** | 🟢 高 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.7（Conformance 六維度含 §7.2 必驗 + 母 plan grep + baton 0 殘留） |
| **依賴關係** | 前置 C1-C6 全 commit |
| **具體實作細節** | Conformance 全綠 → 母 plan .bak→archive、§8.5「PIPE-VISUAL」條目改名 PIPE-SLIDES+狀態 ✅+slides「P3 100% Bypass」句更正逐頁（HTML 包裹、補註、本體不入版控=195e12b 先例）→ baton 一次性 mv（plan/tasks/C1-C7 報告）+ git add → TODO 完成表+索引 ✅+hash 自癒 → msg /tmp |

> **各 Run 執行報告**：C1-C6 各產 `_執行.md`（template_execution、暫存 baton、嚴禁 mv/git add）；C7 一次性歸檔。
> **E2E/golden（baron 運維、非 commit）**：§6.8；B 軌 golden 另捕 + 改善豁免（Q8）。

## §9 Open Questions

plan §9 八題全結清（v1.1）；tasks 階段無新增 OQ。

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | PIPE-SLIDES commit 拆分與驗收清單 |
| 權威源 | 本檔 §8（依 plan v1〔v1.1〕U1-U11 + Q1-Q8 定案）|
| 引用方 | C1-C7 Run/Checkout 執行報告 |
| 不可動唯一源 | §7（對齊 plan §6 + baron 三檔硬限）|
| 改版觸發 | §8/§6 變動 |

### §99.2 Revision 歷程
- v1 (2026-06-11)：初稿——7 commit（C1 骨架註冊 / C2 P1 Vision / C3 P2 六步 key 契約 / C4 P3 逐頁翻譯還原〔最大〕/ C5 P4 接線 / C6 測試補全含 §7.2 key-changing / C7 Checkout 含母 plan Q6/Q7 同步）+ §0.5 盤點 + §6 逐 commit 驗收 + §7 不可動（三檔硬限 + rag_indexer 禁分支污染）+ §8 六維度表
