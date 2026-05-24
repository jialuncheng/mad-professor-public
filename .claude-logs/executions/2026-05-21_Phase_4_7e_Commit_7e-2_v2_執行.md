# Phase 4.7e Commit 7e-2 v2 — 執行報告（pipeline_core 整合 + md_cleaner 對 resume 跳過）

> 基準：7e-1 v2 (`1fb2d7b`) + hotfix (`eb2164c`) 已 ship；目前 HEAD = `eb2164c`
> 完成：本地改檔完成，**尚未 commit、未 push**
> baron Q6 決策：**doc_analyzer 不短路**（vs 舊 7e-2 fdc2838 已 revert）

---

## §0 Sanity Check 結果（實作前已跑、給 baron 確認下游相容性）

### Check A — Metadata 階段對 markdown 的依賴

```
processor/metadata_extractor.py:38   "resume": "prompt/processor/metadata_resume.txt"
```

- `_PROMPT_BY_DOC_TYPE` 已含 resume 專用 prompt（4.7c step 3 落地）
- Stage A LLM page1 call **讀 PDF 第一頁**、不依賴 .md 內容
- Stage B 對 resume skip abstract（既有設計）

**結論：✅ Metadata 階段對 ResumeProcessor 輸出 zero dependency**——不需動 metadata_extractor。

### Check B — Images 目錄結構與下游

```
processor/image_caption_processor.py:34   images_dir = Path(images_dir)
processor/image_caption_processor.py:53   image_files = sorted([...iterdir()...])
```

- ImageCaptionProcessor 用 `iterdir()` + sorted 掃所有 image 檔、**不過濾檔名 pattern**
- SlidesProcessor 寫 `slide_NN.jpg`、ResumeProcessor 寫 `page_NN.jpg` —— 都能被 image_caption 處理

**結論：✅ `page_NN.jpg` 與 `slide_NN.jpg` 同等處理。**

### Check C — markdown 內 image link 格式

`.claude-logs/_phase_4_7e_outputs/` 在 claude-lab 端未建立（vision test 在 OrcStack 跑），無法直接 grep。但從 7e-1 v2 ResumeProcessor 設計：

- Vision prompt 未指示輸出 `![](images/page_NN.jpg)` 連結
- ResumeProcessor 寫 `page_NN.jpg` 到 images/ 目錄（side product）但不在 markdown 內引用

**結論：⚠ 已知限制**——resume.md 不含 `![](images/...)` 連結；image_caption 為 page_NN.jpg 生 caption、但這些 caption 不接回 markdown。對履歷 RAG 影響低（履歷主要文字結構）。**非本 commit 範圍、留 future enhancement**。

### Check D — 後續 stage 對 `_doc_structure.json` 依賴

```
processor/doc_analyzer.py:128     寫 sidecar
processor/md_processor.py:359     讀 sidecar（缺則 fallback empty dict）
pipeline_core.py:59               'analyze': '_doc_structure'  (stage 快取查找)
pipeline_core.py:506              cache hit 判斷
```

**baron Q6 決策**：doc_analyzer **不短路**——academic heading_fix LLM + structure_analyze 對 resume 也跑、`_doc_structure.json` 由 academic 路徑正常寫入（使用 `prompt/doc/heading_fix_resume.txt` 7b 已落地的 resume 專屬 prompt）。

**結論：✅ sidecar 由既有 doc_analyzer 寫、不需本 commit 動 doc_analyzer。**

---

## Commit Hash

**尚未 commit**——等 baron 確認 Sanity Check + diff 後再 commit。

| # | Hash | Subject |
|---|---|---|
| 7e-2 v2 | _（pending）_ | feat(pipeline): resume 走獨立 ResumeProcessor + md_cleaner 跳過（保留 doc_analyzer 雙保險） |

---

## diff stat（uncommitted）

```
 pipeline_core.py                       | 33 ++++++++   (3 處：import + KNOWN_DOC_TYPES + 4-branch routing + md_cleaner skip)
 tools/check_doc_type_registry.py       | 41 ++++++++   (新 PIPELINE_PARSER + KNOWN_DOC_TYPES marker + 2 markers)
 tests/test_pipeline_resume_routing.py  | 96 ++++++++++ (新檔、6 個 routing tests)
 3 files changed, +170 / -4
```

---

## 修法摘要

### 1. `pipeline_core.py` — 3 處改動

