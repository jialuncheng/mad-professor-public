# IMG-FILTER 垃圾圖三規則確定性過濾 — Tasks

> 本文件為 IMG-FILTER 的 Commit 拆分清單（階段 2 產出）。
> 依 `baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（**v2·五 OQ 拍板定稿**）產出，含 4 個 Commit。
> 拆分原則：過濾器本體先行零接線 → engine 純加法注入點獨立 commit（共用關鍵模組、可逆隔離）→ litedoc 接線＋§7.2 整合收尾 → Checkout。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `pipelines/image_filter.py`（三規則過濾器本體）/ `tests/test_image_filter.py`（過濾器單元測試） |
| **修改檔案** | 6 個 | `settings.py`（三常數 C1）/ `.env.example`（C1 同步）/ `pipelines/ingestion_engine.py`（figure_filter 純加法注入 C2）/ `pipelines/litedoc_pipeline.py`（P1 pre-pass 接線 C3）/ `tests/test_ingestion_engine.py`（C2 注入測試＋C3 §7.2 整合）/ `tests/test_litedoc_pipeline.py`（C3 接線測試） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan → `plans/`、tasks → `tasks/`、C1-C3 `_執行.md` → `executions/`，產 `checkout_執行.md` 後逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST 圖片全保留後，born-digital 網頁列印 PDF 之站台 chrome（SpaceX 實證 23 圖中 3 垃圾：147×96／150×88／525×96）一併入文；Vision 描述判垃圾有實證漏判、不可當判官。
- **解法**：四原子 commit——**C1 — Image Filter Module（圖片過濾器模組）**：`pipelines/image_filter.py` 三規則本體＋stdlib 尺寸解析＋settings 三常數＋.env.example＋新測試檔、零接線；**C2 — Engine Figure-Filter Hook（引擎純加法注入點）**：`ingestion_engine` 可選 `figure_filter`（含 DROP 路徑 caption `used` 標記硬要求）；**C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）**：P1 `header_srcs` pre-pass＋注入＋§7.2 整合測試；**C_CHECKOUT — Checkout（收官歸檔）**。
- **影響範圍**：`pipelines/` 三檔（一新增）＋`settings`/`.env.example`＋測試三檔（一新增）；litedoc 唯一 consumer；slides/resume/A 軌/contracts 零碰；litedoc 影子輸出圖片集改變（golden 改善豁免＋影子 E2E）。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/image_filter.py` | **不存在** | 新建：三規則過濾器（面積／長寬比／報頭位置）＋stdlib PNG/JPEG 尺寸解析＋fail-open＋審計 log |
| `pipelines/ingestion_engine.py` | `split_blocks` figure 分支全數入 blocks、無過濾；C4 已立 `slot_context_fn` 純加法前例 | 增可選 `figure_filter=None`（含 caption `used` 標記） |
| `pipelines/litedoc_pipeline.py` | `_build_tiles` 已讀 doc_structure sidecar（報頭行界零成本可得） | pre-pass 產 `header_srcs`＋組 filter 注入 `assemble` |
| `settings.py` | 旗標慣例區（GLOSSARY 段 L114-119） | 增 `IMG_FILTER_ENABLED`／`IMG_FILTER_MIN_AREA`／`IMG_FILTER_MAX_ASPECT` |
| 依賴 | PIL 不在 requirements（實測 ModuleNotFoundError）；MinerU 實產 23/23 jpg | Q1 拍板＝stdlib header 解析、零新依賴 |

---

## §3 觀察問題

### 問題 #1：站台 chrome 垃圾圖入文（本案主標的）
- **證據**：`baton/litedoc_shadow_artifacts/.../images/` 實測——`f3f46cf1` 147×96（Share 鈕）／`b9fb4a41` 150×88（頭像裝飾）／`da5d85f9` 525×96 長寬比 5.47（互動列）；三張位於 md lines 5/8/10（doc_structure 判型行界 max end=18 內）
- **影響**：非文章內容入閱讀視圖／翻譯鏈／存儲

### 問題 #2：spec F7 原門檻有誤殺風險（plan §2.5/§2.6 已校正）
- **證據**：內容圖 `9896a383` 481×369（面積 177,489、太陽能 chart 組成圖）低於 spec 原門檻（長邊 600／面積 200k）；hero 圖 `366e4094` 位於首 heading 前孤兒區（line 35＜line 58）
- **影響**：照抄 spec 門檻會誤殺內容——tasks 一律採 plan 校正值（面積 100k 單軸＋長寬比 4.0＋規則③收窄判型行界）

