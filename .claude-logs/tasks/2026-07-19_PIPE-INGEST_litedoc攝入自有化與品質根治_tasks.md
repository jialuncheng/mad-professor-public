# PIPE-INGEST litedoc 攝入自有化與品質根治 — Tasks

> 本文件為 PIPE-INGEST 的 Commit 拆分清單（階段 2 產出）。
> 依 `baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md`（**v4·純結構化定案**）產出，含 4 個 Commit。
> ⚠️ 本案定位＝**純結構化**（標題/meta/圖片/publisher/dead-code）；雙語括號約束與術語一致（原 plan §2.6/§2.7）**已移交 GLOSSARY-TERMMAP**（前後腳任務、本案不蓋 interim constraints 鷹架）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `pipelines/ingestion_engine.py`（B 軌自有攝入組裝引擎）/ `tests/test_ingestion_engine.py`（引擎單元測試 + §7.2 整合測試） |
| **修改檔案** | 2 個 | `pipelines/litedoc_pipeline.py`（C2 P1 切換消費引擎；C3 P3 譯題單一源 + cover-prompt publisher 正規化 + dead code 移除）/ `tests/test_litedoc_pipeline.py`（對應測試更新） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（本階段設 🟡 WIP、收官結案）/ `prompts/INDEX.md`（提示詞歸檔同步） |
| **Commits** | 4 個 | C1 → C2 → C3 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` baton 之 `_plan.md` → `plans/`、`_tasks.md` → `tasks/`、C1-C3 `_執行.md` → `executions/`，產 `checkout_執行.md` 後逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：litedoc P1 借用 A 軌組裝鏈（`md_processor`/`json_processor`），產物 schema 內嵌 A 軌消費假設，致影子輸出標題錯置（①）、圖片全滅（②·19 figure→0）、meta 塊內文重複（③）；另有 publisher OCR 誤植（⑥）與 dead code 殘留。
- **解法**：三個原子 commit 落地——**C1 — Ingestion Engine（攝入引擎本體）**：純加法新建引擎與測試、零接線；**C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）**：`_build_tiles` 改走引擎、A 軌組裝 import 退場；**C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）**：P3 譯題唯一源 P1 title、cover-prompt publisher 正規化、dead code 移除、§7.2 整合測試；**C_CHECKOUT — Checkout（收官歸檔）**：Conformance + baton 一次性歸檔。
- **影響範圍**：僅 `pipelines/litedoc_pipeline.py` + 2 新檔 + litedoc 測試；A 軌 / resume / slides / section_engine / contracts **零碰**；無 DB schema / API 簽名變動。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | P1 `_build_tiles`（L210-220）走 `MarkdownProcessor`→`JsonProcessor`→`TilingProcessor` 借用鏈；`_load_tiles`（L232）只取 `sections` 丟 `title`；P3 section 模式（L494）譯題撈第一個 title slot；cover-prompt（L60-71）無 OCR 正規化；`_detect_source_lang`（L272-279）dead code | P1 換自有引擎、P3 譯題單一源、cover-prompt 補規則、dead code 移除 |
| `pipelines/ingestion_engine.py` | **不存在** | 新建：md + doc_structure → meta 分離 + section 樹 + figure 帶 `content` 之 processed 相容 JSON |
| `tests/test_ingestion_engine.py` | **不存在** | 新建：引擎單元測試 + §7.2 跨 Phase 整合測試 |
| `tests/test_litedoc_pipeline.py` | 既有 litedoc 測試（26.0K）覆蓋現行借用鏈行為 | C2/C3 依新行為更新（P1 走引擎、譯題單一源）、新增回歸斷言 |

---

## §3 觀察問題

### 問題 #1：figure block 無 `content` 鍵 → 圖片全滅（缺陷②）
- **證據**：`processor/json_processor.py#L154-158`（figure 僅 `{type,src,alt}`）+ `pipelines/section_engine.py#L237`（`if content:` 空即丟）；實證 `baton/litedoc_shadow_artifacts/.../SpaceX_the_Sentient_Sun_tiled.json` figure ×19、含 `content` 者 0、final_shadow_zh 0 張圖
- **影響**：zh 視圖圖片全數靜默丟失、圖說成孤兒段落

