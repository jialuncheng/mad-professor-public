# FITZ-HOTFIX-1 fitz 路標題救回與雜訊通則修復 plan

> 溯源：2026-07-21 baron 影子 E2E（SpaceX & the Sentient Sun.pdf 走 fitz 快速道）回饋四缺陷 → 本 session 逐項實測診斷（本地複現 FitzProcessor 直抽 + 成品 PDF 解剖 + 源 PDF 字級/link/block 掃描）。
> 全部七刀（R1-R7）均有本 session 實測數據當驗收靶；證據見 §3。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST-FITZ 落地後首次真實 E2E（SpaceX 樣本、fitz 路）暴露四缺陷——①標題錯（epigraph 被當標題）②meta/計數雜訊入正文（作者/日期重播、`53 82 Share`）③nav 列入正文④46k 全文只切 1 個 section。診斷結論：**fitz 直抽對「瀏覽器列印網頁」這個 litedoc 主場景有四處啟發式盲區**，全部有確定性通則修法、零 LLM 新增。
- **解法**：八刀——R1 圖框內文字排除／R2 repetition key 加字級（救標題、列印 PDF 通案）／R3 heading 第三級 ###／R4 影子 (測試) 雙後綴修復／R5 link-tiling nav 剝除／R6 meta 值比對歸零／R7 數字為主短行清理／R8 whole-mode 圖片過濾（關閉 filter 旁路缺口）。R1+R2 落地後 SpaceX 樣本可產出 `#` 真標題 + `##`×4 + `###`×3 完整結構。
- **影響**：`processor/fitz_processor.py`（R1/R2/R3/R5）＋ `pipelines/litedoc_pipeline.py`（R4/R6/R7 接線）＋ `pipelines/ingestion_engine.py`（R6 可選純加法）＋ `web_server.py`（R4 擇一端）；MinerU 路／A 軌／resume／slides／section_engine／rag 零改。

---

## §2 目標規格

### R1 — 圖框內文字排除（治圖表黏字搶 heading + 正文圖表殘渣）

`_collect_page` 收文字行時，行 bbox 與該頁任一 image rect 重疊面積 > 50% 者剔除（圖表的可選文字覆蓋層；圖本身已作為 figure 保留、資訊不丟）。
**實測靶**：p6 五行黏字（`SpaceXHasLaunchedMorePayloadstoOrbit` 25.5pt／`ThantheRestoftheWorldCombined` 23.9pt／`AlEZ` 16.9pt／`Restofworld`／`CumulativePayloadsLaunched(Thousands)`）全部 bbox 落圖框內（§3.4）；剔除後 heading 候選淨化為 `[25.6, 20.9, 17.1]`＝真實三層階梯。

### R2 — repetition key 加入字級（救標題、瀏覽器列印 PDF 通案）

`_repetition_key` 由「數字歸一文字」改為「數字歸一文字 + `round(size, 1)`」。
**根因（通案）**：瀏覽器列印必在每頁頁首印 `document.title`（7.0pt chrome）→ 跨頁重複 key 必含標題文字；文章真標題必在第一頁頂部（本例 y0=71.5 < 8% band 界 104）→ **每一份列印網頁 PDF 的真標題都必然撞上自己的頁首 key 被誤殺**。加字級後：7.0 chrome 23 頁照剝、25.6 真標題全文件唯一 → 存活。
**實測靶**：band 內跨頁重複 key 四組——日期戳/標題/頁碼/URL 全 7.0pt；標題 key 之 sizes=[7.0, **25.6**]（§3.2）。

### R3 — heading 第三級 ###（收編小節）

`_heading_sizes` 回 (h1, h2, h3)＝候選前三級、`_heading_level` 對應 `#`/`##`/`###`。
**實測靶**：R1 淨化後候選恰為三級——25.6（標題）/20.9（大節 ×4：Working Back from the Future 等）/17.1（小節 ×3：The Industrial Moon／Compute in the Sky／Mars）（§3.3）。

### R4 — 影子 (測試) 雙後綴修復

現況：P1 影子加 ` (測試)`（`litedoc_pipeline.py:207`）→ P3 譯題把**帶後綴的** title 餵 `translate_unit`（LLM 保留與否隨機）→ web_server 影子寫庫再 append（`web_server.py:776`、無防重）→ 成品 `(測試) (測試)`。
修法（§9 Q4 已拍板·雙保險並做）：P3 譯題餵 `_title_bare`（L596 現成變數、producer 端治本、翻譯輸入保證乾淨）＋ web_server 寫庫端 append 前 `endswith` 防重（一行雙保險）。

