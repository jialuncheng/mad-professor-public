# PIPE-INGEST-FITZ born-digital 文字層快速道與連字修復 plan

> litedoc P1 攝入層新增「文字層快速道」：born-digital PDF（有完整文字層）改由 FitzProcessor（PyMuPDF）本地直抽文字＋圖、按座標組出與 MinerU 同形狀之 .md；無／稀疏文字層維持 MinerU。另立連字壞字（PDF 字型 ToUnicode 共病）規則式修復。下游清洗／判型／組裝／過濾全鏈零改。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：litedoc 大宗（news/web 列印 PDF）多為 born-digital、有完整文字層，卻一律繞道 MinerU（外部服務、慢、佔推理通道、OCR 引入 `AI6Z` 類噪音）；且 PDF 字型層連字壞字（`Pro1les`/`;rst`/`de1ning`）直抽與 MinerU 兩法皆有、換工具修不好，需獨立正規化。
- **解法**：① 新建 `processor/fitz_processor.py`（`FitzProcessor(PDFParser)`）——fitz 抽文字＋圖、按區塊座標依閱讀序組 MinerU 同形 .md（`#` 標題層級由字級推導、`![](images/<fname>)` 圖檔 side-effect、剝列印頁首尾）；② litedoc P1 步驟①前置「文字層閘門」（fitz 每頁字元數試抽）：達標走 FitzProcessor、未達標或任何失敗 fail-open 退現行 MinerU；③ 新建連字修復純函式（保守規則式、行內替換），接線於 litedoc P1 清洗後、判型前（MinerU 與 fitz 兩來源同享）。
- **影響**：僅 litedoc P1 攝入段（`pipelines/litedoc_pipeline.py run_phase1 ①②`）＋新增 `processor/fitz_processor.py`＋新增連字修復模組＋settings 常數；`PDFProcessor`（MinerU）／`md_cleaner`／`DocAnalyzer`／`ingestion_engine`／`image_filter`／tiling／P2-P4／A 軌／resume／slides 零改；零 DB schema、零 API 簽名變動。

---

## §2 目標規格

1. **FitzProcessor（新檔 `processor/fitz_processor.py`）**：繼承 `PDFParser` ABC、完整履行其語意契約（`parse(pdf_path, output_dir) -> Path` = `output_dir/{stem}.md`；圖檔 side-effect 寫 `output_dir/images/`、best-effort 可缺；失敗統一 raise `PDFParseError`；不暴露 impl 細節）。
2. **同形 .md 產出**（下游來源無關之硬保證、**MinerU 同形契約**）：
   - 段落：以 `\n\n` 作段落分隔符（TilingProcessor／ingestion_engine 零感知對接之基準）；
   - 標題：標準 `#`／`##` 語法，層級由字級分群推導（最大字級群→`#`、次級→`##`、正文不加）；
   - 圖片：fitz `doc.extract_image(xref)` 抽出原生 PNG/JPEG 寫入 `images/`、檔名格式化 **`page_{page_idx}_{xref}.{ext}`**（跨頁唯一、防衝突覆寫）、於閱讀序位置嵌 `![](images/<fname>)`（**限 PNG/JPEG 落地**——`image_filter` stdlib 尺寸解析僅覆蓋此二格式、規則①②始終有效）；
   - 閱讀序：按區塊座標排序（litedoc 大宗單欄文章）；
   - 列印雜訊剝除：利用區塊座標 + 跨頁重複偵測，剝除列印頁首尾（URL 戳記、頁碼、日期戳等頂／底 band 重複行）。
3. **文字層閘門（litedoc P1 步驟① 前置、僅 litedoc 路）**：fitz 開檔統計每頁文字字元數，中位數 ≥ `LITEDOC_FITZ_MIN_CHARS_PER_PAGE` → FitzProcessor；未達標（掃描／稀疏）→ 現行 `PDFProcessor()`（MinerU）零改續用。閘門與 FitzProcessor 任何異常一律 **fail-open 退 MinerU**（logger.warning + exc_info、不阻斷攝入）。
4. **meta 純正文、零檔案屬性依賴**（design spec F6 baron 2026-07-19 定案）：**不讀、不留 fallback** 讀 `fitz.metadata`（/Title 等）——cover-prompt 正文抽取（`_extract_litedoc_metadata`）零改；born-digital 直抽保留正文首行 URL → publisher 解碼自然更準（順解缺陷⑥）。
5. **連字修復（獨立小件、防誤殺雙閘）**：新建純函式（落點＝§9 Q1 拍板：litedoc P1 共用步）——保守規則式：
   - **窗口**：僅處理「小寫字母 × 異常字元（如 `1`/`;`）× 小寫字母」窗口（含字首邊界形態如 `;rst`）、候選連字 `fi/fl/ff/ffi/ffl`；
   - **替換前排查（第一閘）**：單字匹配數字縮寫（`\b\d+(st|nd|rd|th|s)?\b`）或版本號（`v\d+` 類）者一律不予替換（防 `1st→fist`／`v1→vfi` 誤殺）；
   - **替換後詞形檢查（第二閘）**：優先載入系統字典（`/usr/share/dict/words`、存在才用）＋內建常見連字字彙集作 fallback 兜底——替換後為有效英文單字方採信，否則保留原樣（fail-open）；
   - **嚴禁增刪行（行內替換不變式）**；接線於 litedoc P1 步驟②（`MarkdownCleaner().clean` 後）、步驟③（`DocAnalyzer.analyze` 判型）前——MinerU 與 fitz 兩來源同享、doc_structure 行索引基準不受汙染。
