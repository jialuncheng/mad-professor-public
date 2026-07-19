# GLOSSARY-TERMMAP 事前定案術語表與 glossary 旗標開啟 — Tasks

> 本文件為 GLOSSARY-TERMMAP 的 Commit 拆分清單（階段 2 產出）。
> 依 `baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（**v2·六 OQ 拍板定稿**）產出，含 6 個 Commit。
> 拆分原則：builder 先行零接線 → litedoc 先行實證（Q6）→ 兩路等價收斂 → 滑窗附論 → **旗標最後點火**（全鏈就緒才開、風險最小化）→ Checkout。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_glossary_termmap.py`（builder 單元測試 + §7.2 整合測試） |
| **修改檔案** | 8 個 | `processor/glossary_extractor.py`（build_termmap 五步）/ `settings.py`（census 常數 C1、旗標翻轉 C5）/ `.env.example`（C5 同步）/ `processor/translator.py`（免括號句）/ `pipelines/litedoc_pipeline.py`（P2 收斂 C2、P3 滑窗 C4）/ `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py`（P2 收斂 C3）/ `pipelines/section_engine.py`（純加法 slot_context_fn C4）＋對應測試檔更新 |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 6 個 | C1 → C2 → C3 → C4 → C5 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan → `plans/`、tasks → `tasks/`、C1-C5 `_執行.md` → `executions/`，產 `checkout_執行.md` 後逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：三路並行翻譯零共享上下文致同一專名多譯（`sentient sun` 三譯）與同字括號噪音（`SpaceX (SpaceX)` ×74）；三路 `_heal_glossary` 之域級早退快取閘門使跨文件累積飛輪第一份後停轉（Q1 判定缺陷）；glossary 注入全鏈接好但旗標關閉。
- **解法**：六原子 commit——**C1 — Termmap Builder（術語定案表產生器）**：`GlossaryManager.build_termmap` 五步＋census 常數＋新測試檔、零接線；**C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）**：litedoc P2 收斂＋translator 免括號句＋§7.2 整合測試；**C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）**；**C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）**：section_engine 純加法＋P3 接線；**C5 — Glossary Flag-On（旗標預設開啟）**：settings 翻轉＋.env.example＋測試旗標掃描；**C_CHECKOUT — Checkout（收官歸檔）**。
- **影響範圍**：`processor/` 兩檔、`pipelines/` 四檔、`settings.py`/`.env.example`、測試若干；A 軌零碰；DB schema／contracts 凍結合約零動；**C5 起全五路 B 軌譯文行為改變**（golden 改善豁免＋影子 E2E）。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `processor/glossary_extractor.py` | `_normalize_key`（L71）/ `query_cascade`（L78）/ `extract_terms`（L122、雙語樣本）/ `upsert_terms`（L177、冪等） | 無 build_termmap；抽詞只餵摘要對、漏 body 長尾 |
| `pipelines/litedoc_pipeline.py` | `_heal_glossary` L422-431（L428-429 早退）；P3 `restore_sections_markdown` 共用單一 `inj`、無滑窗 | P2 收斂 build_termmap；P3 滑窗注入 |
| `pipelines/resume_pipeline.py` | `_heal_glossary` L480-487（同式早退） | P2 收斂（等價替換） |
| `pipelines/slide_pipeline.py` | `_heal_glossary` L653（同式早退） | P2 收斂（等價替換） |
| `processor/translator.py` | L127-136 術語強約束區塊（旗標 gated） | 補「譯名＝原文者免括號」一句 |
| `pipelines/section_engine.py` | `restore_sections_markdown` L343：全 slot 共用同一 `inj` | 純加法 `slot_context_fn` 可選參數 |
| `settings.py` | L112 `LLM_USE_GLOSSARY_ALIGN` 預設 false | C1 增 `GLOSSARY_CENSUS_CHUNK_CHARS`、C5 旗標翻轉 true |

---

## §3 觀察問題

