# 如何新增 doc_type

> 給工程師（含 Claude Code）：新增一個文件類型（doc_type）必須同步
> 更新 **7 個註冊點**，否則 pipeline / 前端 / AI 對話會出現對齊問題。
> 本檔列出全部需動的位置、依賴、驗證流程。
>
> <!-- === [PIPE-SYNC-4 C3 BANNER] === -->
> **⚠️ A 軌 / B 軌雙軌過渡期（PIPE 大改版）**：本檔 §2–§7 描述的「7 註冊點 + `pipeline_core.py` 硬分支」為 **A 軌（舊單體、即將絞殺）**。PIPE 大改版後新增 doc_type **應走 B 軌（`pipelines/` 策略管線插件）＝§1.4 範式**——**嚴禁**在 `pipeline_core.py` 新增硬編碼分支。詳見 **§1.4 A 軌 vs B 軌機制對比與 B 軌加 doc_type 範式**。
> <!-- === [PIPE-SYNC-4 C3 BANNER END] === -->

---

## 1. 概念

### 1.1 doc_type 是什麼
`doc_type` 是「文件處理路由」的列舉值，由使用者於上傳時從前端下拉選單
**手動選擇**（**不是** LLM 自動分類）。值在前端 dropdown 顯示中文標籤，
透過 `POST /api/papers/{id}/confirm_type` 送進後端，於 pipeline 全程經
`output_paths['_confirmed_doc_type']` 傳遞，最終寫入
`Paper.doc_type` 欄位。

### 1.2 doc_type vs domain
| 概念 | 來源 | 用途 |
|---|---|---|
| **doc_type** | 使用者選 | pipeline **處理路由**（決定走 SlidesProcessor / MinerU、是否跑 extra_info、用哪個 heading_fix / structure prompt、translate style hint）|
| **domain** | `DomainDetector` LLM 看第一頁產生 | AI **prompt 描述用**（讓 AI 知道在跟使用者討論的是什麼內容；附加到 character / explain / summary / translate prompt 結尾）|

兩者**互補不衝突**：doc_type 是路由 enum、domain 是自由文字描述。

### 1.3 既有 doc_type 的處理特點

| key | 標籤 | pdf2md | analyze prompt 集 | extra_info | translate style | 典型結構 |
|---|---|---|---|---|---|---|
| `academic` | 學術論文 | MinerU | academic | 跑（process）| 正式學術用語 | title + authors + abstract + IMRaD（Introduction/Methods/Results/Discussion）|
| `book` | 書籍 | MinerU | book | 跑（process）| 流暢書面語 | 章節層次深 |
| `technical` | 技術文件 | MinerU | technical | 跑（process）| 精確技術術語 | API/Configuration 風格章節 |
| `slides` | 簡報 | **SlidesProcessor**（Vision）| slides | **skip**（summary only）| 簡潔條列 | 頁對頁、無 abstract、扁平 |
| `web` | 網頁存檔 | MinerU | web | **skip** | 自然口語化 | 文章標題 + 內文 |
| `news` | 新聞文章 | MinerU | news | **skip** | 新聞文體 | 標題 + byline + 段落 |
| `resume` | 履歷 | MinerU | (Phase 1 reuse academic) | **skip** | 正式商務中文 | 候選人姓名 + Experience/Education/Skills，無 abstract |

---

<!-- === [PIPE-SYNC-4 C3 D9 START] === litedoc + section_engine 落地後回灌 B 軌範式 -->
## 1.4 A 軌 vs B 軌機制對比與 B 軌加 doc_type 範式（PIPE 五路）

> PIPE 大改版以「策略管線（DocumentStrategy 插件）」取代「`pipeline_core.py` 巨型硬分支」。
> 現況：resume／slides／litedoc 三路已落地 B 軌（`pipelines/*_pipeline.py`）。新增 doc_type **走 B 軌**。

### 1.4.1 A 軌 vs B 軌機制對比

| 維度 | A 軌（舊單體、即將絞殺）| B 軌（PIPE 策略管線）|
|---|---|---|
| 註冊方式 | §2 七處硬分支 + `pipeline_core.py` if/elif `doc_type==` | `@PipelineFactory.register('xxx')` 裝飾器**插件式**、零硬分支 |
| 處理邏輯 | `pipeline_core.py` / `processor/*` 內聯 | `pipelines/xxx_pipeline.py` 四 Phase 策略類 |
| 共用邏輯 | 各路複製貼上（LCC/術語/翻譯/section 各自一份）| **消費共用真理源家族**（零造輪）|
| metadata | 寫死欄位 | `PipelineContext.raw_metadata` 旁路欄（三欄 dict）|
| 落地驗證 | 手動 E2E | §7.2 key-changing 整合測試（Checkout 必驗）|

