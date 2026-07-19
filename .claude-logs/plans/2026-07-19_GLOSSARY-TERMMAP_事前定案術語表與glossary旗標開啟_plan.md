# GLOSSARY-TERMMAP 事前定案術語表與 glossary 旗標開啟 plan

> 建立 `GlossaryManager.build_termmap` 五路共用「事前定案術語表」builder（切塊 census → 去重 → DB 分流 → 只翻未知 → 定案 upsert），P3 以定案表注入實現全文術語一致與括號收斂；併同開啟 `LLM_USE_GLOSSARY_ALIGN` 旗標（GLOSSARY-ON）；接收 PIPE-INGEST v4 移交之缺陷④（同字括號噪音）⑤（一名多譯）。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：litedoc 影子輸出同一專名多譯不一致（`sentient sun` 三譯）與「譯名＝原文」括號重複（`SpaceX (SpaceX)` ×74）——根因三層（design spec F3）：①**飛輪早退**——三路 `_heal_glossary` 之 `if existing: return existing` 使某 LCC 域一有詞即不抽新詞不寫庫、跨文件累積第一份後停轉；②**抽詞綁摘要**——`extract_terms` 需雙語對齊樣本、P2 當下唯一譯過的是摘要 → 只抽摘要、漏 body 長尾（SpaceX ×67 橫跨 7 段、a16z ×13/3 段、Starship ×12/5 段）；③glossary 旗標預設關、術語強約束區塊全程不注入。三路並行翻譯零共享上下文，一致性**只能事前定案、無事後補救**。
- **解法**：`GlossaryManager` 新增五路共用 `build_termmap`（N1 沿段落邊界切塊 → N2 逐塊純 LLM census **只認原文專名不翻譯** → N3a term_key 正規化去重 → N3b DB 分流〔`query_cascade` **廢早退、改「已知 ∪ 新」**〕→ N4 僅未知詞一次小呼叫翻譯〔context=摘要〕→ N5 定案表 upsert〔寫「定案」、永不吃收割輸出〕）；三路 P2 `_heal_glossary` 收斂為呼叫共用 builder；P3 經既有 `InjectionContext.glossary` 注入每段 → body 照表翻、全篇一致；併同開啟 `LLM_USE_GLOSSARY_ALIGN`（GLOSSARY-ON）；附論——litedoc P3 注入鄰近 `section_summaries` 之摘要型滑窗（parallel-safe、原料現成）。
- **影響**：`processor/glossary_extractor.py`（build_termmap＋query_cascade 消費側）、`pipelines/litedoc_pipeline.py`／`resume_pipeline.py`／`slide_pipeline.py` P2 glossary 段收斂、`processor/translator.py` 術語強約束區塊補「譯名＝原文者免括號」一句、`settings.py` 旗標預設翻轉＋census 切塊常數、`.env.example` 同步。DB schema 零動（GlobalGlossary 既有表）；A 軌零碰。**旗標開啟影響全五路 B 軌翻譯輸出**（golden 走改善豁免＋影子 E2E）。

---

## §2 目標規格

1. **`GlossaryManager.build_termmap`（共用 builder、五路共享）**：簽名收 `(full_text, abstract, translated_abstract, source_lang, target_lang, domain)` 級參數、回 `{term: translation}` 定案表。五步硬規格：
   - **N1 切塊**：依 `settings.GLOSSARY_CENSUS_CHUNK_CHARS`（新常數、env 可調）沿**段落邊界**累積切塊、不切句中；門檻與翻譯 size-gate（15k）**無關**（前者為 census 召回、後者為輸出品質，兩獨立）。
   - **N2 逐塊 census**：**純 LLM、只認原文專名、不翻譯**（regex 不當判官——CJK 完全失效；整篇一次 census 不採——注意力稀釋致召回掉）；逐塊可並行（比照 P3 並行範式、受 `LLMClient._api_semaphore` 限流）；單塊失敗 soft（該塊詞缺、不阻斷）。
   - **N3a 去重**：term_key 正規化（沿用 `GlossaryManager` 既有 term_key 規則）聯集 → 唯一原文詞集（**同詞只一份 → 「同詞不同譯」衝突根本不發生**、免多數決/reconcile）。
   - **N3b DB 分流**：`query_cascade` 查已知 → `{已知（有譯法）/ 未知}` 兩堆；**廢除「一有詞即早退」語意**——已知照收、未知照抽，跨文件累積飛輪恢復（§9 Q1 拍板前提）。
   - **N4 只翻未知**：未知詞集**一次**批次小呼叫（context=摘要對、引導風格）→ 新 term→譯法；**body 不重翻**（N4 只翻術語清單、P3 主體流程零動）。
   - **N5 定案 upsert**：定案表（＝DB 已知 ∪ 新翻）以既有 `upsert_terms`（`on_conflict_do_nothing` 冪等）寫回；**DB 只吃刻意定案的詞、永不吃 P3 收割輸出**（污染低；測試期壞了清庫重跑即可、清詞工具屬生產後期便利非前提）。
   - LLM 全在 DB 交易外（database SOP）；零文體字面量、route-specific 參數注入（section_engine 紀律）。
