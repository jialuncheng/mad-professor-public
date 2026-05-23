# Phase 4.7e Commit 7e-1 — 執行報告（ResumeProcessor + Vision prompt + chat_with_images）

> 基準：7b 後 worktree 狀態（已 commit `5c182cf`）
> 完成：本地改檔完成，**尚未 commit、未 push**
> 等 baron 跑 `tools/test_resume_vision.py` 看輸出品質後再決定 commit / prompt 迭代

---

## 環境驗證（實作前已跑、記錄供 baron 確認）

```
PyMuPDF 1.27.2.3                                   ✅ 已裝
llm/client.py:86  def chat_stream_by_sentence(     既有 stream method
llm/client.py:192 def chat_with_image(             既有單張 vision
llm/client.py:225 def chat_with_images(            本 commit 新增（複數）
llm/retry.py:29  'timeout'                         retry_call 用字串 match 'timeout' 例外、無內建 timeout 參數
settings.LLM_VISION_MODEL = gemini-3.1-pro-preview ⚠ baron env 用 Pro 預覽（非 Flash），cost / latency 偏高
_api_semaphore 用法：既有 chat/chat_with_image 用 `with` context manager（L62/101/202）
                     新 chat_with_images 用 explicit acquire/try/finally（強化保護）
```

**重要環境發現**：
- `LLM_VISION_MODEL = gemini-3.1-pro-preview` —— baron OrcStack 用 Gemini 3 Pro 預覽版（非 Flash）。多頁履歷 Vision call latency 可能達 30-90s、cost 較高（每 call $0.005-0.01）。本 commit 的 try/finally semaphore 保護**特別有意義**——若 Pro 預覽 timeout、retry 中途拋例外、必須確保 semaphore release，否則整個 LLMClient（並發 6）會被卡死。
- `retry_call` 無內建 timeout 參數、靠字串 match `'timeout'` / `'5xx'` 等例外做 retry —— 新 `chat_with_images` 加 `timeout` 參數**僅介面保留**（advisory，等未來 SDK 升級 plug-in）；目前實際 timeout 由底層 HTTP transport 決定。

---

## Commit Hash

**尚未 commit**——預期 prompt 需迭代 2-3 輪、baron 看樣本輸出後再 commit。

| # | Hash | Subject |
|---|---|---|
| 7e-1 | _（pending）_ | feat(resume): ResumeProcessor + Vision prompt + chat_with_images |

---

## diff stat（uncommitted）

```
 llm/client.py                      |  47 +++++  (新增 chat_with_images，47 行)
 processor/resume_processor.py      | 199 +++++ (新檔)
 prompt/doc/resume_vision.txt       | 114 +++++ (新檔)
 tests/test_resume_processor.py     | 191 +++++ (新檔)
 tools/test_resume_vision.py        | 142 +++++ (新檔)
 5 files changed, +693
```

---

## 修法摘要

### 1. `llm/client.py` 加 `chat_with_images()`（複數版、47 行）

**對齊既有 `chat_with_image()`（單張）**：
- 同 `@retry_call(retries=3, base=2.0)` decorator
- 同 `_convert_messages()` + `types.Content` / `types.Part.from_bytes`
- 迴圈塞多個 image_part（順序保留）

**強化（vs 直接 copy 既有）**：
- **Semaphore 用 explicit `acquire()` + try/finally**（取代既有 4 處 `with LLMClient._api_semaphore:`）：履歷 Vision call 較長（30-90s）、任何例外（含 Pro 預覽 timeout）必須確保 release，否則 LLMClient 並發鎖死。
- **新增 `timeout: float = None` 參數**：advisory only，SDK 不支援 per-call timeout、保留介面為未來 plug-in
- **既有 `chat_with_image()` / `chat_stream_by_sentence` / `chat`：零改動**（已 grep 確認 SlidesProcessor / ImageCaptionProcessor / DomainDetector / MetadataExtractor 4 個既有 caller 不受影響）

### 2. `prompt/doc/resume_vision.txt`（新檔、114 行）