> **🚫 鐵律**：PIPE 大改版後新增 doc_type **嚴禁**在 `pipeline_core.py` 新增 `doc_type==` 硬分支（A 軌即將整路絞殺）。下游（academic／book／technical）一律走 B 軌。

### 1.4.2 B 軌加 doc_type 五步範式

1. **裝飾器註冊**：`pipelines/xxx_pipeline.py` 建 `class XxxPipeline(DocumentStrategy)`，以 `@PipelineFactory.register('xxx')` 註冊（可堆疊多 key，如 litedoc `@register('litedoc')/@register('news')/@register('web')`）；設 `rag_char_threshold`（深結構 ≥10、扁平短文如 resume/slides ≥3）。
2. **import 觸發**：在 `pipelines/__init__.py` 補 `from pipelines import xxx_pipeline`——**觸發裝飾器註冊**（漏 import → `get_strategy('xxx')` 回 NullStrategy、P1 拋 NotImplementedError；PIPE-RESUME C7-hotfix 教訓）。
3. **四 Phase 消費共用真理源家族**（零造輪）：
   - **P1 Ingestion**：MinerU（文字攝入）或 Vision（slides 逐頁），寫 `IngestionMetadataSpec` + 原始 meta 走 `raw_metadata` 旁路；DocAnalyzer 呼叫端**安全映射**（見 §1.4.3）。
   - **P2 Glossary & Context**：`DomainNormalizer.normalize_to_lcc` + `GlossaryManager` 級聯自癒 + `section_engine.build_section_summaries`（key＝原文標題 path）→ `GlossaryReadySpec`；LLM 全在交易外。
   - **P3 Translation & Restore**：`Translator`（NORMAL/DEEP_THINK）+ `section_engine`（`collect_render_slots`／`restore_sections_markdown`／`render_meta_header*`）；rag 旁路另以 `collect_rag_sections`（`summary_key`＝原文標題 path）寫 `ctx.rag_sections`。
   - **P4 Async RAG**：呼共用 `rag_indexer.index(...)`（四產物 FAISS＋paper_chunks＋index_meta＋rag_tree；**rag_indexer 零改**）。
4. **接縫 key 同基準**：P2 產／P3 帶（`summary_key`）／P4 取三方**同為原文標題 path**（譯後 title 僅供顯示、不作 key；對齊 WORKFLOW_SOP §7.1、PIPE-SPEC §1.1②）。
5. **§7.2 key-changing 整合測試**：建 `tests/test_xxx_pipeline.py`，含 P2→P3→P4 串接、**真 transform 改寫 title**（譯文≠原文 key）、斷言下游仍正確消費（堵 RAG-ASYNC-HOTFIX-1 類靜默退化；純 mock 同 key 兩端不認）。

> 真理源契約見 `PIPE-SPEC §1.2`（家族：DomainNormalizer §1.2.1／GLOSSARY-CORE §1.2.2／Translator §1.2.3／MetaNormalizer §1.2.4／section_engine §1.2.5）；落地範例見 `pipelines/resume_pipeline.py`／`slide_pipeline.py`／`litedoc_pipeline.py`。

### 1.4.3 U2.1 DocAnalyzer 呼叫端 doc_type 安全映射

B 軌 P1 呼叫 `DocAnalyzer` 時，**呼叫端**須對 doc_type 做安全映射，避免短扁平文體被 fallback 成 academic 深結構 prompt：

- **扁平短文家族**（litedoc 之 news／web／unknown）：映射為 `'web'`（或對應扁平 prompt 集）——`analyzer_doc_type = ctx.doc_type if ctx.doc_type in ('news','web') else 'web'`；**嚴禁裸傳 unknown 落入 academic fallback**（litedoc 為首個此映射 consumer）。
- **深結構家族**（academic／book／technical）：對齊既有 `STRUCTURE_PROMPTS`／`HEADING_FIX_PROMPTS`（§2.4／§2.5）；technical **屬深結構家族**（非扁平短文、非 litedoc 路）。
- 安全映射屬**呼叫端職責**（DocAnalyzer 本身不改）；新增扁平短文 doc_type 須在 P1 補對應映射分支。
<!-- === [PIPE-SYNC-4 C3 D9 END] === -->

---

## 2. 註冊點清單（7 處）

> **如何找**：`grep -n "=== doc_type-registry ===" <file>` 即可找到所有
> 註冊點，每處上方都有此 marker（驗證腳本依此辨識）。

### 2.1 `web_server.py` — `valid_types`
- **位置**：`confirm_type` endpoint 內（搜 `valid_types =`）
- **形式**：Python list
- **作用**：後端驗證使用者選的 doc_type 合法
- **改動範例**：
  ```python
  valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news', 'resume', '<new>']
  ```

