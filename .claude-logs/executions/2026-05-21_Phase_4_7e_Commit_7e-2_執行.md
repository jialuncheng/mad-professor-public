# Phase 4.7e Commit 7e-2 — 執行報告（pipeline_core 整合 + doc_analyzer 短路）

> 基準：7e-1 (`ffb3000`) ResumeProcessor + Vision prompt 已 ship
> 完成：本地改檔完成，**尚未 commit、未 push**

---

## §0 Sanity Check 結果（實作前先跑、給 baron 確認下游相容性）

### Check A — Metadata 階段對 markdown 的依賴

`processor/metadata_extractor.py` 既有設計：
- `_PROMPT_BY_DOC_TYPE` (L33-46) 已含 `"resume": "prompt/processor/metadata_resume.txt"`（4.7c step 3 落地）
- Stage A LLM page1 call **直接讀 PDF 第一頁圖片**（`extract_metadata_from_first_page_llm`），**不依賴 .md 內容**
- `candidate_name` 欄位 (L54-65) 4.7d Commit 4-2 已為 resume 專屬加入
- Stage B 從 markdown 抽 abstract——但 resume 跳過 abstract 提取（已在 4.7c skip list）

**結論：✅ Metadata 階段對 ResumeProcessor 輸出 zero dependency**——本 commit 不需動 metadata_extractor。

### Check B — Images 目錄結構與下游

- SlidesProcessor 輸出 `images/slide_NN.jpg`、ResumeProcessor 輸出 `images/page_NN.jpg`
- `processor/image_caption_processor.py:39-41` 掃 `images_dir.iterdir()`、**不過濾檔名 pattern**——只要是 image 就會生 caption
- `processor/rag_processor.py:44` 用 `load_caption_map(images_info_path)`、key 用 `images/{filename}` 對齊 markdown 內 `![](images/{filename})` 連結

**結論：✅ `page_NN.jpg` 會被 image_caption 處理**（與 `slide_NN.jpg` 相同邏輯）。

### Check C — markdown 內 image link 格式

樣本目錄 `/tmp/phase_4_7e_samples/` 已被 tmpfs 清掉、無法直接 grep。但從 code 確認：
- SlidesProcessor 顯式寫 `![slide_NN](images/slide_NN.jpg)` 進 markdown（`processor/slides_processor.py:149`）
- **ResumeProcessor 不寫 image link 進 markdown 內容**（vision 直接輸出 prose、無 image 引用）

**結論：⚠ 已知限制**——ResumeProcessor 輸出的 markdown 不含 `![](images/...)` 連結；image_caption 階段會為 page_NN.jpg 生 caption、但這些 caption 不會被 rag_processor 接回 markdown 內。對履歷 RAG 影響低（履歷主要是文字結構而非圖片解讀），但本 commit 報告留註。如需可在 future 補一個「append images_info into resume.md」step——非本 commit 範圍。

### Check D — 後續 stage 對 `_doc_structure.json` 依賴

- `pipeline_core.py:59` 註冊 `'analyze': '_doc_structure'`（stage 快取查找用）
- `pipeline_core.py:506` cache hit 判斷讀此檔
- `processor/md_processor.py:359` 讀 sidecar、若不存在 fallback `structure = {}` (soft-fail OK)
- `processor/doc_analyzer.py:128` 寫 sidecar（既有 academic 路徑）

**結論：✅ 寫最小 sidecar `{"structure": [], "document_type": "resume", "flat_structure": True}` 完全相容**——既滿足 cache hit + md_processor 讀取、又顯式宣告扁平處理。

---

## Commit Hash

**尚未 commit**——等 baron 確認 Sanity Check 結果 + diff 後再 commit。

| # | Hash | Subject |
|---|---|---|
| 7e-2 | _（pending）_ | feat(pipeline): resume 走獨立 ResumeProcessor + doc_analyzer 短路 |

---

## diff stat（uncommitted）

```
 pipeline_core.py                       |  30 ++++++--   (3 處改動 + KNOWN_DOC_TYPES + marker)
 processor/doc_analyzer.py              |  25 ++++++++   (2 函式短路)
 tools/check_doc_type_registry.py       |  37 +++++++--  (新 PIPELINE_PARSER + KNOWN_DOC_TYPES marker)
 tests/test_pipeline_resume_routing.py  | 138 ++++++++   (新檔、8 個測試)
 4 files changed, +230 / -4
```

---

## 修法摘要

### 1. `pipeline_core.py` — 3 處改動

**A. Line 20 加 import**：
```python
from processor.slides_processor import SlidesProcessor
+from processor.resume_processor import ResumeProcessor
from processor.domain_detector import DomainDetector
```