### 問題 #2：譯題撈第一個 title slot → 標題錯置（缺陷①、三受害者）
- **證據**：`pipelines/litedoc_pipeline.py#L494` + `processor/md_processor.py#L264`（title 抽離不入 sections）；實證 tiled.json `title` 欄正確但被 `_load_tiles`（L232）丟棄
- **影響**：zh 扉頁 `#` 標題／HTML `<title>` 分頁名／PDF `/Title` 三處全錯（「從未來逆向推導」）

### 問題 #3：meta 塊落入內文重複（缺陷③）
- **證據**：`processor/md_processor.py#L325-336`（authors 收集遇首個非 author 行即終止）；實證 doc_structure 判型正確（authors=line 6、publication_info=12/16-18）但 `authors_info=''`、meta 塊 10 items 落入孤兒 section
- **影響**：扉頁後 epigraph/byline/publisher/標題/日期/tags 整包重播

### 問題 #4：publisher 照抄 OCR 錯字 + dead code（缺陷⑥）
- **證據**：`pipelines/litedoc_pipeline.py#L60-71`（cover-prompt 無正規化規則、實證 venue=`AI6Z NEWS`）；`#L272-279`（`_detect_source_lang` 零 caller）
- **影響**：扉頁出版方錯誤；dead code 誤用風險

---

## §4 設計方案

### §4.1 C1 — Ingestion Engine（攝入引擎本體）
新建 `pipelines/ingestion_engine.py`：零 doc_type 字面量純函式模組（比照 `section_engine` 設計原則），輸入 cleaned md 全文 + doc_structure 判型 dict，輸出「title + meta 分離產物 + processed.json 相容 section 樹（figure 帶 `content`）」。同 commit 新建 `tests/test_ingestion_engine.py` 覆蓋引擎全規格。**零接線**（litedoc 仍走舊鏈），業務行為零變。

### §4.2 C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）
`litedoc_pipeline._build_tiles` 改為：引擎產 processed 相容 JSON → 寫 `{paper_name}_processed.json` → `TilingProcessor` 續用零改 → `_load_tiles`。`MarkdownProcessor`/`JsonProcessor` import 退場。meta 分離產物使文首 meta 行不再進 tiles（缺陷③ body 側歸零、缺陷② figure 穿透）。更新 `tests/test_litedoc_pipeline.py` P1 相關斷言。

### §4.3 C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）
P3 section 模式改 `translate_unit(title)`（與 whole 模式同式）、廢除 `_extract_translated_title`（缺陷①三受害者 + post-strip key 一併矯正）；cover-prompt 增補 publisher 正規化 / OCR 自癒 / 作者 Title Case 規則（缺陷⑥）；移除 `_detect_source_lang`；補 §7.2 跨 Phase 整合測試（key-changing transform + figure 穿透斷言）。

### §4.4 C_CHECKOUT — Checkout（收官歸檔）
Conformance 五維度 + §7.2 整合測試存在且通過確認 + baton 一次性 `mv` + 逐檔 `git add` 白名單 + `checkout_執行.md` + TODO 雙層結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 引擎 meta 分離誤剔內文行（判型錯誤放大） | 🟡 中 | 僅剔除 doc_structure 明確判型為 meta_types 之行；判型缺失/行號越界 soft-fail 退化為「無 meta 分離」（回到現況行為、不阻斷）；C1 單元測試含「判型行不連續」與 soft-fail 情境 |
| C2 切換後 tiles schema 與 TilingProcessor / section_engine 不相容 | 🟡 中 | §4 接縫契約凍結 processed.json 語意等價 + figure `content` 純加法；C1 測試含 schema 相容斷言；C3 §7.2 整合測試全鏈驗證 |
| 同檔兩 commit（litedoc_pipeline.py C2/C3）staging 混雜 | 🟢 低 | 沿 SOP-COMPLY C1/C2 共檔前例：各 commit 各自產 `.bak`、`git diff --cached --name-only` 白名單自檢 |
| litedoc 既有 26K 測試檔部分斷言綁舊鏈行為 | 🟡 中 | C2/C3 依 plan §6「僅允許依規格更新 litedoc 自身測試」逐條改寫、執行報告記錄每條被更新斷言之對應規格條款 |
| B 軌輸出內容改變（標題/圖片/meta） | 🟡 中 | 影子軌不影響 A 軌；golden 走改善豁免 + baron 影子 E2E（plan §8.2、僅結構項） |

---

