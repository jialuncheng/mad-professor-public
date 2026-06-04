# TRANSLATOR 雙模式原子翻譯器 plan

> 本計畫為 PIPE 大改版的三大共用真理源之一：**Translator 雙模式原子翻譯器**的設計與規格。計畫建立獨立且高內聚的 `Translator` 模組，提供 `NORMAL`（降本提速）與 `DEEP_THINK`（品質優先）雙模式，接收 `InjectionContext` 以強注入標準 LCC 領域、凍結 Glossary 術語庫、前文 Sliding Window 等多維脈絡，為五條策略管線提供統一且無分歧的翻譯底座。本計畫為純規格定義，不含 commit 建議。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：舊系統的翻譯邏輯與提示詞拼接硬編碼於 `TranslateProcessor` 中。在 PipelineCore 重構為四 Phase 後，舊的單體處理器將被廢除；且未來的 `AcademicPipeline`、`BookPipeline` 與 `LiteDocPipeline` 等管線皆急需統一的翻譯接口。如果各管線自行實現 LLM 呼叫與提示詞拼接，會導致雙模式路由不一致、術語約束塊拼接分歧、以及 LCC 收斂信號無法正確消費等問題。
- **解法**：建立獨立的 `Translator` 原子翻譯模組：
  1. **型別安全上下文**：於 `processor/translator.py` 定義並導出 `InjectionContext` 與 `TranslateMode`（含 lcc, glossary, zh_summary, preceding, constraints, domain_name, doc_type 等欄位，對齊 PIPE-SPEC §1.2.3 v3），統一 Phase 2 凍結產物的載入契約。**不混入 `pipelines/contracts.py`**（後者純為四份 Phase 交接合約、物理隔離 doc_type 業務細節，維持 PIPE-CORE 範疇潔癖）。
  2. **提示詞與約束拼接**：統一從 `prompt/translate/` 讀取提示詞，並根據文體（`doc_type`）自動附屬風格提示、LCC 領域說明（讀 `ctx.domain_name`、零 DB），以及 `GlobalGlossary` 術語強約束區塊。
  3. **雙模式路由**：提供 `NORMAL`（`TRANSLATE_MODEL`，降本提速）與 `DEEP_THINK`（`TRANSLATE_MODEL` + `thinking_config(thinking_budget=LLM_THINKING_BUDGET)`，品質優先；對齊 `model_recommendations.md` §1.1）雙模式路由，全域並發受 `LLMClient._api_semaphore` 限制，保障線程安全。
- **影響**：新建 `processor/translator.py` 模組，於其內定義並導出 `InjectionContext`（含 `domain_name`/`doc_type` 兩擴充欄位，**已同步 PIPE-SPEC §1.2.3 v3**）與 `TranslateMode`（**不放 `pipelines/contracts.py`**，保該檔純四份 Phase 交接合約）；**新增 `prompt/translate/caption_translate_prompt.txt`**（圖說專屬提示詞、保留 Figure/Table 編號）。全系統環境變數新增 `LLM_THINKING_BUDGET`（思考預算、預設 0、對齊 `model_recommendations.md` §1.1）。對 `llm/client.py::chat()` 做**受控擴充**（依 SOP §1.1 注入 `thinking_config`、gated `budget>0 且 "3.5" in model`，§4 唯一例外）。本計畫 100% 向下相容（`LLM_THINKING_BUDGET=0` 時行為等同舊狀），既有單體調度與 A 軌不受任何影響。

---

## §2 目標規格

> 以下為原子翻譯器必須達到的「最終狀態」規格（What it should be），可量化檢驗。實作細節屬 tasks 階段。

### U1. InjectionContext 與 TranslateMode 合約
*   **定義並導出於 `processor/translator.py`**（非 `pipelines/contracts.py`——後者僅承載四份 Phase 交接合約、物理隔離 doc_type 業務細節）。
*   採用 Pydantic v2 `ConfigDict(frozen=True, extra="forbid")` 保持不可變性與類型安全。
*   `TranslateMode` 為 Enum，包含 `NORMAL` 與 `DEEP_THINK` 二值。
*   **公開方法簽名**（凍結、逐字對齊 PIPE-SPEC §1.2.3）：
    ```python
    Translator.translate(
        text: str,
        ctx: InjectionContext,
        mode: TranslateMode,
        text_type: str = "content",   # 'title' | 'abstract' | 'content' | 'caption'
    ) -> str
    ```
    > `text_type` 為**本次呼叫屬性**（決定底層提示詞檔與 User Prompt 格式），**獨立參數傳遞、不入 `InjectionContext`**（InjectionContext 僅承載文件級脈絡）。