**B. Module level 加 `KNOWN_DOC_TYPES` + registry marker**（在 `STAGE_NAMES` 之前）：
```python
# === doc_type-registry ===
# Phase 4.7e Commit 7e-2：pipeline 已知 doc_type 全集（對齊
# web_server.valid_types）。新增 doc_type 漏改本處時、_stage_pdf_to_md
# 會 log warning（fallback 走 MinerU），便於偵錯。
# 詳見 docs/HOW_TO_ADD_DOC_TYPE.md。
KNOWN_DOC_TYPES = frozenset({
    'academic', 'book', 'technical', 'slides', 'news', 'web', 'resume'
})
```

**C. `_stage_pdf_to_md` 完整重寫（保留同樣語意 + 加 resume / fallback warn）**：

```python
def _stage_pdf_to_md(self, pdf_path, paper_dir, paper_name, output_paths):
    doc_type = output_paths.get('_confirmed_doc_type', 'academic')

    # === doc_type-registry ===
    if doc_type == 'slides':
        parser = SlidesProcessor()
    elif doc_type == 'resume':
        # Phase 4.7e：履歷用 Vision 整份解析，不走 MinerU + heading_fix
        self.logger.info(f"{...} 履歷類型，使用 Vision 解析")
        parser = ResumeProcessor()
    elif doc_type in KNOWN_DOC_TYPES:
        parser = self.pdf_processor
    else:
        # 未知 doc_type fallback：log warning 留軌跡
        self.logger.warning(
            f"未知 doc_type='{doc_type}'、fallback 至預設 MinerU 路徑、"
            f"請確認 pipeline_core 是否需更新（known: {sorted(KNOWN_DOC_TYPES)}）"
        )
        parser = self.pdf_processor

    markdown_path = parser.parse(str(pdf_path), str(paper_dir))

    # Phase 4.7e：resume 與 slides 同樣跳過 md_cleaner
    if doc_type not in ('slides', 'resume'):
        self.md_cleaner.clean(markdown_path)

    return markdown_path
```

### 2. `processor/doc_analyzer.py` — 2 個函式短路

**A. `_fix_heading_levels` 開頭加 early return**（json 已既有 import）：
```python
def _fix_heading_levels(self, markdown_path: Path, doc_type: str):
    """用 LLM 修正 Markdown 標題層級"""
    # Phase 4.7e Commit 7e-2：resume 走 ResumeProcessor、已輸出正確
    # # 結構（公司 ### 平行、Summary ## 等），跳過 LLM heading fix。
    if doc_type == 'resume':
        self.logger.info(f"[analyze] {doc_type} 走 ResumeProcessor、跳過 heading fix")
        return
    try:
        ...
```

**B. `_analyze_document_structure` 開頭加 minimal sidecar + return**：
```python
def _analyze_document_structure(self, markdown_path: Path, doc_type: str) -> dict:
    """用 LLM 分析文件前段結構"""
    # Phase 4.7e Commit 7e-2：resume 走 ResumeProcessor、不需 LLM structure；
    # 仍寫最小 sidecar 給下游 md_processor 讀（md_processor.py:359 讀
    # _doc_structure.json、若缺 fallback empty dict 行為仍 OK，但顯式寫
    # 出 document_type='resume' + flat_structure=True 讓 md_processor 走
    # 扁平處理路徑）。
    if doc_type == 'resume':
        sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
        minimal = {
            "structure": [],
            "document_type": "resume",
            "flat_structure": True,
        }
        sidecar_path.write_text(json.dumps(minimal, ensure_ascii=False, indent=2), encoding='utf-8')
        self.logger.info(f"[analyze] {doc_type} 走 ResumeProcessor、寫最小 sidecar: {sidecar_path}")
        return minimal
    try:
        ...
```

**為何兩個 sub-stage 各自短路（而非 `analyze()` 入口）**：保險——未來若 `analyze()` 加新 sub-step（如 metadata 補強）也不會誤跑 resume 路徑。

### 3. `tools/check_doc_type_registry.py` — 新 marker + 主集合增 1

**A. 新增 2 個註冊點抽取**：
- `pipeline_core.KNOWN_DOC_TYPES` — 必須等於 truth（加進 `must_equal`）
- `pipeline_core.PIPELINE_PARSER` — 從 `_stage_pdf_to_md` 內所有 `doc_type == 'X'` literal 抽出（subset，目前 = `{slides, resume}`），不要求等於 truth、只報內容供人工確認