### 問題 #3：Vision 不可當判官（方案否決錨）
- **證據**：design spec F7——150×88 裝飾被 Vision 描述成「兩個對比的圓形視野」當內容漏判；23 張 alt 全空（文字啟發式無訊號）
- **影響**：判定只能走確定性幾何規則

---

## §4 設計方案

### §4.1 C1 — Image Filter Module（圖片過濾器模組）
新建 `pipelines/image_filter.py`：`_read_image_size`（stdlib 二進位 header 解析——PNG 讀前 24 bytes、JPEG 掃 SOF marker／SOS·EOI 終止；Q1）＋`make_figure_filter(images_root, header_srcs, *, min_area, max_aspect, enabled)`（三規則任一命中 DROP、`Path(src).name` 路徑解析、fail-open KEEP、逐張 DROP log 審計、`enabled=False`→回 None）；settings 三常數＋`.env.example` 註記。**零接線**（engine/litedoc 未動）→ 零 runtime 變化。

### §4.2 C2 — Engine Figure-Filter Hook（引擎純加法注入點）
`ingestion_engine.split_blocks`／`build_sections`／`assemble` 貫穿可選 `figure_filter=None`；figure 分支於 caption 查找後呼 `filter(src, alt)`——False 即不入 blocks 且 **caption 行 `used[cap_idx]=True` 標記**（防孤兒圖說退化、review 硬要求）；預設 None＝現行為 byte 等價（C4 純加法紀律、引擎零 IO）。

### §4.3 C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）
`_build_tiles` 於 `assemble` 前 pre-pass：doc_structure blocks `max(end)`＝報頭行界 → 掃行界內 `![](src)` 行收 `header_srcs`（structure 缺失→∅）→ `make_figure_filter(images_root=md 同目錄 images/, header_srcs)` 注入 `assemble`；＋§7.2 跨 Phase 整合測試（實體暫存圖檔全鏈、含 481 級內文小 chart KEEP 守門）。

### §4.4 C_CHECKOUT — Checkout（收官歸檔）
Conformance＋§7.2 整合測試確認＋baton 一次性 mv＋逐檔 git add 白名單＋checkout 執行報告＋TODO 雙層結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 內容圖誤殺 | 🟡 中 | plan 校正門檻（面積 3.5×／長寬比 2.2× 邊際）；規則③收窄判型行界；fail-open；DROP 逐張 log；`IMG_FILTER_ENABLED` env 關回；§7.2 含 481 級 KEEP 守門測試 |
| engine 注入點影響既有行為（resume 間接風險） | 🟢 低 | 獨立 commit（C2）可逆隔離；預設 None byte 等價＋回歸測試；litedoc 為唯一注入者 |
| 門檻對其他版型泛化 | 🟡 中 | E2E 第二樣本抽驗；env 可調免 commit |
| stdlib 解析格式覆蓋 | 🟢 低 | PNG＋JPEG 覆蓋 MinerU 實產（23/23 jpg）；其餘格式 fail-open KEEP |
| 同檔多 commit staging 混雜 | 🟢 低 | 各 commit 各自 `.bak`＋`git diff --cached` 白名單自檢 |

---

## §6 測試計畫

> 各 Run 落地前強制 §5 SOP 一致性核查：logging `grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔>`（error 必含 exc_info=True）+ database `grep -nE "\.commit\(\)" <修改檔> | grep -v "with .*session.*begin\(\)"`（期望：無命中（合規）——本案全程零 DB）。全套件基線 **805 passed**、逐 commit 不得低於。

### §6.1 C1 驗收

```bash
ls -la pipelines/image_filter.py tests/test_image_filter.py                     # 兩檔存在非空
grep -n "def make_figure_filter\|def _read_image_size" pipelines/image_filter.py  # 命中
grep -n "IMG_FILTER_ENABLED\|IMG_FILTER_MIN_AREA\|IMG_FILTER_MAX_ASPECT" settings.py .env.example  # 兩檔命中
grep -rn "image_filter" pipelines/ingestion_engine.py pipelines/litedoc_pipeline.py  # 期望：0 命中（零接線）
grep -c "doc_type\|litedoc\|resume\|slides" pipelines/image_filter.py           # 期望：0（零文體字面量）
python3 -m pytest tests/test_image_filter.py -v && python3 -m pytest tests/ -q  # 全綠、≥805
```