## §6 測試計畫

> 各 Run 落地前強制 §5 SOP 一致性核查（BE-Refactor）：logging `grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔>`（logger.error 必含 exc_info=True）+ database `grep -nE "\.commit\(\)" <修改檔> | grep -v "with .*session.*begin\(\)"`（期望：無命中（合規）——本案兩檔均不涉 DB 寫入）。全套件基線 748 passed、逐 commit 不得低於基線。

### §6.1 C1 驗收

```bash
ls -la pipelines/ingestion_engine.py tests/test_ingestion_engine.py            # 兩檔存在非空
grep -c "doc_type" pipelines/ingestion_engine.py                                # 期望：0（零 doc_type 字面量）
grep -n "def assemble" pipelines/ingestion_engine.py                            # 期望：命中（頂層入口）
grep -n "content.*!\[" pipelines/ingestion_engine.py                            # 期望：命中（figure content 重建）
python3 -m pytest tests/test_ingestion_engine.py -v                             # 全綠
python3 -m pytest tests/ -q                                                     # ≥748 passed、零新 fail
grep -rn "ingestion_engine" pipelines/litedoc_pipeline.py                       # 期望：0 命中（C1 零接線）
```

### §6.2 C2 驗收

```bash
grep -n "MarkdownProcessor\|JsonProcessor" pipelines/litedoc_pipeline.py        # 期望：0 命中（借用鏈退場）
grep -n "ingestion_engine" pipelines/litedoc_pipeline.py                        # 期望：命中（P1 已接線）
grep -n "TilingProcessor" pipelines/litedoc_pipeline.py                         # 期望：仍命中（tiling 續用零改）
python3 -m pytest tests/test_litedoc_pipeline.py tests/test_ingestion_engine.py -v   # 全綠
python3 -m pytest tests/ -q                                                     # ≥748 passed
```

### §6.3 C3 驗收

```bash
grep -n "_extract_translated_title\|_detect_source_lang" pipelines/litedoc_pipeline.py  # 期望：0 命中（雙廢除）
grep -n "translate_unit" pipelines/litedoc_pipeline.py                          # 期望：section 與 whole 分支各一處命中
grep -n "a16z\|official name\|Title Case" pipelines/litedoc_pipeline.py         # 期望：cover-prompt 正規化規則命中
grep -rn "def test_.*integration\|key.changing\|key_changing" tests/test_ingestion_engine.py tests/test_litedoc_pipeline.py  # 期望：§7.2 整合測試存在
python3 -m pytest tests/ -q                                                     # ≥748 passed
```

### §6.4 C_CHECKOUT 驗收

```bash
ls .claude-logs/baton/*PIPE-INGEST* 2>/dev/null                                 # 期望：僅剩 litedoc_shadow_artifacts/ 等非本案任務檔（plan/tasks/執行報告已 mv）
ls .claude-logs/plans/*PIPE-INGEST* .claude-logs/tasks/*PIPE-INGEST* .claude-logs/executions/*PIPE-INGEST*  # 歸檔到位
git diff --cached --name-only                                                   # 實貼 checkout 執行報告、須完全等於宣告清單
```

---

## §7 不可動清單

明確劃定修改邊界（承 plan v4 §6、唯一權威源）。**以下在本次修改中嚴禁任何改動：**

- [ ] **A 軌組裝鏈本體**：`processor/md_processor.py`、`processor/json_processor.py`（A 軌全文體 + resume 續用）
- [ ] **A 軌鏈全體**：`pipeline_core.py` / `md_restore_processor` / `translate_processor` / `rag_processor` / `web_server.py`
- [ ] **前兩路**：`pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py`
- [ ] **`pipelines/section_engine.py`**：既有函式簽名與行為零改（figure 走既有 `content`→raw slot 路徑；實作中若發現必須動 → 停、升級 plan 修訂交 baron 重審）
- [ ] **母翻譯提示詞**：`prompt/translate/content_translate_prompt.txt` 等（A 軌共用）
- [ ] **凍結合約**：`pipelines/contracts.py`（`IngestionMetadataSpec` 等欄位零增刪）
- [ ] **`processor/rag_indexer.py`** 與 P2→P4 `summary_key`＝原文標題 path 基準
- [ ] **工具層**：`processor/pdf_processor.py`、`md_cleaner.py`、`doc_analyzer.py`、`tiling_processor.py`（續用零改）
- [ ] **`settings.py` `LLM_USE_GLOSSARY_ALIGN` 預設值**（GLOSSARY-ON 另案）
- [ ] **既有 tests 斷言本體**（僅允許依 plan §2 規格更新 litedoc 自身測試、逐條記錄於執行報告）
- [ ] **禁 constraints 鷹架**：本案嚴禁向 litedoc `InjectionContext.constraints` 加入任何括號/術語約束（v4 定案移交 GLOSSARY-TERMMAP）