6. **設定與開關**：`settings.py` 新增 `LITEDOC_FITZ_ENABLED`（env 單點關回、False 時 P1 行為與現行 byte 等價）、`LITEDOC_FITZ_MIN_CHARS_PER_PAGE`；連字修復開關／常數同置 settings；`.env.example` 同步註記。
7. **範圍圍籬**：本案僅 litedoc 路接線；A 軌 `pipeline_core`、resume／slides／book／academic 各路一律不接（未來各自評估）；`PDFProcessor`（MinerU 路）byte 不動。
8. **零新依賴**：PyMuPDF 已為 pin 依賴（`requirements.txt:26`）；連字詞形檢查用內建規則、**嚴禁引入字典／NLP 第三方套件**。

### §2.5 候選方案（Diverse Rollout）

P1 攝入層架構改動（中大）、屬架構級決策，列候選：

| 方案 | 核心做法 | trade-offs |
|---|---|---|
| 方案 A（選定）**fitz-both** | born-digital 一律 fitz 包辦文字＋圖，單一座標系組 .md | 開發中等；下游零改（同形 .md）；閱讀序／圖位一致無接縫；heading 推導需字級啟發式 |
| 方案 B（否決）**拆分混搭** | fitz 抽文字 + MinerU 抽圖，兩產物合併 | 兩座標系對位接縫（圖插哪一行無共同基準）；仍付 MinerU 成本，速度收益歸零；複雜度最高 |
| 方案 C（否決）**閘門下沉 PDFProcessor 內部** | 在 `PDFProcessor.parse` 內部分流 | 汙染 A 軌共用處理器（pipeline_core 同 import）、違「B 軌自有化」方向；影響面失控 |

- **選定理由**：A＝design spec F6 收斂點（原「有無圖片」分支 A.1.1/A.1.2 取消）——避開兩座標系接縫、下游只吃一個 markdown 檔（來源無關）；閘門放 litedoc P1 呼叫端、A 軌零波及。
- **否決留痕**：B／C 於此留底（CLAUDE.md §1.9），防未來重踩「MinerU 圖 + fitz 文字」混搭與共用處理器內分流兩坑。

---

## §3 現況與證據

- **`pipelines/litedoc_pipeline.py`**：
  - `run_phase1 L132-216`：P1 全鏈 ①`PDFProcessor().parse`（L155、**唯一呼叫點＝本案閘門落點**）→ ②`MarkdownCleaner().clean(md_path)`（L157）→ ③`DocAnalyzer().analyze`（L163、soft-fail、產 `_doc_structure.json` sidecar）→ ④⑤⑥`_build_tiles`（L172）→ ⑦`_extract_litedoc_metadata`（L175、cover-prompt 正文抽 meta）。
  - `_build_tiles L223-`：讀 sidecar（L236）→ `_collect_header_srcs`＋`make_figure_filter`（L245-248、IMG-FILTER C3）→ `ingestion_engine.assemble`（L249）。下游全部只認 `md_path` 一個檔、**來源無關**。
