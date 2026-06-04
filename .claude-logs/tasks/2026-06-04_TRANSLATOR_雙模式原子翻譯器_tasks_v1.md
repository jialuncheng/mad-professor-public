# TRANSLATOR 雙模式原子翻譯器 — Tasks v1

> 本文件為 TRANSLATOR 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_TRANSLATOR_雙模式原子翻譯器_plan_v10.md`（U1-U4，八輪 review 定稿）產出，含 5 個 Commit（C1-C4 實作/測試 + C5 Checkout 收官）。
> **收官歸檔鐵律**：C1-C4 執行期所有 plan/tasks/執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 C5（Checkout）一次性 `mv` + `git add`** 搬移 plan_v10 + tasks + 全部 `C*_執行.md`（WORKFLOW_SOP §3）。
> **上游硬前置（已落地）**：DOMAIN-NORM（`normalize_to_lcc` + `Domains.name`）/ GLOSSARY-CORE（`GlossaryManager.query_cascade`）/ PIPE-CORE（`pipelines/contracts.py` 四合約 + `PipelineContext`）皆已收官；PIPE-SPEC §1.2.3 v3 凍結合約已含 `text_type`/`domain_name`/`doc_type`。
> **旗標複用**：`settings.LLM_USE_GLOSSARY_ALIGN`（DOMAIN-NORM 既建、預設 False）；新增 `LLM_THINKING_BUDGET`（預設 0）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 3 個 | `processor/translator.py`（Translator + InjectionContext + TranslateMode）/ `prompt/translate/caption_translate_prompt.txt`（圖說專屬提示詞）/ `tests/test_translator.py`（8 測試） |
| **修改檔案** | 2 個 | `pipelines/contracts.py`（`GlossaryReadySpec` 補 `domain_name`，先 `.bak`）/ `llm/client.py`（`chat()` 補 `thinking_config` 受控擴充分支，§4 唯一例外，先 `.bak`）；另 `settings.py`（新增 `LLM_THINKING_BUDGET` env，先 `.bak`） |
| **目錄初始化** | 0 個 | —（複用既有 `processor/` `prompt/translate/` `tests/`） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1（合約與 Context）→ C2（Prompt Engine）→ C3（Client thinking_config + 雙模式路由）→ C4（分行容錯 + 單元測試）→ C5（Checkout 收官） |
| **執行報告** | 5 個 | `baton/2026-06-04_TRANSLATOR_C1~C5_執行.md`（套用 template_execution.md、暫存 baton/） |
| **.bak 備份** | 每改既有檔前必備 | C1 改 `pipelines/contracts.py` / C3 改 `llm/client.py`+`settings.py` 前各產 `.bak`，納入該 Commit git add |
| **baton 歸檔** | 1 次 | **僅 C5 收官**一次性 `mv` plan_v10＋tasks＋C1-C5 報告至正式目錄 + `git add` |

> **修改檔案總計校正**：plan §0.5 估「修改 2 檔」係指 contracts.py + client.py 兩處核心接線；本 tasks 另含 `settings.py` 新增 env（純加常數、低風險），合計修改 3 檔，皆改前 `.bak`。

---

## §1 TL;DR（概要）

- **挑戰**：舊翻譯邏輯與提示詞拼接硬編碼於 `TranslateProcessor`；PIPE 四 Phase 重構後五路管線急需統一翻譯接口，否則雙模式路由/術語約束/LCC 消費各自為政。
- **解法**（逐 Commit、中文括號命名）：
  - **C1 — Contract & Context（合約與上下文模型）**：`processor/translator.py` 定義 `InjectionContext`（7 欄 frozen+forbid）+ `TranslateMode`（NORMAL/DEEP_THINK）；`pipelines/contracts.py` 的 `GlossaryReadySpec` 補 `domain_name`（P2→P3 載體）。
  - **C2 — Prompt Engine（提示詞與約束動態注入）**：`Translator` 系統/用戶提示詞拼接——text_type 提示詞檔路由（含 caption 新檔）+ doc_type Style Hints + LCC 領域注入（讀 ctx.domain_name 零 DB）+ Glossary 強約束塊（含大小寫不敏感指令）+ constraints 注入。
  - **C3 — Dual-Mode Routing & Thinking（雙模式路由與思考受控擴充）**：`settings.LLM_THINKING_BUDGET` + `llm/client.py::chat()` 受控加 `thinking_config` 分支（§4 唯一例外）+ Translator NORMAL/DEEP_THINK 路由。
  - **C4 — Formatting Fallback & Tests（分行容錯與單元測試）**：U4 `re.sub` 分行兜底 + `tests/test_translator.py` 8 測試。
  - **C5 — Checkout & Clean（結案收官歸檔）**：Conformance 驗收 + 一次性歸檔 plan_v10/tasks/C1-C5 報告。
- **影響範圍**：1 新翻譯模組 + 1 新 caption 提示詞 + contracts/client/settings 三處附加式接入（全旗標/budget 閘門、零既有路徑改動）+ 測試；`LLM_USE_GLOSSARY_ALIGN`=False 且 `LLM_THINKING_BUDGET`=0 時行為等同舊狀、線上 0 風險。
- **不可動清單**：見 §7。

---

## §2 現況（plan §3 grep，已實地查證）

| 檔案:行 | 現狀 | 待處理 |
|---|---|---|
| `processor/translate_processor.py:208-296` | `translate_text` 硬編碼提示詞載入/文體暗示/LLM 呼叫/分行容錯 | C1-C4 解耦至 `Translator`（translate_processor 本體不動、屬 A 軌） |
| `pipelines/contracts.py:38` | `GlossaryReadySpec{abstract,lcc,glossary,translated_abstract,chapter_summaries}` 缺 domain_name | C1 補 `domain_name: Optional[str]=None` |
| `pipelines/contracts.py` | 四份 Phase 合約（OP-1 落地）；無 InjectionContext/TranslateMode | C1 **不在此新增** InjectionContext/TranslateMode（落 processor/translator.py、避違 docstring） |
| `settings.py:7` | `TRANSLATE_MODEL`（預設 gemini-2.0-flash）；無 `LLM_THINKING_BUDGET` | C3 新增 `LLM_THINKING_BUDGET`（預設 0） |
| `llm/client.py:69` `chat()` | `GenerateContentConfig(temperature, system_instruction)`（L78-80）；無 thinking_config | C3 受控加 thinking_config 分支（gated budget>0 且 "3.5" in model） |
| `prompt/translate/{title,content}_translate_prompt.txt` | 既有（不動）；無 caption | C2 新增 `caption_translate_prompt.txt` |
| `processor/translator.py` / `tests/test_translator.py` | 不存在 | C1/C4 新建 |

---

## §3 觀察問題

### 問題 #1：翻譯邏輯硬編碼、五路管線無統一接口
- **證據**：plan §3——`translate_text L208-296` 硬編碼；PIPE 五路（Academic/Book/Slides/Resume/LiteDoc）均需統一 `Translator`。
- **影響**：需獨立 `Translator(text, ctx, mode, text_type)` 原子接口，集中提示詞拼接 + 雙模式路由。

### 問題 #2：DEEP_THINK 思考落地與熱路徑 DB 查詢
- **證據**：plan U3——SOP §1.1 規範 `thinking_config(thinking_budget)` 而非獨立思考模型；plan §7 Q1——domain_name 須 P2 解析、Translator 零 DB。
- **影響**：thinking 須對 client 受控擴充；domain_name 經 GlossaryReadySpec 載體傳遞、Translator 純函式。

---

## §4 設計方案

> 逐 Commit 落地概要；完整規格見 plan v10 §2（U1–U4）。

- **C1（U1 合約）**：`processor/translator.py` 定義 `class InjectionContext(BaseModel)`（`ConfigDict(frozen=True, extra="forbid")`，欄位 lcc/glossary/zh_summary/preceding/constraints/domain_name/doc_type，逐字對齊 PIPE-SPEC §1.2.3 v3）+ `class TranslateMode(str, Enum)`（NORMAL/DEEP_THINK）；`pipelines/contracts.py::GlossaryReadySpec` 補 `domain_name: Optional[str]=None`。
- **C2（U2 Prompt Engine）**：`Translator` 系統提示詞拼接五步（① text_type→提示詞檔〔title/caption/content〕② doc_type Style Hints〔7 文體〕③ LCC 領域注入〔讀 ctx.domain_name、空則 fallback ctx.lcc、gated LLM_USE_GLOSSARY_ALIGN〕④ Glossary 強約束塊〔含大小寫不敏感指令、gated 旗標〕⑤ constraints 注入）+ 用戶提示詞拼接（title/abstract/zh_summary/preceding/else）+ 新建 caption_translate_prompt.txt。
- **C3（U3 雙模式）**：`settings.LLM_THINKING_BUDGET=int(os.getenv(...,"0"))`；`llm/client.py::chat()` 以 C3 標記包裹加 `if LLM_THINKING_BUDGET>0 and "3.5" in model: config_kwargs["thinking_config"]=types.ThinkingConfig(thinking_budget=...)`；Translator `translate(...,mode)` 路由 NORMAL/DEEP_THINK（皆用 TRANSLATE_MODEL，DEEP_THINK 經 budget 啟用思考）。
- **C4（U4+測試）**：U4 多行 `re.sub(r'([。！？])\s*', r'\1\n', translated)` 兜底 + `tests/test_translator.py` 8 測試。
- **C5**：Checkout 收官歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 修改 `llm/client.py`（§4 不可動、全域共享 client） | 🔴 高 | **plan §4 唯一受控例外**（baron 拍板·路 A、依 model_recommendations.md §1.1）；僅加 thinking_config 分支、`_api_semaphore`/retry/既有路徑不動；`=== [TRANSLATOR C3 START/END] ===` 標記 + 改前 `.bak`；budget=0 時 byte 等價舊行為 |
| 修改 `pipelines/contracts.py`（PIPE-CORE 已落地凍結合約） | 🟡 中 | 僅 `GlossaryReadySpec` 補 Optional 欄位（向後相容、預設 None）；不動其他三合約；改前 `.bak` |
| InjectionContext/TranslateMode 誤放 contracts.py | 🟡 中 | C1 落 `processor/translator.py`（plan F 缺口決議）；contracts.py 僅補 domain_name |
| caption 提示詞改既有檔 | 🟢 低 | **新建** caption_translate_prompt.txt（非改既有 title/content 檔、遵 §4）|
| DEEP_THINK 因預設模型非 3.5 靜默退化 | 🟡 中 | C3 建議同步將 `settings.TRANSLATE_MODEL` 預設改 gemini-3.5-flash（對齊 SOP）；§6 測試顯式設 budget+3.5 mock（plan §2 U3 退化警告） |
| gating `"3.5" in model` 前向不相容 | 🟢 低 | plan §7 Q3 已標 tasks 宜前向相容（白名單/try-except 降級）；C3 實作採此 |
| baton 報告提早 mv/git add | 🔴 高 | C1-C4 全留 baton；唯 C5 收官一次性歸檔 |

---

## §6 測試計畫

> 對齊 plan §6.1（8 測試）；C4 集中建 `tests/test_translator.py`（mock LLM、不實打 API）。

### §6.1 C1 驗收（合約與 Context）
```bash
grep -nE "class InjectionContext|class TranslateMode|frozen=True|extra=.forbid|domain_name|doc_type" processor/translator.py
grep -nE "domain_name" pipelines/contracts.py
python -c "from processor.translator import InjectionContext, TranslateMode; print('OK')"
```
### §6.2 C2 驗收（Prompt Engine）
```bash
grep -nE "caption_translate_prompt|大小寫不敏感|本文件主題領域|術語強約束|額外譯文約束|domain_name|style_hints|doc_type" processor/translator.py
ls prompt/translate/caption_translate_prompt.txt
```
### §6.3 C3 驗收（雙模式 + thinking_config）
```bash
grep -nE "LLM_THINKING_BUDGET" settings.py llm/client.py processor/translator.py
grep -nE "thinking_config|ThinkingConfig|TRANSLATOR C3|3.5. in model" llm/client.py
```
### §6.4 C4 驗收（分行容錯 + 8 測試）
```bash
grep -nE "re.sub|TranslateMode|InjectionContext" tests/test_translator.py
pytest tests/test_translator.py -v   # 期望 8 passed
pytest tests/ -q                     # 既有零迴歸
```

---

## §7 不可動清單

明確劃定修改邊界。**以下嚴禁任何改動：**

- [ ] A 軌舊單體 Pipeline（`pipeline_core.py` 既有 11-stage、`processor/translate_processor.py`）：影子期保持可運行、Flip 前不動。
- [ ] `llm/client.py` `_api_semaphore` 全域並發鎖與 `llm/retry.py` 重試機制——**唯一受控例外**：`chat()` 准加 `thinking_config` 注入分支（gated budget>0 且 "3.5" in model）；其餘並發/retry/既有 config 路徑一律不動。
- [ ] `models.py` 既有 Schema 與 `Domains` 表結構（Translator 純函式、零 DB 耦合；lcc→name 解析屬上游 P2）。
- [ ] `prompt/translate/` 既有提示詞檔（title/content）內容——僅可**新增** caption 檔。
- [ ] PIPE-CORE `pipelines/contracts.py` 其餘三合約（Ingestion/Bilingual/RagDb）——僅可在 `GlossaryReadySpec` 補 domain_name。
- [ ] DOMAIN-NORM `normalize_to_lcc`/`Domains`、GLOSSARY-CORE `GlossaryManager`——僅消費。
- [ ] 主 repo 目錄；baton/ 暫存（C1-C4 嚴禁提前 mv/git add；唯 C5 一次性歸檔）。

---

## §8 推薦 Commit 拆分

### C1 — Contract & Context（合約與上下文模型）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `processor/translator.py`（InjectionContext + TranslateMode）；修改 `pipelines/contracts.py`（GlossaryReadySpec 補 domain_name，先 `.bak`） |
| **安全性** | 🟢 高 — 純新增模組 + 凍結合約補 Optional 欄位（向後相容） |
| **可逆性** | 🟢 高 — 刪新檔 + 還原 contracts.py `.bak` |
| **驗收 grep 條件** | 見 §6.1（InjectionContext/TranslateMode/frozen/forbid/7 欄 + contracts domain_name + import OK） |
| **依賴關係** | 無前置（上游已落地） |
| **具體實作細節** | 1. `cp pipelines/contracts.py .claude-logs/archive/2026-06-04_TRANSLATOR_C1_contracts.py.bak`。2. `processor/translator.py` 定義 `class TranslateMode(str, Enum)`（`NORMAL="normal"` / `DEEP_THINK="deep_think"`）+ `class InjectionContext(BaseModel)`（`model_config=ConfigDict(frozen=True, extra="forbid")`；欄位逐字對齊 PIPE-SPEC §1.2.3 v3：`lcc: str`、`glossary: Dict[str,str]`、`zh_summary: Optional[str]=None`、`preceding: Optional[str]=None`、`constraints: List[str]=[]`、`domain_name: Optional[str]=None`、`doc_type: Optional[str]=None`）。3. `pipelines/contracts.py::GlossaryReadySpec` 以 `# === [TRANSLATOR C1 START/END] ===` 包裹補 `domain_name: Optional[str] = None`（對齊 PIPE-SPEC §1.1② v3）。4. 產 C1 執行報告（baton/）。 |

