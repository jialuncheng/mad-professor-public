# LANG-DETECT cover-prompt 語言欄與 source_lang 正名 plan

> litedoc P1 cover-prompt（既有整檔 metadata LLM 讀取）新增 `language`（ISO 639-1）欄，於字元啟發式落入 catch-all `en` 時以之正名 `source_lang`（it/de/fr 等拉丁語系）——根治拉丁語系文件被判 `en` 致 GlobalGlossary 以錯誤語系分桶之污染。`classify_source_lang` 保留繁中 bypass 原職、零改。零新增偵測器、零多一次 LLM 呼叫。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：`classify_source_lang`（unicode 字元啟發式）只吐 `{zh, hans, ja, ko, en}`——拉丁語系（it/de/fr/es）全落 catch-all `en`；而 `GlobalGlossary` 以 `source_lang` 為聯合唯一鍵分桶 → 義大利文詞條以 `en` 寫入、污染英文命名空間、下一份真英文文件撈到義文詞（design spec F4 實查；schema 本身支援多語、**破的是偵測層**）。
- **解法**：cover-prompt（`_LITEDOC_META_SYSTEM_PROMPT`、既有整檔開頭 LLM 讀取）**多加一個 `language` 欄**（ISO 639-1 主體語言）；P1 新增 `_resolve_source_lang` 合成——字元啟發式非 catch-all（zh/hans/ja/ko）一律維持原判、僅 catch-all `en` 時採信通過白名單（`^[a-z]{2,3}$` 且**拒 zh 前綴**）的 LLM 語言碼；缺欄／怪值 → 退啟發式（與現行 100% 等價）。
- **影響**：僅 `pipelines/litedoc_pipeline.py`（prompt 常數 + P1 source_lang 合成段）＋測試；`section_engine.classify_source_lang` 零改（原職）；P2 glossary 分桶／P3 繁中 bypass gate 消費端零改（自然吃到正名後的值）；零 DB schema、零 API、零新依賴、零多一次 LLM 呼叫。

---

## §2 目標規格

1. **cover-prompt +`language` 欄**：`_LITEDOC_META_SYSTEM_PROMPT` Fields 增列 `language (str: ISO 639-1 two-letter code of the document's main body language, e.g. en/it/de/fr/ja)`；Rules 補一條——依**正文主體語言**判定（非標題/URL 語言）、不確定給 `""`；輸出 keys 清單同步加 `language`。**不加任何其他欄**（`title/authors/date/publisher/url` 規則零動）。
2. **P1 source_lang 合成（新私有 `_resolve_source_lang(meta, heuristic) -> str`）**：
   - 啟發式（`classify_source_lang`）回 `zh`／`hans`／`ja`／`ko`（字元證據、確定性高）→ **一律維持原判、LLM 不得翻案**（繁中 bypass 權威不動搖）；
   - 啟發式回 catch-all `en` → 取 `meta["language"]` 正規化（strip + lower）後過雙重白名單：格式 `^[a-z]{2,3}$` **且非 `zh` 前綴**（HOTFIX-1 鎖一契約：非繁嚴禁 zh* token、防 LLM 回 `zh`/`zh-tw`/`zho` 類值繞過 gate）→ 通過即採（如 `it`/`de`/`fr`；**ISO 639-2 三字碼 `ita`/`deu` 亦合法通過**——glossary `source_lang` 為字串欄、相容）、未過退 `en`（`IT`→lower 後採、`en-US`/`Italian`/空值/缺欄全退 `en`）；
   - `meta` 缺欄／空字串／soft-fail 空 dict → 退啟發式（**行為與現行 100% 等價**）。
3. **正名生效面**：`spec.source_lang` 單點正名後，下游**零改自然生效**——P3 `startswith("zh")` bypass gate（it/de 皆非 zh*、照走翻譯）、P2 `_heal_glossary`／`build_termmap` 之 `source_lang` 參數 → `GlobalGlossary` 以正確語系分桶。
4. **`classify_source_lang` 原職不兼差**：`pipelines/section_engine.py` 本體零改（繁中 bypass gate、HOTFIX-1 契約、book 路共用）。
5. **範圍圍籬**：僅 litedoc 路（cover-prompt 為 litedoc 自有）；resume／slides（Vision 自有語言處理）／book／academic／A 軌零碰。
6. **零新依賴、零新偵測器、零多呼叫**：語言判定搭既有 metadata LLM 呼叫便車（temp=0）；嚴禁引入 langdetect 類第三方套件。