2. **三路 P2 收斂**：litedoc／resume／slides 三份重複 `_heal_glossary` 改為呼叫 `build_termmap`（P2 於摘要譯畢後執行、full_text 各路自備）；三路各自 P2 其餘步序零動。
3. **P3 注入鏈零新機制**：定案表經既有 `GlossaryReadySpec.glossary` → `InjectionContext.glossary` → `translator._build_system_prompt` 術語強約束區塊（translator.py:127 既有 gated 注入）進入每一並行翻譯單元——**translator 注入鏈零改動**、僅靠定案表內容生效。
4. **括號收斂（缺陷④、PIPE-INGEST 移交項）**：術語強約束區塊文案補一句「**術語譯法與原文相同者，直接沿用原文、不得另加括號注解**」（改的是 `translator.py` 旗標 gated 注入區塊、**非** `prompt/translate/*.txt` 母 prompt 檔）。驗收（SpaceX 樣本重跑）：`SpaceX (SpaceX)` 型同字括號 pair 每一專名 ≤1 次。
5. **術語一致硬驗收（缺陷⑤、F1 定案）**：**「同一文件內同一 census 命中專名全文單一譯法」為本案硬驗收**（termmap 注入每段保證之；PIPE-INGEST v4 §2.7 已宣告此硬驗收落於本案）。驗收（SpaceX 樣本重跑）：`sentient sun` 全文單一譯法。census 未命中之殘角詞：測試期清庫重跑即可、不設硬判。
6. **GLOSSARY-ON（併同前置項）**：`settings.py` `LLM_USE_GLOSSARY_ALIGN` 預設翻轉為 true（或 `.env` 樣板明示開啟、依 §9 Q2 拍板形式）；`.env.example` 同步註記；開啟後 P2 建表／P3 注入／領域名注入（translator.py:119）全鏈生效。
7. **連貫附論（摘要型滑窗、design spec 併入 F3 定案）**：litedoc P3 逐 section 翻譯注入**鄰近 section 之 P2 `section_summaries` zh 摘要**（原料現成——P2 已算、現況只餵 P4；本案補 P3 接線）；**parallel-safe**（摘要 P2 預算好、P3 拉現成、並行不變）；**注入容缺**（部分 section 摘要失敗缺 key → 缺則略、零阻斷）；**嚴禁譯文型 preceding 跨 section**（會逼序列、犧牲 RESUME-PERF-1 並行收益）；size-gate 三分支（<15k／無 section／heading 退化）**保留零動**。
8. **已知限制（本案不修、明文記錄）**：多語 source_lang 偵測（義大利文等拉丁語系被 catch-all 判 `en` → 污染 `en` 命名空間）屬 **LANG-DETECT 另案**（design spec F4）、義文樣本進場前必做；英／日／繁中樣本不受影響、本案即可上。first-write-wins 錯詞黏住＝測試期清庫重跑、生產後期才需清詞工具（GLOSSARY-UI、非前提）。

### §2.5 候選方案（Diverse Rollout）

一致性機制屬架構級決策，四案留痕（design spec F3 否決路徑）：

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| 方案 A（選定） | **事前定案術語表**：census 只認詞→唯一詞集只翻一次→定案注入每段 | 衝突根本不發生（免 reconcile）；翻譯量最小（已知免翻）；DB 只吃定案、污染低；跨文件累積恢復；共用 builder 一次做五路受惠 |
| 方案 B（否決） | P3 後收割（從翻完 body 抽詞對回寫） | body 已不一致時收割到任意/錯譯法、寫死 DB 汙染未來——**一致性只能事前決定、無事後補救** |
| 方案 C（否決） | regex 撈專名當判官 | regex 判不了「是不是專名」（拉丁 case 啟發式、CJK 完全失效）；至多當減量前置、不可當判官 |
| 方案 D（否決） | 整篇一次 census（1M context 塞得下） | 注意力稀釋、召回率掉、抽詞不準——改切塊（段落邊界、可並行、wall-clock 不太增） |
| 方案 E（否決） | 本地 census→constraints、不寫 DB | 丟掉跨文件累積（下一份同域文件無法免費取得定譯）；glossary 機制現成只是被旗標關著、「太重」經實查為假議題（每份文件 1 次便宜 LLM + 短查 + 極短冪等寫、交易外） |