### C2 — Prompt Engine（提示詞與約束動態注入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/translator.py`（補 `Translator` 類 + Prompt Engine）；新建 `prompt/translate/caption_translate_prompt.txt` |
| **安全性** | 🟢 高 — 純新增類與提示詞檔、未接線既有 pipeline |
| **可逆性** | 🟢 高 — 還原新檔 |
| **驗收 grep 條件** | 見 §6.2（caption_translate_prompt / 大小寫不敏感 / 本文件主題領域 / 術語強約束 / 額外譯文約束 / style_hints） |
| **依賴關係** | C1（InjectionContext） |
| **具體實作細節** | 1. `Translator` 系統提示詞拼接（plan U2）：① **底層提示詞**——`text_type=="title"`→`title_translate_prompt.txt`、`=="caption"`→新 `caption_translate_prompt.txt`、其餘→`content_translate_prompt.txt`；② **Style Hints**——依 `ctx.doc_type`（預設 academic）附 7 文體提示；③ **LCC 領域注入**——`if settings.LLM_USE_GLOSSARY_ALIGN:` 讀 `ctx.domain_name`（空 fallback `ctx.lcc`）附「本文件主題領域：{}」、**零 DB**；④ **Glossary 強約束塊**——`if ctx.glossary and LLM_USE_GLOSSARY_ALIGN:` 附「術語強約束 System constraint（**大小寫不敏感套用**）」+ 逐項 `- {term_key} → {translation}`；⑤ **constraints 注入**——`if ctx.constraints:` 附「【額外譯文約束】」逐項。2. 用戶提示詞拼接（title/abstract/zh_summary/preceding/else）。3. 新建 `prompt/translate/caption_translate_prompt.txt`（指令保留 Figure/Table 編號與標點）。4. 產 C2 執行報告（baton/）。 |

