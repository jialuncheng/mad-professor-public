# FITZ-HOTFIX-1 fitz 路標題救回與雜訊通則修復 — Tasks

> 本文件為 FITZ-HOTFIX-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_plan.md`（**v4**、六問全數拍板）產出，含 3 個開發 Commit + 1 個 Checkout。
> ⚠️ 提示詞標「plan v3」，實檔 §99.2 已至 **v4**（外部 review 二輪定稿、R8 單點收斂 + 雙語圖片對稱不變式）——本拆分依 **v4** 為準。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | — |
| **修改檔案** | 6 個 | `processor/fitz_processor.py`（R1/R2/R3/R5）／`pipelines/ingestion_engine.py`（R6 `meta_values` 純加法）／`pipelines/litedoc_pipeline.py`（R6 時序前移+接線、R7 清洗步、R4 譯題、R8 P3 圖片過濾）／`tests/test_fitz_processor.py`／`tests/test_ingestion_engine.py`／`tests/test_litedoc_pipeline.py` |
| **零改檔案（原盤點列入、經 grep 更正）** | 1 個 | `web_server.py` — **R4 寫庫端防重已存在**（L775 `endswith(" (測試)")`、PIPE-RESUME SHADOW-HOTFIX-2 落地）→ Q4「雙保險」之 web_server 半邊**已滿足**、本案零改（證據見 §3 問題 #4） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan/tasks/C1-C3 執行報告 → `plans/` + `tasks/` + `executions/` + 逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST-FITZ 落地後首次真實 E2E（SpaceX 樣本走 fitz 快速道）暴露四缺陷——標題全滅（epigraph/圖表黏字搶位）／meta・計數・nav 雜訊入正文／46k 全文塌成 1 section／影子雙 `(測試)` 後綴；另 v3/v4 追加揭露 whole-mode 與 en 側繞過 IMG-FILTER（雙語圖片不對稱）。
- **解法**：三個原子 commit 按「檔案內聚 + Phase 邊界」切——`C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）`（R1/R2/R3/R5、單檔 `fitz_processor.py`）→ `C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）`（R6 含時序前移 + R7、engine 純加法 + litedoc P1）→ `C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）`（R4 + R8、litedoc P3 兩處單點）→ `C_CHECKOUT — 收官歸檔（收官歸檔）`。
- **影響範圍**：litedoc 攝入/翻譯鏈 + fitz impl + engine 純加法參數；MinerU impl／A 軌／resume／slides／section_engine／rag_indexer／image_filter 本體／web_server 零改。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀（grep 實證） | 缺失 / 待處理問題 |
|---|---|---|
| `processor/fitz_processor.py` | `_repetition_key` L57（純數字歸一文字）／`_collect_page` L99（收行、無圖框判定）／`in_band` L119／`_heading_sizes` L207 回 `(h1, h2)` L224／`_heading_level` L227 兩級 | R1 圖框內文字未排除；R2 key 缺字級致真標題被自身頁首 chrome 誤殺；R3 僅兩級；R5 無 link-tiling 判定 |
| `pipelines/litedoc_pipeline.py` | `_build_tiles` **L191** 早於 `_extract_litedoc_metadata` **L194**（時序顛倒）／L207 影子加後綴／L593 `full_text=_read_source_text`、L596 `_title_bare` 現成／L614 `zh_text=full_text`／L623 `whole_mode`／L631 `translate_whole`／L634・L647 `translate_unit(title)` **餵帶後綴 title**／L649 `en_text=full_text` 無條件 | R6 需前移 meta 抽取；R7 清洗步未有數字短行規則；R4 譯題輸入含後綴；R8 三消費者繞過 filter |
| `pipelines/ingestion_engine.py` | `mark_meta_lines(lines, structure, meta_types, title_idx)` L67-72 | R6 需純加法 `meta_values` 可選參數 |
| `web_server.py` | **L773-776 已有 `endswith(" (測試)")` 防重**（SHADOW-HOTFIX-2 區塊 L770-777） | **零缺失** — Q4 雙保險之寫庫端已滿足、本案零改 |

---

## §3 觀察問題

### 問題 #1：真標題被自身列印頁首誤殺（R2·通案）
- **證據**：plan §3.2——band 內跨頁重複 key 四組，標題 key `sizes=[7.0, 25.6]`；7.0＝`document.title` chrome、25.6＝真標題（plan §3.1 y0=71.5 < band 界 104）。
- **影響**：**每一份瀏覽器列印 PDF 的真標題都必然撞上自己的頁首 key**（非本樣本特例）→ 標題全滅 → 連鎖 1 section/whole_mode。

### 問題 #2：圖表黏字搶 heading（R1/R3）
- **證據**：plan §3.3/§3.4——p6 五行黏字（25.5/23.9/16.9…）bbox 全落 image rect 內；現行取前兩級 → h2=25.5 黏字、真大節 20.9 與小節 17.1 被降正文。
- **影響**：輸出僅 `## SpaceXHasLaunched...`、46k 全文 1 section。