- **`processor/pdf_parser.py`**：`PDFParser` ABC（L24-）＝換 impl 的既備介面——`parse(pdf_path, output_dir) -> output_dir/{stem}.md`、圖 side-effect `output_dir/images/`、失敗統一 `PDFParseError`。docstring 明言「換 impl（pdfplumber / Marker / 自家解析）時主程式不必改」——FitzProcessor 為此介面之第二個 impl。
- **`processor/pdf_processor.py`**：MinerU impl（A 軌 pipeline_core 共用）——`markdown_path = output_dir / f"{paper_name}.md"`（L128）、`_copy_images` 落 `output_dir/images/`（L146-148）。本案 byte 不動。
- **`pipelines/image_filter.py`**：尺寸解析＝stdlib PNG/JPEG header（模組 docstring L12「PNG＋JPEG 覆蓋 MinerU 實產」）——fitz 路圖檔限 PNG/JPEG 落地即相容（§2.2）。
- **`requirements.txt:26`**：`PyMuPDF==1.27.2.3`（已 pin、零新依賴）；`import fitz` 既有使用者＝domain_detector／metadata_extractor／resume_processor／slides_processor（皆非 litedoc P1）。
- **連字壞字實證**（design spec F6）：SpaceX.pdf `Pro1les`/`;rst`/`de1ning`——PDF 字型 ToUnicode 映射壞、pypdf 直抽與 MinerU 皆現、換工具修不好 → 需獨立正規化。
- **born-digital 實測**（design spec F6）：SpaceX.pdf 23 頁全有文字層、直抽 OK；直抽首行含 `https://www.a16z.news/...` → publisher 直接正確 a16z（比 OCR `AI6Z` 準）。

### §3.1 grep 鋼鐵證據

```bash
grep -n "PDFProcessor\|def run_phase1\|_build_tiles\|md_path" pipelines/litedoc_pipeline.py
# pipelines/litedoc_pipeline.py:38:from processor.pdf_processor import PDFProcessor
# pipelines/litedoc_pipeline.py:155:md_path = Path(PDFProcessor().parse(str(pdf_path), str(output_dir)))
# pipelines/litedoc_pipeline.py:157:MarkdownCleaner().clean(md_path)
# pipelines/litedoc_pipeline.py:163:DocAnalyzer().analyze(md_path, analyzer_doc_type)
# pipelines/litedoc_pipeline.py:172:tiles = self._build_tiles(md_path, output_dir, paper_name, ctx.doc_type)
# pipelines/litedoc_pipeline.py:236:sidecar = md_path.parent / f"{md_path.stem}_doc_structure.json"

grep -n "fitz\|PyMuPDF" requirements.txt
# requirements.txt:26:PyMuPDF==1.27.2.3               # 核心：精確鎖定避免 breaking change

grep -rn "import fitz" --include="*.py" .
# processor/domain_detector.py:14 / processor/metadata_extractor.py:25 /
# processor/resume_processor.py:23 / processor/slides_processor.py:5（＋tests ×4）
# → litedoc P1 目前零 fitz；FitzProcessor 為新增消費者

sed -n '24,40p' processor/pdf_parser.py
# class PDFParser(ABC): parse(pdf_path, output_dir) -> Path  # output_dir/{stem}.md
# 圖檔以 side-effect 寫入 output_dir/images/（best-effort）；失敗統一 PDFParseError

grep -rn "PDFProcessor" pipelines/*.py | grep -v litedoc
# （零命中——pipelines 內僅 litedoc 消費；A 軌 pipeline_core 另用、本案不碰）
```

---

## §4 跨 Phase 接縫契約

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| 閘門→parser impl | litedoc P1 ① 閘門依每頁字元數擇 impl | `FitzProcessor.parse` 或 `PDFProcessor.parse` | key＝`ctx.pdf_path`；兩 impl 同履行 `PDFParser` ABC、回傳 `output_dir/{stem}.md` **同一路徑基準**（下游 `md_path` 消費零感知） |
| FitzProcessor→下游 .md/圖 | FitzProcessor 產 `output_dir/{stem}.md`＋`images/<fname>`（md 內 src＝`images/<fname>` 相對路徑） | `md_cleaner`/`DocAnalyzer`/`ingestion_engine` 讀 md；`image_filter` 以 `md_path.parent/"images" / Path(src).name` 開檔 | src 相對路徑＝**MinerU 同基準**（`images/` 子目錄＋檔名）；圖檔限 PNG/JPEG → stdlib 尺寸解析同基準有效 |
| 連字修復→判型/組裝 | 修復函式改寫 md 檔文字（P1 ②後③前、行內替換） | `DocAnalyzer.analyze` 產 doc_structure（行索引）；`assemble`/`_collect_header_srcs` 以行界消費 | key＝md 行號；**修復嚴禁增刪行** → 修復後文本與 doc_structure 行索引為同一基準（修復先於 analyze、雙重保證） |

