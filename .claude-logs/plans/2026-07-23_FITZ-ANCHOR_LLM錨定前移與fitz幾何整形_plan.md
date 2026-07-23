# FITZ-ANCHOR LLM 錨定前移與 fitz 幾何整形 plan

> 溯源：FITZ-HOTFIX-1/2/3 三輪打地鼠後 baron 拍板架構轉向（2026-07-23）——「進 FITZ 前跑一次 LLM 協助判斷 Meta、跟 FITZ 資料比對；litedoc 丟第一頁最多第二頁」。核心定調：**重要性判斷全交 LLM（錨定）、fitz 回歸快速抽文字＋清垃圾（幾何）**。
> 本案**取代**原擬 FITZ-HOTFIX-4（未立案）並**退場** FITZ-HOTFIX-3 K2 之 sidecar 管線（已落地、由錨定前移自然吸收）。
> 證據包：`baton/litedoc_shadow_artifacts/Ohtani_v1/`＋源 PDF ×3（gitignored 長駐）＋本案 §3.1 模擬實證。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 TL;DR（概要）

- **挑戰**：fitz 快速道連續三輪 hotfix 的失手全屬同類——幾何啟發式**猜錯「什麼是重要的」**（標題被當浮水印/頁首、lede 被當回聲），每換一個網站版式冒一種新猜錯法；除噪本身（nav/chrome/計數）從未失手。日文 NHK 樣本 E2E 四症狀：標題全滅（描邊 ×4 → 浮水印規則誤殺、精確 key 去重被 ±0.84pt 偏移擊穿）／QA 區 Q×4 攪爛／「史上初」段落被跨頁規則誤殺剩孤兒句／lede 被 echo 子字串誤吃。
- **解法（結構反轉 + 幾何精修）**：**U1** meta 錨定前移——既有 cover-prompt 呼叫**改吃「前 1-2 頁原始文字層」**（fitz 裸抽、零過濾、零新增 LLM 呼叫），title/authors/date/publisher/language 在任何刀動手前定案；**U2** 標題回注——knives 絞完後 md 無錨定 title 之 heading → 升級既有行或注入 `# {title}`（**整類標題誤殺 bug 一勞永逸**）＋回注即告警（版式觀測）；**U3** HOTFIX-3 K2 sidecar 管線退場（裸文字本含 chrome URL、LLM 直解 publisher）；**U4** K1′ ε 容差同位去重（治 QA Q×4 與 section 標題 ×4）；**U5** K2′ 跨頁重複門檻改比例（治內容段誤殺）；**U6** echo 守衛（長度比、防禦性一行）。
- **影響**：`pipelines/litedoc_pipeline.py`（U1/U2/U3/U6 接點）＋`processor/fitz_processor.py`（U3 寫端退場/U4/U5）＋測試；cover-prompt schema、`image_filter`、`section_engine`、`md_cleaner` 浮水印規則本體、A 軌全鏈零改。

---

## §2 目標規格

### U1 — meta 錨定前移（重要性判斷交 LLM、零新增呼叫）

`_extract_litedoc_metadata` 之輸入由「knives 絞完的 md 文首 4000 字」改為「**前 N 頁原始文字層**」：
- 新 helper `_read_anchor_text(pdf_path, max_pages)`：`fitz.open` 逐頁 `get_text("text")`、取前 `LITEDOC_ANCHOR_MAX_PAGES`（settings 常數、預設 2）頁拼接；開檔/解析異常回 `""`（fail-open）。
- 錨定文字非空 → 作 cover-prompt 輸入；**空**（掃描件/加密）→ **退回現行輸入**（cleaned md 文首、行為 100% 等價）。
- 呼叫位置不動（R6 時序：`_build_tiles` 之前）、呼叫次數不變（**同一次 LLM、換更好的輸入**）；cover-prompt 六欄 schema／Rules 零改；`language` 欄（LANG-DETECT）／`meta_values`（R6/K3 消費）自然受惠。
- **與 design spec F6 一致性**：錨定讀的是**正文文字層**（含列印 chrome 文字）、仍**零檔案屬性依賴**（不讀 `/Title` 等）——F6「meta 純正文」定案不破。
- MinerU 路同享（anchor 讀的是 PDF 非 md、與解析引擎無關）；掃描件文字層空 → fallback 保底。