**A. Line ~20 加 import**：
```python
from processor.slides_processor import SlidesProcessor
+from processor.resume_processor import ResumeProcessor
from processor.domain_detector import DomainDetector
```

**B. Module level 加 `KNOWN_DOC_TYPES` + registry marker**（在 `STAGE_NAMES` 之前）：
```python
# === doc_type-registry ===
# Phase 4.7e Commit 7e-2 v2：pipeline 已知 doc_type 全集（對齊
# web_server.valid_types）。新增 doc_type 漏改 _stage_pdf_to_md 時、
# 會 log warning（fallback 走 MinerU），便於偵錯。
KNOWN_DOC_TYPES = frozenset({
    'academic', 'book', 'technical', 'slides', 'news', 'web', 'resume'
})
```

**C. `_stage_pdf_to_md` 4-branch routing**（加 resume + fallback warn + md_cleaner skip 加 resume）：

```python
def _stage_pdf_to_md(self, pdf_path, paper_dir, paper_name, output_paths):
    doc_type = output_paths.get('_confirmed_doc_type', 'academic')

    # === doc_type-registry ===
    if doc_type == 'slides':
        parser = SlidesProcessor()
    elif doc_type == 'resume':
        # Phase 4.7e Commit 7e-2 v2：履歷用 Vision 整份解析、忠實轉錄
        # baron Q6 決策：doc_analyzer 仍跑（academic heading_fix LLM
        # 對 resume 走 prompt/doc/heading_fix_resume.txt、為 ResumeProcessor
        # 偶爾誤判 # 數量時的雙保險）
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

    # Phase 4.7e Commit 7e-2 v2：resume 與 slides 同樣跳過 md_cleaner
    if doc_type not in ('slides', 'resume'):
        self.md_cleaner.clean(markdown_path)

    return markdown_path
```

### 2. `processor/doc_analyzer.py` — **不動**（baron Q6 決策）

ResumeProcessor 輸出 .md 後、doc_analyzer.analyze() 仍對 resume 跑：
- `_fix_heading_levels` 讀 `HEADING_FIX_PROMPTS['resume']` = `prompt/doc/heading_fix_resume.txt`（7b RAG-7b 已落地的 resume 專用 prompt）→ LLM 再修一次 # 數量、做為 ResumeProcessor 偶爾誤判時的雙保險
- `_analyze_document_structure` 用 `STRUCTURE_PROMPTS['resume']` = `prompt/doc/structure_academic.txt`（reuse academic、寫 `_doc_structure.json`）

**7b（heading_fix_resume.txt）在這條路徑下被讀、不再是死碼。**

### 3. `tools/check_doc_type_registry.py` — 新 marker + 主集合增 1

**A. 新增 2 個註冊點抽取**：
- `pipeline_core.KNOWN_DOC_TYPES` — 必須等於 truth（加進 `must_equal` 列表）
- `pipeline_core.PIPELINE_PARSER` — 從 `_stage_pdf_to_md` 內所有 `doc_type == 'X'` literal 抽出（subset，目前 = `{slides, resume}`）、不要求等於 truth、只報內容供人工確認

**B. 加 2 個 marker check**：
- `pipeline_core.py` + `MARKER_PY` + `"KNOWN_DOC_TYPES = frozenset"`
- `pipeline_core.py` + `MARKER_PY` + `"if doc_type == 'slides':"`

**C. 更新報告**：6 registry points (+1 subset) → **7 registry points (+2 subsets)**、7 markers → **9 markers**

實測結果：
```
✓ All doc_types aligned across 7 registry points (+2 subsets):
  academic, book, news, resume, slides, technical, web
  pipeline_core.extra_info_skip (subset): news, resume, slides, web
  pipeline_core.PIPELINE_PARSER (subset, 獨立 parser): resume, slides
✓ All 9 markers present
✓ All required prompts exist
```

### 4. `tests/test_pipeline_resume_routing.py`（新檔、6 個測試）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_pdf_to_md_routes_resume_to_resume_processor` | doc_type='resume' → ResumeProcessor.parse 被呼叫、self.pdf_processor 未被呼叫 |
| 2 | `test_pdf_to_md_routes_academic_to_mineru` | doc_type='academic' → self.pdf_processor.parse 被呼叫、不創 ResumeProcessor / SlidesProcessor |
| 3 | `test_pdf_to_md_skips_md_cleaner_for_resume` | doc_type='resume' → md_cleaner.clean 不被呼叫 |
| 4 | `test_pdf_to_md_runs_md_cleaner_for_academic` | doc_type='academic' → md_cleaner.clean 必被呼叫（對照）|
| 5 | `test_pdf_to_md_unknown_doctype_logs_warning_and_falls_back` | 未知 doc_type → fallback MinerU + log warning |
| 6 | `test_pdf_to_md_slides_routing_still_works` | doc_type='slides' → 仍走 SlidesProcessor + 跳過 md_cleaner（既有路徑不破）|

