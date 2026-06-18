# PIPE-SECTION-BASE 共用 section 機制抽取 plan

> 將 B 軌結構化文體共用之「遞迴標題樹走訪 → 逐節點摘要 / 並行翻譯 / 排版還原 / RAG section 旁路」機制，自 `resume_pipeline` 抽成零 doc_type 耦合之共用引擎，供 litedoc / academic / technical / book 各路消費；本任務為行為等價之抽取重構，不新增功能。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：「遞迴走標題樹 → 逐節點摘要 / 並行翻譯 / 排版還原」是所有結構化文體（resume 已落地、litedoc / academic / technical / book 即將落地）的共同骨幹；現況此機制為 `resume_pipeline` 私有，且 `_normalize_paragraph_breaks` / `_translate_whole` **已被 slide_pipeline 重複實作一份**（resume + slides 兩份），litedoc 將成第三份 → 多路 copy-paste 技術債、修補需多處同步、易 drift。
- **解法**：抽出零 doc_type 耦合之共用 section 引擎（pure-function 模組、translator/llm/doc_type 由呼叫端注入），`resume_pipeline` 改為消費它並移除私有副本；**行為等價**（既有 resume 測試全綠＝鐵證、RESUME-PERF-1 C1「解耦先鎖等價」範式）。
- **影響**：新增 `pipelines/section_engine.py`（暫名）；改 `pipelines/resume_pipeline.py`（私有 helper → 呼叫共用引擎）；新增 `tests/test_section_engine.py`。**零 Schema / 零 API 簽名 / 零 final 輸出 byte 變動 / 零 A 軌變動 / 零 contracts.py 變動。** slide_pipeline 之既有重複副本本案**不收編**（見 §9 Q2）。

---

## §2 目標規格

- **U1 共用引擎模組**：新建零 doc_type 耦合、零 A 軌依賴之共用 section 引擎，內含下列共用機制（自 resume 抽出）：標題樹 DFS 走訪（`_collect_summary_targets` 範式）、批次節點摘要產出 + 翻譯（`_build_section_summaries`/`_generate_section_summaries`/`_translate_section_summaries`）、render slot 收集（`_collect_render_slots`，key=原文標題 path、level=遞迴深度）、並行翻譯 + 保序回填（RESUME-PERF-1）、按 level 排版還原（`_restore_sections_markdown`）、段落正規化（`_normalize_paragraph_breaks`）、heading 退化偵測 + 整檔 fallback（`_is_heading_degraded`/`_translate_whole`）、rag section 旁路收集（`_collect_rag_sections`，summary_key=原文標題 path）。
- **U2 resume 消費共用引擎**：`resume_pipeline` 上述機制改呼叫共用引擎、移除私有副本；其餘 resume 專屬 P1/P2 helper（`_extract_contact` / `_resolve_title` / `_detect_source_lang` / `_heal_glossary` 等攝入層）**不抽、保留私有**。
- **U3 介面參數化（多 consumer 對齊、零 schema 耦合）**：共用引擎介面接受 `doc_type` / `translator` / `InjectionContext` / `llm` 注入；route-specific 行為（STYLE_HINTS、constraints、`_is_chunk_meaningful` 門檻、meta header 欄位集）由**呼叫端傳入、引擎內不寫死任何 doc_type 字面量**。
  - **U3.1 meta header 純格式化器**：`render_meta_header` **不讀 `PipelineContext` / `raw_metadata` 任何 dict**——簽名為 `render_meta_header(title: str, items: List[Tuple[str, str]], sep: str = "：") -> str`，收**已抽好 + 已做 zh/en label 對照**的 `(Label, Value)` 清單，僅負責產 `# 標題` + 無序列表。欄位抽取與語系對照留呼叫端（resume 從 `ctx.raw_metadata` 取 phone/email、litedoc 取 date/publisher）→ 引擎對 metadata 結構完全無知（Zero Schema Coupling）。
  - **U3.2 DFS 接受子樹**：`collect_summary_targets` / 摘要產出邏輯須能接受**任意子標題樹**（非僅 root）輸入，供未來 PIPE-BOOK 以組合方式包成 rolling 摘要引擎（本案不實作 rolling、僅留介面）。
  - 介面設計依據涵蓋 resume 現狀 + litedoc 草案 + academic/technical/book 之 A 軌深結構特徵（§7）。