*   `InjectionContext` 欄位規格：
    *   `lcc: str` — 標準 LCC 一級分類碼（必填，對齊 DOMAIN-NORM 產物）
    *   `glossary: Dict[str, str]` — 凍結最終 Glossary（必填，對齊 GLOSSARY-CORE 雙層融合產物）
    *   `zh_summary: Optional[str] = None` — 中文上下文摘要（依管線而定：全文宏觀摘要 or 逐章故事板 Storyboard，對齊 BOOK P2 產物）
    *   `preceding: Optional[str] = None` — 段落級前文參考（對齊 Sliding Window 語意）
    *   `constraints: List[str] = []` — 額外自訂約束條件
    *   `domain_name: Optional[str] = None` — **P2 預解析的 LCC 領域英文名稱**（取自 `Domains.name`，例 `"Mathematics"`／`"Electronics Engineering"`；DOMAIN-NORM 之 `Domains.name` 儲存英文 LCC 名）；Translator 直接讀取注入 Style Hint，**嚴禁逐段查 DB**（見 §7 Q1 熱路徑連線浪費解法）
    *   `doc_type: Optional[str] = None` — 文件文體類型（用於自動加載對應風格提示）
    > ✅ **合約分歧已決議（baron 拍板·方案 A）**：`domain_name` 與 `doc_type` 為本計畫對 `InjectionContext` 的擴充欄位。已**同步更新 PIPE-SPEC §1.2.3**（v3）補入此二欄位，解除 `extra="forbid"` 衝突；本計畫與 PIPE-SPEC 凍結合約欄位逐字一致。

### U2. 提示詞與約束動態注入 (Prompt Engine)
*   **系統提示詞 (System Prompt)** 拼接規則：
    1.  **底層提示詞載入**：
        *   若 `text_type == "title"`，載入 `prompt/translate/title_translate_prompt.txt`。
        *   若 `text_type == "caption"`，載入 **`prompt/translate/caption_translate_prompt.txt`**（本計畫新增交付物；強制 LLM 保留 `Figure`／`Table` 圖表編號與標點格式，防編號被誤翻或丟失）。
        *   其餘 `text_type` 情況（`content`／`abstract`），載入 `prompt/translate/content_translate_prompt.txt`。
    2.  **文體風格暗示 (Style Hints)**：根據 `ctx.doc_type`（未提供時預設為 `academic`），在系統提示詞尾部追加標準風格提示：
        *   `academic` ➜ `文件為學術論文，請使用正式學術用語，保留英文專有名詞與縮寫。`
        *   `book` ➜ `文件為書籍，請使用流暢自然的書面語，保留專有名詞。`
        *   `technical` ➜ `文件為技術文件，請使用精確的技術術語，保留英文技術詞彙。`
        *   `slides` ➜ `文件為簡報投影片，請保持簡潔的條列式風格，勿過度詮釋。`
        *   `news` ➜ `文件為新聞文章，請使用流暢自然的新聞文體，不要過於學術化。`
        *   `web` ➜ `文件為網頁文章，請使用自然口語化的繁體中文。`
        *   `resume` ➜ `文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文。`
    3.  **LCC 領域名稱注入**：當 `LLM_USE_GLOSSARY_ALIGN == True` 時，**直接讀取 `ctx.domain_name`**——**Translator 本身零 DB 查詢、零 Session 開關**（見 §7 Q1）。
        > **載體鏈（消除斷層）**：P2 一次性唯讀 `session.get(Domains, lcc)` 解析 LCC 領域英文名（`Domains.name`）→ 物理封存於 **`GlossaryReadySpec.domain_name`**（P2→P3 凍結合約，PIPE-SPEC §1.1 ②）→ P3 讀此欄位、複製進每次 `InjectionContext.domain_name` → Translator 直讀。**P3 與 Translator 全程零 DB**。
        *   `ctx.domain_name` 非空 → 系統提示詞尾部追加：`\n\n本文件主題領域：{ctx.domain_name}，請以該領域標準術語翻譯。`（注入英文 LCC 名，LLM 可理解並完成中文術語約束）。
        *   `ctx.domain_name` 為空（上游未解析或無對應領域）→ fallback 直接使用 `ctx.lcc` 代碼字串充當領域名注入。
        *   *註：`lcc→name` 的一次性解析（唯讀 `session.get(Domains, lcc)`）職責屬上游消費管線（P2），不在 Translator 範疇內；Translator 維持純函式、無 DB 耦合。*
    4.  **Glossary 術語強約束區塊**：當 `ctx.glossary` 非空且 `LLM_USE_GLOSSARY_ALIGN == True` 時，在系統提示詞尾部追加：
        ```text
        \n\n【術語強約束 System constraint】以下專有名詞譯法不可違背，翻譯時必須與論文譯本完全一致
        （大小寫不敏感：正文出現相同單詞時，無論其原文大小寫，均強制套用該對應譯法）：
        - {original_term} → {translation}
        ```
        *   *註：注入的原文術語使用 `ctx.glossary` 的**正規化小寫 term_key**（對齊 `GlobalGlossary.term_key` 以簡化查庫）。為防小寫 Constraint 對大寫開頭專名漏配，於**此動態組裝的約束塊內**明加「大小寫不敏感套用」指令——**置於約束塊（執行期拼接文字）而非既有靜態 `content_translate_prompt.txt`，以遵守 §4 不可動清單**。如需保真大小寫，另須上游 `query_cascade` 改回傳 `original_term`（屬 GLOSSARY-CORE 範疇）。*
    5.  **額外約束注入**：當 `ctx.constraints` 非空時，在系統提示詞尾部追加每一項規則，格式為：
        ```text
        \n\n【額外譯文約束】：
        - {constraint_item}
        ```
        *   *註：人名不翻規則等**文字級約束**在此注入；`References skip` 等**結構性跳過**屬 Pipeline 層 `skip_translation` 機制處理（該段 0 API、Translator 根本不被呼叫），Translator 本身僅做文字注入、不經手結構跳過。*