**B. 加 2 個 marker check**：
- `pipeline_core.py` + `MARKER_PY` + `"KNOWN_DOC_TYPES = frozenset"`
- `pipeline_core.py` + `MARKER_PY` + `"if doc_type == 'slides':"`

**C. 更新報告**：
- 從 `6 registry points (+1 subset)` → `7 registry points (+2 subsets)`
- 額外印 `PIPELINE_PARSER (subset, 獨立 parser): resume, slides`

實測結果：
```
✓ All doc_types aligned across 7 registry points (+2 subsets):
  academic, book, news, resume, slides, technical, web
  pipeline_core.extra_info_skip (subset): news, resume, slides, web
  pipeline_core.PIPELINE_PARSER (subset, 獨立 parser): resume, slides
✓ All 9 markers present
✓ All required prompts exist
```

### 4. `tests/test_pipeline_resume_routing.py`（新檔、8 個測試）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_pdf_to_md_routes_resume_to_resume_processor` | doc_type='resume' → ResumeProcessor.parse 被呼叫、self.pdf_processor 未被呼叫 |
| 2 | `test_pdf_to_md_routes_academic_to_mineru` | doc_type='academic' → self.pdf_processor.parse 被呼叫、ResumeProcessor / SlidesProcessor 不被建構 |
| 3 | `test_pdf_to_md_skips_md_cleaner_for_resume` | doc_type='resume' → md_cleaner.clean 不被呼叫 |
| 4 | `test_pdf_to_md_runs_md_cleaner_for_academic` | doc_type='academic' → md_cleaner.clean 必被呼叫（對照）|
| 5 | `test_pdf_to_md_unknown_doctype_logs_warning_and_falls_back` | 未知 doc_type → fallback MinerU + log warning |
| 6 | `test_doc_analyzer_skips_resume_heading_fix` | doc_type='resume' → llm.chat / llm.chat_with_image 都不被呼叫 |
| 7 | `test_doc_analyzer_calls_llm_for_academic_heading_fix` | doc_type='academic' → LLM 必被呼叫（對照）|
| 8 | `test_doc_analyzer_writes_minimal_sidecar_for_resume` | doc_type='resume' → 不打 LLM + 寫合法 sidecar + return value 對齊 |

**mock 策略**：用 `patch('pipeline_core.ResumeProcessor')` patch class、`pc._pdf_processor = MagicMock()` 直接設 underscore 屬性繞 lazy property、`MagicMock()` 替 LLMClient。

---

## 不可動清單（已遵守）

- [x] `processor/resume_processor.py`（7e-1 ship）：未動
- [x] `prompt/doc/resume_vision.txt`（7e-1 ship）：未動
- [x] `llm/client.py`（7e-1 ship）：未動
- [x] `processor/slides_processor.py`：未動（只看不改）
- [x] `processor/md_cleaner.py`：未動（既有架構）
- [x] `processor/md_processor.py`：未動（_SHORT_DOC_TYPES 已含 'resume'）
- [x] `processor/metadata_extractor.py`：未動（Sanity Check A 確認不需動）
- [x] `processor/image_caption_processor.py` / `rag_processor.py`：未動
- [x] `settings.py`：未動
- [x] `prompt/doc/heading_fix_resume.txt`（7b 廢棄但保留）：未動
- [x] DB / 前端 / web_server：未動
- [x] commit / push：未動

---

## 驗證結果

```bash
venv/bin/python -m py_compile pipeline_core.py processor/doc_analyzer.py tools/check_doc_type_registry.py
# PYCOMPILE_OK

venv/bin/python -c "from pipeline_core import PipelineCore; from processor.doc_analyzer import DocAnalyzer; from processor.resume_processor import ResumeProcessor; print('OK')"
# OK

venv/bin/python tools/check_doc_type_registry.py
# ✓ All doc_types aligned across 7 registry points (+2 subsets)
# ✓ All 9 markers present
# ✓ All required prompts exist
# exit 0

venv/bin/pytest tests/test_pipeline_resume_routing.py -v
# 8 passed in 0.55s

venv/bin/pytest tests/ -q
# 148 passed, 3 skipped（140 baseline + 8 新增、零回歸）
```

---

## 端到端驗證計畫（給 baron）

### Test A — 上傳 DeHunt 履歷（驗 resume 走獨立路徑）

