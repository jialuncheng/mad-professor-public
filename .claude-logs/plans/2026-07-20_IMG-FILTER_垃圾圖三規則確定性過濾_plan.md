# IMG-FILTER 垃圾圖三規則確定性過濾 plan

> litedoc 圖片全保留（PIPE-INGEST 交付）之後的品質收尾：以「面積／長寬比／報頭區位置」三條確定性幾何規則，於攝入組裝階段過濾 born-digital 網頁列印 PDF 夾帶之站台 chrome（logo／masthead／社群鈕／互動列），免 Vision、免 LLM、記 log 不靜默丟。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST 使 litedoc 圖片全保留後，網頁列印 PDF 的站台 chrome 一併入文——SpaceX 實證 23 張圖中 3 張為垃圾（147×96 頭像裝飾、150×88 互動列、525×96 Share 橫條）。**Vision 描述不能當判官**（design spec F7 實證：互動列認得出、但 150×88 裝飾被描述成「兩個對比的圓形視野」當內容漏判）——Vision 會盡責描述 logo，靠描述判垃圾必漏。
- **解法**：純幾何確定性過濾（零 LLM）——①**面積**（`area < IMG_FILTER_MIN_AREA`）②**長寬比**（`max(w/h,h/w) > IMG_FILTER_MAX_ASPECT`）③**報頭區位置**（圖片行落於前段結構判型覆蓋行界內、複用 PIPE-INGEST doc_structure 既有判型），任一命中即 DROP、互為保險；hook 於 `ingestion_engine` figure block 產生處（純加法可選 `figure_filter` 注入、比照 `slot_context_fn` 範式）、過濾器本體獨立模組；**保守取向**（門檻依本 session 實測校正、fail-open、逐張 log 審計）。
- **影響**：新增 `pipelines/image_filter.py`＋`ingestion_engine` 純加法注入點＋`litedoc_pipeline` P1 接線＋`settings` 三常數；litedoc 為唯一 consumer（slides Vision 頁圖／resume 無圖／A 軌零經此路）；DB schema／contracts 零動；litedoc 影子輸出圖片集改變（golden 改善豁免＋影子 E2E）。

---

## §2 目標規格

1. **過濾器本體（新模組 `pipelines/image_filter.py`、零文體字面量）**：`make_figure_filter(images_root, header_srcs, *, min_area, max_aspect, enabled) -> Optional[Callable[[str, str], bool]]`——回傳 `filter(src, alt) -> bool`（True＝KEEP／False＝DROP）：
   - **規則①面積**：實體圖檔 `w*h < min_area`（預設 `IMG_FILTER_MIN_AREA=100_000`）→ DROP。
   - **規則②長寬比**：`max(w/h, h/w) > max_aspect`（預設 `IMG_FILTER_MAX_ASPECT=4.0`）→ DROP。
   - **規則③報頭區位置**：`src ∈ header_srcs`（呼叫端預掃注入、定義見第 3 條）→ DROP。
   - **路徑解析**：實檔定位一律 `images_root / Path(src).name`（basename 解析、相容 `images/<hash>.jpg` 等相對路徑結構；2026-07-20 review 提醒）。
   - **fail-open**：圖檔缺失／格式無法解析 → KEEP＋`logger.warning`（寧留勿誤刪）。
   - **審計不靜默**：每張 DROP `logger.info`（src＋實測尺寸＋命中規則）；`enabled=False` 或參數缺 → 回 `None`（呼叫端不注入、行為零變）。
   - 尺寸讀取方案依 §9 Q1 拍板。