依 design §2.1 完整 prompt + **3 條強化指令**：

| 強化區段 | 對應問題 | 內容 |
|---|---|---|
| **多語履歷規則** | 雙語履歷（Priyal_Shah 英中並列）prompt 易搖擺 | 「**雙語履歷以英語為主**、中文姓名 / 公司中英並陳」+「絕對不要在『翻譯』和『保留原文』之間搖擺」 |
| **Vision 輸出規則（防 hallucination）** | LLM 把履歷強塞 markdown table | 「Working Experience 一律 list + prose」「唯一可用 table 場景：原 PDF 真的是 table」「不要憑空生成 PDF 內沒有的資訊」 |
| **輸出限制（嚴格遵守）** | LLM 加 preamble / 末尾客套 | 顯式禁止 14 種 preamble 範例（中英）：「以下是」「Here is」「Below is」「I have parsed」「希望這對您有幫助」等 |

其他內容依 design §2.1：主標題 # 規則、Candidate Summary ## 合併原則、Working Experience ### 平行規則、Technical Skills ## 跨文件 RAG key、6 條邊界 case。

### 3. `processor/resume_processor.py`（新檔、199 行）

依 design §1.1 骨架 + **2 點強化**：

**強化 A — 圖檔大小檢查（防 API 超時）**：
```python
MAX_PAGE_JPEG_BYTES = 10 * 1024 * 1024  # 10 MB
RENDER_MATRIX_LOW = fitz.Matrix(1.5, 1.5)

# 在 _render_pages 內：
pix = doc[i].get_pixmap(matrix=RENDER_MATRIX)
jpg = pix.tobytes("jpeg")
if len(jpg) > MAX_PAGE_JPEG_BYTES:
    self.logger.warning(...)
    pix = doc[i].get_pixmap(matrix=RENDER_MATRIX_LOW)
    jpg = pix.tobytes("jpeg")
```

**強化 B — Post-process 移 preamble + strip code fence + validate**：
```python
def _post_process_vision_output(self, raw, paper_name):
    # 1. strip code fence (```markdown ... ``` 或 ``` ... ```)
    # 2. 移 preamble（14 種中英 prefix、找第一個 # 開頭行作真正起點）
    return text

def _validate_vision_output(self, text, paper_name):
    # 第一個非空行非 # 開頭 → raise PDFParseError
    # 無 ## Working Experience → log warning（學生 / 自由業可能無）
```

呼叫順序：`_render_pages` → `_analyze_resume`（Vision call）→ `_post_process_vision_output`（拔殼 + 移 preamble）→ `_validate_vision_output`（驗證）→ 寫檔。

### 4. `tests/test_resume_processor.py`（新檔、11 個測試、191 行）

不打實際 LLM、用 `MagicMock`：

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_parse_creates_md_file` | mock LLM → .md 寫出、檔名 = `{stem}.md`、內容符合預期 |
| 2 | `test_parse_creates_page_images` | 2 頁 PDF → `images/page_01.jpg` + `page_02.jpg`、JPEG magic bytes |
| 3 | `test_render_dpi_correct` | 確認 RENDER_MATRIX = 2.5 |
| 4 | `test_vision_call_passes_images_and_model` | `chat_with_images` 收到 2 張 image + `LLM_VISION_MODEL`（monkeypatched）|
| 5 | `test_strip_code_fence_markdown` | ` ```markdown\n#...\n``` ` → strip |
| 6 | `test_strip_code_fence_plain` | ` ```\n#...\n``` ` → strip |
| 7 | `test_remove_preamble_en` | `"Here is the parsed resume:\n\n# Title"` → 移 preamble + log warning |
| 8 | `test_remove_preamble_zh` | `"以下是您的履歷整理：\n\n# Title"` → 移 preamble + log warning |
| 9 | `test_validate_no_heading_raises` | 非 # 開頭、非 preamble pattern → raise `PDFParseError("不是 # 開頭")` |
| 10 | `test_validate_no_working_experience_warns` | 無 `## Working Experience` → log warning（不 raise）|
| 11 | `test_failure_raises_pdfparseerror` | LLM `RuntimeError` → 包成 `PDFParseError("Vision resume parse failed")` |