### U2 — 標題回注與比對告警（整類標題誤殺的最終保底）

P1 步驟 ②'（cleaner／連字／R7 之後、③ DocAnalyzer **之前**）：
- 正規化比對（去空白 casefold）：錨定 `title` 是否存在於 md——
  1. 已存在為 heading 行 → 不動；
  2. 存在為**正文行**（heading 偵測漏判）→ **就地升級** `# ` 前綴（不重複注入）；
  3. **全文缺席**（被任何刀誤殺）→ md 頂部**注入** `# {title}`。
- 情形 2/3 均 `logger.warning`（`[FITZ-ANCHOR] 標題回注 site=… case=promote/inject`）——哪個網站版式又騙過幾何層、有觀測不必等 E2E。
- 錨定 title 空 → 整步跳過（現行 `_resolve_title` 兜底鏈 meta.title→首 `#`→paper_name 原樣運作）。
- 效果：**標題必達 md** → DocAnalyzer 有錨點（判型變準、K3 連帶受益）→ ingestion title／譯題／PDF Title 全鏈保底；echo-strip 比對對象變成完整長標題 → lede 子字串誤中自然解除。

### U3 — HOTFIX-3 K2 sidecar 管線退場（被 U1 吸收）

裸文字層**本來就含**列印頁尾 URL（NHK 實證 `https://news.web.nhk/...`）→ cover-prompt rule 1 直接解 publisher。移除：fitz `_URL_RE` 捕捉與 `{stem}_source_hints.json` 寫檔、litedoc `_load_source_hints`（`litedoc:480`）與 `hints=` 參數接線（`litedoc:274`）、`_extract_litedoc_metadata` 恢復單參數。K1（同位去重、由 U4 取代精修）與 K3（meta 歸零、**保留不動**）不在退場之列。

### U4 — K1′ ε 容差同位去重（治正文/結構層的描邊 ×N）

`_collect_page` 去重由精確 key `(text, round(y0,1), round(x0,1), round(size,1))` 改**容差聚類**：同頁同 `(text, round(size,1))` 群內、與已保留行 `|Δx0| ≤ 3.0 且 |Δy0| ≤ 3.0`（settings 常數可調）→ 判 text-stroke/shadow 重繪副本、丟棄；距離超過 → 合法異位重複、保留。**每頁獨立**（跨頁歸 R2）。
**實測靶**：NHK 描邊偏移 ±0.84pt（`45.24/46.08×2/46.91`、精確 key 收 4→3、3≥3 照殺）；Q 行 n=4、A 行 n=1（QA 攪爛根源）；6 個 section 標題 log `(4 次)` 全滅。

### U5 — K2′ 跨頁重複門檻改比例（治內容段誤殺）

`_repeated_band_keys` 門檻由「≥2 頁」改「**≥ max(2, ceil(頁數×50%))**」：chrome 特徵＝近全頁重複（SpaceX 23/23、NHK 10/10）；內容重複＝少數頁（NHK「史上初」段 2/10、其前兩行落頂 band 被誤殺剩孤兒 `めてです。`×2）。
**實測靶**：門檻 5（10 頁）下 chrome 四組照殺、「史上初」段落完整存活（§3.1 模擬已證）。

### U6 — echo 守衛（防禦性一行）

`_title_echo_match` 之子字串分支（`sa in sb or sb in sa`）加長度比守衛：`min(len)/max(len) ≥ 0.5` 才視為回聲——「大谷翔平」(4 字) ⊂ lede (88 字) ratio 0.045 不再誤中；真回聲（整行≈標題）照剝。U2 落地後屬雙保險、成本一行。

### §2.5 候選方案（Diverse Rollout）