### 問題 #3：nav / meta / 計數雜訊入正文（R5/R6/R7）
- **證據**：plan §3.5（nav 行 5 links 覆蓋 84%、全 23 頁命中恰 1 行零誤殺）／§3.6（`MARC ANDREESSEN`・`JUN 15` 各洩 1 次、MinerU 對照組 0 次）／§3.7（`53 82 Share` 同 block 併行逃過純數字規則）。

### 問題 #4：影子雙後綴 —— ⚠️ plan↔代碼落差（本階段 grep 更正）
- **plan v4 §2 R4 敘述**：「web_server 影子寫庫再 append（`web_server.py:776`、**無防重**）」。
- **實測反證**：
  ```
  web_server.py:770  # === [PIPE-RESUME SHADOW-HOTFIX-2 START] ===
  web_server.py:775      if _tt_val and not str(_tt_val).endswith(" (測試)"):
  web_server.py:776          meta_dict['translated_title']['value'] = f"{_tt_val} (測試)"
  ```
  **防重守衛已存在**（SHADOW-HOTFIX-2 落地）。
- **真因重判**：P3 L634/L647 `translate_unit(title)` 餵**帶後綴** title → LLM 回傳**後綴變體**（全形 `（測試）`／空格差異／譯寫 `(Test)`）→ 半形 `endswith` 失配 → web_server 再 append → 成品出現兩個形態不一的後綴。
- **處置**：R4 治本點**收斂為單一 P3 端**（餵 `_title_bare`、LLM 永不見後綴 → 輸出恆乾淨 → 既有 endswith 守衛恰好生效一次）；`web_server.py` **本案零改**（Q4「雙保險」之寫庫端已由 SHADOW-HOTFIX-2 滿足）。
- **⚠️ 提請 baron 確認**：若仍欲強化寫庫端（正規化全形/空白後再比對），屬**額外加碼**、非本案必需；建議維持零改（P3 治本後變體不再產生、加碼屬 YAGNI）。

### 問題 #5：whole/en 側繞過 IMG-FILTER（R8）
- **證據**：plan §3.9 + v4 review——`_read_source_text` 直讀原始 md（L503）；三消費者 is_zh（L614）／whole（L631）／**en_text（L649 無條件）** 全繞過；致 whole 模式垃圾圖可見 + **section mode 雙語圖片不對稱**。

---

## §4 設計方案

### §4.1 C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）
單檔 `processor/fitz_processor.py` 四刀內聚：R1 圖框內文字排除（`_collect_page` 收行時 bbox×image rect 重疊 >50% 剔除）→ R2 `_repetition_key` 加 `round(size,1)`（救標題、chrome 照剝）→ R3 `_heading_sizes` 回三級 + `_heading_level` 對應 `#`/`##`/`###` → R5 link-tiling nav 剝除（≥3 links 且覆蓋 ≥60%）。四刀有序：R1 先淨化候選、R3 三級階梯才成立（plan §2 R3 實測靶 `[25.6, 20.9, 17.1]` 為 R1 後結果）。

### §4.2 C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）
R6：`ingestion_engine.mark_meta_lines`/`assemble` 增 `meta_values` 純加法可選參數（預設 None byte 等價）+ **litedoc `_extract_litedoc_metadata` 前移至 `_build_tiles` 之前**（plan §3.8 grep 證 L191/L194 顛倒、唯讀零副作用）+ 呼叫端組值集合注入。R7：litedoc P1 清洗步（md_cleaner 後、與連字修復同段）加數字為主短行清理（≤3 token 且數字 token 過半、markdown 語法行首 `#!>-*|` 跳過、數字 token `^\d+([.,]\d+)*$`）。