### C3 — Dual-Mode Routing & Thinking（雙模式路由與思考受控擴充）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `settings.py`（+`LLM_THINKING_BUDGET`，先 `.bak`）/ `llm/client.py`（`chat()` 補 thinking_config 分支，先 `.bak`）/ `processor/translator.py`（雙模式路由） |
| **安全性** | 🟡 中 — 動全域共享 client；但 budget=0 時 byte 等價、全 gated |
| **可逆性** | 🟢 高 — 還原兩 `.bak` |
| **驗收 grep 條件** | 見 §6.3（LLM_THINKING_BUDGET / thinking_config / ThinkingConfig / TRANSLATOR C3 標記 / gating） |
| **依賴關係** | C1 + C2 |
| **具體實作細節** | 1. 兩檔改前各 `.bak`（納入 git add）。2. `settings.py` 加 `LLM_THINKING_BUDGET = int(os.getenv("LLM_THINKING_BUDGET", "0"))`（C3 標記）；**建議同步將 `TRANSLATE_MODEL` 預設改 `gemini-3.5-flash`**（對齊 SOP §1.1、否則 DEEP_THINK 退化、plan §2 U3 警告）。3. `llm/client.py::chat()` L78-80 config 建構以 `# === [TRANSLATOR C3 START/END] ===` 包裹：依 SOP §1.1 範例，`config_kwargs={temperature, system_instruction}`；**前向相容判定**（plan §7 Q3——勿硬編碼 "3.5"、宜正向白名單或 try/except 降級）下 `if LLM_THINKING_BUDGET>0 and <思考世代模型判定>: config_kwargs["thinking_config"]=types.ThinkingConfig(thinking_budget=LLM_THINKING_BUDGET)`；`_api_semaphore`/retry/既有路徑不動。4. `Translator.translate(text, ctx, mode, text_type="content")` 統一呼叫 `LLMClient.get_instance().chat(..., model=settings.TRANSLATE_MODEL)`；NORMAL/DEEP_THINK 差異由 budget 注入決定。5. 產 C3 執行報告（baton/）。 |