- **U4 接縫契約零位移**：抽取後 `section_summaries` 之 key 與 `rag_sections` 之 `summary_key` 仍＝**原文標題 path**（P2 產 / P3 帶 / P4 取同基準、RAG-ASYNC-HOTFIX-1）；抽取不得改變 key 基準。
- **U5 行為等價 + 測試**：`resume_pipeline` 既有測試（含 RAG-ASYNC-HOTFIX-1 P2→P3→P4 key-changing 整合測試）抽取後**全綠**；新增 `tests/test_section_engine.py` 直接覆蓋共用引擎。
- **U6 治理**：模組 + 改動處加 `# === [PIPE-SECTION-BASE] ===` marker；deviation 誠實列（另立 PIPE-SECTION-BASE 代號、非 INFRA-3〔INFRA-3 主題＝chunking/TextTiling 解耦、不同〕）。

<!-- === [WORKFLOW-4 C1 U4] === 選用章節：Diverse Rollout 多候選探索（StraTA §4.2 移植） -->
### §2.5 候選方案（Diverse Rollout）（選用）

> 本案為**架構級**決策（共用引擎的形態決定後續四路如何消費、難回頭），故觸發多候選探索。

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| **方案 A（選定）pure-function 模組** | `pipelines/section_engine.py` 一組純函式，translator/llm/doc_type 全由參數注入；pipeline 以**組合**呼叫（如 `section_engine.restore_sections(tiles, translator, inj, ...)`）| 難易：中（純函式好測、無繼承）/ 衝擊：小（resume 改呼叫點、介面顯式）/ 擴充：高（任何 pipeline import 即用、與 `DocumentStrategy` ABC 無菱形繼承）；**對齊既有 `rag_indexer.py` 先例（standalone 模組、零耦合、doc_type 參數化）** |
| 方案 B（否決）Mixin 類 | `SectionPipelineMixin`，pipeline 多重繼承 `DocumentStrategy + SectionPipelineMixin` | 難易：中 / 衝擊：中（改類定義）/ 擴充：中——但與 `DocumentStrategy` ABC 多重繼承增認知負荷、隱式 self 狀態依賴難測、易把 route-specific 狀態漏進共用層 |
| 方案 C（否決）Base 類 | 共用引擎做成 `DocumentStrategy` 的中間基類、各 pipeline 繼承 | 難易：高 / 衝擊：大（動繼承鏈、改 factory 註冊範式）/ 擴充：低——強耦合繼承樹、最違「最小干擾」、與既有 `@register` 扁平註冊衝突 |

- **選定理由**：方案 A 與專案既有共用真理源範式（`rag_indexer` / `domain_normalizer` / `translator` 皆 standalone 模組 + 注入）一致、可測性最高、對既有 `DocumentStrategy`/`factory` 零衝擊、route-specific 不可能滲進共用層（全靠參數）。
- **否決留痕**：B/C 之繼承耦合在 2 人 / 五路規模屬過度抽象、違 `CLAUDE.md §1.9` 與最小干擾;未來若引擎狀態複雜化再評估、但本案不採。
<!-- === [WORKFLOW-4 C1 U4 END] === -->

---

## §3 現況與證據