- **選定理由**：A 案唯一同時達成「全文一致硬保證」「翻譯量最小」「跨文件累積」「五路共用」四目標。
- **否決留痕**：B-E 留底如上（CLAUDE.md §1.9；均為 design spec §5 誠實留痕之定案）。

---

## §3 現況與證據

- **三路 `_heal_glossary` 重複（收斂對象）**：
  - `pipelines/litedoc_pipeline.py`：`L343` 呼叫、`L422-431` 本體——`L428-429` `existing = gm.query_cascade(...)` → `if existing: return existing`（**飛輪早退**：一有詞即回、不抽不寫）。
  - `pipelines/resume_pipeline.py`：`L371` 呼叫、`L480-487` 本體（同式早退 L486-487）。
  - `pipelines/slide_pipeline.py`：`L530` 呼叫、`L653` 本體（同式）。
  - **早退之原始設計動因（2026-07-19 review 歷史追溯、Q1 判定依據）**：三路 P2 docstring 明文「Glossary 級聯自癒（query_cascade→**缺詞** extract_terms→upsert）」（`resume:336`、`slides:489`）——「缺詞才抽」＝為省 `extract_terms` 同步 LLM 呼叫之**域級成本快取閘門**，設計假設「該 LCC 域已有詞＝術語庫已建成、可直接沿用」。該假設忽略「新文件引入新術語（長尾）」：域被首份文件寫入（可能僅數詞）後、後續同域文件全數跳過自癒 → **飛輪第一步即停轉**。判定＝優化過度之設計缺陷（Q1 拍板廢除）。
- **processor/glossary_extractor.py（既有機制、build_termmap 之地基）**：
  - `query_cascade L78`：級聯查詢（domain → general）；`extract_terms L122`：**雙語樣本**抽詞（現況只餵 abstract 對 → 漏 body 長尾之結構性原因）；`upsert_terms L177` + `on_conflict_do_nothing L212`：冪等寫回（first-write-wins）。
  - LLM 於 DB 交易外（模組 docstring L13 明示）。
- **旗標鏈（現況全關）**：`settings.py:112` `LLM_USE_GLOSSARY_ALIGN` 預設 false；`processor/translator.py:119`（領域名注入）與 `:127`（術語強約束區塊 `if settings.LLM_USE_GLOSSARY_ALIGN and ctx.glossary`）雙 gate——**P2 建表→P3 注入全鏈接好、只是被旗標關著**（v1 plan U4 原設計、「太重」為假議題）。
- **注入合約（零改消費）**：`GlossaryReadySpec.glossary`（contracts 凍結欄）→ litedoc P3 `L481` `glossary=gspec.glossary` 組 `InjectionContext` → translator 每單元注入。
- **section_summaries 現況（附論原料）**：litedoc P2 `L351` `build_section_summaries` 產 `{原文標題 path: zh 摘要}` → 現況**只餵 P4 RAG**（`L596`）、P3 未注入——「現成」＝摘要已算、注入待接。
- **body 長尾實證（SpaceX 樣本、design spec F3）**：SpaceX ×67 橫跨 7 段、a16z ×13/3 段、Starship ×12/5 段、Mars ×12/6 段——要一致的詞橫跨多段、僅抽摘要必漏。
- **缺陷④⑤量化基線（PIPE-INGEST 移交）**：影子 PDF 同字括號 pair 106/107（`SpaceX (SpaceX)` ×74）；`sentient sun` 三譯（有意識/有感知/有知覺）。

### §3.1 grep 鋼鐵證據