---

## §8 推薦 Commit 拆分

### C1 — Ingestion Engine（攝入引擎本體）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `pipelines/ingestion_engine.py`、新增 `tests/test_ingestion_engine.py`（兩檔皆全新、無 `.bak`） |
| **安全性** | 🟢 高 — 純加法新模組、零接線（litedoc 仍走舊鏈）、零 runtime 行為變化；不涉 DB / logging 特殊分支 |
| **可逆性** | 🟢 高 — `git revert` 即刪兩新檔、零殘留 |
| **驗收 grep 條件** | 見本檔 §6.1（兩檔存在／零 doc_type 字面量／`assemble` 入口／figure content 重建／新測試全綠／全套件 ≥748／litedoc 零接線確認） |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 新建 `pipelines/ingestion_engine.py`，模組 docstring 標註 `[PIPE-INGEST C1]`、設計原則（零 doc_type 字面量、route-specific 注入、零 import A 軌 processor）。② 實作純函式：`extract_title(lines) -> (title, title_line_idx)`——取首個 `#` 行文字（`lstrip('#').strip()`）、無則 `('', None)`；`split_meta(lines, structure, meta_types) -> (meta: Dict[str, List[str]], body_line_flags: List[bool])`——遍歷 `structure['structure']` blocks、`type in meta_types`（呼叫端注入、litedoc 傳 `("title","authors","publication_info")`）之 `start..end` 行號標記為 meta 行並按 type 歸類；**不受行連續性限制**（逐 block 獨立標記）；structure 為 None / 無 `structure` 鍵 / 行號越界 → soft-fail 回 `({}, 全 False)`（無 meta 分離、logger.warning 一次）；title 行（`extract_title` 之 idx 與 structure type=title blocks）一律標 meta。③ `split_blocks(lines) -> List[dict]`——行級掃描比照 `json_processor` 語意：figure（`^!\[..\](..)` → `{"type":"figure","src","alt","content":"![alt](src)"}`、上下行匹配 caption 樣式（自帶同語意 regex、零 import A 軌）則附 `caption`）；table（`^<html><body><table>` → `{"type":"table","content":原行}`）；formula（`$$..$$` 塊 → `{"type":"formula","content":"$$ .. $$"}`）；其餘 → `{"type":"text","content":行}`。④ `build_sections(body_lines) -> List[dict]`——依 heading 層級建樹：非首 `#` 之 heading 行起新 section `{"title","level"(=heading 井號數),"content":[blocks],"children":[]}`、層級棧組裝父子（比照 md_processor `build_hierarchy` 語意）；首個 heading 前之孤立內容 → 無標題容器 section（`title=''`）；section `title` 一律＝md heading 原文文字**零加工**（P2/P4 原文標題 path 基準零位移）。⑤ 頂層入口 `assemble(markdown_text, structure, *, meta_types) -> {"title": str, "meta": Dict[str, List[str]], "sections": List[dict]}`——串 ①②③④、sections 為 processed.json 相容 schema（TilingProcessor 直接可餵、`index`/`part` 由 tiling 自補不在引擎產）。⑥ logging 依 SOP：異常路徑 `logger.warning(..., exc_info=True)`、無裸 commit（模組零 DB）。⑦ 新建 `tests/test_ingestion_engine.py`：title 抽取（有/無 `#`）；meta 分離（判型行**不連續**情境——epigraph 夾於 byline 前、對映 SpaceX 實證）；soft-fail 三態（structure None / 空 dict / 行號越界）；figure `content=![alt](src)` 重建 + caption 關聯；table/formula 語意等價（對照 json_processor 產物欄位）；section 樹層級與孤兒容器；title 零加工斷言；**零 doc_type 字面量之源碼掃描斷言**（讀模組源碼 `assert 'litedoc' not in src and 'resume' not in src ...`、比照 section_engine 慣例）；schema 相容（`assemble` 產物直餵 `TilingProcessor._merge_small_text_blocks` 級別純函式不炸、或欄位集斷言）。 |