- **`pipelines/resume_pipeline.py`**（待抽取之共用機制，grep 實證行號）：
  - `_collect_summary_targets` L480：DFS 走標題樹收 (node_key, title, content)、`node_key = f"{path_prefix}/{title}"`（標題 path）。
  - `_build_section_summaries` L448 / `_generate_section_summaries` L507 / `_translate_section_summaries` L533 / `_node_content_text` L496 / `_parse_indexed` L579：批次節點摘要產出 + 翻譯（三安全鎖）。
  - `_collect_render_slots` L849：DFS 收翻譯 slot、title slot 記 key=原文標題 path（RAG-ASYNC-HOTFIX-1）+ `level=min(2+depth,6)`（HEADING-HOTFIX-1）。
  - `_restore_sections_markdown` L746：並行翻譯（`ThreadPoolExecutor` + 保序回填、RESUME-PERF-1）+ 按 level 還原。
  - `_collect_rag_sections` L811：建 rag_sections、`summary_key`=原文標題 path（與 P2/P4 同基準）。
  - `_translate_whole` L904 / `_t` L913 / `_is_heading_degraded` L1008 / `_flatten_sections` L1030 / `_own_text_len` L1038 / `_normalize_paragraph_breaks` L968 / `_render_meta_header` L922 / `_single_container_sections` L840。
  - **保留私有（攝入層、不抽）**：`_extract_metadata` L233 / `_build_tiles` L248 / `_resolve_title` L293 / `_detect_source_lang` L308 / `_extract_contact` L316 / `_make_summary` L427 / `_heal_glossary` L591 / `_resolve_domain_name` L608。
- **`pipelines/slide_pipeline.py`**（重複實證）：
  - `_normalize_paragraph_breaks` L431、`_translate_whole` L937——**與 resume 重複兩份**；litedoc 將成第三份。
- **consumer 對齊證據（A 軌 doc_analyzer / rag_processor / md_restore）**：
  - `technical` 不在 `FLAT_DOC_TYPES`(`doc_analyzer.py:100`) / 不在 `_SHORT_DOC_TYPES`(`rag_processor.py:16`) / 不在 `ABSTRACT_NO_DOC_TYPES`(`md_restore_processor.py:397`) → 深結構 + 有摘要 + 非短文,與 academic/book 同族 → 共用引擎須支援深層多 section + 有摘要文體。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "def _" pipelines/resume_pipeline.py    # 30 私有 helper、待抽 vs 保留分界（§3）