### R5 — link-tiling nav 剝除（通則）

一行文字被 **≥3 個獨立 link rect** 覆蓋 **≥60% 面積** → 導覽/連結列 → 剝除。抓 nav 的結構本質（一行由多連結平鋪）而非字面；信號＝PDF link 註記（瀏覽器列印保留）。雙閾值各擋一種誤殺：≥3 links 擋「帶連結的標題/裸 URL 行」（單 link）；≥60% 擋「正文句內 inline link」（覆蓋率低）。無 link 註記之 PDF → 規則自然停用（fail-open 傾向保留）。
**實測靶**：全 23 頁掃描命中**恰 1 行**＝`America | Tech | Opinion | Culture | Charts`（覆蓋 84%、5 links）；7 真標題/epigraph/正文全零命中（§3.5）。

### R6 — meta 值比對歸零（確定性兜底）

meta 分離現況僅靠 DocAnalyzer（LLM）判型行號；fitz md 前段形狀走樣（標題被 R2 bug 誤殺失錨 + 圖行/計數/nav 混雜）→ 判型失準 → 作者/日期原文行洩入 body 與扉頁渲染版重播。R2/R1/R5 落地後判型大概率自癒，但補一道**確定性兜底**：cover-prompt 已抽出 authors/date/publisher **值** → 行文字正規化（casefold/去分隔）後等於已抽 meta 值或其變體者 → 標 meta 剝除。零新 LLM、不依賴判型心情、MinerU/fitz 兩來源同享。
**⚠️ 物理接線時序（外部 review 2026-07-21 核心發現、grep 已證）**：現行 `run_phase1` 中 `_build_tiles`（L191、內呼 `assemble`）在 `_extract_litedoc_metadata`（L194）**之前**執行——R6 要把 meta 值注入 assemble，必須把 `_extract_litedoc_metadata` **前移至 `_build_tiles` 之前**。該函式僅唯讀吃 `markdown_text`（簽名單參數、零 tiles 依賴）→ 調序安全無副作用；`_resolve_title`/`source_lang` 合成等後續消費不受影響（一併前移或原位皆可、以 diff 最小為準）。
**實測靶**：新成品 `MARC ANDREESSEN`/`JUN 15` 各洩 1 次；MinerU 舊成品同 grep 零次（判型在 MinerU 形狀上有效之對照組）（§3.6）。

### R7 — 數字為主短行清理（通則、兩來源同享）

行 ≤3 token 且數字 token **過半** → 剝除。接線於 litedoc P1 清洗步（md_cleaner 後、與連字修復同段）。
**精度守衛（外部 review 2026-07-21 補強、採納）**：
- **markdown 語法行跳過**：行首為 `#`／`!`／`>`／`-`／`*`／`|` 者一律不碰——防誤殺 `- 1`（列表項）/`# 1`（標題）/`![alt](src)`（圖行）/`| 1 |`（表格列）；
- **數字 token 判定**：`re.match(r"^\d+([.,]\d+)*$", token)` 精確匹配整數/千分位/小數——`v1.2`/`M1` 等含字母 token 自動不計為數字（勘誤：`50%` 不在此 regex 覆蓋內、視為非數字 token——更保守、符合寧漏勿誤殺）。
**設計依據（block 分組運氣）**：源 PDF `53`/`82`/`Share` 同 block → fitz 併一行 `53 82 Share`（帶詞、逃過既有純數字行規則）；`561` 獨立 block → 獨行純數字（被既有規則殺）。既有規則只覆蓋分組運氣好的形態；R7 token 過半判定對分組**不敏感**（§3.7）。
**誠實邊界**：`561 Likes` 型（1/2 不過半）會逃——保守版先行（寧漏勿誤殺、同連字修復哲學）、真撞到再收緊。

### R8 — whole-mode 圖片過濾（關閉 filter 旁路缺口、baron 拍板選 B·2026-07-21）