### C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`（+ `pipelines/litedoc_pipeline.py.bak`）、修改 `tests/test_litedoc_pipeline.py`（+ `tests/test_litedoc_pipeline.py.bak`） |
| **安全性** | 🟡 中 — 動 litedoc P1 業務碼；但影子軌不影響 A 軌交付、resume/slides 零 import 本檔、§7.2 整合測試（C3）+ 既有測試防護 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 回滾至借用鏈；`.bak` 留檔可 `git show` 追溯 |
| **驗收 grep 條件** | 見本檔 §6.2（MarkdownProcessor/JsonProcessor 0 命中／ingestion_engine 命中／TilingProcessor 仍在／litedoc+engine 測試全綠／全套件 ≥748） |
| **依賴關係** | 前置：C1（引擎已存在且測試全綠） |
| **具體實作細節** | ① `cp pipelines/litedoc_pipeline.py pipelines/litedoc_pipeline.py.bak`（同 tests 檔）。② 頂部 import 區：刪 `from processor.json_processor import JsonProcessor`、`from processor.md_processor import MarkdownProcessor`；增 `from pipelines import ingestion_engine`。③ 改寫 `_build_tiles(md_path, output_dir, paper_name, doc_type)`：讀 `md_path` 全文；讀 doc_structure sidecar `{md_path.parent}/{md_path.stem}_doc_structure.json`（json.loads、失敗 → None、soft）；`result = ingestion_engine.assemble(markdown_text, structure, meta_types=("title","authors","publication_info"))`；將 `{"title": result["title"], "sections": result["sections"]}` 寫 `{paper_name}_processed.json`（沿用現行檔名、審計連續性；`_structured.json` 不再產出）；`TilingProcessor().process(processed, tiled, doc_type=doc_type)` 續用零改；回傳 `self._load_tiles(tiled)`（`_load_tiles` 本體零改——meta 行已於引擎層剔除、`title` 欄仍由 P1 `_resolve_title` 鏈為權威源）。④ P1 其餘鏈（PDFProcessor/MarkdownCleaner/DocAnalyzer/cover-prompt/`classify_source_lang`）**零動**。⑤ 更新 `tests/test_litedoc_pipeline.py`：P1 組裝相關 mock 由 MarkdownProcessor/JsonProcessor 改 stub `ingestion_engine.assemble`；新增斷言——文首 meta 行（authors/publication_info 判型）不出現於 tiles 任何 text block、figure block 帶 `content`；每條被更新斷言於執行報告§4 記錄對應 plan §2 條款。⑥ 落地前 §5 SOP 雙核查 grep 實貼執行報告。 |

### C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`（+ 本 commit 新拷 `.bak`）、修改 `tests/test_litedoc_pipeline.py`（+ 本 commit 新拷 `.bak`）、修改 `tests/test_ingestion_engine.py`（補 §7.2 整合測試、無 `.bak`——C1 新檔延續編修） |
| **安全性** | 🟡 中 — 動 P3 譯題鏈與 cover-prompt；廢除路徑（`_extract_translated_title`/`_detect_source_lang`）均先 grep 確認零外部 caller；whole 模式同式已在線驗證過 |
| **可逆性** | 🟢 高 — `git revert` 單 commit 回滾；`.bak` 留檔 |
| **驗收 grep 條件** | 見本檔 §6.3（雙廢除 0 命中／translate_unit 兩分支命中／cover-prompt 正規化規則命中／整合測試存在／全套件 ≥748） |
| **依賴關係** | 前置：C2（P1 已走引擎，整合測試才能驗全鏈） |
| **具體實作細節** | ① 產本 commit `.bak`。② `run_phase3` section 分支（現 L487-494）：`translated_title = self._extract_translated_title(slots, zh_by_index) or title` → `translated_title = section_engine.translate_unit(title, inj, tr, "title") if title else title`（與 whole 分支 L486 同式；is_zh 分支零動）；刪除 `_extract_translated_title` 方法整段（先 `grep -rn "_extract_translated_title" --include="*.py"` 確認僅本檔引用）。③ 刪除 `_detect_source_lang` 方法整段（L272-279；先 grep 確認零 caller）。④ `_LITEDOC_META_SYSTEM_PROMPT` 增補規則（英文、與既有 prompt 風格一致）：publisher 輸出正式出版方名稱並修正明顯 OCR 變形（附例 `AI6Z -> a16z`）；authors 正規化 Title Case（`MARC ANDREESSEN -> Marc Andreessen`）；不虛構缺值（沿用既有 Rule 2）。⑤ 補 §7.2 跨 Phase 整合測試（置 `tests/test_ingestion_engine.py`、命名含 `integration`）：構造含 meta 塊（epigraph 夾 byline）+ 2 圖 + 3 section 之 cleaned md + 判型 dict → `assemble` → `section_engine.collect_render_slots` → **key-changing mock 翻譯**（譯文≠原文、如前綴 `[譯]`）→ 按 `restore_sections_markdown` 範式組裝；斷言：2 個 figure `content` 全數穿透至輸出 markdown；文件 title 不出現於 body；meta 行零重播；section title slot `key`＝原文標題 path 可對位查 mock `section_summaries`。⑥ 更新 `tests/test_litedoc_pipeline.py`：section 模式譯題斷言改「呼叫 `translate_unit(title)`、不讀 slot」；post-strip 以正確譯題 key 生效之斷言；cover-prompt 規則存在斷言（讀 `_LITEDOC_META_SYSTEM_PROMPT` 字串含正規化關鍵句）。⑦ 落地前 §5 SOP 雙核查 grep 實貼執行報告。 |

