# PIPE-INGEST-FITZ born-digital 文字層快速道與連字修復 — Tasks

> 本文件為 PIPE-INGEST-FITZ 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md`（v2、六 OQ 已拍板）產出，含 3 個開發 Commit + 1 個 Checkout。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 4 個 | `processor/fitz_processor.py` / `pipelines/ligature_repair.py` / `tests/test_fitz_processor.py` / `tests/test_ligature_repair.py` |
| **修改檔案** | 4 個 | `pipelines/litedoc_pipeline.py`（P1 ①閘門＋②修復接線）/ `settings.py`（三常數）/ `.env.example`（註記）/ `tests/test_litedoc_pipeline.py`（閘門・回歸・§7.2 測試） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（WIP→逐 commit ✅→雙層結案）/ `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan/tasks/C1-C3 執行報告 → `plans/` + `tasks/` + `executions/` + 逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：litedoc 大宗 born-digital PDF 一律繞道 MinerU（慢、佔推理通道、OCR 噪音如 `AI6Z`）；PDF 字型層連字壞字（`Pro1les`/`;rst`）兩攝入法共病、無人修。
- **解法**：三個原子 commit——`C1 — Fitz Processor（Fitz 直抽處理器）`（純加法新檔、`PDFParser` 第二 impl、零接線）→ `C2 — Ligature Repair（連字修復純函式）`（純加法新檔、雙閘防誤殺、零接線）→ `C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）`（唯一接線點：P1 ①文字層閘門 + ②修復步 + settings 三常數 + §7.2 整合測試）→ `C_CHECKOUT — 收官歸檔（收官歸檔）`。
- **影響範圍**：僅 litedoc P1 攝入段 + 兩個純加法新模組；MinerU 路／A 軌／resume／slides／下游 P2-P4 零改；零 DB、零 API 簽名。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | `run_phase1` L155 唯一呼叫 `PDFProcessor().parse`（MinerU）；L157 `MarkdownCleaner().clean` | born-digital 無快速道；連字壞字無修復步 |
| `processor/pdf_parser.py` | `PDFParser` ABC 既備（parse 契約 + `PDFParseError` + images/ side-effect） | 僅一個 impl（MinerU）；本案不改、僅新增第二 impl |
| `processor/pdf_processor.py` | MinerU impl、A 軌 pipeline_core 共用、產 `{stem}.md` + `images/` | 零缺失——本案 byte 不動（後盾） |
| `requirements.txt:26` | `PyMuPDF==1.27.2.3` 已 pin | 零缺失——零新依賴 |
| `settings.py` | 已有 `IMG_FILTER_*`（L127-132）等 env 常數慣例 | 缺 `LITEDOC_FITZ_ENABLED` / `LITEDOC_FITZ_MIN_CHARS_PER_PAGE` / `LITEDOC_LIGATURE_REPAIR_ENABLED` |
| `pipelines/image_filter.py` | stdlib 尺寸解析、覆蓋 PNG/JPEG | 零改——fitz 路圖檔限 PNG/JPEG 落地即同基準相容 |

---

## §3 觀察問題

### 問題 #1：born-digital PDF 全數繞道 MinerU
- **證據**：`pipelines/litedoc_pipeline.py:155`（`PDFProcessor().parse` 為 P1 唯一攝入路）；design spec F6 實測 SpaceX.pdf 23 頁全有文字層、pypdf 直抽 OK。
- **影響**：速度／推理通道成本白付；OCR 引入 publisher 噪音（`AI6Z`）；MinerU 跨頁截斷已知限制（#8）。

### 問題 #2：連字壞字無修復
- **證據**：design spec F6——SpaceX.pdf `Pro1les`/`;rst`/`de1ning`、PDF 字型 ToUnicode 映射壞、直抽/MinerU 共病。
- **影響**：正文噪音進 tiles → 翻譯/RAG/顯示全鏈帶病。

### 問題 #3：閘門不可下沉共用處理器
- **證據**：`processor/pdf_processor.py` 為 A 軌 pipeline_core 共用；plan §2.5 方案 C 否決留痕。
- **影響**：拆分必須把閘門放 litedoc 呼叫端（C3），C1/C2 保持零接線純加法。

---

## §4 設計方案

### §4.1 C1 — Fitz Processor（Fitz 直抽處理器）
純加法新建 `processor/fitz_processor.py`：`FitzProcessor(PDFParser)` 完整履行 ABC 契約（`parse(pdf_path, output_dir) -> output_dir/{stem}.md`、圖 side-effect `images/`、失敗統一 `PDFParseError`）＋模組級 `median_page_chars(pdf_path)` 閘門輔助（供 C3 呼叫端判定、本 commit 不接線）。同形 .md 硬契約：`\n\n` 段落分隔、標準 `#`/`##`（字級分群推導）、`![](images/page_{page_idx}_{xref}.{ext})` 閱讀序嵌入（限 PNG/JPEG 落地）、區塊座標排序、跨頁重複頁首尾剝除。**零 `fitz.metadata` 讀取**。附 `tests/test_fitz_processor.py`（fitz 程式化生成 PDF fixture、零網路零 MinerU）。