2. **engine 純加法注入點**：`ingestion_engine.split_blocks`／`assemble` 增可選 `figure_filter=None`——figure block 產生時 `filter(src, alt)` 為 False 即不入 blocks（其 caption 若已關聯亦一併不入；**實作硬要求**：DROP 路徑必須將 caption 行於 `used` 陣列標 `used[cap_idx] = True`、防圖說退化為孤兒 text block 留在輸出——2026-07-20 review 提醒）；**預設 None＝現行為 byte 等價**（比照 C4 `slot_context_fn` 純加法紀律、零文體字面量、引擎自身零 IO——讀檔在呼叫端注入的 closure 內）。
3. **litedoc P1 接線與 `header_srcs` 界定**：`_build_tiles` 於 `assemble` 前 pre-pass——取 doc_structure 判型 blocks 之 `max(end)` 為**報頭行界**、掃 markdown 該行界（含）以內之 `![](src)` 行收集 `header_srcs`；組 `make_figure_filter(images_root=該 paper output images/, header_srcs, ...)` 注入 `assemble`。doc_structure 缺失（soft 路）→ `header_srcs=∅`（規則③自然停用、①②照跑）。
4. **settings 三常數**（env 可調、免 commit）：`IMG_FILTER_ENABLED`（預設 true、單點關回）／`IMG_FILTER_MIN_AREA=100000`／`IMG_FILTER_MAX_ASPECT=4.0`；`.env.example` 同步註記。
5. **門檻校正（對 design spec F7 之修正、依本 session 全 23 圖實測）**：spec 原建議「長邊 <600 或面積 <200k」會**誤殺內容圖** `481×369`（面積 177,489、太陽能對比 chart 之組成圖）——實測分布：垃圾面積 ≤50,400／內容最小面積 177,489（**3.5× 邊際**）、垃圾長寬比極端值 5.47／內容最大 1.85（**2.2× 邊際**）→ **廢除「長邊」軸、面積單軸 100k**＋長寬比 4.0；「怎麼設都不誤判」之 spec 措辭不成立、以實測邊際取代。
6. **規則③收窄（對 spec 之修正）**：spec 原述「落在 meta/報頭區（複用 meta 分離）」——實測**首 heading 前孤兒容器含正文 hero 圖**（`366e4094fa` 1082×722 無人船照、位於 line 35＜首 heading line 58），故規則③**不得**粗放為「孤兒容器即 DROP」；界定＝**doc_structure 判型覆蓋行界內**（SpaceX 判型 max end=18：3 垃圾位於 lines 5/8/10 命中、hero 圖 line 35 安全）。
7. **驗收（SpaceX 樣本重跑、硬判）**：3 垃圾全 DROP（`f3f46cf1` 147×96／`b9fb4a41` 150×88／`da5d85f9` 525×96）、**20 內容全 KEEP**（含最險兩案：`9896a383` 481×369 chart、`366e4094` 孤兒區 hero 圖）；log 中三筆 DROP 審計記錄俱在。
8. **範圍外（明文）**：Vision 不參與丟的決策（僅留給保留圖之 caption 用途、現況零動）；slides Vision 頁圖／resume 無圖零碰；A 軌 md_restore 圖片路零碰；fitz 文字層快速道屬 PIPE-INGEST-FITZ（F6）另案。

### §2.5 候選方案（Diverse Rollout）

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| 方案 A（選定） | 幾何三規則確定性過濾（面積／長寬比／報頭位置、零 LLM） | 確定性、零成本零時延；實測 3 垃圾全中／20 內容全留（門檻校正後）；門檻 env 可調 |
| 方案 B（否決） | Vision 描述判垃圾 | design spec F7 實證漏判（150×88 裝飾被描述成內容）；Vision 盡責描述 logo → 結構性漏；且每圖一次 LLM 成本 |
| 方案 C（否決） | 不濾、交前端 CSS 隱藏小圖 | 垃圾圖仍入 RAG／翻譯鏈與存儲；治標於顯示層、debt 留管線 |
| 方案 D（否決） | alt／caption 文字啟發式 | MinerU 產 alt 常為空（實測 23 張 alt 全空）、無訊號可用 |

- **選定理由**：A 為唯一同時確定性、零成本、可審計之路線；spec F7 定案方向、門檻經實測校正。
- **否決留痕**：B-D 留底如上（B 之實證見 design spec F7「關鍵反直覺」）。

---

## §3 現況與證據

- **pipelines/ingestion_engine.py**：`split_blocks`（figure block 產生處、`_FIGURE_RE` 命中→`{"type":"figure","src","alt","content"}`）——現況**無任何過濾**、全數入 blocks；`assemble` 為頂層入口。C4 已立 `slot_context_fn` 純加法注入前例。
- **pipelines/litedoc_pipeline.py**：`_build_tiles`（PIPE-INGEST C2）——讀 cleaned md＋doc_structure sidecar→`assemble`→processed.json→tiling；doc_structure 判型 blocks（`{start,end,type}`）已在現場、報頭行界可零成本取得。
- **settings.py**：旗標慣例區（`LLM_USE_GLOSSARY_ALIGN` L114 等）——三常數依同式追加。
- **依賴**：`requirements.txt:26` PyMuPDF==1.27.2.3（已 pin）；**PIL／Pillow 不在依賴**（本 session 實測 `ModuleNotFoundError`）→ 尺寸讀取需 stdlib header 解析或 fitz（§9 Q1）。
- **實測 23 圖全量分布**（`baton/litedoc_shadow_artifacts/.../images/`、stdlib header 解析、本 session 實跑）：