```bash
# OrcStack 端、push 後重新上傳 DeHunt 履歷
# 觀察 logs/pipeline.log，應看到:
#   [paper_id=N] 履歷類型，使用 Vision 解析
#   [analyze] resume 走 ResumeProcessor、跳過 heading fix
#   [analyze] resume 走 ResumeProcessor、寫最小 sidecar: .../DeHunt_..._doc_structure.json
# 應「不」看到:
#   [md_cleaner] 開始清理...（被跳過）
#   [doc_analyzer] heading fix 輸入: N 行 heading（被跳過）

# 看 output/1/DeHunt_*/DeHunt_*.md：
#   應等同 7e-1 vision test 的輸出（FOCALTECH / NOVATEK 都 ###）

# 看 output/1/DeHunt_*/DeHunt_*_doc_structure.json:
#   應為 {"structure": [], "document_type": "resume", "flat_structure": true}

# 看 output/1/DeHunt_*/DeHunt_*_structured.json:
#   應有 6 個 ### 公司 children（md_processor 走 flat_structure 路徑）
```

### Test B — 上傳新 academic paper（驗 routing 不破既有）

```bash
# 上傳一份 academic paper、確認既有 MinerU + heading_fix LLM 路徑正常
# logs/pipeline.log 應看到:
#   [pdf_processor] 開始 pdf=...（MinerU）
#   [md_cleaner] 開始清理...
#   [analyze] heading fix 輸入: N 行 heading
#   [analyze] structure 分析範圍: N 行（doc_type=academic, 上限=500）
```

### Test C — 上傳 slides（驗既有 slides 路徑不破）

```bash
# 上傳一份 slides、確認 SlidesProcessor 路徑保持
# logs/pipeline.log 應看到:
#   [paper_id=N] 簡報類型，使用 Vision 解析
#   開始 Vision 解析簡報: ...
#   共 N 頁
# 應「不」看到:
#   [md_cleaner]（slides 已跳過）
```

### Test D — 未知 doc_type（驗 fallback warning）

合成測試（內部、不需上傳）：本 commit 已有 unit test 5
（`test_pdf_to_md_unknown_doctype_logs_warning_and_falls_back`）覆蓋。

---

## 已知限制

| 限制 | 影響 | 解法 |
|---|---|---|
| ResumeProcessor 輸出 markdown 不含 `![](images/...)` 連結 | image_caption 仍會為 `page_NN.jpg` 生 caption、但 caption 不接回 markdown | 履歷主要文字結構、影響低；若 baron 需要可 future 補「append images_info into resume.md」step |
| 7a (md_cleaner) 7b (heading_fix_resume.txt) 對 resume 廢棄但未標 deprecation | code 內仍指向 prompt 檔（HEADING_FIX_PROMPTS['resume']） | 7e-4 補 deprecation 註解 |
| metadata_extractor 對 resume 走 markdown 抽取 abstract 的路徑 | 早在 4.7c 已 skip（resume 無 abstract）| 不需動 |
| 既有 6 份 resume 不自動受益 | 需 RAG-2 backfill CLI 或手動重上傳 | 7e-3 baron 手動重上傳 |

---

## 7e-3 後續工作備忘

依 design §6：
1. OrcStack 端手動重上傳 6 份履歷
2. 檢查每份 `_structured.json` / `_rag_tree.json` chunk 結構
3. 跑跨文件 skills 查詢（如「會 Verilog 的 candidate」）驗證 D3 設計
4. diff vs 原 MinerU 輸出（確認補抽公司 + Skills 區段彙整效果）

## 7e-4（可選）後續

- `processor/md_cleaner.py` 註解 resume 已跳過（既有 pipeline_core L562 跳過已生效、md_cleaner 自身不需動）
- `prompt/doc/heading_fix_resume.txt` 檔首加 `<!-- DEPRECATED Phase 4.7e: ResumeProcessor 取代 -->`
- `processor/doc_analyzer.py` `HEADING_FIX_PROMPTS['resume']` 註解加 deprecation 標籤
- `docs/HOW_TO_ADD_DOC_TYPE.md` 補 ResumeProcessor / PIPELINE_PARSER marker 說明

---

## 回退方式

未 commit、直接：
```bash
git checkout pipeline_core.py processor/doc_analyzer.py tools/check_doc_type_registry.py
rm tests/test_pipeline_resume_routing.py
```

若已 commit：
```bash
git revert <hash> --no-edit
```

---

## 狀態

**本地改檔完成、未 commit、未 push**——等 baron：
1. 過目 Sanity Check 4 項結果（§0）
2. 過目 diff（4 檔 +230 / -4）
3. 確認 `tools/check_doc_type_registry.py` 報「7 registry points + 2 subsets, 9 markers」OK
4. 確認 8 個 routing test 涵蓋面充足

確認後 commit + push → 進 7e-3 OrcStack 端到端驗證（Test A/B/C）。