| 決策點 | 方案 | 取捨 |
|---|---|---|
| 錨定輸入 | **A（選定）前 1-2 頁裸文字層（text-based）** | 零新增呼叫（既有 cover-prompt 換輸入）、零新依賴；title-as-image 版式抓不到（fallback 鏈兜底、見 §5） |
| | B（否決）首頁 render 成圖 → Vision 錨定 | 可吃 title-as-image、但多一次 Vision 呼叫+延遲；litedoc 大宗 born-digital 文字層齊全、YAGNI；未來真撞 title-as-image 再升級 |
| | C（否決）繼續純幾何 hotfix 打地鼠 | 病史證偽：HOTFIX-1 八刀→2→3→4 擬案、每版式一輪；結構性反轉才收斂 |
| 標題保底 | **A（選定）md 回注（promote-else-inject）** | 與哪把刀誤殺無關、終局保底；含就地升級防重複 |
| | B（否決）fitz 層 protect-list（錨定 title 傳入 knives 豁免） | 需穿線 fitz 簽名、且各刀都要判豁免——侵入面大；回注等效且單點 |
| U4 去重 | **A（選定）ε 容差聚類** | 偏移量實測 ±0.84pt ≪ 3.0；(3 次)/(4 次) 並存證明精確 key 不可靠 |
| | B（否決）加大 round 粒度（round 到 5pt） | bin 邊界照樣劈開（46.08 vs 46.91 可跨 bin）；容差是距離語意、bin 是格子語意 |

---

## §3 現況與證據

- **病史（打地鼠實錄）**：HOTFIX-1 八刀（R1-R8）→ HOTFIX-2 兩刀（行界/對稱）→ HOTFIX-3 三刀（K1 精確去重/K2 sidecar/K3 歸零）→ NHK E2E 仍四症狀 → 擬 HOTFIX-4 三刀時 baron 拍板轉向。失手全屬「猜錯重要性」類；除噪類（nav/chrome/計數/垃圾圖）零失手。
- **NHK 樣本量測**（源 PDF 實測、本 session）：
  - 標題描邊 ×4、x0＝`45.2417/46.0770×2/46.9122`（±0.84pt）→ HOTFIX-3 精確 key 收 4→**3**、`WATERMARK_HEADING_THRESHOLD=3` → 照殺（log `(3 次)` 鐵證）；
  - 6 個 section 標題 log `(4 次)`＝一份未收；
  - QA 區 Q 行 n=4／A 行 n=1 → Q 殘骸攪爛 Q/A 流（`Q．ぬるっと Q．ぬるっと` 併行實錄）；
  - 「史上初」段落 p2/p5 重複、前兩行 y0=40.6/63.1 落頂 band（<67）→ R2「≥2 頁」門檻誤當 chrome、殺頭留孤兒 `めてです。`×2；
  - lede 被吃鏈：K3 正確移除 date 行 → echo-strip 首匹配滑至 lede → `_title_echo_match` 子字串分支「大谷翔平」⊂ lede → 誤剝。
- **chrome 頁數分布**：SpaceX 23/23、NHK 10/10（比例門檻設計依據）。

### §3.1 模擬實證（本 session、scratchpad 子類覆寫零碰業務碼）

U4+U5 依本規格離線重演 NHK 源 PDF（fitz→cleaner→ligature 確定性鏈）、before/after：

| 驗收點 | 現行 | 模擬修復後 |
|---|---|---|
| 標題 | 全滅 | `# ドジャース 大谷翔平 二刀流復帰戦`＋`# で先頭打者HR 投げては4勝目` |
| section 樹 | 全滅（1 section→whole） | `##`×2＋`###`×3＋`## 一問一答` 全回歸 → section mode |
| QA 區 | Q 連發無答案 | **14 組 Q/A 全數成對逐字完整** |
| 史上初段 | 孤兒 `めてです。`×2 | 段落完整（×2＝源頁面本身重複、誠實殘差） |
| 行數 | 132（含屍痕空行） | 118 |