**根因（§3.9 更正後真相 + v4 外部 review 擴充）**：IMG-FILTER 掛在 `_build_tiles` → **只過濾 tiles**；而 P3 以 `full_text`（`_read_source_text` **直讀 P1 原始 md**、`litedoc:503`）為素材的消費者有**三個**、全部繞過 filter：
1. **whole mode** `translate_whole(full_text)`（`litedoc:631`）——觸發面通案：`whole_mode = len<15k or not sections or degraded`（`litedoc:623`）、不只 heading 塌陷文件（本例 1 section → `is_heading_degraded` L334 `<2` 判 True）、**所有 <15k 正常短文（litedoc 大宗）同樣繞過**；
2. **is_zh 分支** `zh_text = full_text`（`litedoc:614`）；
3. **en 側（所有模式）** `en_text = full_text`（`litedoc:649`、**grep 已證無條件**）——即 **section mode 下 zh 走過濾後 tiles、en 走未過濾原文 → `final_zh.md`／`final_en.md` 圖片數量不對稱**（大改版以來即存在之雙通道失配、v4 review 發現）。
**修法（v4 單點收斂）**：P3 **單一接線點**——`full_text = self._read_source_text(ctx)`（L593）與 title echo strip 之後、`is_zh` 分支之前，對 `full_text` 做一次**行級圖片過濾**（逐行 `_FIGURE_RE`、複用 `image_filter.make_figure_filter`、`images_root=md_path.parent/"images"` 與 `_build_tiles` 同基準、DROP 即刪行、filter None→no-op、fail-open）→ 三個消費者一次全收斂＋**保證 section mode 雙語圖片 100% 對稱**。零改 `image_filter.py` 本體、零改 engine。
**實測靶**：本例 page_0 四圖（72×72 ×2／1456×5／1456×1442）過濾後應僅剩 hero；R1/R2 落地後本文件回 section mode、R8 靶轉由 <15k 短文樣本 + zh/en 圖片對稱斷言承接。

### §2.5 候選方案（Diverse Rollout）

| 決策點 | 方案 | 取捨 |
|---|---|---|
| R2 救標題 | **A（選定）repetition key + round(size)** | 一行改動、chrome 全 7.0 照剝、通案自校準 |
| | B（否決）第一頁縮窄 band | 治標——頁首 chrome 與標題距離隨版式浮動、閾值難定 |
| | C（否決）標題白名單（與 meta.title 比對豁免） | 循環依賴——meta.title 正是靠 md 抽的 |
| R7 閾值 | **A（選定）數字 token 過半（保守）** | `53 82 Share`(2/3)/`561`(1/1) 中；`Chapter 5`(1/2) 不中 |
| | B（否決）數字≥1 + 非數字全為短 UI 詞 | 覆蓋 `561 Likes` 但 `Chapter 5` 誤殺風險、複雜度升 |
| R6 落點 | **A（推薦）litedoc 呼叫端組值集合 + engine `mark_meta_lines` 純加法可選參數** | engine 零 doc_type 耦合維持、值由呼叫端注入 |
| | B（備選）僅 litedoc 端後處理 | 不動 engine、但 fitz/MinerU 之外未來 consumer 不受惠 |

---

## §3 現況與證據（本 session 實測、2026-07-21）

### §3.1 標題在文字層（推翻 title-as-image 初判）

```
源 PDF p0（頁高 1296、頂 band < 104）：
y0=  21.2 size= 7.0 BAND | SpaceX & the Sentient Sun   ← 列印頁首 chrome
y0=  71.5 size=25.6 BAND | SpaceX & the Sentient Sun   ← 真標題（band 內！）
y0= 111.2 size=14.4      | Earth is the cradle of humanity...
```

### §3.2 band 內跨頁重複 key 字級分布（R2 靶）

```
頁數=23  sizes=[7.0]        | #/#/# #:#（日期戳）
頁數=23  sizes=[7.0, 25.6]  | SpaceX & the Sentient Sun   ← 25.6 被誤殺
頁數=23  sizes=[7.0]        | 第#⾴（共#⾴）
頁數=23  sizes=[7.0]        | https://www.a#z.news/p/...
```

### §3.3 全文件字級→字元量分布（R1/R3 靶）

```
25.6:    25 | SpaceX & the Sentient Sun（真標題）
25.5:    36 | SpaceXHasLaunchedMorePayloadstoOrbit（圖表黏字·搶 h2）
23.9:    29 | ThantheRestoftheWorldCombined（圖表黏字）
20.9:   118 | Working Back from the Future（真大節 ×4·被降正文）
17.1:    41 | The Industrial Moon（真小節 ×3·被降正文）
15.2: 43305 | 正文（眾數 ✅）
```