### §4.3 C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）
R4：P3 L634/L647 `translate_unit(title)` → `translate_unit(_title_bare)`（治本、`_title_bare` L596 現成）。R8：P3 單點接線——`full_text = _read_source_text(ctx)` 與 title echo strip 之後、`is_zh` 分支之前，對 `full_text` 行級圖片過濾（複用 `image_filter.make_figure_filter`、`images_root=md_path.parent/"images"` 同基準、DROP 即刪行、filter None→no-op、fail-open）→ 一次覆蓋 is_zh/whole/en_text 三消費者 + 立「section mode 雙語圖片對稱」不變式。

### §4.4 C_CHECKOUT — 收官歸檔（收官歸檔）
Conformance（plan v4 §2 八刀對照 + §8.1 測試 + §7.2 必驗）→ TODO 雙層結案 → baton 一次性 `mv` + 逐檔 `git add` → `checkout_執行.md`（staged-set 實貼）→ `/tmp` msg。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| R1 誤殺文繞圖之正當文字 | 🟡 中 | 50% 重疊閾值 + 單元測試（重疊 <50% 保留）；`LITEDOC_FITZ_ENABLED` env 總關回 |
| R5 誤殺參考文獻等多連結行 | 🟡 中 | ≥3 links + ≥60% 雙閾值（plan §3.5 實測零誤殺）；無 link 註記自然停用 |
| R6 誤殺正文再提及作者名之行 | 🟡 中 | 比對限「整行**等於**meta 值/變體」非子字串包含；測試守門（正文句含作者名不剝） |
| R7 誤殺比分/統計行 | 🟢 低 | 三條件齊備（≤3 token + 數字過半 + 非 markdown 語法行）；保守版先行 |
| R6 時序前移引入副作用 | 🟢 低 | `_extract_litedoc_metadata` 唯讀單參數（grep 證）；C2 加呼叫序斷言測試 |
| R8 誤刪正當圖片行 | 🟢 低 | 複用同一 filter（同旗標/門檻）；只刪 DROP、KEEP 原樣；旗標關雙路 no-op |
| MinerU 路回歸 | 🟢 低 | R1/R2/R3/R5 僅 fitz_processor 內；R6/R7/R8 屬兩來源同享之淨化收緊；flag off byte 等價測試 |
| golden 基準 | 🟢 低 | B 軌影子改善豁免慣例；A 軌零觸碰 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "def _repetition_key" -A 4 processor/fitz_processor.py      # 期望：含 round(size, 1)
grep -n "def _heading_sizes" -A 2 processor/fitz_processor.py       # 期望：回 (h1, h2, h3)
grep -n "image rect\|_rect_overlap\|link" processor/fitz_processor.py  # 期望：R1/R5 判定命中
venv/bin/python -m pytest tests/test_fitz_processor.py -q            # 期望：新測試全過
```
測試（plan §8.1 靶）：R1 黏字 fixture 剔除 / 文繞圖（重疊 <50%）保留；R2 7.0 chrome 剝 + 25.6 同文存活；R3 三級對應 + 兩級文件回歸；R5 84%/5-links 命中、單 link 標題行與 inline link 正文行不命中、無 link 註記 no-op。

### §6.2 C2 驗收

```bash
grep -n "meta_values" pipelines/ingestion_engine.py pipelines/litedoc_pipeline.py  # 期望：純加法參數 + 呼叫端注入
grep -n "_extract_litedoc_metadata\|_build_tiles(md_path" pipelines/litedoc_pipeline.py  # 期望：meta 行號 < tiles 行號
venv/bin/python -m pytest tests/test_ingestion_engine.py tests/test_litedoc_pipeline.py -q
```
測試：R6 值比對剝除（`MARC ANDREESSEN AND MICHAEL MCGUINESS` 剝、正文句含 `Marc Andreessen` 不剝）+ **呼叫序斷言**（meta 抽取先於 assemble、mock 捕捉）+ `meta_values=None` byte 等價；R7 `53 82 Share`/`561` 剝、`Chapter 5`/完整句不剝、**markdown 語法行守衛**（`- 1`/`# 1`/`![alt](src)`/`| 1 |` 全不剝）、`v1.2`/`M1` 不計數字。

### §6.3 C3 驗收