### 2.2 `static/index.html` — `DOC_TYPES`（dropdown 選項）
- **位置**：`setupDropdown` IIFE 內（搜 `const DOC_TYPES =`）
- **形式**：JS array of `[key, label]`
- **作用**：自訂 dropdown 顯示用
- **改動範例**：
  ```js
  ['<new_key>', '<中文標籤>'],
  ```
- 排序建議：**排尾**（與後端 valid_types 同序、最低認知成本）。

### 2.3 `static/index.html` — `DOC_TYPE_LABELS`
- **位置**：業務 JS 區（搜 `const DOC_TYPE_LABELS =`）
- **形式**：JS object literal
- **作用**：`showConfirmModal` 預設標籤顯示
- **改動範例**：
  ```js
  <new_key>: '<中文標籤>',
  ```
- ⚠ 標籤文字必須與 `DOC_TYPES` 一致；驗證腳本不檢查標籤是否相同但仍應同步。

### 2.4 `processor/doc_analyzer.py` — `HEADING_FIX_PROMPTS`
- **位置**：模組頂部（搜 `HEADING_FIX_PROMPTS = {`）
- **形式**：Python dict[str, str]
- **作用**：依 doc_type 路由到對應 heading-level 修正 prompt
- **改動範例**（reuse 既有 prompt）：
  ```python
  '<new_key>': 'prompt/doc/heading_fix_academic.txt',  # reuse academic
  ```
- **改動範例**（新建專用 prompt）：
  ```python
  '<new_key>': 'prompt/doc/heading_fix_<new_key>.txt',
  ```

### 2.5 `processor/doc_analyzer.py` — `STRUCTURE_PROMPTS`
- **位置**：與 HEADING_FIX_PROMPTS 緊鄰
- **形式**：同 2.4
- **作用**：依 doc_type 路由到對應結構抽取 prompt（產出 structure.json）
- **改動範例**：同 2.4 替換檔名

### 2.6 `processor/translate_processor.py` — `style_hints`
- **位置**：`_get_prompt_for_translation` 方法內（搜 `style_hints = {`）
- **形式**：Python dict[str, str]
- **作用**：依 doc_type 附加翻譯風格提示到 translate system prompt
- **改動範例**：
  ```python
  '<new_key>': '文件為<描述>，請<風格指引>。',
  ```
- 風格指引建議：1 句話、明示「保留 X / 避免 Y」、與其他 hint 風格一致。

### 2.7 `pipeline_core.py` — `_stage_extra_info` 分流
- **位置**：`_stage_extra_info` 方法內（搜 `if doc_type in (`）
- **形式**：Python tuple
- **作用**：列在此 tuple 內的 doc_type 跳過 extra_info（不做 question /
  formula / graph 等學術衍生），只跑 `generate_document_summary`
- **改動範例**：
  ```python
  if doc_type in ('news', 'web', 'slides', 'resume', '<new_key>'):
  ```
- ⚠ 是否加入 skip 名單取決於 doc_type 的性質：
  - **無 abstract / 結構扁平 / 不適合產生學術衍生**（如 news/slides/履歷）→ 加入
  - **有結構性章節、適合學術衍生**（如 academic/book/technical）→ 不加

---

## 3. 新增 doc_type 必填問題清單

逐項確認，再開始改 code：

| 問題 | 範例 |
|---|---|
| **英文 key**（小寫、無底線、可選短連字號）| `resume`, `legal`, `recipe` |
| **中文標籤**（給使用者看，2–4 字） | `履歷`, `法律文件`, `食譜` |
| **預設排序位置** | 排尾（推薦）/ 排首 / 與相關類聚集 |
| **translate style hint**（一句話） | 「文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文」 |
| **是否走 extra_info** | 有 abstract → 走；無 abstract → 加入 skip 名單 |
| **是否要新 prompt 還是 reuse** | Phase 1 reuse academic、Phase 2 寫專用 |
| **典型結構**（給 prompt 設計參考）| 第一頁有什麼？標題層級慣例？無 abstract/references？|
| **是否需 `is_*_pdf()` 偵測** | 只有 slides 做（圖文比例可靠）；其他依使用者選擇即可 |
| **pdf2md 走哪條** | 大多走 MinerU；slides 走 SlidesProcessor（不在本檔 7 註冊點，但要先確認）|

---

## 4. prompt 設計指南

### 4.1 `heading_fix_<type>.txt`
**目的**：給 LLM 依文件類型結構，判斷每個標題行該用幾個 `#`。
**輸入變數**：`{headings}`（所有標題行的「行號: 內容」清單）
**輸出**：JSON `{"行號": #數量, ...}`，#數量範圍 1–4