---

## 與舊 7e-2 (`fdc2838`、已 revert) 對照表

| 元件 | 舊 7e-2 | v2 |
|---|---|---|
| `pipeline_core.py` import + KNOWN_DOC_TYPES + routing + md_cleaner skip | ✅ 同 | ✅ **完全保留** |
| `pipeline_core.py` 加未知 doc_type fallback warning | ✅ 同 | ✅ **完全保留** |
| `processor/doc_analyzer.py` 短路 resume（`_fix_heading_levels` early return + `_analyze_document_structure` 寫 minimal sidecar） | ✅ 有 | ❌ **拿掉**（baron Q6 決策：academic LLM 雙保險）|
| `tools/check_doc_type_registry.py` 新 PIPELINE_PARSER + KNOWN_DOC_TYPES marker | ✅ 同 | ✅ **完全保留** |
| `tests/test_pipeline_resume_routing.py` routing tests | ✅ 8 個（含 2 個 doc_analyzer 短路測試）| ⚠ **6 個**（拿掉 2 個 doc_analyzer 短路測試、新加 1 個 slides 路徑保護測試）|

**淨影響**：academic heading_fix LLM 也會對 resume 跑、做為 ResumeProcessor 偶爾誤判 # 數量時的雙保險（baron Q6）。

---

## 不可動清單（已遵守）

- [x] `processor/resume_processor.py`（7e-1 v2 ship）：未動
- [x] `prompt/doc/resume_vision.txt`（7e-1 v2 + hotfix ship）：未動
- [x] `llm/client.py`（7e-1 v2 ship）：未動
- [x] `processor/slides_processor.py`：未動
- [x] `processor/md_cleaner.py`：未動
- [x] `processor/md_processor.py`：未動（_SHORT_DOC_TYPES 已含 'resume'）
- [x] `processor/metadata_extractor.py`：未動（4.7c 已有 resume 專用 prompt）
- [x] `processor/image_caption_processor.py` / `rag_processor.py`：未動
- [x] **`processor/doc_analyzer.py`**：未動（baron Q6: 不短路、academic LLM 雙保險）
- [x] `settings.py`：未動
- [x] `prompt/doc/heading_fix_resume.txt`（7b 既有）：未動（Q6 下反而被用）
- [x] DB / 前端 / web_server：未動
- [x] commit / push：未動

---

## 驗證結果

```bash
venv/bin/python -m py_compile pipeline_core.py tools/check_doc_type_registry.py
# PYCOMPILE_OK

venv/bin/python -c "from pipeline_core import PipelineCore, KNOWN_DOC_TYPES; \
    print(sorted(KNOWN_DOC_TYPES))"
# ['academic', 'book', 'news', 'resume', 'slides', 'technical', 'web']

venv/bin/python tools/check_doc_type_registry.py
# ✓ 7 registry points (+2 subsets)
# ✓ 9 markers present
# ✓ All required prompts exist
# exit 0

venv/bin/pytest tests/test_pipeline_resume_routing.py -v
# 6 passed in 0.60s

venv/bin/pytest tests/ -q
# 149 passed, 3 skipped（143 baseline + 6 新增、零回歸）
```

---

## 端到端驗證計畫（給 baron OrcStack）

### Test A — 重新上傳 DeHunt 履歷（驗 resume 走獨立路徑）

```bash
# 觀察 logs/pipeline.log，應看到：
#   [paper_id=N] 履歷類型，使用 Vision 解析
#   開始 Vision 解析履歷: ...
#   共渲染 11 頁、送 Vision 整份解析
#   Vision 解析履歷完成: .../{paper}.md
#   [analyze] heading fix 輸入: N 行 heading   ← academic 仍跑（Q6 雙保險）
#   [analyze] structure 分析範圍: N 行（doc_type=resume, 上限=500）
# 應「不」看到：
#   清理完成: .../{paper}.md（md_cleaner 被跳過）

# 看 output/1/DeHunt_*/DeHunt_*.md：
#   應等同 7e-1 vision test 輸出（# Tzung-Yuan Lee (李宗原) + FOCALTECH / NOVATEK 都 ###）

# 看 _doc_structure.json：
#   academic 路徑正常寫入、document_type=resume
```