### §4.2 C2 — Ligature Repair（連字修復純函式）
純加法新建 `pipelines/ligature_repair.py`：`repair_ligatures(text: str) -> str` 純函式——「小寫×異常字元×小寫」窗口（含 `;rst` 字首形態）、候選 `fi/fl/ff/ffi/ffl`、**雙閘**（替換前 `\b\d+(st|nd|rd|th|s)?\b`/`v\d+` 排查；替換後詞形檢查＝系統字典 `/usr/share/dict/words` 優先＋內建兜底字彙集）、不確定保留、**行數不變式**。零接線。附 `tests/test_ligature_repair.py`。

### §4.3 C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）
唯一接線 commit：
- `settings.py` 三常數（`LITEDOC_FITZ_ENABLED` 預設 true / `LITEDOC_FITZ_MIN_CHARS_PER_PAGE=150` / `LITEDOC_LIGATURE_REPAIR_ENABLED` 預設 true）+ `.env.example` 註記；
- `run_phase1` ①：閘門（enabled 且 `median_page_chars ≥ 門檻` → `FitzProcessor().parse`、否則現行 MinerU；FitzProcessor 例外 fail-open 退 MinerU + warning `exc_info=True`）；
- `run_phase1` ②後③前：`repair_ligatures` 修復步（flag 閘、改寫 md 檔、行數不變）；
- litedoc 測試：路由三態（fitz/退 MinerU/fail-open）、flag off byte 等價回歸、**§7.2 整合測試**（fitz 生成實體 PDF → 真 FitzProcessor→cleaner→修復→`_build_tiles` 端到端）。