grep -nE "def _normalize_paragraph_breaks|def _translate_whole" pipelines/slide_pipeline.py
# → slide_pipeline.py:431 / :937（重複已存在）
grep -n "node_key = f" pipelines/resume_pipeline.py    # :491 node_key=標題 path（接縫基準）
grep -n "FLAT_DOC_TYPES = \|_SHORT_DOC_TYPES = \|ABSTRACT_NO_DOC_TYPES = " processor/*.py
# → technical 三集合皆缺席＝深結構家族
```

---

## §4 跨 Phase 接縫契約

> 本案為抽取重構、不改 Phase 邊界，但共用引擎正是 P2/P3 產 → P4 取之 handoff 機制的實作體，故接縫基準必須凍結不位移。

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| P2→P4 節點摘要 | 共用引擎 `collect_summary_targets` 產 `section_summaries`，key＝**原文標題 path** | P4 `rag_indexer._walk` 以 `summary_key` 查 | key＝原文標題 path；抽取前後 producer 寫入與 consumer 查找**為同一基準、零位移** |
| P3→P4 rag section | 共用引擎 `collect_rag_sections` 產 `ctx.rag_sections`，`summary_key`＝**原文標題 path** | P4 `rag_indexer.index` 消費 | summary_key＝原文標題 path；與 P2 section_summaries key 同基準（RAG-ASYNC-HOTFIX-1） |

填寫規範與 worked example 見 `.claude-logs/ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **抽錯抽象**（抽成 resume 形狀、後續路用不了） | 🟡 中 | 介面設計依據顯式對齊三類 consumer（§7、resume 現狀 + litedoc 草案 + academic/technical/book A 軌特徵）;route-specific 全參數化、引擎內零 doc_type 字面量;後續路若需更多＝**加法擴充**、不推翻 |
| **行為退化**（抽取改到 final 輸出 / 召回） | 🟡 中 | 行為等價硬約束:resume 既有測試（含 RAG-ASYNC-HOTFIX-1 key-changing 整合測試）全綠為鐵證;RESUME-PERF-1 C1「解耦先鎖等價」範式 |
| **scope creep 滲入 slides** | 🟢 低 | 本案**不收編** slide_pipeline 既有兩份重複（slides 有 golden + 已 ship 風險）;slides 收編留待後續、見 §9 Q2 |
| **接縫 key 位移** | 🟡 中 | §4 凍結;新增 base 層 key-changing 整合測試 + resume 既有整合測試雙鎖 |
| **book rolling 摘要需求未涵蓋** | 🟢 低 | 共用引擎提供 batch 摘要;book 滾動章節摘要屬後續加法擴充、本案不實作（§9 Q3）|

對齊 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] `pipelines/slide_pipeline.py` 全檔——本案不收編其重複副本（避免動已 ship + golden 路）。
- [ ] `pipelines/contracts.py` 四凍結合約——key 基準（原文標題 path）零變動、不新增/改欄位。
- [ ] `processor/rag_indexer.py`——P4 消費端不動（本案只改 producer 端的實作歸屬、不改 consumer）。
- [ ] `resume_pipeline` 攝入層私有 helper（`_extract_contact` / `_resolve_title` / `_detect_source_lang` / `_heal_glossary` / `_extract_metadata` / `_build_tiles` 等）——resume 專屬、不抽。
- [ ] A 軌全部（`pipeline_core.py` / `processor/*` 非本案新增者 / `web_server.py`）——零改動。
- [ ] resume `final_zh` / `final_en` 輸出 byte——抽取後須等價。
- [ ] 既有 `DocumentStrategy` ABC / `factory` 註冊範式——方案 A 不動繼承鏈。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| 跨 Phase 接縫契約唯一源 | `.claude-logs/ref/WORKFLOW_SOP.md §7` |
| 專案進度框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| consumer ① resume 現狀 | `pipelines/resume_pipeline.py`（§3 grep 行號）|
| consumer ② litedoc 草案 | 本對話設計收斂（news/web/unknown、短扁平、MinerU 文字、raw_metadata 旁路）|
| consumer ③ academic/technical/book 特徵 | A 軌 `doc_analyzer.py:100` / `rag_processor.py:16` / `md_restore_processor.py:397`（technical 深結構家族佐證）|
| 行為等價重構範式 | RESUME-PERF-1 C1（解耦先鎖等價）|
| 接縫 key 基準 | RAG-ASYNC-HOTFIX-1（原文標題 path、P2 產/P3 帶/P4 取同基準）|

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行（行為等價鐵證）**：
  ```bash
  pytest tests/test_resume_pipeline.py -v   # 抽取後全綠＝行為等價（含 key-changing 整合測試）
  pytest tests/ -q                          # 全套件維持基線（640 passed）
  ```
- **預計新增**：`tests/test_section_engine.py` 直接覆蓋共用引擎——標題樹 DFS 走訪 / 批次摘要保序 / 並行翻譯 byte 等拍保序 + 限流 + 單 unit 失敗退原文 / heading 退化 fallback / `summary_key`＝原文標題 path / **base 層 P2→P3→P4 key-changing 整合測試**（真翻譯改 key、斷言下游正確消費、堵 RAG-ASYNC-HOTFIX-1 類退化）。

### §8.2 手動端到端（E2E）驗證流程

1. baron 影子重傳一份既有履歷 → final_zh / final_en 與抽取前**逐 byte 一致**（行為等價）。
2. RAG 召回分數分布、chunks 量級與抽取前一致（section_summaries / rag_sections key 未位移）。
3. （無需 golden 重捕——final byte 不變;為 B 軌、capture 走 A 軌不受影響。）

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 🟢 共用引擎形態（module / mixin / base）? | **方案 A：pure-function 模組**（§2.5） | 對齊 rag_indexer 等既有共用真理源範式、可測性最高、對 DocumentStrategy/factory 零衝擊、route-specific 不可能滲入 |
| **Q2** 🟢 是否順手收編 slide_pipeline 的 2 份重複（`_normalize_paragraph_breaks`/`_translate_whole`）? | **本案不收、留後續** | slides 已 ship + 有 golden + 近期 HOTFIX-5/6 多輪微調;本案保「行為等價 + 最小干擾」、以 resume 首發驗證;slides+litedoc 收編待引擎穩定後另立小任務 |
| **Q3** 🟢 book 的 rolling 章節摘要需求是否本案實作? | **不實作、但 DFS 接受子樹輸入留擴充**（U3.2） | 本案 consumer 為 resume/litedoc（皆 batch）;DFS 可吃任意子標題樹 → PIPE-BOOK 未來組合包成 rolling、不推翻 |
| **Q4** 🟢 `_render_meta_header`（讀 raw_metadata）納入共用還是留 resume? | **納入共用、且銳化為純格式化器**（U3.1）：簽名收 `(Label, Value)` tuples、引擎零讀 `raw_metadata`、呼叫端先抽欄 + zh/en label 對照再傳入 | 各文體欄位/語系差異極大;純格式化器使引擎對 metadata 結構完全無知（Zero Schema Coupling）、徹底貫徹方案 A「route-specific 不滲共用層」 |
| **Q5** 🟢 共用模組落點 / 命名? | **`pipelines/section_engine.py`** | 與 `pipelines/` 其他模組同層;名稱表「section 機制引擎」、區別 `rag_indexer`（P4 索引）|
| **Q6** 🟢 §7.2 整合測試:既有 resume key-changing 整合測試是否即足夠? | **既有 resume 綠 + base 層另寫獨立 key-changing 測試（雙鎖）** | 抽取後 resume 整合測試綠證「resume 路徑不退化」;base 層獨立測試（Mock Translator 改 key）證「引擎本身對任意 doc_type 不位移 key」、為後續四路鋪保護網 |

> **§9 狀態**：六 Open Questions 經 baron review 全 🟢 定案（Q4 銳化為純格式化器〔U3.1〕、Q3 補 DFS 子樹輸入〔U3.2〕）→ 進入可拆 tasks 狀態。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SECTION-BASE 共用 section 機制抽取之目標規格，作為 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查 + tasks 拆分引用;Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-SECTION-BASE tasks / 執行報告;litedoc plan（消費共用引擎）|
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 拍板過程;嚴禁含 commit 拆分（屬 tasks 階段）|
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成、經 baron 同意歸檔至 archive/ |
| **重複防護** | 僅定義技術規格;工作目錄與流程規格引用 CLAUDE.md / WORKFLOW_SOP.md;接縫契約引用 WORKFLOW_SOP §7 |

### §99.2 Revision 歷程

- v2 (2026-06-18)：baron review 拍板、§9 六 OQ 全 🟢 定案；**Q4 銳化**——`render_meta_header` 收 `(Label, Value)` tuples、引擎零讀 raw_metadata（U3.1 Zero Schema Coupling）；**Q3 補**——DFS 接受任意子標題樹輸入供 book 未來組合 rolling（U3.2）；U3 升級為「參數化 + 零 schema 耦合」。U1-U6 結構不變、進入可拆 tasks 狀態
- v1 (2026-06-18)：初版（BE-Refactor;U1-U6;§2.5 三候選〔A pure-function 模組選定〕;§4 接縫 key 零位移;§9 六 OQ 待 baron 拍板〔Q1 形態 / Q2 slides 收編 / Q3 book rolling / Q4 meta header / Q5 命名 / Q6 §7.2 雙鎖〕;行為等價 RESUME-PERF-1 C1 範式;依據對齊三類 consumer）