### C4 — Formatting Fallback & Tests（分行容錯與單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/translator.py`（U4 分行兜底）；新建 `tests/test_translator.py`（8 測試） |
| **安全性** | 🟢 高 — 兜底邏輯 + 純測試新增 |
| **可逆性** | 🟢 高 — 還原 |
| **驗收 grep 條件** | 見 §6.4（`pytest tests/test_translator.py -v` 8 passed + 既有零迴歸） |
| **依賴關係** | C1 + C2 + C3 |
| **具體實作細節** | 1. `Translator` 末加多行兜底：原文行數 >1 且譯文行數較少時 `re.sub(r'([。！？])\s*', r'\1\n', translated).strip()`。2. `tests/test_translator.py` 8 測試（plan §6.1、mock LLM）：`normal_mode`（budget=0）/ `deep_think_mode`（**顯式設 LLM_THINKING_BUDGET=2048 + mock 含 "3.5" 模型名**，斷言 config 含 thinking_config）/ `style_hints`（7 doc_type）/ `prompt_file_routing`（title/caption/content）/ `lcc_domain_injection`（`ctx.domain_name="Electronics Engineering"` 注入；None fallback lcc；**斷言零 DB**）/ `glossary_injection`（含大小寫不敏感指令；旗標 off 不注入）/ `formatting_fallback`（三行→單行重分行）/ `user_prompt_references`（zh_summary/preceding）。3. 產 C4 執行報告（baton/）。 |