```bash
grep -n "translate_unit(_title_bare\|translate_unit(title" pipelines/litedoc_pipeline.py  # 期望：譯題餵 _title_bare
grep -n "make_figure_filter" pipelines/litedoc_pipeline.py            # 期望：P1 _build_tiles + P3 單點兩處
git diff --stat web_server.py                                         # 期望：零 diff（防重已存在）
venv/bin/python -m pytest tests/test_litedoc_pipeline.py -q
```
測試：R4 譯題輸入斷言不含 ` (測試)`、成品 translated_title 恰一後綴；R8 whole 路四圖 fixture → 僅剩 hero、旗標關四行原樣（no-op）、fail-open 缺檔保留、**section mode 雙語對稱**（`final_en` 圖集 == `final_zh` 圖集 == tiles 過濾後集合）。

### §6.4 全域防呆 + §7.2 整合（每 commit / 收官）

```bash
venv/bin/python -m pytest tests/ -q     # 期望：920 基線不退、逐 commit 遞增
git diff --stat processor/pdf_processor.py pipelines/section_engine.py pipelines/image_filter.py processor/rag_indexer.py contracts.py web_server.py  # 期望：全零 diff
```
**§7.2 跨 Phase 整合測試（Checkout 必驗）**：實體 born-digital PDF（含列印頁首 chrome + 三級標題 + 圖框黏字 + nav 行 + meta 行 + `53 82 Share` + 垃圾圖）→ 真 FitzProcessor → 真 cleaner/repair/R7 → 真 `_build_tiles`（R6 meta_values）→ 真 P3（R4/R8）端到端，斷言：`#`+`##`+`###` 三級結構成立、標題正確、nav/meta/計數/黏字零殘留、雙語圖片對稱。

### §6.5 SOP 一致性核查（每 commit 落地前必貼）

```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔.py>   # logger.error 必含 exc_info=True
grep -nE "\.commit\(\)" <修改檔.py> | grep -v "with .*session.*begin\(\)"      # 期望：無命中（本案零 DB）
```

---

## §7 不可動清單

- [ ] `processor/pdf_processor.py`（MinerU impl）／`pipeline_core.py`／A 軌處理器鏈 — byte 不動
- [ ] `pipelines/section_engine.py`／`processor/rag_indexer.py`／`contracts.py` — 零改
- [ ] `pipelines/image_filter.py` 三規則與門檻 — 零改（R8 只複用 `make_figure_filter`）
- [ ] **`web_server.py`** — 零改（R4 寫庫端防重已存在、§3 問題 #4）
- [ ] resume／slides／book／academic 各路 — 零碰
- [ ] `LITEDOC_FITZ_ENABLED`／`IMG_FILTER_ENABLED`／`LLM_USE_GLOSSARY_ALIGN` 旗標語意 — 零改
- [ ] cover-prompt 既有六欄（title/authors/date/publisher/url/language）規則 — 零改（R6 只消費其輸出值）
- [ ] 同形 .md 硬契約（`\n\n` 段落／`![](images/)`／`page_{page_idx}_{xref}` 命名） — 不變（R3 新增 `###` 屬既有 markdown 語法）
- [ ] **嚴禁** `git commit`／`git push`（baron 手動）

---

## §8 推薦 Commit 拆分

### C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `processor/fitz_processor.py`、`tests/test_fitz_processor.py` + 2 個 `.bak`（`.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_fitz_processor.py.bak`／`..._C1_test_fitz_processor.py.bak`） |
| **安全性** | 🟡 中 — 觸碰 fitz 攝入核心啟發式（標題判定/行收集）；但單檔內聚、MinerU 路零涉、`LITEDOC_FITZ_ENABLED` env 總關回 |
| **可逆性** | 🟢 高 — `git revert C1`；或 env 關回退 MinerU |
| **驗收 grep 條件** | §6.1 全項 + §6.4 全域防呆 + §6.5 SOP 雙核查 |
| **依賴關係** | 無前置 |
| **具體實作細節** | **R1 圖框內文字排除**：`_collect_page`（L99）收行時，先取該頁 image rects（`page.get_image_rects` 或既有 images 收集結果之 rect），對每行 bbox 計算與任一 image rect 之重疊面積比（`intersect` 面積 / 行 bbox 面積），**> 0.5 者剔除**（不入 lines）；圖本身仍作 figure 保留、資訊不丟。**R2 repetition key 加字級**：`_repetition_key`（L57）由 `re.sub(r"\d+","#",text)` 改為回 `(數字歸一文字, round(size,1))` 之複合 key（或字串拼接 `f"{norm}|{round(size,1)}"`）；呼叫端 `_repeated_band_keys` 與剝除判定同步用複合 key——7.0pt chrome 23 頁照剝、25.6 真標題全文件唯一故存活。**R3 heading 第三級**：`_heading_sizes`（L207）回 `(h1, h2, h3)`＝候選前三級（`candidates[0:3]`、不足補 0.0）；`_heading_level`（L227）簽名對應擴充、`size >= h3` 回 3 → `###`；`_assemble` 之 `"#" * level` 天然支援。**R5 link-tiling nav 剝除**：`_collect_page` 取 `page.get_links()` 之 rect 清單；行 bbox 被 **≥3 個獨立 link rect** 覆蓋合計 **≥60% 面積** → 剔除；無 link 註記（空清單）→ 規則自然停用。四刀有序落地（R1 先淨化 → R3 三級階梯方成立）。日誌依 logging SOP（異常 `exc_info=True`）。測試依 §6.1 靶。 |