現行 `_heading_sizes` 取前兩級 → h1=25.6（已被 R2 bug 剝除）、h2=25.5（黏字）→ 輸出僅 `## SpaceXHasLaunched...`、真標題全滅、46k 全文 1 section。

### §3.4 圖表黏字全落圖框內（R1 靶）

p6 五行（25.5/23.9/16.9/13.4/12.6）bbox 與 image rect 重疊判定全 `True`。

### §3.5 link-tiling 全文件掃描（R5 靶）

nav 行覆蓋率 84%、5 links；23 頁全掃**命中恰 1 行**、零誤殺（epigraph/正文/`Share` 按鈕字全 0%）。

### §3.6 meta 洩漏對照（R6 靶）

新成品（fitz 路）：`MARC ANDREESSEN` ×1、`JUN 15` ×1、`53 82` ×1 洩入 body；扉頁另有渲染版（重播）。MinerU 舊成品：`MARC ANDREESSEN` ×0（判型於 MinerU 形狀有效）、惟 `561`/`Share` 各 ×1（計數洩漏兩路皆有、R7 兩來源同享之依據）。

### §3.7 block 分組運氣（R7 設計依據）

```
源 PDF p0 text blocks：
block= 6 | '53' '82' 'Share'  → fitz 併一行「53 82 Share」→ 帶詞、逃過純數字行規則
block=22 | '561'              → 獨行純數字 → 被 md_cleaner Step 1 殺
```

### §3.8 R6 時序 grep 鋼鐵證據（外部 review 核心發現、2026-07-21 覆驗）

```bash
grep -n "_build_tiles\|_extract_litedoc_metadata" pipelines/litedoc_pipeline.py
# pipelines/litedoc_pipeline.py:191:tiles = self._build_tiles(md_path, output_dir, paper_name, ctx.doc_type)
# pipelines/litedoc_pipeline.py:194:meta = self._extract_litedoc_metadata(markdown_text)   ← 在 tiles 之後！
# _extract_litedoc_metadata 簽名僅吃 markdown_text（唯讀、零 tiles 依賴）→ 前移安全
```

### §3.9 小圖未濾真因（v3 更正——推翻 v1「環境問題」誤判、入刀單 R8）

**v1 誤判與更正經過（誠實留痕）**：v1 依「本機同碼複現 `_build_tiles` 三垃圾圖全 DROP」判定環境問題、不入刀單。後經逐一證偽——`.env.example` byte 比對（殺「沒 pull」）、成品 fitz 症狀（殺「沒重啟」）、baron 親查 `.env` 無 IMG_FILTER key（殺「設 false」）——環境假說全滅，回頭追代碼三 grep 定案真因：

```
標題全滅（R2 誤殺+黏字搶位）→ 1 section → is_heading_degraded（<2 判 True、section_engine:334）
→ whole_mode=True（litedoc:623）→ P3 translate_whole(full_text)
→ full_text＝_read_source_text＝直讀 P1 原始 md（litedoc:503、未過濾）
→ 圖片行原封入譯文 → 垃圾圖可見。IMG-FILTER 本身照常運作（殺的是 tiles、本模式 tiles 只餵 RAG）
```

**排查方法論教訓**：v1 驗了「filter 會殺」（producer）、未驗「輸出通道消不消費 filter 產物」（consumer）——正是 §7 接縫契約要防的 producer/consumer 脫節、此次發生在排查層而非實作層。
**可驗證預言**：真跑機 log 應含 3 條 `[img-filter] DROP`（規則① ×2／規則② ×1）——filter 有跑、白跑；E2E 時順手確認。
**處置**：入刀單 **R8**（baron 拍板選 B）；環境查證步取消。

---