### 問題 #1：飛輪早退（Q1 已拍板＝缺陷）
- **證據**：`pipelines/litedoc_pipeline.py#L428-429`（`if existing: return existing`）；resume L486-487／slides L653 同式；docstring「query_cascade→**缺詞** extract_terms」＝域級成本快取閘門意圖
- **影響**：域被首份文件寫入後、後續同域文件全跳過自癒，跨文件累積停轉

### 問題 #2：抽詞綁摘要、漏 body 長尾
- **證據**：`glossary_extractor.py#L122` `extract_terms(source_text, translated_text, ...)` 需雙語對齊樣本、P2 僅有摘要對；SpaceX 實證 SpaceX ×67/7 段、Starship ×12/5 段
- **影響**：要一致的高頻詞根本不在 glossary、注入形同虛設

### 問題 #3：並行翻譯零共享上下文 → 多譯與括號重複
- **證據**：`section_engine.py#L343` 全 slot 共用單一 `inj`、`InjectionContext.preceding` 從未設；影子 PDF 同字括號 pair 106/107
- **影響**：缺陷④⑤（PIPE-INGEST v4 移交本案根治）

### 問題 #4：旗標關閉、注入鏈休眠
- **證據**：`settings.py#L112` 預設 false；`translator.py#L119/#L127` 雙 gate
- **影響**：P2 建表→P3 注入全鏈存在但零生效

---

## §4 設計方案

### §4.1 C1 — Termmap Builder（術語定案表產生器）
`GlossaryManager` 新增 `build_termmap` 五步（N1 段落邊界切塊 → N2 逐塊純 LLM census 只認詞不翻〔並行、單塊 soft〕→ N3a `_normalize_key` 去重 → N3b `query_cascade` 分流已知∪未知〔廢早退語意〕→ N4 未知詞一次批次翻譯〔context=摘要對〕→ N5 `upsert_terms(source="termmap_decided")` 定案寫回）＋ `settings.GLOSSARY_CENSUS_CHUNK_CHARS=6000`。**零接線**（三路仍走 `_heal_glossary`、旗標仍關）→ 零 runtime 變化。

### §4.2 C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）
litedoc P2 `_heal_glossary` → `build_termmap`（full_text 已在 P2 現場）；`translator.py` 強約束區塊補免括號句；§7.2 整合測試（termmap 注入 key-changing mock 翻譯 → 全篇一致＋免括號指令斷言）。旗標仍關、runtime 零變化（測試以 monkeypatch 開旗標驗證鏈路）。

### §4.3 C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）
兩路 `_heal_glossary` → `build_termmap`（full_text 各路自備：resume＝P2 已讀 md 全文、slides＝合併頁文本）；等價替換、既有測試斷言零動為底線。

### §4.4 C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）
`section_engine.restore_sections_markdown` 增可選 `slot_context_fn`（預設 None＝現行為 byte 等價、resume 零變）；litedoc P3 建 per-section factory：以 slot 之原文標題 path 查鄰近 `section_summaries` zh 摘要 → 注入 `InjectionContext.preceding`；容缺（缺 key 略過）；size-gate 三分支零動。

### §4.5 C5 — Glossary Flag-On（旗標預設開啟）
`settings.py` `LLM_USE_GLOSSARY_ALIGN` 預設翻轉 true；`.env.example` 同步註記（含關回方式）；掃描未自行 patch 旗標之既有測試、必要時測試檔顯式 patch False（斷言本體零動）。**最後點火**：C1-C4 全鏈就緒後才開。

> **點火後影子 E2E 觀察項（C3 §7 負向自評移入·2026-07-19）**：slides 之 census 源 `full_text` 含 Vision `figure_description`（`slide_pipeline.py:503-505` 顯式 join `title+content+figure_description` → L531 `_heal_glossary` → `build_termmap` census）——旗標點火後，Vision 圖描文字可能引入**少量非正文專名**入 termmap。census prompt 之專名界定為第一道濾網（低風險），故不預先修；**留旗標開啟後影子 E2E 觀察**（旗標關時 census 休眠、無此暴露）。**若確認需濾**，濾點乾淨定點打擊：於 `slide_pipeline.py:505` 之 census `full_text` 移除 `u.get("figure_description")`（**僅動 census 源、不牽動 P3 rag_sections 旁路**——rag 旁路另在 L695-696 併 content+figure_description，兩者互不影響），或於 census prompt 收緊專名界定。