### §4.4 C_CHECKOUT — 收官歸檔（收官歸檔）
Conformance 驗收（plan v2 §2 對照 + §7.2 必驗）→ TODO 雙層結案 → baton 一次性 `mv` + 逐檔 `git add` → `checkout_執行.md`（staged-set 實貼）→ `/tmp` msg 草稿。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| heading 字級推導與 MinerU 產出落差 → 判型/切節漂移 | 🟡 中 | C1 測試鎖同形契約；C3 影子 E2E SpaceX 對照；`LITEDOC_FITZ_ENABLED=false` 秒回 MinerU |
| 連字修復誤殺（`1st`/`v1` 類） | 🟡 中 | C2 雙閘 + 誤殺守門測試（字典缺席環境走兜底集斷言） |
| C3 接線破壞現行 MinerU 路 | 🟢 低 | flag off byte 等價回歸測試；fail-open 全包 try |
| A 軌回歸 | 🟢 低 | `pdf_processor.py`/`md_cleaner.py` byte 不動（§7 + git diff 自檢） |
| golden 基準 | 🟢 低 | litedoc 影子軌、循 B 軌改善豁免慣例；A 軌 golden 零觸碰 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "class FitzProcessor(PDFParser)" processor/fitz_processor.py        # 期望：命中（ABC 第二 impl）
grep -n "PDFParseError" processor/fitz_processor.py                          # 期望：命中（失敗統一型別）
grep -n "page_{" processor/fitz_processor.py                                 # 期望：命中（圖檔命名防衝突）
grep -n "\.metadata" processor/fitz_processor.py                             # 期望：無命中（零檔案屬性依賴）
grep -rn "fitz_processor" pipelines/ web_server.py pipeline_core.py          # 期望：零命中（C1 零接線）
venv/bin/python -m pytest tests/test_fitz_processor.py tests/ -x -q          # 期望：新測試全過、全套件零回歸
```

### §6.2 C2 驗收

```bash
grep -n "def repair_ligatures" pipelines/ligature_repair.py                  # 期望：命中
grep -n "words" pipelines/ligature_repair.py                                 # 期望：命中（系統字典優先＋兜底集）
grep -rn "ligature_repair" pipelines/litedoc_pipeline.py processor/          # 期望：零命中（C2 零接線）
venv/bin/python -m pytest tests/test_ligature_repair.py tests/ -x -q         # 期望：新測試全過、全套件零回歸
```

### §6.3 C3 驗收

```bash
grep -n "LITEDOC_FITZ_ENABLED\|LITEDOC_FITZ_MIN_CHARS_PER_PAGE\|LITEDOC_LIGATURE_REPAIR_ENABLED" settings.py   # 期望：三常數
grep -n "FitzProcessor\|median_page_chars\|repair_ligatures" pipelines/litedoc_pipeline.py                     # 期望：閘門＋修復接線命中
git diff --stat processor/pdf_processor.py processor/md_cleaner.py           # 期望：零 diff（A 軌後盾 byte 不動）
grep -n "TestFitzIntegration\|integration" tests/test_litedoc_pipeline.py    # 期望：§7.2 整合測試存在
venv/bin/python -m pytest tests/ -q                                          # 期望：全套件通過（基線 831 → 遞增）
```

### §6.4 SOP 一致性核查（每 commit 落地前必貼）

```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <修改檔.py>   # logger.error 必含 exc_info=True
grep -nE "\.commit\(\)" <修改檔.py> | grep -v "with .*session.*begin\(\)"      # 期望：無命中（本案零 DB）
```

---

## §7 不可動清單

- [ ] `processor/pdf_processor.py` 全檔（MinerU impl、A 軌共用；閘門嚴禁下沉）
- [ ] `processor/pdf_parser.py` `PDFParser` ABC 簽名與語意契約
- [ ] `processor/md_cleaner.py`（A 軌共用；連字修復嚴禁寫入）
- [ ] `processor/doc_analyzer.py` 判型邏輯與 doc_structure schema
- [ ] `pipelines/ingestion_engine.py` / `pipelines/image_filter.py`（含三門檻常數）/ `pipelines/section_engine.py`
- [ ] litedoc P1 ③-⑦ 既有步序、`_extract_litedoc_metadata` cover-prompt（`language` 欄屬 LANG-DETECT、嚴禁夾帶）、`classify_source_lang`
- [ ] `contracts.py` 凍結合約；resume／slides／A 軌 `pipeline_core.py`／`web_server.py`／`paper_manager.py`
- [ ] **嚴禁**新第三方依賴；**嚴禁**讀 `fitz.metadata`；**嚴禁** `git commit`／`git push`（baron 手動）

---

## §8 推薦 Commit 拆分

### C1 — Fitz Processor（Fitz 直抽處理器）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `processor/fitz_processor.py`、新增 `tests/test_fitz_processor.py`（全新檔、無 `.bak`） |
| **安全性** | 🟢 高 — 純加法新檔、零接線（無任何業務碼 import）、runtime 零影響 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾（無他檔耦合） |
| **驗收 grep 條件** | §6.1 全項 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `FitzProcessor(PDFParser)`：`parse(pdf_path, output_dir)` — `fitz.open` 逐頁 `get_text("dict")` 取區塊（含字級 span）、按座標排序組閱讀序；字級分群（最大群→`#`、次級→`##`、正文不加）；段落以 `\n\n` 分隔（MinerU 同形契約）；跨頁重複行偵測（頂／底 band + 出現 ≥2 頁）剝列印頁首尾；`page.get_images()`→`doc.extract_image(xref)` 抽原生圖、**僅 PNG/JPEG 落地** `output_dir/images/page_{page_idx}_{xref}.{ext}`、於對應座標位嵌 `![](images/<fname>)`；寫 `output_dir/{stem}.md` 回傳 Path；任何解析異常統一 raise `PDFParseError`（不洩漏 impl 細節）；**全檔零 `fitz.metadata` 讀取**。② 模組級 `median_page_chars(pdf_path) -> float`：逐頁 `get_text()` 字元數取中位數（閘門輔助、C3 才接線）。③ 測試：fitz 程式化生成 born-digital fixture（`insert_text`/`insert_image`、零網路）——同形契約（`\n\n`/`#`/`##`）、閱讀序、頁首尾剝除、圖檔命名唯一性與 PNG/JPEG 限定、`median_page_chars` 有字/無字鴻溝、壞檔 `PDFParseError`。日誌依 logging SOP（異常 `exc_info=True`）。 |

### C2 — Ligature Repair（連字修復純函式）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `pipelines/ligature_repair.py`、新增 `tests/test_ligature_repair.py`（全新檔、無 `.bak`） |
| **安全性** | 🟢 高 — 純函式零副作用、零接線、零依賴新增 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾 |
| **驗收 grep 條件** | §6.2 全項 |
| **依賴關係** | 無前置（與 C1 互相獨立） |
| **具體實作細節** | ① `repair_ligatures(text: str) -> str`：逐行處理（**行數不變式**——僅行內替換、嚴禁增刪行）；tokenize 逐詞掃「小寫字母×異常字元（`1`/`;` 等常見壞映射）×小寫字母」窗口（含字首形態如 `;rst`）；**第一閘**＝替換前正則排查：詞匹配 `\b\d+(st|nd|rd|th|s)?\b` 或 `v\d+`（版本號）一律跳過；候選連字 `fi/fl/ff/ffi/ffl` 逐一嘗試；**第二閘**＝替換後詞形檢查：模組載入時嘗試讀 `/usr/share/dict/words`（存在才用、lazy 一次快取）＋內建常見連字字彙集（`first/profiles/defining/...` 兜底常數）——替換結果為有效詞方採信、否則保留原樣（fail-open）。中文行／非 ASCII 窗口天然不命中。② 測試：`Pro1les→Profiles`/`;rst→first`/`de1ning→defining` 正修；`1st`/`2nd`/`v1`/`v1.2`/`M1 晶片`/中文行不動（雙閘守門）；行數不變式；monkeypatch 字典缺席→兜底集仍正修。 |