```bash
# 三路 _heal_glossary 與早退（本 session 實跑）
grep -n "_heal_glossary\|if existing" pipelines/litedoc_pipeline.py pipelines/resume_pipeline.py pipelines/slide_pipeline.py
# → litedoc:343/422/428-429、resume:371/480/486-487、slides:530/653

# glossary_extractor 地基
grep -n "def query_cascade\|def extract_terms\|def upsert_terms\|on_conflict_do_nothing" processor/glossary_extractor.py
# → :78 / :122 / :177 / :212

# 旗標鏈（全關）
grep -n "LLM_USE_GLOSSARY_ALIGN" settings.py processor/translator.py
# → settings:112（預設 false）、translator:119/:127（雙 gate）

# section_summaries 現況只餵 P4
grep -n "section_summaries" pipelines/litedoc_pipeline.py   # → P2 產 :351、P4 消費 :596、P3 零命中
```

---

## §4 跨 Phase 接縫契約

本案為 P2（建表）→ P3（注入翻譯）跨 Phase handoff＋五路共用 builder，逐條凍結：

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| N2 census → N3 去重/分流 | 逐塊 census 產原文專名候選集 | N3a 以 **term_key 正規化**（沿用 GlossaryManager 既有規則）聯集去重、N3b 以同一 term_key 查 `query_cascade` | key＝**正規化 term_key**；census 產出、去重、DB 查詢**三者同一正規化函式**、不得各自實作 |
| N4/N5 定案表 → P3 注入 | `build_termmap` 回 `{term: translation}` 定案表、經 P2 併入 `GlossaryReadySpec.glossary` | P3 `InjectionContext.glossary` → `translator._build_system_prompt` L127 既有區塊逐單元注入 | 欄位＝**既有凍結合約 `glossary` 欄**（contracts 零動）；producer 寫入與 consumer 注入為同一 dict、無中間轉換 |
| N5 定案表 → GlobalGlossary | `upsert_terms`（冪等）寫 `(source_lang, target_lang, domain, term_key)` | 下一份同域文件 N3b `query_cascade` 直接查得（跨文件累積） | 聯合唯一鍵＝既有 schema 零動；**DB 只吃定案表、永不吃 P3 收割輸出**（單向寫入不變式） |
| P2 section_summaries → P3 滑窗注入（附論） | P2 `build_section_summaries` 產 `{原文標題 path: zh 摘要}`（既有） | litedoc P3 逐 section 以**原文標題 path** 查鄰近摘要注入 | key＝**原文標題 path**（與 P4 `summary_key` 同基準、RAG-ASYNC-HOTFIX-1 既有契約）；**注入容缺**（缺 key 略過、零阻斷） |
| 五路 → build_termmap | 各路 P2 以參數注入（full_text／abstract 對／source_lang／domain） | builder 零文體字面量、純參數消費 | route-specific 全留呼叫端（section_engine 紀律）；三路 `_heal_glossary` 收斂後**單一實作源** |