### C5 — Checkout & Clean（結案收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`+`git add` baton/ plan_v10→`plans/` + tasks→`tasks/` + C1-C5 報告→`executions/`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ |
| **驗收 grep 條件** | `ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ \| grep TRANSLATOR`（齊全）；`ls .claude-logs/baton/ \| grep -c TRANSLATOR` # 期望：0 |
| **依賴關係** | C1-C4（全部報告已產於 baton/） |
| **具體實作細節** | 1. Conformance 三維度驗收（目標規格 U1-U4 / 測試 §6.1-§6.4 / 不可動清單 git 全量證據 + 上游：簽名逐字對齊 PIPE-SPEC §1.2.3 v3）→ 產 `baton/2026-06-04_TRANSLATOR_C5_執行.md`。2. **一次性歸檔**（WORKFLOW_SOP §3）：`mv` plan_v10 baton→`plans/`；tasks baton→`tasks/`；C1-C5 `_執行.md` baton→`executions/`。3. `git add` 上述正式檔 + `processor/translator.py`/`pipelines/contracts.py`/`llm/client.py`/`settings.py`/`prompt/translate/caption_translate_prompt.txt`/`tests/test_translator.py` + 全部 `.bak` + prompts/INDEX + TODO（**明確列檔、嚴禁 `git add -A`**）。4. **更新 TODO.md**：TRANSLATOR 移入 ✅ 已完成表（Hash 待 baron 回填）+ 刪 active 條目 + 索引標 ✅ + 歷史 Hash 自癒。5. 驗 baton/ 無 TRANSLATOR 殘留。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3）。 |