### §6.2 C2 驗收

```bash
grep -n "figure_filter" pipelines/ingestion_engine.py                           # split_blocks/build_sections/assemble 貫穿命中
grep -rn "figure_filter" pipelines/litedoc_pipeline.py                          # 期望：0 命中（C2 未接線）
python3 -m pytest tests/test_ingestion_engine.py -v && python3 -m pytest tests/ -q  # 全綠、≥805
```

### §6.3 C3 驗收

```bash
grep -n "header_srcs\|make_figure_filter" pipelines/litedoc_pipeline.py         # 命中（pre-pass＋注入）
grep -rn "integration" tests/test_ingestion_engine.py | grep -i "img\|filter"   # §7.2 整合測試存在（或於 test_litedoc_pipeline）
python3 -m pytest tests/test_litedoc_pipeline.py tests/test_image_filter.py -q && python3 -m pytest tests/ -q  # ≥805
```

### §6.4 C_CHECKOUT 驗收

```bash
ls .claude-logs/baton/*IMG-FILTER* 2>/dev/null             # 期望：任務檔已清
ls .claude-logs/plans/*IMG-FILTER* .claude-logs/tasks/*IMG-FILTER* .claude-logs/executions/*IMG-FILTER*
git diff --cached --name-only                               # 實貼、須完全等於宣告清單
```

---

## §7 不可動清單

承 plan v2 §6（唯一權威源）。**嚴禁任何改動：**