## §4 跨 Phase 接縫契約

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| R6 meta 值 | P1 cover-prompt 抽 `authors`/`date`/`publisher` 值（**前移至 `_build_tiles` 之前**、§2 R6 時序） | `ingestion_engine.assemble` 新增 `meta_values` 純加法可選參數（預設 None byte 等價） | key＝**正規化行文字**（casefold/去分隔）；比對值與 cover-prompt 抽出值**同一來源同一正規化**、不得各自另抽；時序保證＝producer 先於 consumer 執行 |
| R4 譯題 | P1 title（唯一源、影子帶 ` (測試)`） | P3 `translate_unit` 餵 `_title_bare`（去後綴）；web_server 影子寫庫**唯一** append 點 | 後綴唯一 producer＝web_server（P3 譯文保證乾淨）→ 成品恰一個 `(測試)` |
| R1-R3/R5 md 產出 | FitzProcessor 產同形 .md | md_cleaner/DocAnalyzer/ingestion_engine 零感知消費 | 同形 .md 契約不變（`\n\n` 段落/`#`-`###` 標題/`![](images/)`）；R3 新增 `###` 屬既有 markdown 語法、下游天然支援 |
| R8 圖片過濾雙通道 | `make_figure_filter`（同一工廠、同一旗標、同一門檻） | **P3 單點接線**（`_read_source_text` 後、is_zh 分支前）一次覆蓋三消費者：is_zh（L614）／whole（L631）／en_text（L649）＋既有 tiles 路（`_build_tiles`） | `images_root=md_path.parent/"images"`、src basename 解析——與 `_build_tiles` **同一路徑基準**；旗標關 → 全路同步 no-op；**不變式＝section mode 雙語圖片對稱** |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| R1 誤殺「疊在圖上的正當文字」（雜誌式版面） | 🟡 中 | litedoc 大宗＝單欄文章、文繞圖罕見；閾值 50% 重疊 + 單元測試守門；fitz 路整體有 `LITEDOC_FITZ_ENABLED` env 總關回 |
| R2 改 key 使「同文同級」真內容跨頁重複被剝 | 🟢 低 | 行為與現行一致（現行已剝）、R2 只收窄不放寬 |
| R5 誤殺正當多連結行（參考文獻列） | 🟡 中 | litedoc=news/web 非學術；≥3 links + ≥60% 雙閾值實測零誤殺；無 link 註記自然停用 |
| R6 值比對誤殺正文中再次提及作者名之行 | 🟡 中 | 比對限「行文字**等於**meta 值/變體」非子字串包含——正文句含作者名不等於整行是作者名 |
| R7 誤殺比分/統計類正文行 | 🟢 低 | 需「獨立成段 + ≤3 token + 數字過半」三條件齊備；保守版先行、測試守門 |
| R8 誤刪 whole 路正當圖片行 | 🟢 低 | 複用同一 filter（同旗標/門檻/23 圖實測校正）、只刪 DROP 行 KEEP 原樣；旗標關即雙路 no-op；MinerU 來源 whole 路同受惠 |
| MinerU 路回歸 | 🟢 低 | R1/R2/R3/R5 僅 fitz_processor 內；R6/R7/R8 兩來源同享屬淨化收緊、flag off byte 等價測試 |
| golden 基準 | 🟢 低 | B 軌影子改善豁免慣例；A 軌零觸碰 |

---

## §6 不可動清單

- `processor/pdf_processor.py`（MinerU impl）／`pipeline_core.py`／A 軌處理器鏈——byte 不動
- `pipelines/section_engine.py`／`processor/rag_indexer.py`／`contracts.py`——零改
- resume／slides／book／academic 各路——零碰
- `pipelines/image_filter.py` 三規則與門檻——零改（§3.8 環境問題不動代碼）
- `LITEDOC_FITZ_ENABLED`／`IMG_FILTER_ENABLED`／`LLM_USE_GLOSSARY_ALIGN` 旗標語意——零改
- cover-prompt 既有六欄（title/authors/date/publisher/url/language）規則——零改（R6 只消費其輸出值）

---

## §7 規格依據

- `plans/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md` §2.2（同形 .md 硬契約）§5（heading 落差/多欄風險表——本案即該風險真實兌現之修復）
- `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` F6（文字層快速道）F5（meta 歸零——R6 為其 fitz 路補強）
- `WORKFLOW_SOP.md` §7（接縫契約）；`baton/README.md`（本 plan 暫存與歸檔流程）
- PIPE-LITEDOC-HOTFIX-1／SHADOW-HOTFIX-2（影子 (測試) 後綴沿革——R4 修其雙 append 回歸）

---

## §8 驗證計畫

### §8.1 自動化單元測試