### §4.6 C_CHECKOUT — Checkout（收官歸檔）
Conformance＋§7.2 整合測試確認＋baton 一次性 mv＋逐檔 git add 白名單＋checkout 執行報告＋TODO 雙層結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C5 旗標開啟改變全五路譯文 | 🔴 高 | 點火獨立末位 commit、env 單點關回；影子軌不影響 A 軌；測試期 glossary 表可清庫重跑；baron 影子 E2E（plan §8.2） |
| census 新增 LLM 呼叫之成本/時延 | 🟡 中 | 逐塊並行＋semaphore 限流；常數 env 可調；已知詞免翻、body 不重翻 |
| C3 動 resume/slides（等價替換走樣） | 🟡 中 | 兩路既有測試全綠為底線；替換僅 `_heal_glossary` 內部、P2 其餘步序零動；分開 commit 獨立可逆 |
| C4 section_engine 簽名擴充影響 resume | 🟡 中 | 純加法可選參數、預設 None byte 等價；resume 呼叫零改；若無法純加法 → 依 plan Q4 當場剝離另案 |
| C5 未 patch 旗標之測試意外打 LLM | 🟡 中 | C5 實作細節含全測試掃描步驟；conftest／mock 範式沿用；CI 無金鑰環境天然攔截 |
| 同檔多 commit（litedoc C2/C4、settings C1/C5）staging 混雜 | 🟢 低 | 各 commit 各自 `.bak`＋`git diff --cached` 白名單自檢（SOP-COMPLY 前例） |

---

## §6 測試計畫

> 各 Run 落地前強制 §5 SOP 一致性核查：logging `grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔>`（error 必含 exc_info=True；glossary_extractor 既有 logger.error 均已帶 exc_info）+ database `grep -nE "\.commit\(\)" <修改檔> | grep -v "with .*session.*begin\(\)"`（期望：無命中（合規））。全套件基線 **780 passed**、逐 commit 不得低於。

### §6.1 C1 驗收

```bash
grep -n "def build_termmap" processor/glossary_extractor.py                     # 命中
grep -n "GLOSSARY_CENSUS_CHUNK_CHARS" settings.py processor/glossary_extractor.py  # 兩檔命中
grep -rn "build_termmap" pipelines/                                             # 期望：0 命中（C1 零接線）
python3 -m pytest tests/test_glossary_termmap.py -v                             # 全綠
python3 -m pytest tests/ -q                                                     # ≥780、零新 fail
```

### §6.2 C2 驗收

```bash
grep -n "build_termmap" pipelines/litedoc_pipeline.py                           # 命中（收斂）
grep -n "if existing" pipelines/litedoc_pipeline.py                             # 期望：0 命中（早退廢除）
grep -n "不得另加括號\|不加括號" processor/translator.py                          # 命中（免括號句）
grep -rn "integration\|termmap" tests/test_glossary_termmap.py | grep -i "test" # §7.2 整合測試存在
python3 -m pytest tests/ -q                                                     # ≥780
```

### §6.3 C3 驗收

```bash
grep -n "build_termmap" pipelines/resume_pipeline.py pipelines/slide_pipeline.py  # 各命中
grep -n "if existing" pipelines/resume_pipeline.py pipelines/slide_pipeline.py    # 期望：0 命中
python3 -m pytest tests/test_resume_pipeline.py tests/test_slide_pipeline.py -q   # 全綠（斷言本體零動）
python3 -m pytest tests/ -q                                                       # ≥780
```

### §6.4 C4 驗收