（U1/U2 屬 LLM 錨定與回注、模擬不含；其確定性部分——裸文字含標題 ×4 與 chrome URL——已由源 PDF 解剖直接證明。）

### §3.2 grep 鋼鐵證據

```bash
grep -n "hints=self._load_source_hints" pipelines/litedoc_pipeline.py
# 274:            markdown_text, hints=self._load_source_hints(output_dir, pdf_path)   ← U3 退場點
grep -n "def _load_source_hints" pipelines/litedoc_pipeline.py
# 480:    def _load_source_hints(...)                                                  ← U3 退場點
grep -n "dedup_key = (text, round(y0, 1)" processor/fitz_processor.py
# 248:  dedup_key = (text, round(y0, 1), round(float(x0), 1), round(size, 1))          ← U4 改造點
grep -n "len(hit) >= 2" processor/fitz_processor.py   # （實際行號以現碼為準）
# _repeated_band_keys 門檻                                                            ← U5 改造點
grep -n "sa in sb or sb in sa" pipelines/section_engine.py
# 622:    if sa == sb or sa in sb or sb in sa:                                         ← U6 守衛點
grep -n "_META_INPUT_CHARS" pipelines/litedoc_pipeline.py
# 64:_META_INPUT_CHARS = 4000（U1 錨定文字沿用同截斷窗語意）
```

---

## §4 跨 Phase 接縫契約

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| 錨定 meta | U1 cover-prompt（裸文字輸入）產 title/authors/date/publisher/language | `_resolve_title`／`_resolve_source_lang`／R6 `meta_values`／K3 值比對／扉頁渲染 | 欄位 schema 與現行 cover-prompt **完全同形**（六欄零改）——所有既有消費者零感知；值正規化沿用 `ingestion_engine.normalize_meta_values` 單一源 |
| 錨定 title → md | U2 回注器（promote-else-inject） | DocAnalyzer（判型錨點）→ ingestion_engine（title 抽取）→ P3 譯題 | key＝**正規化標題文字**（去空白 casefold）；回注在 ③ analyze **之前** → sidecar 行號含回注行、下游行界同基準 |
| U3 退場 | （廢）fitz sidecar 寫端 | （廢）litedoc `_load_source_hints` | 生產者消費者**同案同刀移除**、嚴禁只刪一端（防半殘管線） |
| U4/U5 md 產出 | fitz 幾何整形後同形 .md | cleaner/DocAnalyzer/engine 零感知 | 同形 .md 契約不變（PIPE-INGEST-FITZ §2.2） |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 錨定 LLM 誤判 title（幻覺/選錯行） | 🟡 中 | temp=0＋輸入含完整版面線索（比受損 md 好判）；回注採 promote-else-inject 不產生重複標題；E2E 兩樣本把關；錨定空/怪值 → 兜底鏈原樣 |
| title 在第 3 頁之後的版式 | 🟢 低 | litedoc 大宗＝新聞/網頁列印、標題必在首頁；`LITEDOC_ANCHOR_MAX_PAGES` 常數可調 |
| title-as-image 版式（文字層無標題） | 🟢 低 | 錨定抓不到 → 回注跳過 → 現行兜底鏈（paper_name＝檔名常為正題）；未來升級 Vision 錨定（§2.5 B 留痕） |
| U4 誤合「3pt 內合法重複文字」 | 🟢 低 | 同頁同文同級且距 ≤3pt＝視覺重疊、無正當版式如此排；ε settings 可調 |
| U5 比例門檻對極短 PDF（2-3 頁） | 🟢 低 | `max(2, …)` 下限保住 2 頁件現行為；chrome 仍全頁出現、照殺 |
| U3 移除後 publisher 回歸 | 🟢 低 | 裸文字含同一 URL、同一 rule 1 解碼——NHK 實證輸入面更完整；SpaceX（body 自帶 URL）零差異 |
| MinerU 路 / A 軌回歸 | 🟢 低 | 錨定屬純輸入改善＋fallback 等價；fitz 幾何改動不出 `fitz_processor`；A 軌零觸碰 |
| golden | 🟢 低 | B 軌影子改善豁免慣例 |