- R1：p6 黏字 fixture（行 bbox 在 image rect 內）剔除；文繞圖模擬行（重疊 <50%）保留
- R2：7.0 chrome 23 頁照剝 + 25.6 同文唯一行存活（§3.2 fixture 化）
- R3：`[25.6, 20.9, 17.1]` 候選 → `#`/`##`/`###` 對應；兩級文件回歸不變
- R4：影子 P3 譯題輸入斷言不含 ` (測試)`；成品 translated_title 恰一個後綴
- R5：84%/5-links 命中、單 link 標題行/inline link 正文行不命中、無 link 註記 no-op
- R6：`MARC ANDREESSEN AND MICHAEL MCGUINESS` 行（casefold 等於 authors 值變體）剝除；正文句含 `Marc Andreessen` 不剝
- R7：`53 82 Share`/`561` 剝；`Chapter 5`/含數字完整句不剝；**markdown 語法行守衛**——`- 1`/`# 1`/`![alt](src)`/`| 1 |` 全不剝；`v1.2`/`M1` token 不計數字
- R6 時序：`_extract_litedoc_metadata` 於 `_build_tiles` 前執行之順序斷言（mock 呼叫序捕捉）
- R8：whole 路 `full_text` 含 4 圖 fixture（72×72×2/1456×5/1456×1442）→ 過濾後僅剩 hero 行；旗標關 → 四行原樣（no-op byte 等價）；filter fail-open（缺檔）→ 該行保留；**section mode 雙語對稱斷言**——`final_en` 圖片集合 == `final_zh` 圖片集合 ==（tiles 過濾後集合） |
- 全套件 920 passed 基線不退

### §8.2 手動端到端（E2E）驗證流程（baron）

1. 真跑機 log 驗 §3.9 預言：`grep "img-filter"` 應見 3 條 DROP（filter 有跑、白跑之證）——確認後環境無罪定讞（原「查 .env/重啟」前置取消、v3 已證非環境問題）
2. 重傳 `SpaceX & the Sentient Sun.pdf` 走影子軌，驗收：
   - 標題＝`SpaceX & the Sentient Sun` 系譯題、恰一個 `(測試)`、PDF /Title 同步正確
   - 結構＝`#` + `##`×4 + `###`×3（section mode、P2 摘要/滑窗/RAG 粒度回魂）
   - 扉頁後零 meta 重播、零 `53 82 Share`/`561`、零 nav 行、零圖表黏字段落
   - 垃圾小圖（72×72×2、1456×5）消失、內容圖含 hero 1456×1442 全在
3. **R8 短文靶**：另傳一份 <15k 短文（whole mode）驗垃圾圖同樣被濾（雙通道同享之 E2E 證）
4. 第二樣本（另一站列印 PDF）泛化驗證 + 掃描樣本退 MinerU 回歸

---

## §9 Open Questions（六問全數拍板 2026-07-21·baron 採納外部 review 覆核後方案、無翻案）