```bash
grep -n "slot_context_fn" pipelines/section_engine.py pipelines/litedoc_pipeline.py  # 各命中
python3 -m pytest tests/test_resume_pipeline.py -q                              # resume 零變（預設路徑 byte 等價）
python3 -m pytest tests/ -q                                                     # ≥780
```

### §6.5 C5 驗收

```bash
grep -n "LLM_USE_GLOSSARY_ALIGN" settings.py                                    # 預設 "true"
grep -n "LLM_USE_GLOSSARY_ALIGN" .env.example                                   # 註記命中
python3 -m pytest tests/ -q                                                     # ≥780（全套件於新預設下綠燈）
```

### §6.6 C_CHECKOUT 驗收

```bash
ls .claude-logs/baton/*GLOSSARY-TERMMAP* 2>/dev/null      # 期望：任務檔已清（僅餘長駐/證據檔）
ls .claude-logs/plans/*GLOSSARY-TERMMAP* .claude-logs/tasks/*GLOSSARY-TERMMAP* .claude-logs/executions/*GLOSSARY-TERMMAP*
git diff --cached --name-only                              # 實貼 checkout 報告、須完全等於宣告清單
```

---

## §7 不可動清單

承 plan v2 §6（唯一權威源）。**嚴禁任何改動：**

- [ ] **GlobalGlossary schema**（`models.py` 聯合唯一鍵零動）
- [ ] `pipelines/contracts.py` 凍結合約（`GlossaryReadySpec.glossary` 欄沿用零增刪）
- [ ] `prompt/translate/*.txt` 母翻譯提示詞檔（免括號句改 translator.py gated 區塊）
- [ ] `pipeline_core.py` 及 A 軌鏈全體
- [ ] `pipelines/ingestion_engine.py`（PIPE-INGEST 剛落地零碰）
- [ ] 三路 P2 glossary 段**以外**步序；litedoc P3 size-gate 三分支結構
- [ ] `section_engine` 既有行為（C4 僅純加法、預設參數下 byte 等價；resume 呼叫零改）
- [ ] `glossary_extractor` 既有三函式簽名（`query_cascade`／`extract_terms`／`upsert_terms` 對外行為不破壞）
- [ ] `processor/rag_indexer.py` 與 `summary_key`＝原文標題 path 基準
- [ ] 既有 tests 斷言本體（僅允許依規格新增／更新 glossary 相關測試＋C5 旗標顯式 patch、逐條記錄於執行報告）

---

## §8 推薦 Commit 拆分