### 5. `tools/test_resume_vision.py`（新檔、CLI 驗證腳本、142 行）

對 `/tmp/phase_4_7e_samples/resume_samples/` 6 份履歷各跑一次、輸出寫 `.claude-logs/_phase_4_7e_outputs/{paper}/`（gitignored）。

**強化（vs 簡單迭代）**：
- `structure_check()` 自動偵測 6 種結構問題：
  - ❌ 缺主標題（# 開頭）
  - ⚠ ### 數量 = 0 / 僅 1 個（平行公司未被識別）
  - ⚠ 缺 `## Working Experience` / `## Candidate Summary` / `## Technical Skills` 區段
  - ⚠ Vision Hallucination 風險：>2 個 markdown table
- **每份印耗時 + 平均耗時**（評估 Vision call latency）
- **末尾估算 cost**（提醒 baron 6 × Vision call 約 $0.5-1）
- 失敗單份不中止迴圈、繼續下一份

**不自動跑**（會花錢）：
```bash
venv/bin/python tools/test_resume_vision.py
```

---

## 與既有架構對齊度

| 面向 | SlidesProcessor | ResumeProcessor | 對齊度 |
|---|---|---|---|
| 繼承 | `PDFParser` ABC | 同 | ✅ |
| 入口 | `parse(pdf, dir) -> Path` | 同（call `process()`）| ✅ |
| 渲染 | PyMuPDF `Matrix(2.0)` | `Matrix(2.5)` + fallback `Matrix(1.5)` | ✅ 同 PyMuPDF、dpi 因履歷字密更高 |
| Vision call | per-page `chat_with_image` | one-shot `chat_with_images`（新介面）| ✅ 不同設計（履歷整份結構連貫） |
| 輸出 | `output_dir/{stem}.md` | 同 | ✅ |
| images side product | `slide_NN.jpg` | `page_NN.jpg` | ✅ 同模式 |
| 失敗模式 | warn + skip 該頁 | raise `PDFParseError` | ⚠ 不同（履歷強耦合、不可丟頁） |
| LLMClient 用法 | `self.llm = llm or LLMClient.get_instance()` | 同 | ✅ |
| Semaphore 保護 | `with LLMClient._api_semaphore:`（既有）| explicit `acquire/try/finally`（強化）| ✅ 等效，更明確 |

---

## prompt 完整內容（為了報告自包含）

見 `prompt/doc/resume_vision.txt` 114 行。骨架：

```
你是處理「履歷 / Curriculum Vitae」的 AI 助手...

# 輸出格式（嚴格遵守）
  # {職稱} Resume - {人名}
  ## Candidate Summary  (Edu / Skills / Honors / Languages 合併 prose)
  ## Working Experience
    ### {公司} - {職稱} ({期間})  (每公司平行、最新在上)
  ## Technical Skills  (條列、跨文件 RAG key)

# 主標題規則（fallback: Candidate Resume - {人名}）
# Working Experience 規則（平行、補抽 plain text、自傳不重複）
# Candidate Summary 規則（合併、prose、不複製 Working Experience）
# Technical Skills 規則（彙整、跨文件 RAG key）

# 多語履歷規則（雙語以英語為主、絕不搖擺）       ← 強化 1
# 邊界 case（純圖檔 / 自由業 / 雙語 / 推薦信 / 浮水印 / 學生）
# Vision 輸出規則（防 hallucination：不亂塞 table、不憑空生成）  ← 強化 2
# 輸出限制（嚴格遵守、禁 preamble / code fence / 末尾客套）       ← 強化 3
```

---

## 不可動清單（已遵守）