填寫規範見 `.claude-logs/ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| heading 層級推導（字級啟發式）與 MinerU 產出有落差 → 判型/切節漂移 | 🟡 中 | litedoc 大宗＝單欄文章、標題字級鴻溝明顯；閘門僅 litedoc 路；影子 E2E 以 SpaceX 對照；`LITEDOC_FITZ_ENABLED=false` env 單點回 MinerU |
| 多欄／圖表密集版面閱讀序錯亂 | 🟡 中 | 座標排序對單欄對味（design spec F6 明言 litedoc 對味、多欄較難）；任何解析異常 fail-open 退 MinerU；不達標樣本天然走 MinerU |
| 連字修復誤替換（`1st`/`v1.2` 等合法數字） | 🟡 中 | 雙閘（§2.5）：替換前數字縮寫/版本號正則排查＋替換後詞形檢查〔系統字典優先＋內建兜底集〕；不確定保留原樣；單元測試守門誤殺樣本 |
| MinerU 路／A 軌回歸 | 🟢 低 | `pdf_processor.py`/`pipeline_core` byte 不動；閘門在 litedoc 呼叫端；flag off 路徑 byte 等價回歸測試 |
| golden 基準 | 🟢 低 | litedoc 屬 B 軌影子、循 PIPE-LITEDOC「改善豁免」慣例；A 軌 golden 零觸碰 |
| 舊資料 | 🟢 低 | 純攝入期行為；既有已入庫 paper 零影響、無 backfill |

---

## §6 不可動清單

- [ ] `processor/pdf_processor.py` 全檔（MinerU impl、A 軌 pipeline_core 共用；閘門嚴禁下沉此檔）
- [ ] `processor/pdf_parser.py` `PDFParser` ABC 簽名與語意契約（FitzProcessor 實作之、不改之）
- [ ] `processor/md_cleaner.py`（A 軌共用；連字修復嚴禁寫入此檔）
- [ ] `processor/doc_analyzer.py` 判型邏輯與 doc_structure schema
- [ ] `pipelines/ingestion_engine.py`／`pipelines/image_filter.py`（含三門檻常數）／`pipelines/section_engine.py`
- [ ] litedoc P1 ③-⑦ 既有步序與 `_extract_litedoc_metadata` cover-prompt（meta 純正文已定案；`language` 欄屬 LANG-DETECT、本案嚴禁夾帶）
- [ ] `contracts.py` `IngestionMetadataSpec` 等凍結合約；`classify_source_lang`（HOTFIX-1 原職、不兼差）
- [ ] resume／slides／book／academic 各路與 A 軌 `pipeline_core.py`／`web_server.py`／`paper_manager.py`
- [ ] **嚴禁**引入任何新第三方依賴（字典／NLP／影像套件）；**嚴禁**讀取 `fitz.metadata`（/Title 等檔案屬性）

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| F6 設計定案（fitz 首選／收斂點／meta 純正文／連字＝字型層共病） | `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` §F6、§3.1 序 4 |
| PDFParser 換 impl 契約 | `processor/pdf_parser.py` docstring（L1-13） |
| 跨 Phase 接縫契約／§7.2 整合測試 | `ref/WORKFLOW_SOP.md §7` |
| logging SOP（BE-Refactor 必讀） | `sop/2026-05-23_logging_SOP_手冊.md`（fail-open 一律 exc_info=True） |
| database SOP（BE-Refactor 必讀） | `sop/2026-05-23_database_SOP_手冊.md`（本案零 DB 寫入、核查照跑） |
| image_filter 尺寸解析格式覆蓋 | `pipelines/image_filter.py` docstring（PNG/JPEG） |
| 進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：`venv/bin/python -m pytest tests/ -v`（基線 831 passed、零回歸）。
- **預計新增**：
  - `tests/test_fitz_processor.py`：以 fitz 程式化生成 born-digital 測試 PDF（零網路、零 MinerU）——`parse` 產 `{stem}.md`＋`images/`；字級→heading 層級（標準 `#`/`##`）；`\n\n` 段落分隔同形契約；閱讀序；跨頁重複頁首尾剝除；圖檔 PNG/JPEG 落地＋`page_{page_idx}_{xref}.{ext}` 命名唯一性（跨頁多圖不覆寫）＋md src 相對路徑；壞檔 raise `PDFParseError`。
  - 閘門測試（litedoc 測試檔）：有文字層→fitz 路；零/稀疏文字層→MinerU 路（mock `PDFProcessor.parse`）；FitzProcessor 拋例外→fail-open 退 MinerU＋warning log；`LITEDOC_FITZ_ENABLED=false` → 與現行路徑等價回歸。
  - 連字修復單元：`Pro1les→Profiles`、`;rst→first`、`de1ning→defining` 正修；`1st`/`2nd`/`v1`/`v1.2`/`M1 晶片`/中文行 不動（**雙閘誤殺守門**：第一閘正則排查＋第二閘詞形檢查；字典缺席環境走內建兜底集斷言）；行數不變式斷言。
  - **§7.2 跨 Phase 整合測試**：fitz 生成含標題／圖／頁首尾雜訊之實體 PDF → 真 FitzProcessor → 真 cleaner＋連字修復 → `_build_tiles` 端到端——斷言 tiles 結構、figure 穿透 image_filter、doc_structure 行界同基準（key-changing＝真實 PDF→md 轉換）。