*   **用戶提示詞 (User Prompt)** 拼接規則：
    *   `text_type == "title"` ➜ `f"需要翻譯的標題:\n{text}\n\n直接輸出："`
    *   `text_type == "abstract"` ➜ `f"需要翻譯的內容:\n{text}\n\n直接輸出："`
    *   `ctx.zh_summary` 存在時 ➜ `f"摘要翻譯參考:\n{zh_summary}\n\n需要翻譯內容:\n{text}\n\n直接輸出："`
    *   `ctx.preceding` 存在時 ➜ `f"前文翻譯參考:\n{preceding}\n\n需要翻譯內容:\n{text}\n\n直接輸出："`
    *   其餘無參考情況 ➜ `f"需要翻譯的內容:\n{text}\n\n直接輸出："`

### U3. 雙模式翻譯路由 (Translate Modes & Env Config)

> **權威依據**：模型選型與 Dynamic Thinking 落地方式**全面對齊 `sop/model_recommendations.md` §1.1**（含其 TIP 之 `LLM_THINKING_BUDGET` env + `thinking_config` 代碼範例）。標準思維模式＝**`gemini-3.5-flash` + `thinking_config(thinking_budget=N)`**，**非**獨立「-thinking」模型名稱路由（baron 拍板·路 A）。

*   **`NORMAL` 模式**：
    *   使用 `settings.TRANSLATE_MODEL`（依 SOP §1.1 推薦預設對齊 `gemini-3.5-flash`、env 可覆寫）。
    *   `thinking_budget=0`（不啟用思考）、降本提速，用於大量正文段落。
*   **`DEEP_THINK` 模式**：
    *   使用同一 `settings.TRANSLATE_MODEL`（`gemini-3.5-flash`）+ **啟用 `thinking_config(thinking_budget=settings.LLM_THINKING_BUDGET)`**（品質優先），用於標題、大綱與摘要翻譯。
    *   新增環境變數 `LLM_THINKING_BUDGET`（預設 `0`＝關閉；> 0 時啟用思考、對齊 SOP §1.1）。
    *   *廢棄 v1 的 `TRANSLATE_DEEP_THINK_MODEL=gemini-2.0-flash-thinking` 獨立模型名稱方案*（SDK 已支援 `thinking_config`、且 SOP 規範以 budget 控制思考；理由見 §7 Q2）。
    > ⚠️ **思考退化警告**：由於 `llm/client.py` 設有 `"3.5" in model` 的硬性閘門，`DEEP_THINK` 僅在 `TRANSLATE_MODEL` 為思考支援世代模型時生效。本計畫實施時，**建議同步將 `settings.py` 的 `TRANSLATE_MODEL` 預設值改為 `gemini-3.5-flash`（對齊 SOP）**；否則在預設狀態（`gemini-2.0-flash`）下，`DEEP_THINK` 會因閘門不成立而**靜默退化為無思考的 `NORMAL` 模式**。（閘門前向相容性另見 §7 Q3。）