### C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/ingestion_engine.py`、`pipelines/litedoc_pipeline.py`、`tests/test_ingestion_engine.py`、`tests/test_litedoc_pipeline.py` + 4 個 `.bak`（`.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_*.bak`） |
| **安全性** | 🟡 中 — 含 P1 步序調整（meta 抽取前移）；但唯讀零副作用（grep 證）、engine 參數純加法預設 None byte 等價 |
| **可逆性** | 🟢 高 — `git revert C2`；或對照 `.bak` 還原 |
| **驗收 grep 條件** | §6.2 全項 + §6.4 全域防呆 + §6.5 SOP 雙核查 |
| **依賴關係** | 無前置（與 C1 正交；R6/R7 為兩來源同享之淨化、不依賴 fitz 改動） |
| **具體實作細節** | **① R6 engine 純加法**：`mark_meta_lines`（L67-72）增可選參數 `meta_values: Optional[Set[str]] = None`（**預設 None → 行為 byte 等價**）；內部於既有判型標記後，對未標 meta 之行做**正規化比對**（`casefold()` + 去分隔符/多餘空白）——等於 `meta_values` 任一值或其變體者追加標為 meta；`assemble` 同步貫穿該參數（簽名末位、預設 None）。**② R6 litedoc 時序前移**：將 `meta = self._extract_litedoc_metadata(markdown_text)`（現 L194）**移至 `tiles = self._build_tiles(...)`（現 L191）之前**（該函式簽名單參數唯讀 `markdown_text`、零 tiles 依賴、plan §3.8 grep 已證安全）；`_resolve_title`/`source_lang` 合成等後續消費以 diff 最小為準（一併前移或原位皆可）。**③ R6 呼叫端注入**：由 `meta` 之 `authors`（list→逐項）/`date`/`publisher` 值組正規化值集合，傳入 `_build_tiles` → `assemble(..., meta_values=...)`。**④ R7 數字為主短行清理**：於 litedoc P1 清洗步（`MarkdownCleaner().clean` 後、與 `repair_ligatures` 同段）加行級規則——**行首為 `#`／`!`／`>`／`-`／`*`／`|` 一律跳過**（防誤殺列表/標題/圖行/表格列）；其餘行 split token，`len(tokens) <= 3` 且數字 token（`re.match(r"^\d+([.,]\d+)*$", tok)`）**過半** → 剝除（刪行）；`v1.2`/`M1` 含字母自動不計、`50%` 視為非數字（更保守）。兩來源（fitz/MinerU）同享。測試依 §6.2 靶（含呼叫序斷言與 `meta_values=None` 等價回歸）。 |