### C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`、`settings.py`、`.env.example`、`tests/test_litedoc_pipeline.py` + 4 個 `.bak`（入 `.claude-logs/archive/`、隨本 commit `git add`） |
| **安全性** | 🟡 中 — 唯一接線點、觸碰 P1 攝入主流程；flag off byte 等價 + fail-open 雙保險 |
| **可逆性** | 🟢 高 — `git revert C3` 回滾接線；或免 revert `LITEDOC_FITZ_ENABLED=false` env 秒回 MinerU |
| **驗收 grep 條件** | §6.3 全項 + §6.4 SOP 雙核查 |
| **依賴關係** | 前置 C1（FitzProcessor/median_page_chars）+ C2（repair_ligatures） |
| **具體實作細節** | ① `settings.py`（IMG_FILTER 區塊後、沿 env 慣例）：`LITEDOC_FITZ_ENABLED`（default "true"）/ `LITEDOC_FITZ_MIN_CHARS_PER_PAGE=150` / `LITEDOC_LIGATURE_REPAIR_ENABLED`（default "true"）；`.env.example` 註記三常數（kill-switch 範例）。② `run_phase1` 步驟①改閘門：`if settings.LITEDOC_FITZ_ENABLED and median_page_chars(pdf_path) >= 門檻:` → `try: md_path = FitzProcessor().parse(...)`、`except Exception → logger.warning(exc_info=True) + 退 MinerU`；else → 現行 `PDFProcessor().parse` 原樣；閘門判定結果 `logger.info`（路由審計）。③ 步驟②後③前插修復步：flag on 時 `md_path.write_text(repair_ligatures(md_path.read_text()))`（在 `MarkdownCleaner().clean` 後、`DocAnalyzer().analyze` 前——doc_structure 行索引同基準）。④ 測試：閘門路由三態（born-digital→fitz／稀疏→MinerU〔mock parse〕／FitzProcessor 拋例外→fail-open 退 MinerU + warning）；兩 flag off → 現行路徑等價回歸（spy 斷言 PDFProcessor 被呼、md 未改寫）；**§7.2 整合測試**：fitz 生成含標題/圖/頁首尾雜訊/連字壞字之實體 PDF → 真 `FitzProcessor`→真 cleaner→真 `repair_ligatures`→真 `_build_tiles` 端到端——斷言 tiles 結構、連字已修、figure 穿透 image_filter、doc_structure 行界同基準（key-changing＝真實 PDF→md 轉換）。⑤ §6.4 SOP 雙核查實貼。 |

### C_CHECKOUT — 收官歸檔（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `archive/TODO_done_archive.md` / `prompts/`（本任務全數提示詞 + INDEX.md）/ baton→`plans/`+`tasks/`+`executions/` 歸檔檔 / `executions/<日期>_PIPE-INGEST-FITZ_checkout_執行.md` |
| **安全性** | 🟢 高 — 純文件歸檔、零業務代碼 |
| **可逆性** | 🟢 高 — `git revert` 回滾歸檔 commit |
| **驗收 grep 條件** | Conformance 對照 plan v2 §2 全項 + `§7.2 整合測試存在且通過` + staged-set 自檢（`git diff --cached --name-only` ＝ 宣告清單完全相等） |
| **依賴關係** | 前置 C1-C3 全數 ship |
| **具體實作細節** | 依 WORKFLOW_SOP §3 收官鐵律：Conformance 驗收 → TODO 雙層結案（active 移除 + archive 表格 + pointer + 類別索引）→ baton 一次性 `mv`（標準 mv、禁 git mv）→ 逐檔顯式 `git add`（嚴禁 `git add .`/`-A`/目錄）→ `checkout_執行.md`（staged-set 實貼 + §8 一行 commit）→ `/tmp` msg 草稿；commit 由 baron 手動。 |

---

## §9 Open Questions

無。（plan v2 六 OQ 已於 2026-07-21 review 全數拍板、無遺留。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-INGEST-FITZ 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-INGEST-FITZ executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（拆分階段）；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計規格唯一源＝plan v2；全局硬規則唯一源＝CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-21)：初版拆分完成——C1 Fitz Processor（純加法）/ C2 Ligature Repair（純加法）/ C3 Litedoc P1 Gate Wiring（唯一接線 + §7.2 整合測試）/ C_CHECKOUT；依 plan v2（六 OQ 拍板）