*   **全域並發安全與 client 受控擴充**：
    *   `Translator` 統一呼叫 `LLMClient.get_instance().chat(...)`，底層自動受 `LLMClient._api_semaphore`（`LLM_MAX_CONCURRENT`）線程安全保護與流控。
    *   啟用 thinking 需對 `llm/client.py::chat()` 的 `GenerateContentConfig` 建構做**受控擴充**：依 SOP §1.1 範例，僅當 `LLM_THINKING_BUDGET > 0 且 "3.5" in model` 時注入 `thinking_config=types.ThinkingConfig(thinking_budget=...)`；**此為對 §4 不可動清單 `llm/client.py` 的唯一例外**（明確界定範圍、見 §4 註解）。

### U4. 多行重分行容錯 (Formatting Fallback)
*   為防止 LLM 翻譯多行內容時丟失換行結構，保留並整合 `TranslateProcessor` 的分行兜底邏輯：
    *   當原始 `text` 拆分行數 `len(original_lines) > 1`，且翻譯結果行數少於原始行數時，使用正則表達式強制按句號重新分行（`re.sub(r'([。！？])\s*', r'\1\n', translated).strip()`），確保前後行數結構對稱。

---

## §3 現況與證據

現有專案中，與原子翻譯及提示詞拼接相關的邏輯位置盤點如下：

- **`processor/translate_processor.py`**：
  - `translate_text L208-296`：包含目前的提示詞載入、文體暗示的硬編碼、LLM 客戶端調用、以及多行分行容錯。這些邏輯需完全解耦至 `Translator`。
- **`processor/translator.py`（新建）**：
  - 於此定義 `InjectionContext` 與 `TranslateMode` 的 Pydantic 模型（**不放 `pipelines/contracts.py`**，避免違反該檔「不含 doc_type 業務細節」docstring 與「四份 Phase 合約」範疇）。
- **`pipelines/contracts.py`**：
  - 目前定義四份 Phase 合約（`IngestionMetadataSpec` 等）；**本計畫僅補 `GlossaryReadySpec` 一欄位、不新增 InjectionContext/TranslateMode**。
  - **`GlossaryReadySpec` 補欄位**：現有 `{abstract, lcc, glossary, translated_abstract, chapter_summaries}` 缺 `domain_name`，須補 `domain_name: Optional[str] = None`（對齊 PIPE-SPEC §1.1 ② v3），作為 P2→P3 領域英文名（`Domains.name`）的凍結載體，消除 domain_name 傳遞斷層（否則 P3 仍須重查 DB）。
- **`settings.py`**：
  - `TRANSLATE_MODEL L7`：`TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-2.0-flash")`（依 `model_recommendations.md` §1.1 預設宜對齊 `gemini-3.5-flash`）。需新增 `LLM_THINKING_BUDGET` 思考預算配置（預設 0）。
- **`llm/client.py`**：
  - `chat L69` 之 `GenerateContentConfig` 建構（L78-80：僅 `temperature`+`system_instruction`）：依 `model_recommendations.md` §1.1 TIP 做受控擴充，加入 `thinking_config` 注入分支。已驗 SDK 支援（`types.ThinkingConfig` 存在、`GenerateContentConfig.thinking_config` 欄位存在）。

### §3.1 grep 鋼鐵證據

```bash
# 1. 檢視目前硬編碼於 translate_processor.py 的 translate_text 方法
grep -n "def translate_text" processor/translate_processor.py
# 208:    def translate_text(self, text_type, content, previous_translation=None, use_abstract_reference=False):

# 2. 檢視目前已落地的 pipelines/contracts.py 模型
grep -n "class " pipelines/contracts.py
# 20:class IngestionMetadataSpec(BaseModel):
# 38:class GlossaryReadySpec(BaseModel):
# 54:class BilingualMarkdownSpec(BaseModel):
# 69:class RagDbSpec(BaseModel):
```