### Test B — 上傳 academic paper（驗 routing 不破既有）

```bash
# logs/pipeline.log 應看到：
#   [pdf_processor] 開始 pdf=...（MinerU）
#   清理完成: ...（md_cleaner 跑）
#   [analyze] heading fix 輸入: N 行 heading
#   [analyze] structure 分析範圍: N 行（doc_type=academic, 上限=500）
```

### Test C — 上傳 slides（驗既有 slides 路徑不破）

```bash
# logs/pipeline.log 應看到：
#   [paper_id=N] 簡報類型，使用 Vision 解析
#   開始 Vision 解析簡報: ...
#   共 N 頁
# 應「不」看到：
#   清理完成（md_cleaner 跳過、既有設計）
```

### Test D — Web 端實測對照（baron 之前觀察的問題）

baron 之前觀察：
> web 上傳 DeHunt 走 MinerU 路徑、FOCALTECH / NOVATEK 沒被補抽 ###

7e-2 v2 整合後：
- web 上傳 DeHunt 走 **ResumeProcessor**（4-branch routing 命中 elif doc_type == 'resume'）
- DeHunt .md 應含 6 家公司 ###（vs MinerU 路徑只抽 3 家）

---

## 已知限制

| 限制 | 影響 | 解法 |
|---|---|---|
| ResumeProcessor 輸出 .md 不含 `![](images/...)` 連結 | image_caption 仍會為 page_NN.jpg 生 caption、但 caption 不接回 markdown | 履歷主要文字結構、影響低；future enhancement |
| `doc_analyzer.py` 對 resume 仍跑 LLM（baron Q6 決策） | 多一次 LLM call（cost / latency）；好處：可修 ResumeProcessor 偶爾誤判 # 數量 | 設計選擇、不算 bug |
| 7e-3 既有 resume backfill 需手動重上傳 | DeHunt + 黃忠偉 + 江元杰 等舊上傳的 resume 仍是 MinerU 結果、不會自動受益 | 7e-3 手動重新上傳 3 份 |
| Priyal_Shah API 不穩 | 可能 vision call 失敗 | 既有 retry decorator 處理；極端時手動重跑 |

---

## 7e-3 後續工作備忘

依 v2 plan §6：

1. OrcStack 端手動重新上傳 3 份待 backfill 履歷：
   - DeHunt（驗 FOCALTECH / NOVATEK 補抽 ###）
   - 黃忠偉（驗 hotfix 投遞抬頭排除 + `# 黃忠偉`）
   - 江元杰（驗 plain text 公司補抽）
2. 對比新舊 `final_*_zh.md`：
   - 主標題：應為 `# {人名}`（v2 ResumeProcessor 輸出 → md_restore §4.1 #1/#2 路徑）
   - section 結構：應為原 PDF section 名稱（個人資料 / 學歷 / 工作經歷 等中文 / Education / Working Experience 等英文）
   - 公司 ### 平行：應補抽完整
3. 跑跨文件 RAG 查詢：「會 Verilog 的 candidate」/「在 ITRI 工作過的人」等
4. 看 `_doc_structure.json` 確認 academic 雙保險 LLM 是否誤改 # 數量（若有、回頭評估 Q6 決策）

---

## 7e-4（可選）

- `processor/md_cleaner.py` 註解 resume 已跳過（既有 pipeline_core 跳過已生效、md_cleaner 自身不需改）
- `docs/HOW_TO_ADD_DOC_TYPE.md` 補 ResumeProcessor / PIPELINE_PARSER / KNOWN_DOC_TYPES 說明
- 7a 7b 不刪、不加 deprecation（v2 下 7a 對 academic / book / news 仍有用、7b 在 doc_analyzer 仍被讀為雙保險）

---

## 回退方式

未 commit、直接：
```bash
git checkout pipeline_core.py tools/check_doc_type_registry.py
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
2. 過目 diff（3 檔 +170 / -4）
3. 確認 `tools/check_doc_type_registry.py` 報「7 registry points + 2 subsets, 9 markers」OK
4. 確認 6 個 routing test 涵蓋面充足

確認後 commit + push → baron OrcStack 端到端 Test A/B/C/D → 進 7e-3 backfill 3 份履歷。