| 類別 | 圖 | 尺寸 | 面積 | 長寬比 | 命中 |
|---|---|---|---|---|---|
| 垃圾 | `f3f46cf1`（Share 鈕） | 147×96 | 14,112 | 1.53 | ①（③ lines 5-10 報頭區） |
| 垃圾 | `b9fb4a41`（頭像裝飾） | 150×88 | 13,200 | 1.70 | ①③ |
| 垃圾 | `da5d85f9`（互動列橫條） | 525×96 | 50,400 | **5.47** | ①②③ |
| **內容邊界** | `9896a383`（太陽能 chart 組成圖、§2.5 誤殺風險案例） | 481×369 | **177,489** | 1.30 | 零命中（KEEP ✓） |
| **內容邊界** | `366e4094`（hero 無人船照、首 heading 前孤兒區） | 1082×722 | 781,204 | 1.50 | 零命中（KEEP ✓、規則③收窄後） |
| 內容其餘 ×18 | — | 長邊 1292-1718 | 940k-2.40M | 1.04-1.85 | 零命中 |

- **報頭區證據**：doc_structure 判型 blocks max end＝18；3 垃圾圖位於 md lines 5／8／10（首 heading `## Solar Arrays...`＝line 58 之前、且在判型行界內）；hero 圖 line 35（行界外）。
- **alt 全空實證**：23 張 `![](images/...)` alt 均為空字串（方案 D 否決依據）。

### §3.1 grep 鋼鐵證據

```bash
# figure block 產生處（hook 點）
grep -n "_FIGURE_RE\|\"type\": \"figure\"" pipelines/ingestion_engine.py
# → _FIGURE_RE 定義 + split_blocks figure 分支（content=![alt](src)）

# doc_structure 已在 litedoc P1 現場（報頭行界零成本）
grep -n "doc_structure\|structure = json.loads" pipelines/litedoc_pipeline.py
# → _build_tiles sidecar 讀取（PIPE-INGEST C2）

# PIL 不在依賴（本 session 實測 ModuleNotFoundError）；PyMuPDF 已 pin
grep -n -i "pillow\|PyMuPDF" requirements.txt   # → 僅 :26 PyMuPDF==1.27.2.3

# 23 圖尺寸分布：stdlib PNG/JPEG header 解析實跑（輸出見 §3 表）
```

---

## §4 跨 Phase 接縫契約

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| litedoc P1 pre-pass → filter 規則③ | P1 掃報頭行界內 `![](src)` 行產 `header_srcs` 集合 | `make_figure_filter` closure 以 **src 字串**比對 | key＝markdown 之 **src 原文字串**（與 engine `_FIGURE_RE` 抽出之 src **同一來源行、零轉換**）；行界＝doc_structure 判型 blocks `max(end)`（與 PIPE-INGEST meta 分離同一 sidecar 快照） |
| filter → engine figure 分支 | `make_figure_filter` 回 `filter(src, alt) -> bool` | `split_blocks` figure block 產生前呼叫、False 即不入 blocks（含已關聯 caption） | 注入介面＝可選參數 `figure_filter`（預設 None 行為零變、C4 純加法範式）；engine 零 IO——讀檔封裝於呼叫端 closure |
| filter → 圖檔實體 | P1 注入 `images_root`（該 paper output `images/`） | filter 以 `images_root / basename(src)` 解析實檔讀尺寸 | src 相對路徑（`images/<hash>.jpg`）與 MinerU 落檔**同一目錄基準**（PIPE-INGEST 既有）；解析失敗 fail-open KEEP |