---

## §4 不可動清單

明確劃定修改邊界，防止邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **A 軌舊單體 Pipeline（`pipeline_core.py` 既有 11-stage 邏輯）**：影子期內全程保持可運行，在 Flip 前嚴禁刪除或更動。
- [ ] **`llm/client.py` 內 `_api_semaphore` 全域並發鎖與 `llm/retry.py` 重試機制**：直接複用，嚴禁改動。
  > ⚠️ **唯一受控例外（baron 拍板·路 A）**：依 `model_recommendations.md` §1.1 TIP，准許對 `chat()` 的 `GenerateContentConfig` 建構**新增** `thinking_config` 注入分支（gated `LLM_THINKING_BUDGET > 0 且 "3.5" in model`）。範圍嚴格限此一分支；`_api_semaphore`／`retry`／既有 `temperature`+`system_instruction` 路徑與並發語意一律不動。
- [ ] **`models.py` 既有 Schema 與 `Domains` 表結構**：本計畫不增加或變更 DB 欄位（Translator 純函式、零 DB 耦合；`lcc→name` 解析屬上游 P2 職責）。
- [ ] **`prompt/translate/` 底下既有提示詞檔案內容**（`title_translate_prompt.txt`／`content_translate_prompt.txt`）：本計畫僅負責讀取與拼接，不得更動文字檔本身。
  > 註：本計畫**新增**一份 `prompt/translate/caption_translate_prompt.txt`（圖說專屬提示詞，屬交付物、非既有檔修改），不在本不可動範圍。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 專案進度賽制管控框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| PipelineCore 大改版（三大共用真理源 U8／合約對齊） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md §2 U8` |
| 凍結接口合約／Translator 雙模式規格 | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md §1.2.3` |
| 三層解耦調度骨架（合約導出路徑） | `.claude-logs/plans/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md` |
| 領域標準化對齊器（已落地） | `.claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md` |
| 中央領域術語庫（已落地） | `.claude-logs/plans/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md` |
| **模型選型與 Dynamic Thinking 落地規範（U3 權威源）** | `.claude-logs/sop/model_recommendations.md §1.1`（`gemini-3.5-flash` + `LLM_THINKING_BUDGET`/`thinking_config` 範例） |
| 資料庫唯讀查詢／極短交易語意（§7 Q1 依據） | `.claude-logs/sop/2026-05-23_database_SOP_手冊.md 原則 2/3` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**（防 Regression 底線）：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**（`tests/test_translator.py`）：
  *   `test_translator_normal_mode`：注入 Mock LLM，驗證 `NORMAL` 模式路由到 `TRANSLATE_MODEL` 且 `thinking_budget=0`（不啟用思考）。
  *   `test_translator_deep_think_mode`：驗證 `DEEP_THINK` 模式使用 `TRANSLATE_MODEL`（`gemini-3.5-flash`）並注入 `thinking_config(thinking_budget=LLM_THINKING_BUDGET)`（mock client，斷言 config 含 thinking_config 且 budget>0）。**測試必須顯式設定 `LLM_THINKING_BUDGET=2048`（>0）並 mock 含 "3.5" 的模型名**，否則 gating（`budget>0 且 "3.5" in model`）不成立、`thinking_config` 不注入而使斷言失效（即 DEEP_THINK 退化 NORMAL，見 §2 U3 思考退化警告）。
  *   `test_translator_style_hints`：依序傳入不同的 `ctx.doc_type`，斷言 System Prompt 尾部附加了正確的文體風格提示。
  *   `test_translator_prompt_file_routing`：斷言 `text_type` 路由正確載入底層提示詞檔——`title`→`title_translate_prompt.txt`、`caption`→`caption_translate_prompt.txt`、`content`/`abstract`→`content_translate_prompt.txt`。
  *   `test_translator_lcc_domain_injection`：傳入 `ctx.domain_name="Electronics Engineering"`（英文 LCC 名、與 U1 例一致），驗證領域名稱被正確拼入 System Prompt；`ctx.domain_name=None` 時 fallback 用 `ctx.lcc`；**斷言 Translator 過程零 DB 查詢**（無 session/Domains 存取）。
  *   `test_translator_glossary_injection`：傳入 `glossary={"riesling": "雷司令"}`，驗證術語約束區塊被正確生成且 term_key 原樣注入；在 `LLM_USE_GLOSSARY_ALIGN=False` 時斷言約束區塊不被注入。
  *   `test_translator_formatting_fallback`：模擬原文為三行，而 Mock LLM 僅回傳單行（無換行符），驗證是否能正確按句號重新分行。
  *   `test_translator_user_prompt_references`：測試用戶提示詞拼接，驗證傳入 `zh_summary` 及 `preceding` 時是否正確生成參考區塊。