---

## §6 不可動清單

- cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` 六欄 schema 與 Rules——零改（U1 只換輸入來源）
- `processor/md_cleaner.py` 浮水印規則本體／`WATERMARK_HEADING_THRESHOLD`——零改（U4 從供給端治、規則保留 MinerU 路戰功）
- HOTFIX-3 **K3**（`_strip_meta_source_lines` 行級歸零）——零改（本案受益者非改造對象）
- `pipelines/image_filter.py`／`section_engine`（除 U6 一行守衛外）／`ingestion_engine`／`rag_indexer`／contracts——零改
- `PDFParser` ABC 簽名／A 軌全鏈／resume／slides／book——零碰
- `LITEDOC_FITZ_ENABLED` 等旗標語意——零改（新常數純加法）

---

## §7 規格依據

- baron 架構拍板（2026-07-23）：「進 FITZ 前跑一次 LLM 協助判斷 Meta、跟 FITZ 資料比對；litedoc 丟第一頁最多第二頁」——本案 U1/U2 之直接授權源
- `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` F6：meta 純正文、零檔案屬性依賴（U1 一致性論證見 §2）；F6 fitz 直抽定位（幾何層回歸本職）
- `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md` §1.2.6 ingestion 契約家族（本案不動 engine、僅供給端）
- `plans/2026-07-21_PIPE-INGEST-FITZ_..._plan.md` §2.2 同形 .md 硬契約（U4/U5 維持）
- `hotfixes/2026-07-22_FITZ-HOTFIX-3_..._hotfix.md`（K2 退場對象、K3 保留；其「族群教訓」章之雙通道鐵律本案沿用）
- `ref/WORKFLOW_SOP.md` §1.2 BE-Refactor（logging/database SOP 必讀、§5 核查）＋§7 接縫契約；`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §1.1 雙軌制

---

## §8 驗證計畫

### §8.1 自動化單元測試

- U1：錨定文字非空 → cover-prompt 輸入＝裸文字（捕 messages 斷言含 chrome URL 行）；掃描件（空文字層）→ fallback 現行輸入 byte 等價；`LITEDOC_ANCHOR_MAX_PAGES` 截頁斷言
- U2：三分支各測（heading 已在→不動／正文行→就地升級不重複／缺席→頂部注入）＋ 回注 warning 斷言；錨定空 → 跳過、兜底鏈原樣
- U3：`grep _load_source_hints`／`source_hints` 全庫歸零（dead code 清除斷言）；`_extract_litedoc_metadata` 恢復單參數
- U4：±0.84pt ×4 fixture → 收斂 1 份；3pt 外同文行保留；每頁獨立（跨頁不誤合）；**§3.1 模擬表全項轉正式 fixture**（標題×2 heading／section 樹／QA 14 組成對／史上初完整）
- U5：10 頁 chrome 10/10 殺、內容段 2/10 留；2 頁件行為等價
- U6：4字⊂88字 不判回聲；整行≈標題照剝
- SOP §5 雙 grep（logging/database）實貼；全套件基線（993 passed 起算）不退

### §8.2 §7.2 跨 Phase 整合測試（Checkout 必驗）

真實 born-digital PDF（fitz 現造：描邊 ×4 標題＋×4 Q 行＋2/N 頁重複內容段＋全頁 chrome）→ 真 FitzProcessor（U4/U5）→ 真 cleaner → mock 錨定 meta → U2 回注 → 真 `_build_tiles` → P3——斷言：標題存活入 heading、QA 成對、內容段完整、chrome 零殘留、meta 零重播（key-changing：PDF→md→tiles）。

### §8.3 手動端到端（E2E）驗證流程（baron）