### §2.5 候選方案（Diverse Rollout）

source_lang 權威層歸屬屬語系正確性的架構決策，列候選：

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| 方案 A（選定）**catch-all 限定採信** | 啟發式 zh/hans/ja/ko 維持原判；僅 catch-all `en` 時採白名單過濾後的 LLM `language` | 修的正是破口（拉丁語系）、爆炸半徑最小；繁中 bypass 權威零動搖；LLM 波動不影響 CJK 判定 |
| 方案 B（否決）**LLM 全權＋啟發式兜底** | `language` 欄直接設 source_lang、缺欄才退啟發式 | 繁中 bypass 改繫於 LLM 輸出——temp=0 仍有波動、`zh`/`zh-tw` 類 token 需逐值防禦；HOTFIX-1 契約風險面全開 |
| 方案 C（否決）**引入第三方偵測器** | langdetect / fasttext 等獨立語言偵測 | 違 design spec F4「零新增偵測器」定案；新依賴、新失效面；LLM 便車已零成本 |

- **選定理由**：A＝design spec F4 方向（cover-prompt +1 欄）＋最小信任轉移——只把「啟發式自認不知道（catch-all）」的空間讓給 LLM、字元證據確定的判定不讓渡。
- **否決留痕**：B／C 留底（CLAUDE.md §1.9），防未來把繁中 bypass 權威交給 LLM 或引入偵測依賴重踩。

---

## §3 現況與證據

- **`pipelines/section_engine.py`**：
  - `classify_source_lang L576-`（docstring 明言 HOTFIX-1 鎖一契約）：回傳 ∈ `{'zh','hans','ja','ko','en'}`；`detect_zh_tw` 字元計數（kana/hangul/CJK/簡體標記/ASCII 主導）——**拉丁語系無任何分支、全落最終 `en`**。
- **`pipelines/litedoc_pipeline.py`**：
  - `_LITEDOC_META_SYSTEM_PROMPT L67-84`：五欄（title/authors/date/publisher/url）＋publisher OCR 自癒＋Title Case；**無 language 欄**。
  - `_extract_litedoc_metadata L360-`：整檔開頭 `[:_META_INPUT_CHARS]` 送 LLM（temp=0）、soft-fail 空 dict——**+1 欄零多呼叫的載體**。
  - `run_phase1 L193`：`source_lang = section_engine.classify_source_lang(_lang_sample)`——**唯一 setter、本案合成點**；L222 入 `IngestionMetadataSpec.source_lang`。
  - P2 `run_phase2 L415`：`source_lang = (ctx.ingestion.source_lang ...) or "en"` → L435 傳 `_heal_glossary(full_text, source_lang, _TARGET_LANG, ...)`——glossary 分桶消費端。
- **`models.py`**：
  - `GlobalGlossary L285-307`：`source_lang` ISO 語系碼欄（L288 註 `"en"/"de"/"ja" → "zh-tw"`）、聯合唯一約束含 `source_lang`（L300）＋級聯索引（L303）——**schema 本身支援多語、破的是偵測層**（design spec F4「關鍵」）。

### §3.1 grep 鋼鐵證據

```bash
sed -n '576,584p' pipelines/section_engine.py
# def classify_source_lang(sample: str) -> str:
#   回傳 ∈ {'zh'(繁), 'hans'(簡), 'ja', 'ko', 'en'}；下游 startswith('zh') gate 僅繁中 bypass
#   ⚠️ 簡體嚴禁 'zh-cn'/'zh-hans'（四處 startswith('zh') gate 誤判 bypass）→ 本案 LLM 值拒 zh 前綴同理

grep -n "language" pipelines/litedoc_pipeline.py
# （prompt 常數區零命中——cover-prompt 現無 language 欄）

grep -rn "source_lang" pipelines/litedoc_pipeline.py
# 193: source_lang = section_engine.classify_source_lang(_lang_sample)   ← 唯一 setter
# 222: source_lang=source_lang（入 IngestionMetadataSpec）
# 415: source_lang = (ctx.ingestion.source_lang ...) or "en"             ← P2 消費
# 435: full_text, source_lang, _TARGET_LANG, ...                         ← glossary 分桶入口

grep -n "source_lang" models.py
# 288: source_lang / target_lang: ISO 語系碼（如 "en"/"de"/"ja" → "zh-tw"）
# 300: UniqueConstraint("source_lang", "target_lang", "term_key", "domain", ...)
# 303: Index("ix_glossary_cascade", "source_lang", "target_lang", "domain")
```