填寫規範見 `ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 內容圖誤殺（過濾器最大風險） | 🟡 中 | 門檻依實測校正（面積 3.5×／長寬比 2.2× 邊際、廢長邊軸）；規則③收窄至判型行界；fail-open；逐張 log 審計可追；`IMG_FILTER_ENABLED` env 單點關回；驗收含兩個最險邊界案例硬判 |
| engine 注入點影響既有行為 | 🟢 低 | 純加法可選參數、預設 None byte 等價（C4 前例＋identity 式回歸測試）；litedoc 為唯一注入者 |
| 不同文章版型之門檻泛化性 | 🟡 中 | SpaceX 單樣本校正——第二樣本（`The_hidden_risks...`）納入 E2E 抽驗；門檻 env 可調免 commit；保守取向（僅丟明確迷你/極端） |
| doc_structure 缺失時規則③失效 | 🟢 低 | 設計內降級（`header_srcs=∅`、①②照跑）；SpaceX 3 垃圾單靠①即全中（③屬保險） |
| 圖檔格式非 PNG/JPEG | 🟢 低 | fail-open KEEP＋warning；MinerU 實際產物為 jpg（23/23） |

---

## §6 不可動清單

- [ ] `pipelines/ingestion_engine.py` 既有函式行為（僅純加法可選參數；預設路徑 byte 等價）
- [ ] `pipelines/section_engine.py`／`processor/rag_indexer.py`／三路 pipeline 之非 P1 段——零碰
- [ ] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py`——零碰（無 engine 圖片路）
- [ ] A 軌鏈全體（`md_restore_processor` 圖片路含 Vision alt）——零碰
- [ ] `pipelines/contracts.py` 凍結合約／`models.py`——零動
- [ ] Vision caption 用途（保留圖之描述、現況）——零動；Vision 不得參與 DROP 決策
- [ ] PIPE-INGEST 既有 meta 分離／title／figure content 契約——零動（本案僅在 figure 入樹前加一道閘）
- [ ] 既有 tests 斷言本體（僅允許新增；engine 既有 figure 測試必須在預設 None 下全數原樣通過）

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| **design spec F7 定案** | `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`——三規則方向／Vision 反直覺實證／保守＋log 原則／「接 PIPE-INGEST 圖片保留後」順序 |
| **spec 門檻修正宣告** | 本 plan §2.5／§2.6——spec 原門檻（長邊 600／面積 200k）與「零誤判」措辭經全 23 圖實測**修正**（481×369 內容 chart 誤殺、孤兒區 hero 圖）；PIPE-SYNC-5 回灌時一併更正 spec F7 數字 |
| 前置交付 | PIPE-INGEST（圖片全保留＋meta 分離＋doc_structure sidecar 讀取）——`plans/2026-07-18_PIPE-INGEST_..._plan.md` |
| 純加法注入前例 | GLOSSARY-TERMMAP C4 `slot_context_fn`（`pipelines/section_engine.py`）；引擎零 IO 紀律 |
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| BE-Refactor 必讀 SOP | `sop/2026-05-23_logging_SOP_手冊.md`、`sop/2026-05-23_database_SOP_手冊.md`（本案零 DB；log 審計依 logging SOP） |
| 進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 實測證據 | `baton/litedoc_shadow_artifacts/.../images/` 23 圖 stdlib 實測（§3 表）＋ md 行號對照 |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：
  ```bash
  venv/bin/python -m pytest tests/ -q    # 基線 805 passed、不得低於基線
  ```
- **預計新增的測試**：
  - `tests/test_image_filter.py`（新檔）：規則①面積（14k DROP／177k KEEP、門檻邊界值）；規則②長寬比（5.47 DROP／1.85 KEEP）；規則③（src ∈ header_srcs DROP、∉ KEEP）；任一命中即 DROP 之組合；fail-open（缺檔／壞檔 KEEP＋warning）；`enabled=False`→回 None；DROP log 含 src＋尺寸＋規則（caplog 斷言）；PNG 與 JPEG 兩格式尺寸解析。
  - `tests/test_ingestion_engine.py` 擴充：`figure_filter=None` 預設行為 byte 等價（既有 figure 測試原樣過）；注入 filter 時 DROP 之 figure（含其 caption）不入 blocks、KEEP 者 content 契約零變。
  - `tests/test_litedoc_pipeline.py` 擴充：P1 接線——報頭行界 pre-pass 產 `header_srcs` 正確（判型行界內圖收入、行界外 hero 圖不收）；doc_structure 缺失→③停用①②照跑；`IMG_FILTER_ENABLED=False`→零過濾回歸。
  - **§7.2 跨 Phase 整合測試**：擬真 md（報頭區 2 小圖＋內文 1 小 chart 圖 481 級＋1 大圖）＋判型 dict＋實體暫存圖檔 → P1 `_build_tiles` 全鏈 → 斷言：報頭小圖 DROP、**內文小 chart KEEP**（門檻校正之守門測試）、大圖 KEEP 且 figure `content` 穿透 tiling。

### §8.2 手動端到端（E2E）驗證流程（baron、測試服）