### C1 — Termmap Builder（術語定案表產生器）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/glossary_extractor.py`（+ `.bak`）、修改 `settings.py`（+ `.bak`）；新增 `tests/test_glossary_termmap.py`（無 `.bak`） |
| **安全性** | 🟢 高 — 純加法方法與常數、零接線（`grep -rn "build_termmap" pipelines/` = 0）、旗標仍關、零 runtime 變化 |
| **可逆性** | 🟢 高 — `git revert` 完全回滾；`.bak` 留檔 |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `settings.py` 增 `GLOSSARY_CENSUS_CHUNK_CHARS = int(os.getenv("GLOSSARY_CENSUS_CHUNK_CHARS", "6000"))`（置 L112 旗標附近、註記 Q3 拍板）。② `glossary_extractor.py` 增模組常數 `_CENSUS_SYSTEM_PROMPT`（純 LLM census：**只認原文專名、不翻譯**；界定＝專有名詞〔人/組織/產品/地名/作品名〕＋文件內高頻重複領域術語、排除一般詞彙與動詞片語〔Q5〕；輸出 JSON 字串陣列、無可抽輸出 `[]`）與 `_TERM_TRANSLATE_SYSTEM_PROMPT`（批次翻譯未知詞：逐行 `[i] 譯法`、以摘要對引導風格、譯法與原文相同時原樣輸出）。③ `GlossaryManager` 新增私有輔助：`_split_census_chunks(full_text, chunk_chars) -> List[str]`（以 `\n\n` 段落累積、段落自身超限單獨成塊、不切句中）；`_census_chunk(chunk) -> List[str]`（1 次 LLM、temperature=0、`_parse` 容錯 fence、失敗回 `[]` soft＋`logger.warning(exc_info=True)`）；`_translate_unknown_terms(terms, abstract, translated_abstract, ...) -> Dict[str, str]`（**一次**批次呼叫、`parse` 逐行 `[i]`、失敗回 `{}` soft）。④ 公開 `build_termmap(full_text, abstract, translated_abstract, source_lang, target_lang, domain, *, chunk_chars=None, max_workers=None) -> Dict[str, str]`：N1 切塊（`chunk_chars or settings.GLOSSARY_CENSUS_CHUNK_CHARS`）→ N2 `ThreadPoolExecutor` 並行 census（workers=`max_workers or settings.LLM_MAX_CONCURRENT`、底層受 `_api_semaphore` 限流）→ N3a `self._normalize_key` 去重（**與 upsert/query 同一函式**、§4 契約）→ N3b `query_cascade` 分流 `{已知/未知}` → N4 `_translate_unknown_terms`（未知空集則跳過）→ N5 `upsert_terms(新翻對, source="termmap_decided")` → 回 `{**已知, **新翻}`（term_key: translation）。全程 LLM 於 DB 交易外；任何失敗降級回 `query_cascade` 結果（不阻斷）。⑤ 新增 `tests/test_glossary_termmap.py`（mock llm＋in-memory session_factory、沿用 GlossaryManager 依賴注入範式）：N1 切塊三態（段落邊界/超長段/短文單塊）；N2 census mock 只認詞（斷言 census prompt 含「不翻譯」語意、單塊失敗 soft）；N3a 去重（`SpaceX`/`spacex `多形一份）；**N3b 廢早退回歸斷言**（DB 已有詞時仍對未知詞呼叫翻譯並 upsert——直接對映 Q1）；N4 已知詞零翻譯呼叫（mock call count）；N5 upsert `source="termmap_decided"`；builder 失敗降級回已知。 |

### C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`（+ `.bak`）、修改 `processor/translator.py`（+ `.bak`）、修改 `tests/test_litedoc_pipeline.py`（+ `.bak`）、修改 `tests/test_glossary_termmap.py`（C1 新檔延續、補 §7.2 整合測試）；translator 既有測試檔若有斷言強約束區塊全文者一併更新（+ `.bak`） |
| **安全性** | 🟡 中 — 動 litedoc P2 與 translator gated 區塊；旗標仍關 → 生產 runtime 零變化；鏈路以測試 patch 旗標驗證 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 回滾；`.bak` 留檔 |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 前置：C1 |
| **具體實作細節** | ① litedoc `_heal_glossary` 本體改為：`return gm.build_termmap(full_text, abstract, translated_abstract, source_lang, _TARGET_LANG, lcc)`（早退段整段刪除；`full_text` 由 `run_phase2` 現場 `self._read_source_text(ctx)` 傳入——簽名擴 `full_text` 參數、呼叫點 L343 同步）。② `translator.py` L132-136 術語強約束區塊文案補一句：「**術語譯法與原文相同者，直接沿用原文、不得另加括號注解原文。**」（僅 gated 區塊字串、母 prompt 檔零動）。③ `tests/test_glossary_termmap.py` 補 **§7.2 跨 Phase 整合測試**：mock 全文（同一專名跨 ≥3 段、含譯=原文詞如 `SpaceX`）→ `build_termmap`（mock llm census/翻譯、key-changing：譯文≠原文）→ 定案表塞 `InjectionContext.glossary` → monkeypatch 旗標 True → `Translator()._build_system_prompt` 斷言：每術語強約束行存在、免括號句存在；斷言同一專名在模擬多段注入下譯法唯一（termmap 保證之結構性驗證）。④ `tests/test_litedoc_pipeline.py`：P2 glossary 測試改斷言呼叫 `build_termmap`（stub 之）與旗標關時 glossary={} 回歸；被更新斷言逐條記錄執行報告。⑤ §5 SOP 雙核查 grep 實貼。 |