| # | 問題 | 拍板方案 | 理由 |
|---|---|---|---|
| Q1 | 工作流判定：BE-Hotfix（單發）or BE-Refactor（plan→tasks→C1..）？ | ✅ **BE-Refactor 常規六階段**、拆 2-3 commits（C1=R1/R2/R3/R5 fitz_processor 內聚、C2=R6/R7/**R8** 清洗與 meta〔含 R6 時序調整〕、C3=R4 影子鏈；細分由 tasks 階段定） | 八刀跨 4 檔、非單點緊急修補；R1-R3/R5 同檔內聚可一 commit |
| Q2 | R3 第三級做不做？ | ✅ **做** | 成本一行級距擴充；17.1 小節 ×3 實測存在、不做則 P2/RAG 粒度少一層 |
| Q3 | R7 閾值保守版（過半）or 收緊版？ | ✅ **保守版（過半）+ review 精度守衛**（markdown 語法行跳過 + 數字 token 精確 regex） | `561 Likes` 型漏網實測本站不存在（獨行皆純數字）；誤殺比漏殺貴 |
| Q4 | R4 修 P3 端 or web_server 端？ | ✅ **雙保險並做**：P3 餵 `_title_bare`（治本、翻譯輸入乾淨）+ web_server append 前 `endswith` 防重 | 後綴唯一 producer 歸 web_server、譯文保證乾淨；防重一行成本 |
| Q5 | R6 落點 engine 純加法 or litedoc 端後處理？ | ✅ **`ingestion_engine.assemble` 增設 `meta_values` 純加法可選參數**（值集合由呼叫端注入；內部接 `mark_meta_lines` 比對）；**並依 §3.8 前移 `_extract_litedoc_metadata` 至 `_build_tiles` 之前**（唯讀零副作用、grep 已證 L191/L194 現序顛倒） | 維持 engine 零 doc_type 耦合；未來 consumer 同受惠；預設 None byte 等價 |
| Q6 | ~~環境問題（§3.9）是否併入本案驗收？~~ | ❌ **v3 作廢**——經逐一證偽確認**非環境問題**、真因＝whole mode 繞過 filter（§3.9 更正） | 原判斷基於不完整排查（只驗 producer 未驗 consumer）；改由 Q7 承接 |
| Q7 | 小圖缺陷處置：A（僅 §3.9 更正+已知限制）or B（+R8 補刀關缺口）？ | ✅ **B（baron 拍板 2026-07-21）**——R8 行級圖片過濾；**v4 依外部 review 擴充**：接線點收斂為 P3 單點（`_read_source_text` 後）、一次覆蓋 is_zh/whole/en_text 三消費者 | litedoc 大宗＝<15k 短文即 whole mode、缺口不關等於每份短文垃圾圖照漏；**且 section mode `en_text=full_text`（L649 grep 證）致雙語圖片不對稱——單點接線順帶根治**；小刀、同旗標同門檻零新面 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | 修復 fitz 快速道首次真實 E2E 暴露之四缺陷（標題誤殺/雜訊入正文/nav 洩漏/section 塌陷）+ 影子雙後綴 |
| 用途 | 階段 2 拆 tasks 之依據；R1-R7 驗收靶全錨定 §3 實測數據 |
| 權威源 | 本檔 §1–§9 |
| 引用方 | 後續 tasks / 執行報告 / PIPE-SYNC-6 回灌 |
| 約束事項 | §6 不可動清單；baton 暫存至 Checkout 一次性歸檔 |
| 改版觸發條件 | §1–§9 任一變動 |
| 刪除條件 | 收官歸檔 plans/ 後依 WORKFLOW_SOP §2 長存 |

### §99.2 Revision 歷程

- v4 (2026-07-21)：外部 review 二輪定稿——**R8 接線點單點收斂**（P3 `_read_source_text` 後、is_zh 分支前、一次覆蓋三消費者 is_zh L614／whole L631／en_text L649）+ **新發現 grep 證實**：section mode `en_text = full_text`（L649 無條件）→ zh（過濾 tiles）/en（未過濾原文）**雙語圖片不對稱**、單點接線順帶根治並立「section mode 雙語圖片對稱」不變式（§4 R8 行 + §8.1 對稱斷言）；Q7 補 v4 擴充註
- v3 (2026-07-21)：**§3.9 誤判更正 + R8 補刀**（baron 拍板選 B）——小圖未濾真因由「.202 環境問題」更正為「whole mode 繞過 filter」（`_read_source_text` 直讀原始 md、`litedoc:503`/`:623`、`is_heading_degraded<2`；環境假說經 example 比對/fitz 症狀/baron 親查 .env 三重證偽；排查教訓＝驗 producer 未驗 consumer、§7 接縫盲點）；新增 R8 whole-mode 行級圖片過濾（複用 `make_figure_filter`、雙通道同基準、§4 接縫列）＋ §5 R8 風險 ＋ §8.1 R8 測試 ＋ §8.2 改 log DROP 預言驗證與短文靶 ＋ §9 Q6 作廢 Q7 拍板；七刀→八刀
- v2 (2026-07-21)：外部 review 定稿——**R6 物理接線時序**（`_extract_litedoc_metadata` 前移至 `_build_tiles` 之前、§3.8 grep 證 L191/L194 現序顛倒、唯讀零副作用）+ **R7 精度守衛**（markdown 語法行首 `#!>-*|` 跳過 + 數字 token `^\d+([.,]\d+)*$` 精確 regex、勘誤 `50%` 不在覆蓋屬更保守）+ §9 六問全數拍板（Q4 雙保險並做／Q5 assemble `meta_values` 參數落點）+ §4 R6 列時序保證 + §8.1 補 R6 順序斷言與 R7 守衛測試；環境註記改 §3.9
- v1 (2026-07-21)：初版——七刀（R1-R7）＋ §3 八組實測證據＋ §9 六問；診斷 session 同日落檔