- [ ] `pipelines/ingestion_engine.py` 既有函式行為（僅純加法可選參數、預設路徑 byte 等價；既有 figure 測試必須在預設 None 下原樣通過）
- [ ] `pipelines/section_engine.py`／`processor/rag_indexer.py`／三路 pipeline 之非 P1 段
- [ ] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py`（無 engine 圖片路、零碰）
- [ ] A 軌鏈全體（含 `md_restore_processor` 圖片路與 Vision alt）
- [ ] `pipelines/contracts.py`／`models.py`（零動、本案零 DB）
- [ ] Vision caption 用途（保留圖之描述）——零動；Vision 不得參與 DROP 決策
- [ ] PIPE-INGEST 既有 meta 分離／title／figure `content` 契約（本案僅 figure 入樹前加一道閘）
- [ ] 門檻採 plan v2 校正值（100k／4.0／廢長邊軸）——嚴禁回用 design spec F7 原始數字（600／200k、有實測誤殺）
- [ ] 既有 tests 斷言本體（僅允許新增）

---

## §8 推薦 Commit 拆分

### C1 — Image Filter Module（圖片過濾器模組）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `pipelines/image_filter.py`、新增 `tests/test_image_filter.py`（皆全新、無 `.bak`）；修改 `settings.py`（+ `.bak`）、修改 `.env.example`（+ `.bak`） |
| **安全性** | 🟢 高 — 純加法新模組＋常數、零接線（grep 實證）、零 runtime 變化；零 DB／零 LLM |
| **可逆性** | 🟢 高 — `git revert` 完全回滾；`.bak` 留檔 |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `settings.py` GLOSSARY 段後追加（IMG-FILTER C1 marker）：`IMG_FILTER_ENABLED = os.getenv("IMG_FILTER_ENABLED", "true").lower() in ("1","true","yes")`／`IMG_FILTER_MIN_AREA = int(os.getenv(..., "100000"))`／`IMG_FILTER_MAX_ASPECT = float(os.getenv(..., "4.0"))`（各附 plan 校正依據行註）；`.env.example` 檔尾補 IMG-FILTER 段（三常數＋關回方式）。② 新建 `pipelines/image_filter.py`（零文體字面量、docstring 標 IMG-FILTER C1 與三規則）：`_read_image_size(path) -> Optional[Tuple[int,int]]`——PNG（`\x89PNG\r\n\x1a\n` 簽名→`struct.unpack('>II', data[16:24])`）；JPEG（`\xff\xd8` 起、掃 marker 迴圈：SOF0-SOF15〔跳 C4/C8/CC〕→ `struct.unpack('>HH', seg[5:9])` 取 h,w、遇 SOS(0xDA)/EOI(0xD9) 終止防無效掃描、依 seglen 跳段）；其餘格式回 None。③ `make_figure_filter(images_root, header_srcs, *, min_area=None, max_aspect=None, enabled=None) -> Optional[Callable[[str,str],bool]]`：`enabled` 缺省讀 `settings.IMG_FILTER_ENABLED`、False→回 `None`；閉包 `_filter(src, alt="")`——規則③ `src in header_set`→DROP＋`logger.info`（src＋規則③）；實檔＝`Path(images_root)/Path(src).name`（review 硬要求）；`_read_image_size` 異常/None/非正尺寸→KEEP＋`logger.warning(..., exc_info=True 異常時)`（fail-open）；規則① `w*h < min_area`→DROP＋log（src＋`{w}x{h}`＋area＋規則①）；規則② `max(w/h,h/w) > max_aspect`→DROP＋log（規則②）；否則 KEEP。④ 新建 `tests/test_image_filter.py`：以 bytes 手工構造 header-only PNG（IHDR 尺寸即所需）與 JPEG（SOI+SOF0）暫存檔——規則① DROP（147×96 級）／KEEP（481×369 級、**守門**）＋門檻邊界（area==min_area→KEEP）；規則②（5.47 DROP／1.85 KEEP、aspect==max→KEEP）；規則③（src∈header DROP、∉ KEEP）；任一命中即 DROP 組合；fail-open ×3（缺檔／垃圾 bytes／未知格式→KEEP＋warning）；`enabled=False`→None；DROP log 內容斷言（caplog：src＋尺寸＋規則）；PNG＋JPEG 雙格式解析各一。⑤ SOP：模組零 DB；log 依規範。 |

### C2 — Engine Figure-Filter Hook（引擎純加法注入點）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/ingestion_engine.py`（+ `.bak`）、修改 `tests/test_ingestion_engine.py`（+ `.bak`） |
| **安全性** | 🟡 中 — 動共用引擎；純加法可選參數、預設 None byte 等價；獨立 commit 可逆隔離；C2 階段 litedoc 未接線（grep 實證）→ 生產零變化 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 回滾 |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 前置：C1（測試需 make_figure_filter 構造 filter；engine 本體僅依賴 Callable 介面） |
| **具體實作細節** | ① `split_blocks(lines, *, figure_filter: Optional[Callable[[str,str],bool]] = None)`：figure 分支於 `_find_caption` 之後、block append 之前加閘——`if figure_filter is not None and not figure_filter(src, alt): `→ **caption 行標記 `used[cap_idx]=True`**（若有關聯、review 硬要求防孤兒圖說）→ `i += 1; continue`（block 與 caption 皆不入）；KEEP 路徑零變。② `build_sections(lines, meta_flags, *, figure_filter=None)` 與 `assemble(markdown_text, structure, *, meta_types=..., figure_filter=None)` 貫穿傳遞（`flush()` 內 `split_blocks(buffer, figure_filter=figure_filter)`）。③ docstring 標註 IMG-FILTER C2 marker、純加法契約（預設 None＝現行為）、引擎零 IO（讀檔封裝於呼叫端 closure）。④ `tests/test_ingestion_engine.py` 擴充：預設 None 行為等價（既有 SAMPLE_MD 輸出與未傳參數完全相同）；注入 `lambda src, alt: False`→figure block 與其 caption 均不入 blocks 且 caption 不退化為 text（**孤兒圖說守門**）；注入 `lambda: True`→契約零變（content=`![alt](src)` 原樣）；選擇性 DROP（兩圖僅濾一）順序不亂。⑤ SOP 雙核查實貼（本 commit 零新 log、零 DB）。 |