1. 重傳 `SpaceX & the Sentient Sun.pdf` 走 litedoc 影子軌。
2. **硬判**：閱讀視圖 3 垃圾圖（Share 鈕／頭像裝飾／互動列橫條）消失；內容圖 20 張全在——特別抽驗 `9896a383`（太陽能 chart 組成圖）與 `366e4094`（hero 無人船照）；後端 log 三筆 DROP 審計記錄（src＋尺寸＋規則）。
3. 重傳第二樣本（`The_hidden_risks_in_Taiwan_s_boom`）驗門檻泛化、無內容圖誤殺。
4. RAG 一輪迴歸（圖片過濾不影響 text chunks）。

---

## §9 Open Questions

> **五項均已於 2026-07-20 由 baron 拍板、全數採納推薦方案**（review 併兩條實作硬要求：DROP 路徑 caption `used[cap_idx]=True` 標記防孤兒圖說退化、路徑解析 `images_root / Path(src).name`——均已回灌 §2.1/§2.2）；本節留痕為決策紀錄、後續 tasks 拆分直接引用。

| 開放問題 | 拍板方案（✅ 定案） | 理由 |
|---|---|---|
| Q1：圖檔尺寸讀取方案 | ✅ **stdlib 二進位 header 解析（PNG＋JPEG）**、解析失敗 fail-open KEEP（PNG 讀前 24 bytes；JPEG 掃 SOF marker、SOS/EOI 終止防無效掃描） | 零新依賴；MinerU 實產 23/23 皆 jpg、兩格式全覆蓋（本 session 已以 stdlib 實測全量成功）；fitz 開圖檔屬 document API 殺雞用牛刀；Pillow 新依賴違 YAGNI |
| Q2：`IMG_FILTER_ENABLED` 總開關是否設置 | ✅ **設置**（settings/env、預設 true、單點關回） | 過濾屬「刪內容」型操作、單點關回保險成本一行；比照旗標慣例 |
| Q3：門檻預設值 | ✅ **MIN_AREA=100000、MAX_ASPECT=4.0、廢長邊軸** | 實測邊際：面積垃圾 ≤50.4k／內容 ≥177k（100k 居中 3.5×/1.77× 雙向緩衝）；長寬比 5.47 vs 1.85（4.0 居中）；長邊軸會誤殺 481×369 內容圖、廢除 |
| Q4：DROP 之 figure 的關聯 caption 處置 | ✅ **一併不入 blocks**（`used[cap_idx]=True` 標記、實作硬要求入 §2.2） | 圖已除、孤兒圖說即 PIPE-LITEDOC-QA 缺陷同型噪音；caption 若誤含正文（罕見）可由 fail-open 傾向與門檻保守性兜底 |
| Q5：過濾器歸屬 | ✅ **獨立 `pipelines/image_filter.py`**（engine 零 IO 紀律、book/academic 可繼承） | engine 零 IO 紀律（讀檔封裝於呼叫端注入之 closure）；未來 book/academic 文字路直接復用；與 section_engine/ingestion_engine 職責分離 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 IMG-FILTER 垃圾圖三規則確定性過濾的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 IMG-FILTER tasks / 執行報告；PIPE-SYNC-5 回灌案（spec F7 門檻更正） |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格；引擎注入紀律唯一源＝section_engine 設計原則；spec F7 為方向依據、門檻數字以本 plan 實測校正為準（回灌後 spec 同步） |

### §99.2 Revision 歷程

- v2 (2026-07-20)：review 定稿——§9 五 OQ 全數拍板採納推薦（Q1 stdlib 解析／Q2 設總開關／Q3 100k+4.0 廢長邊／Q4 caption 一併不入／Q5 獨立模組）；§2.1 補路徑解析硬要求（`images_root / Path(src).name`）；§2.2 補 caption DROP 路徑 `used[cap_idx]=True` 標記硬要求（防孤兒圖說退化、review 實作提醒）
- v1 (2026-07-20)：初版——依 design spec F7 立案；全 23 圖 stdlib 實測校正門檻（**廢長邊軸**、面積 100k／長寬比 4.0、雙向邊際量化）＋規則③收窄至判型行界（兩個誤殺風險案例實證：481×369 內容 chart、孤兒區 hero 圖）；§2.5 四候選留痕（Vision 判官否決有 spec 實證）；§4 凍結三條 handoff（src 同源零轉換／注入介面純加法／images_root 同目錄基準）；§9 五 OQ