### C_CHECKOUT — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：`baton/2026-07-18_PIPE-INGEST_..._plan.md` → `plans/`、`baton/2026-07-19_PIPE-INGEST_..._tasks.md` → `tasks/`、C1-C3 `_執行.md` → `executions/`；新增 `executions/2026-MM-DD_PIPE-INGEST_checkout_執行.md`；更新 `TODO.md`（結案雙層）+ `archive/TODO_done_archive.md` |
| **安全性** | 🟢 高 — 純文件歸檔、零業務代碼 |
| **可逆性** | 🟢 高 — 檔案移動可逆、`git revert` 可回滾 |
| **驗收 grep 條件** | 見本檔 §6.4（baton 清空本案任務檔／plans/tasks/executions 歸檔到位／`git diff --cached --name-only` 白名單全等自檢實貼） |
| **依賴關係** | 前置：C1-C3 全部 ship 完（baron 回填 hash） |
| **具體實作細節** | ① Conformance 五維度驗收（plan §2 十一規格項對照 C1-C3 報告；tasks §6 驗收全綠；不可動清單 §7 逐項打勾；提示詞歸檔稽核；msg 草稿）。② **§7.2 整合測試存在且通過**確認（跨 Phase 任務 Checkout 必驗、缺則不得 🟢）。③ baton 一次性 `mv`（標準 `mv`、嚴禁 `git mv`）+ 逐檔顯式 `git add`（嚴禁 `git add .`/`-A`/目錄；含 C2/C3 之 4 個 `.bak`）。④ commit 前 `git diff --cached --name-only` 自檢、staged 集合須完全等於宣告清單、實貼 checkout 執行報告。⑤ TODO 雙層結案（active 移除 + `archive/TODO_done_archive.md` 表格 + 索引 pointer + 類別索引）。⑥ 產 `checkout_執行.md`（§8 僅一行 commit 指令、輕量慣例）。⑦ 唤起後續銜接註記：GLOSSARY-ON + GLOSSARY-TERMMAP 前後腳開案（plan §2.11）。 |

---

## §9 Open Questions

無。（plan v4 §9 六 OQ 已全數拍板結案；v4「選 1」定案本案純結構化、術語/括號移交 GLOSSARY-TERMMAP。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-INGEST 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-INGEST executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動 §7 不可動清單所列檔案；嚴禁 constraints 鷹架（v4 移交 GLOSSARY-TERMMAP）；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan v4 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則；接縫契約唯一源＝plan v4 §4 |

### §99.2 Revision 歷程

- v1 (2026-07-19)：初版拆分——依 plan v4（純結構化定案）拆 C1 引擎本體 / C2 P1 切換 / C3 譯題單一源與清理 / C_CHECKOUT 四 commits；§7 增「禁 constraints 鷹架」邊界；§6 各 commit 驗收指令 + SOP 雙核查前置