- [x] `pipeline_core.py`：未動（7e-2 才動）
- [x] `processor/doc_analyzer.py`：未動（7e-2 才動）
- [x] `processor/slides_processor.py`：未動（只看不改）
- [x] `processor/pdf_parser.py`（ABC）：未動
- [x] `processor/md_cleaner.py`：未動（7a 不動）
- [x] 既有 `chat_with_image()`（單張）：未動 — 已 grep 4 個既有 caller 全部不變
- [x] `settings.py`：未動（沿用既有 `LLM_VISION_MODEL`）
- [x] `tools/check_doc_type_registry.py`：未動（7e-4 才更新）
- [x] `prompt/doc/heading_fix_resume.txt`（7b 既有）：未動
- [x] DB / 前端 / web_server：未動
- [x] commit / push：未動

### 既有 `chat_with_image` callers 確認（已 grep）

```
processor/image_caption_processor.py:100   ✅ 既有，未動
processor/slides_processor.py:170, 183     ✅ 既有，未動
processor/metadata_extractor.py:404        ✅ 既有，未動
processor/domain_detector.py:59            ✅ 既有，未動
tests/test_metadata_extractor.py:40, 309   ✅ 既有，未動
```

---

## 驗證結果

```bash
venv/bin/python -m py_compile llm/client.py processor/resume_processor.py tools/test_resume_vision.py
# PYCOMPILE_OK

venv/bin/python -c "from processor.resume_processor import ResumeProcessor; print('OK')"
# OK

venv/bin/python -c "from llm.client import LLMClient; print(hasattr(LLMClient, 'chat_with_images'))"
# True

venv/bin/pytest tests/test_resume_processor.py -v
# 11 passed in 2.66s

venv/bin/pytest tests/ -q
# 140 passed, 3 skipped（129 baseline + 11 新增、零回歸）
```

---

## 下一步驗證（給 baron）

### 1. 跑 CLI 對 6 份樣本

⚠ **會打 LLM API（gemini-3.1-pro-preview）、估 $0.5-1**：

```bash
# 確認樣本已解壓
ls /tmp/phase_4_7e_samples/resume_samples/
# CV_Chinyu_Lin_2308 / DeHunt_CTO_Tzung-Yuan_Lee / Priyal_Shah_CV / YuLun_Wu_CV / 江元杰 / 黃忠偉

# 確認 GEMINI_API_KEY 設好
echo $GEMINI_API_KEY | head -c 10

# 跑驗證
venv/bin/python tools/test_resume_vision.py
```

輸出位置：`.claude-logs/_phase_4_7e_outputs/{paper_name}/{paper_name}.md`（+ `images/page_NN.jpg`）

### 2. 審視重點（每份 .md）

| 項 | 重點 | 樣本對照 |
|---|---|---|
| 主標題格式 | `# {職稱} Resume - {人名}` | 全部 6 份 |
| Working Experience 平行 | 每公司獨立 `###`、不互為子節 | 全部 6 份 |
| **plain text 公司補抽** | FOCALTECH-SYSTEM / NOVATEK 是否被識別 ### | **DeHunt（11 頁）** |
| Technical Skills 彙整 | 跨各處、條列、硬技能優先 | 全部 6 份 |
| 多語履歷穩定性 | 中英並列 / 純中文正確 | **黃忠偉 / Priyal_Shah / 江元杰** |
| 自傳重複不重建 | 黃忠偉自傳 4 家公司**不**再開 ### | **黃忠偉** |
| 雙語並列 | 同 PDF 英中→視為一人 + 英語為主 | **Priyal_Shah** |
| 結構奇特 case | SERVICES OFFERED / 自由業 → 「Freelance」fallback | **Priyal_Shah / YuLun_Wu_CV / 江元杰** |
| 學生 / 短履歷 | 1 頁完整、結構簡 | **CV_Chinyu_Lin（1 頁）** |
| **無 table 濫用** | 履歷不應有 >2 個 table（structure_check 會 warn）| 全部 6 份 |
| **無 preamble** | 第一行直接 `#` | 全部 6 份 |

### 3. 結構強度檢核 warnings