### §8.2 手動端到端（E2E）驗證流程

1. 影子重傳 `baton/SpaceX & the Sentient Sun.pdf`：後端 log 確認**走 fitz 路**（閘門判定 log）；產出 23 頁全文完整（無 MinerU 跨頁截斷）；`Pro1les`/`;rst`/`de1ning` 類連字壞字消失；publisher＝a16z（正文 URL 直抽）。
2. IMG-FILTER 續效驗證：3 垃圾圖 DROP／20 內容圖 KEEP（含 481×369 chart 與 hero）——fitz 路圖檔與過濾器同基準。
3. 上傳一份掃描（無文字層）樣本：log 確認閘門退 MinerU、產出鏈正常。
4. `LITEDOC_FITZ_ENABLED=false` 重傳：確認整鏈回 MinerU、行為與現行一致（應急開關實測）。

---

## §9 Open Questions（六問全數拍板 2026-07-21·baron 採納推薦、無翻案）

| 開放問題 | 拍板方案 | 理由 |
|---|---|---|
| Q1 連字修復落點 | ✅ **litedoc P1 共用步**（獨立純函式模組、P1 ②後③前接線） | 字型層共病 MinerU 路也有——放 FitzProcessor 只修一半；md_cleaner 是 A 軌共用不可動；P1 呼叫端接線＝兩來源同享＋零 A 軌波及 |
| Q2 修復策略保守度 | ✅ 「小寫×異常字元×小寫」窗口＋`fi/fl/ff/ffi/ffl`＋**雙閘**（替換前數字縮寫/版本號排查＋替換後詞形檢查〔系統字典優先＋內建兜底集〕）、不確定保留 | 漏修僅局部可讀噪音、誤殺改壞正確文本；雙閘將誤殺率壓近零；零新依賴（§2.8） |
| Q3 閘門門檻 | ✅ `LITEDOC_FITZ_MIN_CHARS_PER_PAGE=150`、以**中位數**判定 | born-digital 網頁列印每頁遠超此值、掃描＝0，鴻溝巨大；中位數抗封面／尾頁稀疏頁干擾；env 可調免 commit |
| Q4 `LITEDOC_FITZ_ENABLED` 預設 | ✅ **true**（env 單點關回） | litedoc 仍屬影子軌——風險已被影子隔離；預設開最大化影子 E2E 曝光（IMG-FILTER 同慣例）；出事 `=false` 秒回 MinerU |
| Q5 FitzProcessor 失敗策略 | ✅ fail-open 退 MinerU（warning + `exc_info=True`、不阻斷） | MinerU 是既存可靠後盾；攝入層新 impl 任何失敗不應中斷文獻攝入 |
| Q6 混合型 PDF（部分頁有字部分掃描） | ✅ 不做 per-page 混合模式、由中位數閘門整份二擇一 | litedoc 大宗單型；混合模式＝兩座標系接縫重現（§2.5 方案 B 同坑）、YAGNI |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-INGEST-FITZ born-digital 文字層快速道與連字修復 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-INGEST-FITZ tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md；F6 設計定案唯一源＝design spec、本檔僅凍結為規格 |

### §99.2 Revision 歷程

- v2 (2026-07-21)：review 定稿——外部 review 無結構性缺失（肯認閘門/修復上置 litedoc 呼叫端之 A 軌隔離）；兩實作細則回灌 §2〔§2.2 MinerU 同形契約明確化（`\n\n` 段落分隔＋標準 `#`/`##`）＋圖片命名 `page_{page_idx}_{xref}.{ext}` 防衝突／§2.5 連字防誤殺雙閘（替換前 `\b\d+(st|nd|rd|th|s)?\b`/`v\d+` 排查＋替換後系統字典優先/內建兜底集詞形檢查）〕；§5/§8.1 對應同步；§9 六 OQ 全數拍板採納推薦（無翻案）
- v1 (2026-07-21)：初版——依 design spec F6（fitz-both 收斂點／meta 純正文零檔案屬性／連字＝PDF 字型層共病）凍結規格；§2.5 三候選留痕（fitz-both 選定、拆分混搭與閘門下沉否決）；六 OQ 待 baron 拍板