### §6.2 手動端到端（E2E）驗證流程

1.  **環境變數設定**：設定 `LLM_TRANSLATE_MODEL=gemini-3.5-flash`、`LLM_THINKING_BUDGET=2048`（啟用思考）與 `LLM_USE_GLOSSARY_ALIGN=true`。
2.  **單元測試執行**：執行 `pytest tests/test_translator.py -v`，確保 8 項單元測試全綠通過。
3.  **既有測試回歸**：執行 `pytest tests/ -v`，確保既有單元測試（包含 `test_glossary_core.py` 與 `test_domain_normalizer.py`）無 Regression。

---

## §7 Open Questions

| 開放問題 | 決議（baron 拍板） | 理由 |
|---|---|---|
| **LCC 領域名稱查詢是否會對 SQLite 交易造成鎖定衝突？並避免熱路徑連線浪費** | **✅ 已決議：`lcc→name` 解析移出 Translator 熱路徑——由上游 P2 一次性唯讀 `session.get(Domains, lcc)` 解析，置入 `InjectionContext.domain_name`，Translator 直讀、零 DB 查詢** | (1) 鎖定：唯讀 `session.get` 不開交易、WAL 下讀寫不互斥、`database_SOP` 原則 2/3 僅約束寫入，無鎖風險（對齊落地 `domain_normalizer._cache_lookup`）；(2) 效能：BookPipeline P3 逐段 × 並行章節若每段查 DB＝數千次冗餘 SELECT/Session 開關，故解析下放 P2 一次完成、P3 純記憶體讀。 |
| **DEEP_THINK 模式應傳 thinking budget 還是模型名稱路由？** | **✅ 已決議（路 A、對齊 SOP）：`gemini-3.5-flash` + `thinking_config(thinking_budget=LLM_THINKING_BUDGET)`** | (1) `model_recommendations.md` §1.1 為模型配置權威源、其 TIP 明訂以 `LLM_THINKING_BUDGET`+`thinking_config` 啟用思考；(2) **SDK 確實支援**（實測 `types.ThinkingConfig` 存在、`GenerateContentConfig.thinking_config` 欄位存在）——v1「SDK 不支援」之陳述為誤、已更正；(3) 純模型名稱路由（`gemini-2.0-flash-thinking`）屬實驗/棄用世系且對 3.5+ 系列無法經模型名啟用思考；(4) 代價＝對 `llm/client.py::chat()` 做受控擴充（§4 唯一例外、依 SOP §1.1 範例 gated `budget>0 且 "3.5" in model`）。 |
| **thinking 啟用判定 `"3.5" in model` 是否前向相容？**（tasks 實作注意） | **⚠️ 註記（非規格變更）：tasks 實作 `llm/client.py` 時勿硬編碼 `"3.5"`、宜前向相容** | `"3.5" in model` 為 SOP §1.1 過渡期硬編碼，**會排除現行 GA 思考模型 `gemini-2.5-flash`/`gemini-2.5-pro`**（SOP 矩陣自身亦把 `LLM_DOMAIN_MODEL` 推薦為 `2.5-pro`）**與未來 `4.0-*`**。plan 規格層維持對齊 SOP 描述即可；**tasks 代碼實作宜改為前向相容判定**——正向白名單（如 `2.5`/`3.x`/`4.x` 思考世代集合 env 化）或 `try/except` 捕捉「不支援 thinking」API 錯誤後自動降級 fallback。參考 Google 官方思考文件 `https://ai.google.dev/gemini-api/docs/thinking`。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 TRANSLATOR 雙模式原子翻譯器的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 TRANSLATOR tasks / 執行報告；`TRANSLATE-BOOK` plan |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，合約與管線調度唯一源在 PIPE-SPEC；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v10 (2026-06-04)：**第八輪交叉比對四項處置（baron 拍板·直接落地）**——(一.1) 同步更新 **PIPE-SPEC §1.2.3 L109** `domain_name` 描述「中文名」→「英文名（=`Domains.name`）」，消除 PIPE-SPEC 內部 §1.2.3 vs §1.1② 矛盾。(一.2) 同步更新 **PIPE master v10** §2 U8（L70）與 §8.4 TRANSLATOR 列（L242）的 `translate()` snippet 簽名補 `text_type="content"` + `InjectionContext` 欄位補 `domain_name`/`doc_type`。(二.1) U2.4 Glossary 約束塊**動態組裝文字**內明加「大小寫不敏感套用」指令——**置於執行期約束塊而非既有靜態 `content_translate_prompt.txt`，以遵守 §4 不可動清單**（避開 baron 原建議落點與 §4 之衝突）。(二.2) §6 `test_translator_deep_think_mode` 補註：測試須顯式設 `LLM_THINKING_BUDGET=2048` 並 mock 含 "3.5" 模型名，否則 gating 不成立致斷言失效。(一.3 其他 plan 對 PIPE master 檔名指標落後 v1/v6/v7/v8 屬非阻塞、deferred 後續批次。)
- v9 (2026-06-04)：**第七輪計數對齊**——§6.2 單元測試計數 `7 項→8 項`（補 v8 新增 `test_translator_prompt_file_routing` 後的計數漏改）；全文硬編碼計數複查確認無其他殘留（「四份 Phase 合約」等為正確結構常數）。純文字計數修正、PIPE-SPEC 未動。
- v8 (2026-06-04)：**第六輪交叉比對·caption 專屬提示詞（baron 拍板·直接落地）**——新增交付物 `prompt/translate/caption_translate_prompt.txt`（圖說專屬提示詞，強制保留 `Figure`／`Table` 圖表編號與標點、防誤翻丟失）；§2 U2.1 載入規則補 `text_type == "caption"` 分支、§1 影響補列新檔、§4 不可動釐清（既有 prompt 檔不動／新增 caption 檔屬交付物）、§6 新增 `test_translator_prompt_file_routing`（title/caption/content 路由斷言）。另：標題（title）走 `DEEP_THINK` 經 baron 評估**維持不改**（標題短 Token 低、譯名敏感、高性價比）。本輪僅改 TRANSLATOR plan、PIPE-SPEC 未動。
- v7 (2026-06-04)：**第五輪嚴格交叉比對兩缺口處置（baron 拍板·直接落地）**——(G 殘留) §6.1 `test_translator_lcc_domain_injection` 測試範例 `ctx.domain_name` 由中文「半導體晶片」改英文「Electronics Engineering」（與 U1「英文 LCC 名」正名一致，補第三輪 Finding B 漏改）。(H 明示) U3 `DEEP_THINK` 段下補「思考退化警告」——明示 `"3.5" in model` 硬閘門使 `DEEP_THINK` 僅在 `TRANSLATE_MODEL` 為思考世代模型時生效，建議實施時同步將 `settings.TRANSLATE_MODEL` 預設改 `gemini-3.5-flash`，否則靜默退化為 `NORMAL`。本輪僅改 TRANSLATOR plan、PIPE-SPEC 未動。
- v6 (2026-06-04)：**第四輪嚴格交叉比對三缺口處置（baron 拍板·直接落地）**——(D 設計缺口) U2 補「步驟 5 額外約束注入」——`ctx.constraints` 非空時逐項注入系統提示詞【額外譯文約束】（人名不翻等文字級約束；References skip 屬 Pipeline 層 `skip_translation`、Translator 不經手），消除「constraints 欄位宣告但 U2 從未消費」死欄位。(F 落點) `InjectionContext`/`TranslateMode` 改**定義於 `processor/translator.py`**、**不放 `pipelines/contracts.py`**（§1/§2 U1/§3 同步）——避免違反 contracts.py「不含 doc_type 業務細節」docstring 與「四份 Phase 合約」範疇；contracts.py 本計畫僅補 `GlossaryReadySpec.domain_name` 一欄位。(E 措辭) `zh_summary` 描述統一為「中文上下文摘要（依管線：全文宏觀 or 逐章故事板）」，PIPE-SPEC §1.2.3 + plan U1 同步。
- v5 (2026-06-04)：**第三輪嚴格交叉比對三缺口處置（baron 拍板·直接落地）**——(A 關鍵) `translate()` 簽名補 `text_type: str = "content"`（'title'|'abstract'|'content'|'caption'，獨立參數、不入 InjectionContext），消除「U2 依賴 text_type 但 PIPE-SPEC §1.2.3 簽名無此參數」之硬不一致；**同步更新 PIPE-SPEC §1.2.3 簽名 v3**；U1 補公開方法簽名。(B 語意) `domain_name` 正名——DOMAIN-NORM `Domains.name` 實為**英文 LCC 名**（`"Mathematics"` 等），plan 內「領域中文名」字眼全面正名為「LCC 領域英文名稱」（U1 欄位／U2.3 載體鏈與注入說明），注入英文領域名 LLM 可理解、功能無損。(C 細節) U2.4 術語約束註解更正——注入的是 `ctx.glossary` 之**正規化小寫 term_key**（非「原始 term_key」），LLM 大小寫不敏感、功能無影響。
- v4 (2026-06-04)：**第二輪 review 兩發現處置**——(1) **Finding 1（落地）**：補 domain_name 的 P2→P3 凍結載體——`GlossaryReadySpec` 補 `domain_name`（同步 PIPE-SPEC §1.1 ② v3 + 標註 `pipelines/contracts.py` 須補欄位），消除「P2 解析→P3 無載體仍須重查 DB」斷層；U2.3 補明載體鏈（P2→GlossaryReadySpec→P3→InjectionContext，P3 與 Translator 全程零 DB）、§3 標 contracts.py 補欄位需求。(2) **Finding 2（加註記）**：§7 新增 Open Question——`"3.5" in model` 為過渡硬編碼（已排除現行 GA `gemini-2.5-flash`/`2.5-pro` 與未來 4.0），plan 規格維持對齊 SOP、**tasks 實作宜前向相容**（正向白名單/try-except 降級），附 Google 官方思考文件連結。
- v3 (2026-06-04)：**baron 三項拍板落地**——(1) **doc_type 方案 A**：`InjectionContext` 補 `doc_type` 並**同步更新 PIPE-SPEC §1.2.3 v3**（解 `extra="forbid"` 分歧、本計畫與凍結合約欄位一致）；(2) **LCC 領域名稱熱路徑解法**：新增 `InjectionContext.domain_name`，`lcc→name` 解析下放上游 P2 一次性唯讀完成，Translator 零 DB 查詢（U2.3／§4／§6／§7 Q1 同步、PIPE-SPEC §1.2.3 補欄位）；(3) **DEEP_THINK 路 A 對齊 SOP**：廢 `gemini-2.0-flash-thinking` 獨立模型名稱方案，改 `gemini-3.5-flash` + `LLM_THINKING_BUDGET`/`thinking_config`（U3／§1／§3／§4／§6／§7 Q2 同步），明確引用 `model_recommendations.md` §1.1、`llm/client.py::chat()` 列為 §4 唯一受控例外、更正 v1「SDK 不支援 thinking budget」之誤；§5 規格依據新增 model_recommendations.md／database_SOP 兩引用。
- v2 (2026-06-04)：**第一輪 review 校正（非模型部分直接落地）**——(1) §3／§3.1 `translate_text` 行號對齊當前代碼庫 `L204→L208`（範圍 `L204-270→L208-296`；GLOSSARY-CORE C3 加 `import settings` 後偏移，已實地 grep 驗證）；(2) §2 U1 `InjectionContext.doc_type` 加註「合約分歧待同步」——此欄位超出 PIPE-SPEC §1.2.3 凍結合約（`extra="forbid"`），標明落地前須二擇一（更新 PIPE-SPEC §1.2.3／改 translate() 參數）。**模型相關（U3 雙模式模型選型／DEEP_THINK thinking budget／§7 Q2）暫不動，待 baron 依 model_recommendations.md SOP 拍板**（見本輪 review 模型建議）。
- v1 (2026-06-04)：初版建立，依據 PIPE-SPEC §1.2.3 規格，定義 `InjectionContext` 合約模型（U1）、提示詞與約束拼接（U2）、`NORMAL` 與 `DEEP_THINK` 雙模式路由與全系統環境變數（U3）、以及多行分行容錯（U4）。