CLI 自動跑 `structure_check()` 印出每份 warnings、預期：
- **理想**：6 份全部 `✓ 結構完整`
- **可接受**：CV_Chinyu_Lin 單頁可能 `⚠ ### 僅 1 個`（合理、單份工作）
- **要 prompt 迭代**：任何份出現 `❌ 缺主標題` / `⚠ 結構強度可能不足` / `⚠ Vision Hallucination 風險`

### 4. 平均耗時 / cost 估算

CLI 末尾印：
```
平均耗時 XX.Xs（min ... / max ...）
估算 cost ≈ $0.5 - $1（6 份 vision call、模型依 LLM_VISION_MODEL）
```

⚠ baron OrcStack 用 **Pro 預覽**、cost 偏高；可考慮 7e-3 backfill 前切到 Flash 試試。

### 5. 看到問題的處理流程

- **prompt 不夠強**（主標題格式錯 / 公司沒被識別 / 多語亂跳）→ 改 `prompt/doc/resume_vision.txt` 再跑、迭代 2-3 輪
- **Vision 失準到 prompt 救不回**（如 Pro 預覽對特定 layout 處理差）→ 評估切 Flash / Q5 拆語言版本
- **prompt 滿意 + 6 份結構強度全通過** → commit 7e-1 → 進 7e-2 pipeline 整合

---

## 已知限制 / 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| Vision prompt 邊界 case 失準 | 🟡 中 | structure_check 自動偵測；迭代 2-3 輪 |
| 多語履歷穩定性 | 🟡 中 | prompt 強化 1（雙語以英語為主、絕不搖擺）；Q5 拆語言版本為 fallback |
| Pro 預覽 latency / cost | 🟡 中 | timeout 參數已預留；可改 LLM_VISION_MODEL env 切 Flash |
| 長履歷 token 撞限制 | 🟢 低 | Q2 估 Gemini 1M context 充裕 + 10 MB 單頁圖大小自動降 dpi |
| Vision 回非預期格式 | 🟢 低（已防禦） | post-process 三道：strip fence / 移 preamble / validate `^#` |
| Semaphore 永鎖（Vision 例外）| 🟢 低（已防禦） | explicit acquire/try/finally |
| `chat_with_images()` 破壞既有 vision 調用 | 🟢 低 | 新 method、`chat_with_image()` 零改動、4 個既有 caller 已 grep 確認 |
| 與 SlidesProcessor 模板偏離 | 🟢 低 | 高對齊度（見「對齊度」表）|

---

## 7e-2 後續工作備忘（下一輪）

依 design §3：

```python
# pipeline_core.py
# L19
from processor.resume_processor import ResumeProcessor

# L529-540（_stage_pdf_to_md）
if doc_type == 'slides':
    parser = SlidesProcessor()
elif doc_type == 'resume':
    parser = ResumeProcessor()
else:
    parser = self.pdf_processor
markdown_path = parser.parse(str(pdf_path), str(paper_dir))
if doc_type not in ('slides', 'resume'):
    self.md_cleaner.clean(markdown_path)


# processor/doc_analyzer.py — _fix_heading_levels 短路
if doc_type == 'resume':
    return

# processor/doc_analyzer.py — _analyze_document_structure 短路
# 寫最小 _doc_structure.json
```

加 `tools/check_doc_type_registry.py` 新 marker `PIPELINE_PARSER`（偵測 slides + resume 走獨立 parser）。

---

## 回退方式

未 commit、直接：
```bash
git checkout llm/client.py
rm processor/resume_processor.py \
   prompt/doc/resume_vision.txt \
   tests/test_resume_processor.py \
   tools/test_resume_vision.py
rm -rf .claude-logs/_phase_4_7e_outputs
```

---

## 狀態

**本地改檔完成、未 commit、未 push**——等 baron 跑 `tools/test_resume_vision.py` 看：
- structure_check warnings（理想 6 份全 `✓ 結構完整`）
- 各份 .md 輸出品質
- 平均耗時 + cost 估算
再決定：
1. 直接 commit 7e-1
2. 改 prompt 迭代後 commit
3. 切 Flash model 後 commit