---

## §4 跨 Phase 接縫契約

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| P1→P2 語系分桶 | P1 `_resolve_source_lang` 設 `IngestionMetadataSpec.source_lang`（ISO 639-1 小寫、非繁嚴禁 zh* token） | P2 `run_phase2` 讀 `ctx.ingestion.source_lang` → `_heal_glossary`／`build_termmap` → `GlobalGlossary.source_lang` 聯合鍵 | key＝**ISO 語系碼字串本身**；producer 寫入與 glossary 查詢/upsert 為同一 token（單點正名、消費端零轉換）；it 文件產 `it` 桶、en 文件仍 `en` 桶——跨文件不再互污 |
| P1→P3 繁中 bypass | 同上 `source_lang` | P3 `startswith("zh")` gate（僅繁中 bypass 翻譯） | 同基準保證＝**非繁值嚴禁 zh 前綴**（HOTFIX-1 鎖一）——白名單「拒 zh 前綴」在 producer 端強制、gate 端零改 |

填寫規範見 `.claude-logs/ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| LLM `language` 誤判（如義英混排判 en） | 🟢 低 | 誤判回 `en`＝現行行為、零退化；誤判他拉丁碼影響僅 glossary 分桶（測試期 DB 可丟）；temp=0 求穩 |
| LLM 回 zh* 類 token 破繁中 gate | 🟡 中 | 白名單雙閘（格式＋拒 zh 前綴）在 producer 端硬擋；測試以 `zh`/`zh-tw`/`Chinese` 參數化鎖死 |
| 既有 en 桶內的義文污染詞 | 🟢 低 | 不追溯清理——測試期 DB 可丟、清庫重跑即淨（RESCUE 慣例）；生產後期屬 GLOSSARY-UI |
| 英文/CJK 文件回歸 | 🟢 低 | 啟發式非 catch-all 一律維持原判；缺欄退啟發式＝100% 等價；既有測試全量回歸 |
| cover-prompt 改動影響其他五欄抽取品質 | 🟢 低 | 僅增列一欄與一條規則、既有規則零動；既有 meta 測試回歸鎖住 |
| golden 基準 | 🟢 低 | litedoc 影子軌、B 軌改善豁免慣例；A 軌零觸碰 |

---

## §6 不可動清單

- [ ] `pipelines/section_engine.py` `classify_source_lang`／`detect_zh_tw` 本體（原職：繁中 bypass gate、HOTFIX-1 契約、book 路共用；**嚴禁兼差**）
- [ ] P3 `startswith("zh")` bypass gate 與 P2 glossary 消費端簽名（單點正名、消費端零改）
- [ ] `models.py` `GlobalGlossary` schema（聯合鍵已支援多語、零動）
- [ ] cover-prompt 既有五欄（title/authors/date/publisher/url）之規則與語意
- [ ] `_TARGET_LANG = "zh-tw"` 系統固定目標語
- [ ] resume／slides／book／academic 各路與 A 軌全檔
- [ ] **嚴禁**引入第三方語言偵測依賴；**嚴禁**新增獨立偵測器或多一次 LLM 呼叫

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| F4 設計定案（+language 欄／零新偵測器／classify 不兼差／多語 glossary 前置） | `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` §F4、§3.1 序 ※ |
| HOTFIX-1 鎖一契約（非繁零 zh* token） | `pipelines/section_engine.py` `classify_source_lang` docstring |
| GlobalGlossary 多語 schema | `models.py` L285-307 |
| 跨 Phase 接縫契約／§7.2 整合測試 | `ref/WORKFLOW_SOP.md §7` |
| logging／database SOP（BE-Refactor 必讀） | `sop/2026-05-23_logging_SOP_手冊.md`／`sop/2026-05-23_database_SOP_手冊.md` |
| 進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：`venv/bin/python -m pytest tests/ -q`（基線 875 passed、零回歸）。
- **預計新增**（`tests/test_litedoc_pipeline.py`）：
  - prompt 契約：`_LITEDOC_META_SYSTEM_PROMPT` 含 `language` 欄與 keys 清單。
  - 合成矩陣（`_resolve_source_lang`）：啟發式 `zh`/`hans`/`ja`/`ko` ＋ LLM 任意值 → 維持原判；啟發式 `en` ＋ `it`/`de`/`fr` → 採信；＋ `zh`/`zh-tw`/`ZH`/`Chinese`/`italian`/空/缺欄 → 退 `en`（白名單參數化鎖死）。
  - P1 端到端（mock LLM 回 `language:"it"`）：`spec.source_lang == "it"` 且不帶 zh 前綴。
  - **§7.2 跨 Phase 整合測試**：P1（mock cover-prompt 回 `it`、key-changing＝語系 token 由 catch-all `en`→`it`）→ P2 真步序（mock LLM/Glossary stub）——斷言 `_heal_glossary`／`build_termmap` 收到的 `source_lang == "it"`＋P3 gate 不 bypass（走翻譯）；對照組英文文件全鏈仍 `en`。

### §8.2 手動端到端（E2E）驗證流程

1. 影子上傳**義大利文樣本**：後端 log `source_lang=it`；`GlobalGlossary` 新詞條 `source_lang='it'`（SQL 抽查）；譯文正常繁中。
2. 影子重傳英文樣本（SpaceX）：`source_lang=en` 回歸、glossary 仍寫 en 桶。
3. 繁中樣本：`source_lang=zh`、bypass 不翻譯（HOTFIX-1 回歸）；簡體樣本：`hans` 轉繁照舊。
4. SQL 驗桶隔離：`SELECT DISTINCT source_lang FROM global_glossary` 出現 `it` 且英文桶無義文新詞。

---

## §9 Open Questions（四問全數拍板 2026-07-21·baron 採納推薦、無翻案）

| 開放問題 | 拍板方案 | 理由 |
|---|---|---|
| Q1 LLM 採信範圍 | ✅ **僅啟發式 catch-all `en` 時採信**（§2.5 方案 A） | 拉丁語系全落 `en` 是當前唯一偵測破口；字元統計確定的 CJK/繁中判定不讓渡給 LLM、繁中 bypass 權威零動搖 |
| Q2 是否加 env flag | ✅ **不加**（無 `LITEDOC_LANG_DETECT_ENABLED`） | 合成邏輯內建雙重安全網——缺欄／格式不符自動降級退啟發式、與現行 100% 等價；+1 欄小改再包 flag 屬過度設計（YAGNI）；系統性誤判修 prompt 即可 |
| Q3 語言碼白名單 | ✅ 格式 `^[a-z]{2,3}$`（strip+lower 後）**且拒 `zh` 前綴** | ISO 639-1/2 完整覆蓋（含三字碼 `ita`/`deu`）；`zh`/`zh-tw`/`zho`/`Chinese`/`italian`/`hans` 類值全數擋下；拒 zh 前綴＝HOTFIX-1 鎖一在 producer 端的延伸強制 |
| Q4 既有 en 桶污染詞處理 | ✅ **不追溯清理** | 本案聚焦攝入偵測層根治；測試期 DB 可丟、清庫重跑即淨（RESCUE-1 慣例）；生產歷史詞條清理屬 GLOSSARY-UI、非本案前提 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 LANG-DETECT cover-prompt 語言欄與 source_lang 正名 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 LANG-DETECT tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md；F4 設計定案唯一源＝design spec、本檔僅凍結為規格 |

### §99.2 Revision 歷程

- v2 (2026-07-21)：review 定稿——外部 review 無結構性缺失（肯認 catch-all 限定採信＝最小信任轉移、HOTFIX-1 producer 端拒 zh 前綴封鎖；`_resolve_source_lang(meta, heuristic)` 簽名與白名單邊界枚舉逐行確認）；一實作確認回灌 §2.2（白名單相容 ISO 639-2 三字碼 `ita`/`deu`、邊界案例明文化 `IT`/`en-US`/`Italian`/`zho`）；§9 四 OQ 全數拍板採納推薦（無翻案）
- v1 (2026-07-21)：初版——依 design spec F4（cover-prompt +language 欄／零新偵測器零多呼叫／classify_source_lang 原職不兼差）凍結規格；§2.5 三候選留痕（catch-all 限定採信選定、LLM 全權與第三方偵測器否決）；四 OQ 待 baron 拍板