填寫規範見 `ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 旗標開啟改變**全五路** B 軌譯文輸出 | 🔴 高 | 影子軌不影響 A 軌交付；golden 走改善豁免＋baron 影子 E2E（§8.2）；測試期 DB 可丟、壞了清庫重跑（`glossary` 表 truncate）即全部重來；旗標可隨時 env 關回（單點回退） |
| census 成本與時延（每文件新增 N 塊 LLM 呼叫） | 🟡 中 | 逐塊並行＋semaphore 限流、wall-clock 增量有限；切塊常數 env 可調；成本結構＝N 次 census＋1 次未知詞翻譯（已知免翻、body 不重翻）——經 design spec F2 實查非效能問題 |
| 廢早退後 DB 寫入頻率上升、錯詞 first-write-wins 黏住 | 🟡 中 | 寫入僅「定案表」（非收割）、冪等極短交易；測試期清庫重跑即可；生產後期才需 GLOSSARY-UI（明文非前提） |
| 三路 P2 收斂改動 resume／slides（PIPE-INGEST 期間不可動之兩路） | 🟡 中 | 本案範圍**明文擴及三路 P2 glossary 段**（收斂為呼叫共用 builder、其餘步序零動）；三路既有測試全綠為底線；行為變化僅「glossary 內容更豐」、非流程結構變化 |
| translator 強約束區塊文案補句、影響五路 | 🟢 低 | 改動位於旗標 gated 區塊（translator.py:127）、旗標關即零效；**母 prompt txt 檔零動**；文案僅約束「同字免括號」單一語意 |
| 附論滑窗注入需動 section_engine 翻譯簽名 | 🟡 中 | 僅允許**純加法**（新參數帶預設、resume 現行呼叫零變）；若 review 發現無法純加法 → 附論拆出另案、不阻本案主體（§9 Q4） |
| DB schema／contracts 凍結合約 | 🟢 低 | GlobalGlossary 表與 `GlossaryReadySpec.glossary` 欄全零動 |

---

## §6 不可動清單

- [ ] **GlobalGlossary schema** 與 `models.py` 相關表定義（聯合唯一鍵零動）
- [ ] `pipelines/contracts.py` 凍結合約（`GlossaryReadySpec.glossary` 欄沿用、零增刪）
- [ ] `prompt/translate/*.txt` 母翻譯提示詞檔（括號收斂改 translator.py gated 區塊、不動母檔）
- [ ] `pipeline_core.py` 及 A 軌鏈全體
- [ ] `pipelines/ingestion_engine.py`（PIPE-INGEST 剛落地、本案零碰）
- [ ] 三路 P2 之 glossary 段**以外**步序（摘要／LCC／節點摘要等零動）；P3 size-gate 三分支結構零動
- [ ] `section_engine` 既有函式行為（附論注入僅允許純加法、預設參數下 byte 等價）
- [ ] `processor/rag_indexer.py` 與 P2→P4 `summary_key` 基準
- [ ] `glossary_extractor` 既有三函式簽名（`query_cascade`／`extract_terms`／`upsert_terms` 供 build_termmap 消費、對外行為不破壞；「廢早退」改的是**呼叫端語意**、非 query_cascade 本體）
- [ ] 既有 tests 斷言本體（僅允許依本案規格新增或更新 glossary 相關測試、逐條記錄於執行報告）

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| **design spec F2／F3／F1 定案** | `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`——F2（旗標開啟、「太重」假議題實查）／F3（事前定案術語表五步、三層問題、否決路徑、連貫附論併入）／F1（「全文單一譯法」硬驗收落於本案）／baron 選 1（與 PIPE-INGEST 前後腳） |
| **PIPE-INGEST 移交宣告** | `plans/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md` v4 §2.6/§2.7/§2.11——缺陷④⑤/括號之接收方＝本案 |
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| BE-Refactor 必讀 SOP | `sop/2026-05-23_logging_SOP_手冊.md`、`sop/2026-05-23_database_SOP_手冊.md`；落地前 §5 SOP 一致性核查 |
| 進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.3／§4.4） |
| 共用引擎紀律（前例） | `pipelines/section_engine.py` 設計原則（零文體字面量＋注入）；`processor/rag_indexer.py`（B 軌自有範式） |
| GLOSSARY-CORE 既有機制 | `processor/glossary_extractor.py`（級聯查詢／交易外抽詞／冪等回填——本案地基、TODO GLOSSARY-CORE 條目） |
| 缺陷量化基線 | `baton/litedoc_shadow_artifacts/`＋PIPE-INGEST plan §3（同字括號 106/107、sentient sun 三譯） |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：
  ```bash
  venv/bin/python -m pytest tests/ -q    # 基線 780 passed、不得低於基線
  ```
- **預計新增的測試**：
  - `tests/test_glossary_termmap.py`（新檔）：N1 切塊（段落邊界不切句中／門檻 env 可調）；N2 census mock LLM（只認詞不翻、單塊失敗 soft）；N3a term_key 正規化去重（同詞多形一份）；N3b 分流（已知∪新、**廢早退回歸斷言**——DB 有詞時仍抽仍寫）；N4 只翻未知（已知零翻譯呼叫）；N5 定案 upsert 冪等；**§7.2 跨 Phase 整合測試**：mock 全文（多段重複專名）→ build_termmap → 定案表注入 mock translator（key-changing）→ 斷言同一專名各段譯法一致、同字詞不加括號指令存在於 system prompt。
  - 三路 P2 測試更新：`_heal_glossary` 收斂後呼叫 build_termmap 之斷言（三檔既有 glossary 測試依規格改寫、逐條記錄）。
  - translator 測試：強約束區塊含「譯名＝原文免括號」句（旗標開時）；旗標關時零注入（回歸）。
  - 附論：litedoc P3 滑窗注入測試（鄰近摘要入 prompt、缺 key 容缺、size-gate 三分支零動回歸）。

### §8.2 手動端到端（E2E）驗證流程（baron、測試服）

1. 開旗標、清 glossary 表（測試期基線歸零），重傳 `SpaceX & the Sentient Sun.pdf` 走 litedoc 影子軌。
2. **硬驗收**：`sentient sun`／`mass driver`／`Starship` 等 census 命中專名**全文單一譯法**；`SpaceX (SpaceX)` 型同字括號每一專名 ≤1 次。
3. 查 DB `GlobalGlossary`：SpaceX 文件之定案詞已入庫（source_lang=en、domain=該文 LCC）。
4. **跨文件累積驗證**：重傳第二份同域英文樣本（如 `The_hidden_risks_in_Taiwan_s_boom`）→ 第一份之定譯被 N3b 直接查得沿用（免費一致）。
5. resume／slides 各抽一樣本重跑影子軌，確認 P2 收斂後零退化（譯文品質與既有欄位齊備）。
6. 附論抽驗：litedoc 長文跨段代名詞／指涉連貫較旗標前無退化。

---

## §9 Open Questions

> **六項均已於 2026-07-19 由 baron 拍板、全數採納推薦方案**（review 併 Q1 歷史追溯——早退＝域級成本快取閘門之優化過度缺陷）；本節留痕為決策紀錄、後續 tasks 拆分直接引用。

| 開放問題 | 拍板方案（✅ 定案） | 理由 |
|---|---|---|
| Q1：三路 `_heal_glossary` 之 `if existing: return existing` 早退是**有意設計**還是缺陷？ | ✅ **確定為缺陷、廢除**（改「已知 ∪ 未知」分流、僅未知詞呼叫翻譯） | 歷史追溯（§3 早退動因）：原為省 `extract_terms` LLM 呼叫之域級快取閘門、假設「域有詞＝庫已建成」——忽略新文件長尾、飛輪第一步停轉；廢除後兼顧成本（已知免翻）與飛輪滾動、寫入仍為冪等定案 |
| Q2：GLOSSARY-ON 形式 | ✅ **settings 預設翻轉 true**、`.env` 保留單點關回 | 內部小專案直接全開、簡化多路部署；env 保險留存 |
| Q3：`GLOSSARY_CENSUS_CHUNK_CHARS` 預設值 | ✅ **6000**（約 2-4 段、env 可調） | 兼顧注意力聚焦（召回率）與 API 呼叫次數；微調走 env 不需 commit |
| Q4：連貫附論（section_summaries 滑窗注入）歸屬 | ✅ **併入本案**；section_engine 採純加法參數、受阻可隨時剝離 | 原料現成（P2 已算）、僅 P3 接線；design spec §3.1 明文併入 F3 |
| Q5：census 專名界定範圍 | ✅ **專有名詞＋高頻領域術語**（排除一般詞彙與動詞片語） | 聚焦缺陷④⑤實際詞型、精確控制定案表體積 |
| Q6：三路 P2 收斂順序 | ✅ **分開落地**（litedoc 先行驗證、resume/slides 隨後等價收斂；拆分細節留 tasks） | litedoc 為缺陷現場先行實證；最大化隔離 Regression 風險 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GLOSSARY-TERMMAP 事前定案術語表與 glossary 旗標開啟的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 GLOSSARY-TERMMAP tasks / 執行報告；PIPE-SYNC-5 回灌案（glossary 機制章） |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格；build_termmap 落地後長期契約權威源為 PIPE-SPEC（PIPE-SYNC-5 回灌後）；LANG-DETECT（F4）／GLOSSARY-UI（清詞工具）／IMG-FILTER 各屬另案不在本檔重寫 |

### §99.2 Revision 歷程

- v2 (2026-07-19)：review 定稿——§9 六 OQ 全數拍板採納推薦（Q1 早退確定為缺陷廢除／Q2 settings 翻轉 true／Q3 6000／Q4 附論併案純加法／Q5 專名收斂界定／Q6 三路分開落地）；§3 補早退原始設計動因（三路 docstring「缺詞 extract_terms」＝域級成本快取閘門、假設「域有詞＝庫已建成」忽略長尾 → 優化過度缺陷、Q1 判定依據）
- v1 (2026-07-19)：初版——依 design spec F2/F3/F1 定案（v4 選 1、與 PIPE-INGEST 前後腳）立案；§2 八規格項（build_termmap 五步／三路收斂／注入鏈零改／括號收斂／術語硬驗收／GLOSSARY-ON／連貫附論／已知限制）；§2.5 五候選留痕（B-E 否決）；§4 凍結五條 handoff（term_key 三方同函式／定案表單向寫入／summary_key 同基準）；§9 六 OQ（Q1 飛輪早退判缺陷待拍板）