---

## §9 Open Questions

| 開放問題 | 推薦答案 | 理由 |
|---|---|---|
| **`settings.TRANSLATE_MODEL` 預設是否本任務一併改 `gemini-3.5-flash`** | **建議於 C3 一併改預設（對齊 SOP §1.1）** | 否則 DEEP_THINK 因 gating「思考世代模型」不成立而靜默退化 NORMAL（plan §2 U3 警告）；改預設為純常數變更、低風險、env 仍可覆寫。若 baron 偏好保守維持 2.0-flash 預設，則 DEEP_THINK 需部署端顯式設 3.5 模型 + budget。 |
| **thinking gating 前向相容判定的具體實作** | **正向白名單（思考世代集合 env 化）或 try/except 捕「不支援 thinking」降級**（plan §7 Q3） | SOP §1.1 的 `"3.5" in model` 排除現行 GA `gemini-2.5-flash/pro` 與未來 4.0；tasks 實作宜彈性化，避免硬編碼。具體集合/降級策略於 C3 實作時敲定。 |
| **`processor/translator.py` 被 `pipelines/` import 的循環依賴風險** | **單向：pipelines 策略 import translator；translator 不 import pipelines** | translator 僅依賴 llm/settings/GlossaryManager（消費），不反向依賴 pipelines/orchestrator，無循環。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 TRANSLATOR 的 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` C1–C5 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | InjectionContext/TranslateMode 落 processor/translator.py（非 contracts.py）；llm/client.py 僅准 thinking_config 受控例外；既有提示詞檔不動（僅新增 caption）；嚴禁自動 git commit/push；C1–C4 報告嚴禁移動、唯 C5 收官一次性歸檔；修改既有檔前 `.bak` |
| **改版觸發條件** | plan v10 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | Translator 契約唯一源在 PIPE-SPEC §1.2.3；模型/thinking 規範唯一源在 model_recommendations.md §1.1；LCC/Glossary 收斂唯一源在 DOMAIN-NORM/GLOSSARY-CORE；本檔僅定義拆分細節與驗收指令 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：初版拆分，依 plan v10（八輪 review 定稿、U1–U4）拆為 5 Commit——C1 Contract & Context（InjectionContext 7 欄 frozen+forbid + TranslateMode 落 processor/translator.py / GlossaryReadySpec 補 domain_name）/ C2 Prompt Engine（系統提示詞五步 + 用戶提示詞 + caption 新檔 + 大小寫不敏感指令）/ C3 Dual-Mode Routing & Thinking（LLM_THINKING_BUDGET env + client.py thinking_config 受控例外 + 雙模式路由 + 前向相容 gating）/ C4 Formatting Fallback & Tests（re.sub 兜底 + 8 pytest）/ C5 Checkout 收官；簽名逐字對齊 PIPE-SPEC §1.2.3 v3；不給 commit 建議；C1/C3 改既有檔前 `.bak`；C1-C4 留 baton、唯 C5 一次性歸檔；§5 標 client.py 受控例外/contracts 補欄位/DEEP_THINK 退化三大風險；§9 標預設模型/前向相容/循環依賴三 Open Questions。