### C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`、`tests/test_litedoc_pipeline.py` + 2 個 `.bak`（`.claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_*.bak`）；**`web_server.py` 零改**（§3 問題 #4） |
| **安全性** | 🟢 高 — P3 兩處單點；R4 僅換譯題輸入變數（`_title_bare` L596 現成）、R8 複用既有 filter 工廠與門檻 |
| **可逆性** | 🟢 高 — `git revert C3`；R8 另可 `IMG_FILTER_ENABLED=false` env no-op |
| **驗收 grep 條件** | §6.3 全項 + §6.4 全域防呆 + §6.5 SOP 雙核查 |
| **依賴關係** | 無前置（與 C1/C2 正交；惟 §7.2 整合測試建議置本 commit 或 Checkout 前，屆時三刀齊備） |
| **具體實作細節** | **① R4 譯題治本**：P3 `translated_title = section_engine.translate_unit(title, inj, tr, "title")`（**L634 與 L647 兩處**）之第一參數由 `title` 改為 `_title_bare`（L596 已定義＝`title.replace(" (測試)","").strip()`）——LLM 永不見後綴 → 輸出恆乾淨 → `web_server.py:775` 既有 `endswith` 守衛恰好生效一次、成品恰一個 `(測試)`。**⚠️ `web_server.py` 零改**（防重已由 SHADOW-HOTFIX-2 落地、§3 問題 #4 grep 證；若 baron 另欲強化全形/空白正規化比對，屬額外加碼、非本案範圍）。L656 既有 post-strip `.replace(" (測試)","")` 維持不動（雙重保險）。**② R8 P3 單點圖片過濾**：於 `full_text = self._read_source_text(ctx)`（L593）與 `strip_title_echo`（L597）之後、`is_zh` 分支（L614）之前，插入行級過濾——`fig_filter = image_filter.make_figure_filter(Path(md_path).parent / "images", header_srcs=set())`（`images_root` 與 `_build_tiles` **同一基準**；md_path 由 output_dir/paper_name 推得或沿用既有取法）；逐行以 figure regex 比對，命中且 `fig_filter(src, alt)` 回 False → **刪該行**；`fig_filter is None`（旗標關）→ 整段 no-op；解析失敗 fail-open 保留。一次覆蓋 is_zh（L614）／whole（L631）／en_text（L649）三消費者，並立**「section mode 雙語圖片對稱」不變式**。測試依 §6.3 靶。 |

### C_CHECKOUT — 收官歸檔（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `archive/TODO_done_archive.md` / `prompts/`（本任務全數提示詞 + INDEX.md）/ baton→`plans/`+`tasks/`+`executions/` 歸檔檔 / `executions/<日期>_FITZ-HOTFIX-1_checkout_執行.md` |
| **安全性** | 🟢 高 — 純文件歸檔、零業務代碼 |
| **可逆性** | 🟢 高 — `git revert` 回滾歸檔 commit |
| **驗收 grep 條件** | Conformance 對照 plan v4 §2 八刀全項 + **§7.2 整合測試存在且通過** + staged-set 自檢（`git diff --cached --name-only` ＝ 宣告清單完全相等） |
| **依賴關係** | 前置 C1-C3 全數 ship |
| **具體實作細節** | 依 WORKFLOW_SOP §3 收官鐵律：Conformance 驗收（含 §3 問題 #4 plan↔代碼落差之處置留痕）→ TODO 雙層結案（active 移除 + archive 表格 + pointer + 類別索引）→ baton 一次性 `mv`（標準 mv、禁 git mv；plan/tasks/C1-C3 執行報告）→ 逐檔顯式 `git add`（嚴禁 `git add .`/`-A`/目錄；含 C1-C3 之 8 個 `.bak`）→ `checkout_執行.md`（staged-set 實貼 + §8 一行 commit）→ `/tmp` msg 草稿；commit 由 baron 手動。 |

---

## §9 Open Questions

無。（plan v4 §9 六問已於 2026-07-21 全數拍板、無遺留。）

> ⚠️ **一項執行期發現待 baron 知悉（非 OQ、已依 grep 證據處置）**：plan §2 R4 所述「web_server 無防重」與現況不符——`web_server.py:775` 已有 `endswith(" (測試)")` 守衛（SHADOW-HOTFIX-2）。本 tasks 據此將 R4 收斂為**單一 P3 端治本**、`web_server.py` 列入不可動清單。詳見 §3 問題 #4。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FITZ-HOTFIX-1 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FITZ-HOTFIX-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（拆分階段）；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；八刀規格唯一源＝plan v4；全局硬規則唯一源＝CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-21)：初版拆分完成——C1 Fitz Processor Refinement（R1/R2/R3/R5 單檔內聚）/ C2 P1 Meta & Noise Cleanup（R6 含時序前移 + R7）/ C3 P3 Title & Figure Convergence（R4 + R8）/ C_CHECKOUT；依 plan **v4**（六問拍板、R8 單點收斂）；**執行期 grep 更正**：R4 web_server 端防重已存在（SHADOW-HOTFIX-2）→ 收斂為單一 P3 端治本、`web_server.py` 入不可動清單（§3 問題 #4）