**模板骨架**（仿 `heading_fix_news.txt`）：
```
以下是一份<文件類型描述> Markdown 的所有標題行（格式：行號: 標題內容）：

{headings}

請根據<文件類型描述>的結構邏輯，判斷每個標題應該使用幾個 # 符號。

規則：
- <H1 用途>用 #（一個）
- <H2 用途>用 ##（兩個）：<具體舉例，含中英雙語>
- <H3 用途>用 ###（三個）
- <H4 用途>用 ####（四個）（如有）

注意：<該類型的結構特性，如「結構扁平」「不要過度深化」>

只輸出 JSON，key 為行號（數字），value 為 # 數量（1-4）：
{"行號": 數量, ...}
```

### 4.2 `structure_<type>.txt`
**目的**：給 LLM 抽取文件「前段」的結構區段（title/authors/abstract 等）。
**輸入變數**：`{content}`（前段內容，格式「原始行號: 內容」）
**輸出**：JSON `{"structure":[{"start":行號,"end":行號,"type":"類型"},...]}`

**模板骨架**（仿 `structure_news.txt`）：
```
以下是一份<文件類型描述>的前段內容（格式：原始行號: 內容，空行已省略但行號保留）：

{content}

請分析這份<文件類型描述>的前段結構，回傳 JSON：

{
  "structure": [
    {"start": 起始行號, "end": 結束行號, "type": "類型"}
  ]
}

type 選項：
- title：<該類型主標題定義>
- authors：<作者/作者群定義；履歷可對應 contact info>
- ...（依該 doc_type 結構列）
- other：其他無法分類的內容

注意：<該類型沒有什麼結構元素，如「無 abstract / references」>

只輸出 JSON，不要任何解釋。
```

### 4.3 既有 6 個 prompt 的對比參考
| doc_type | 主標題定義 | 特殊區段 | 無此元素 |
|---|---|---|---|
| academic | 論文主標題 | abstract / publication_info / authors / intro_text / section_heading | – |
| book | 書名 | section_heading | abstract / authors |
| technical | 文件主標題 | section_heading | abstract |
| slides | 封面標題 | authors / publication_info / section_heading（每頁標題）| abstract / preface |
| news | 新聞標題 | authors（記者）/ publication_info / intro_text / section_heading | abstract / references |
| web | 文章標題 | section_heading | abstract / authors / refs |
| resume（草稿）| 候選人姓名 = title | contact / summary / section_heading / experience / education / skills | abstract / references / equations / figures |

---

## 5. 驗證流程

依序：

1. **改完 7 處註冊點**（含 marker、依本檔 §2 範例）
2. **如需新 prompt**：寫進 `prompt/doc/heading_fix_<key>.txt` 與
   `prompt/doc/structure_<key>.txt`；改 doc_analyzer 兩 dict 指向新檔
3. **跑驗證腳本**（從專案根目錄）：
   ```
   python tools/check_doc_type_registry.py
   ```
   預期看到 ✓；任一不對齊 → exit 1
4. **`py_compile`** 改過的 .py 通過
5. **`pytest tests/test_metadata_extractor.py -q`** 仍 18 passed 3 skipped
6. **端到端**（OrcStack 重啟後）：
   - 前端 dropdown 應出現新選項
   - 上傳測試文件 → 選新 doc_type → confirm → pipeline 跑完
   - DB `Paper.doc_type` 為新 key
   - AI 對話應自然稱呼新類型（character_prompt 已通用化、domain 注入會
     補回具體名詞）

---

## 6. 反例：不該做的

- ❌ 在某個註冊點漏加新 key（驗證腳本會抓出）
- ❌ 重新加一個 LLM 自動分類層（doc_type 是使用者選的）
- ❌ 為新 doc_type 改 ai_router_prompt / ai_character_prompt 措辭（這些
  已通用化，靠 domain 注入補具體名詞）
- ❌ 在 `_stage_extra_info` 為新 doc_type 加新分支（只能加入或不加入 skip
  tuple，不要再分流）
- ❌ 在 `md_processor.SLIDES_DOC_TYPES` 隨意擴充（會影響
  collecting_authors 邏輯；先實測再決定）

---

## 7. 與此檔相關的 marker / 工具

- **marker 文字**（精確）：
  - Python：`# === doc_type-registry ===`
  - JS（HTML 內）：`// === doc_type-registry ===`
  - 緊接下一行：`# 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md`
- **驗證腳本**：`tools/check_doc_type_registry.py`
- **本檔位置**：`docs/HOW_TO_ADD_DOC_TYPE.md`