### C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`（+ `.bak`）、修改 `tests/test_litedoc_pipeline.py`（+ `.bak`）、修改 `tests/test_ingestion_engine.py`（補 §7.2 整合測試、+ 本 commit 新拷 `.bak`） |
| **安全性** | 🟡 中 — 動 litedoc P1；影子軌不影響 A 軌；`IMG_FILTER_ENABLED=false` 即回全保留行為 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 回滾；env 關回不需 revert |
| **驗收 grep 條件** | 見 §6.3 |
| **依賴關係** | 前置：C1＋C2 |
| **具體實作細節** | ① `litedoc_pipeline` 增 `from pipelines import image_filter`（IMG-FILTER C3 marker）。② 新增私有輔助 `_collect_header_srcs(markdown_text, structure) -> set`：structure 無效→回 `set()`；`hdr_end = max(block["end"] for block in structure["structure"])`（容錯 int 轉換、異常回 ∅ soft）；掃 `lines[:hdr_end+1]` 以 `re.match(r"^!\[.*?\]\((.*?)\)", line.strip())` 收 src（**與 engine `_FIGURE_RE` 同語意、src 零轉換**——§4 接縫契約）。③ `_build_tiles`：讀 structure 之後、`assemble` 之前——`header_srcs = self._collect_header_srcs(markdown_text, structure)`；`fig_filter = image_filter.make_figure_filter(md_path.parent / "images", header_srcs)`（enabled 由 settings 內部判、關閉時回 None）；`assemble(..., figure_filter=fig_filter)`。④ 測試（`test_litedoc_pipeline.py`）：pre-pass 正確（行界內圖入 `header_srcs`、行界外 hero 不入）；structure 缺失→∅（①②照跑之單元斷言由 filter 測試把關）；`IMG_FILTER_ENABLED=False` monkeypatch→`assemble` 收 None（零過濾回歸）。⑤ **§7.2 跨 Phase 整合測試**（置 `test_ingestion_engine.py` 或 litedoc 測試、命名含 `integration`）：tmp_path 建擬真 md（報頭區 2 行小圖＋判型 dict＋內文 1 張 481×369 級小 chart＋1 張大圖）＋實體 header-only 圖檔 → 真 `_build_tiles` 全鏈（真 TilingProcessor bypass）→ 斷言：報頭 2 小圖 DROP（tiles 零出現）、**內文小 chart KEEP**（門檻校正守門）、大圖 KEEP 且 figure `content` 穿透 tiling、DROP 圖之 caption 未殘留。⑥ SOP 雙核查實貼。 |

### C_CHECKOUT — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：plan → `plans/`、tasks → `tasks/`、C1-C3 `_執行.md` → `executions/`；新增 `executions/2026-MM-DD_IMG-FILTER_checkout_執行.md`；`TODO.md`＋`archive/TODO_done_archive.md` 雙層結案 |
| **安全性** | 🟢 高 — 純文件歸檔 |
| **可逆性** | 🟢 高 — 檔案移動可逆 |
| **驗收 grep 條件** | 見 §6.4 |
| **依賴關係** | 前置：C1-C3 全部 ship 完（baron 回填 hash） |
| **具體實作細節** | ① Conformance 驗收（plan v2 §2 八規格項對照 C1-C3 報告；tasks §6 全綠；不可動 §7 逐項；提示詞歸檔稽核）。② **§7.2 整合測試存在且通過**確認（Checkout 必驗）。③ baton 一次性 `mv`＋逐檔顯式 `git add`（含各 commit `.bak`；嚴禁 `git add .`/`-A`/目錄）。④ `git diff --cached --name-only` 白名單自檢實貼、多一檔少一檔即停。⑤ TODO 雙層結案＋hash 回填。⑥ `checkout_執行.md`（§8 僅一行 commit、輕量慣例）。⑦ 後續銜接註記：baron 影子 E2E（plan §8.2 硬判——3 垃圾 DROP／20 內容 KEEP 含兩邊界案例／log 三筆審計）、PIPE-INGEST-FITZ（F6）、PIPE-SYNC-5 回灌（含 spec F7 門檻更正）。 |

---

## §9 Open Questions

無。（plan v2 §9 五 OQ 已全數拍板結案；本 tasks 依 Q1-Q5 定案拆分。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 IMG-FILTER 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 IMG-FILTER executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動 §7 不可動清單；門檻嚴禁回用 spec F7 原始數字；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；接縫契約唯一源＝plan v2 §4；門檻校正依據唯一源＝plan v2 §2.5/§2.6 |

### §99.2 Revision 歷程

- v1 (2026-07-20)：初版拆分——依 plan v2（五 OQ 拍板）自主規劃四 commits：C1 過濾器本體＋常數零接線 / C2 engine 純加法注入獨立 commit（共用模組可逆隔離）/ C3 litedoc pre-pass 接線＋§7.2 整合 / C_CHECKOUT；§7 增「門檻嚴禁回用 spec 原始數字」邊界