### C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/resume_pipeline.py`（+ `.bak`）、修改 `pipelines/slide_pipeline.py`（+ `.bak`）；`tests/test_resume_pipeline.py`／`tests/test_slide_pipeline.py` 若有 `_heal_glossary` stub 需對位更新（各 + `.bak`、斷言本體零動） |
| **安全性** | 🟡 中 — 動兩路 P2；等價替換（旗標關＝零 runtime；旗標開後行為差異僅「已知∪未知」較早退更豐） |
| **可逆性** | 🟢 高 — 單 commit 回滾、兩檔 `.bak` |
| **驗收 grep 條件** | 見 §6.3 |
| **依賴關係** | 前置：C1（C2 非硬前置、但依 Q6 序列於 litedoc 實證後執行） |
| **具體實作細節** | ① resume `_heal_glossary`（L480-487）與 slides `_heal_glossary`（L653-）本體同式改呼 `build_termmap`、早退段刪除；`full_text` 來源——resume＝P2 既有 markdown 全文變數、slides＝P2 現場合併頁面文本（兩路各自現地取得、不新增跨 Phase 傳遞）；呼叫點（resume L371／slides L530）簽名同步。② 兩路 P2 其餘步序（摘要/LCC/節點摘要/storyboard）**零動**。③ 測試：兩檔既有 glossary 相關 stub 對位 `build_termmap`；既有斷言本體零動、全綠為底線。④ SOP 雙核查實貼。 |

### C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/section_engine.py`（+ `.bak`）、修改 `pipelines/litedoc_pipeline.py`（+ 本 commit 新拷 `.bak`）、修改 `tests/test_litedoc_pipeline.py`（+ 新拷 `.bak`）、`tests/test_section_engine.py` 補純加法回歸（+ `.bak`） |
| **安全性** | 🟡 中 — 動共用 section_engine；**純加法護欄**：新參數 `slot_context_fn=None` 預設路徑 byte 等價、resume 呼叫零改；若實作發現無法純加法 → 停、依 plan Q4 剝離另案交 baron |
| **可逆性** | 🟢 高 — 單 commit 回滾 |
| **驗收 grep 條件** | 見 §6.4 |
| **依賴關係** | 前置：C2（litedoc P2 收斂後、P3 滑窗與 termmap 注入同場驗證） |
| **具體實作細節** | ① `section_engine.restore_sections_markdown` 簽名增可選 `slot_context_fn: Optional[Callable[[int, Dict], Any]] = None`——提供時每一翻譯單元以 `slot_context_fn(i, slot)` 取得該單元 `InjectionContext`、None 時沿用共用 `inj`（現行為 byte 等價）；docstring 標註 parallel-safe（factory 純讀、無跨執行緒狀態）。② litedoc `run_phase3` section 分支建 factory：預掃 slots 序列、為每 index 記其所屬 section 之原文標題 path（title slot 之 `key`）→ factory 依 path 查 `gspec.section_summaries` 之**前一/後一鄰近 section** zh 摘要（**容缺**：缺 key 略過該側）→ 組 `InjectionContext(..., preceding="鄰近段落摘要參考：…")`（其餘欄位同共用 inj；frozen model 以建新實例實現）；無 `section_summaries` 時 factory 不啟用（傳 None、行為零變）。③ **嚴禁**譯文型 preceding（不得以其他 slot 譯文為 preceding——跨 section 逼序列）；size-gate 三分支與 whole/is_zh 路零動。④ 測試：`test_section_engine.py` 補「未傳 slot_context_fn ＝現行為 byte 等價」回歸與「傳入時逐 slot 收到對應 ctx」；`test_litedoc_pipeline.py` 補滑窗注入（鄰近摘要入 preceding、缺 key 容缺、summaries 空時零啟用）。⑤ SOP 雙核查實貼。 |