1. NHK 樣本重傳：標題完整譯題＋恰一 `(測試)`／section mode（P3 log `mode=section sections≥5`）／QA 區成對／publisher=NHK／扉頁後零 meta 重播／log 浮水印剝除行全消失
2. SpaceX 回歸：標題／21 圖／meta／termmap 各項不退化
3. 第三樣本（新站台、未調校過版式）泛化驗證——本案的成敗判準是**新版式不再需要 hotfix**

---

## §9 Open Questions（六問全數拍板 2026-07-23·baron 採納外部 review 覆核後方案、無翻案）

| # | 問題 | 拍板方案 | 理由 |
|---|---|---|---|
| Q1 | 錨定頁數固定 2 or settings 常數？ | ✅ **settings 常數 `LITEDOC_ANCHOR_MAX_PAGES=2`** | baron 拍板「第一頁最多第二頁」為預設；長封面版式免改碼熱調 |
| Q2 | 錨定 LLM 失敗（空/異常）時？ | ✅ **fail-open 全鏈**——輸入退 md 文首、回注跳過、兜底鏈原樣（行為與現行 100% 等價） | 錨定屬增強層、不得成為新單點故障（SPOF） |
| Q3 | U3 退場時機——同案移除 or 過渡共存？ | ✅ **同案移除**（生產/消費端同刀、含測試） | 消費者僅一處、共存＝兩套 publisher 來源徒增判讀歧義；HOTFIX-3 執行報告已留審計 |
| Q4 | U6 echo 守衛帶不帶（U2 後理論用不到）？ | ✅ **帶**（一行） | 短標題＋錨定失敗 fallback 的極端組合仍可能重現 lede 誤吃；防禦成本趨零 |
| Q5 | MinerU 路是否同享錨定？ | ✅ **同享**（anchor 讀 PDF 與解析引擎無關；掃描件空文字層自動 fallback） | 純改善零風險。**精度勘誤（v2、對 review 措辭）**：受惠者＝**litedoc 之 MinerU fallback 路（B 軌內）**；真 A 軌（`pipeline_core`+`metadata_extractor`）本案零碰、其 `/Author` 檔案屬性污染（`authors: Baron` 實證）**不在本案治癒範圍**、屬另案 |
| Q6 | 模擬 harness 是否隨案入 tests？ | ✅ **入**（§3.1 模擬表全項轉 fixture、含 14 組 QA 成對與標題存活斷言） | 「先模擬後拍板」流程的直接資產、防回歸即驗收 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | 結構性反轉 litedoc P1 重要性判斷（LLM 錨定）＋ fitz 幾何層精修（ε 去重/比例門檻）；終結標題/meta 誤殺類 hotfix 循環 |
| 用途 | 階段 2 拆 tasks 之依據；驗收靶錨定 §3 實測與 §3.1 模擬 |
| 權威源 | 本檔 §1–§9 |
| 引用方 | 後續 tasks／執行報告／PIPE-SYNC-6 回灌（含 HOTFIX-3 族群教訓與本案架構轉向） |
| 約束事項 | §6 不可動清單；baton 暫存至 Checkout 一次性歸檔；不含 commit 拆分建議（歸階段 2） |
| 改版觸發條件 | §1–§9 任一變動 |
| 刪除條件 | 收官歸檔 plans/ 後長存 |

### §99.2 Revision 歷程

- v2 (2026-07-23)：外部 review 定稿——**全數肯認、零新增規格**、六 OQ 照推薦拍板（Q1 常數/Q2 fail-open/Q3 同案移除/Q4 帶守衛/Q5 同享/Q6 入 tests）；一處精度勘誤：review 稱錨定「根除 A 軌檔案屬性污染」過譽——受惠者僅 litedoc 之 MinerU fallback 路、真 A 軌（`pipeline_core`）零碰屬另案（Q5 註記）
- v1 (2026-07-23)：初版——六規格項（U1 錨定前移/U2 標題回注/U3 K2 退場/U4 ε 去重/U5 比例門檻/U6 echo 守衛）＋NHK 全量測證據＋§3.1 模擬 before/after＋六 OQ；取代 FITZ-HOTFIX-4 擬案