### C5 — Glossary Flag-On（旗標預設開啟）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `settings.py`（+ 本 commit 新拷 `.bak`）、修改 `.env.example`（+ `.bak`）；掃描後若有未 patch 旗標之測試需顯式 patch False 之測試檔（各 + `.bak`、斷言本體零動） |
| **安全性** | 🟡 中 — 一行預設翻轉、但**全五路 B 軌譯文行為自此改變**；影子軌不影響 A 軌；env 單點關回；測試期 glossary 表可清庫重跑 |
| **可逆性** | 🟢 高 — env `LLM_USE_GLOSSARY_ALIGN=false` 即時關回（不需 revert）；commit 本身可 revert |
| **驗收 grep 條件** | 見 §6.5 |
| **依賴關係** | 前置：C1-C4 全鏈就緒（**最後點火**） |
| **具體實作細節** | ① `settings.py:112` 預設值 `"false"` → `"true"`、行註補「GLOSSARY-TERMMAP C5 點火（Q2 拍板）；關回：env 設 false」。② `.env.example` 對應段補旗標說明（預設開、關回方式、census 常數一併註記）。③ **全測試掃描**：`grep -rn "LLM_USE_GLOSSARY_ALIGN" tests/` 盤點各測試 patch 現況；對「依賴旗標關」但未顯式 patch 之測試檔補 `monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)`（**斷言本體零動**、逐檔記錄執行報告）；確認無測試在新預設下真實打 LLM（mock 齊備）。④ 全套件於新預設跑綠（≥780）。⑤ SOP 雙核查實貼。 |

### C_CHECKOUT — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：plan → `plans/`、tasks → `tasks/`、C1-C5 `_執行.md` → `executions/`；新增 `executions/2026-MM-DD_GLOSSARY-TERMMAP_checkout_執行.md`；`TODO.md` + `archive/TODO_done_archive.md` 雙層結案 |
| **安全性** | 🟢 高 — 純文件歸檔 |
| **可逆性** | 🟢 高 — 檔案移動可逆 |
| **驗收 grep 條件** | 見 §6.6 |
| **依賴關係** | 前置：C1-C5 全部 ship 完（baron 回填 hash） |
| **具體實作細節** | ① Conformance 驗收（plan v2 §2 八規格項對照 C1-C5 報告；tasks §6 全綠；不可動 §7 逐項；提示詞歸檔稽核）。② **§7.2 整合測試存在且通過**確認（Checkout 必驗）。③ baton 一次性 `mv`（標準 mv）＋逐檔顯式 `git add`（含各 commit `.bak`；嚴禁 `git add .`/`-A`/目錄）。④ `git diff --cached --name-only` 白名單自檢實貼、多一檔少一檔即停。⑤ TODO 雙層結案＋hash 回填。⑥ `checkout_執行.md`（§8 僅一行 commit、輕量慣例）。⑦ 後續銜接註記：baron 影子 E2E（plan §8.2 硬驗收——全文單一譯法/同字括號 ≤1/跨文件累積）、LANG-DETECT（義文前置）、IMG-FILTER、PIPE-SYNC-5 回灌。 |

---

## §9 Open Questions

無。（plan v2 §9 六 OQ 已全數拍板結案；本 tasks 依 Q1-Q6 定案拆分。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GLOSSARY-TERMMAP 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 GLOSSARY-TERMMAP executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動 §7 不可動清單；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push`；C4 純加法受阻即停交 baron |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；接縫契約唯一源＝plan v2 §4；歷史動因唯一源＝plan v2 §3 |

### §99.2 Revision 歷程

- v1 (2026-07-19)：初版拆分——依 plan v2（六 OQ 拍板）自主規劃六 commits：C1 builder 零接線 / C2 litedoc 先行（Q6）+免括號句+§7.2 / C3 兩路等價收斂 / C4 滑窗純加法 / C5 旗標末位點火 / C_CHECKOUT；§6 各 commit 驗收＋SOP 前置；§7 增 C4 純加法受阻即停條款
