# Phase 4.7e Commit 7e-1 v2 — 執行報告（ResumeProcessor 重寫、忠實轉錄哲學）

> 基準：7e-1 (`ffb3000`) + 7e-2 (`fdc2838`) 已 revert（`ce91665` / `32563b5`）；目前 HEAD = `ce91665`
> 完成：本地改檔完成，**尚未 commit、未 push**
> 等 baron 跑 `tools/test_resume_vision.py` 看 6 份輸出品質後再決定 commit

---

## Commit Hash

**尚未 commit**——v2 預期需 prompt 迭代 1-2 輪（vs 舊 7e-1 的 2-3 輪、因 v2 邏輯更簡單且加了明確黑名單規則）。

| # | Hash | Subject |
|---|---|---|
| 7e-1 v2 | _（pending）_ | feat(resume): ResumeProcessor 重寫、忠實轉錄 + 主標題黑名單對齊手冊 v2 |

---

## diff stat（uncommitted）

```
 llm/client.py                      |  46 +++++  (chat_with_images，與舊 7e-1 完全相同)
 processor/resume_processor.py      | 222 +++++ (新檔、v2 validate 加黑名單檢查)
 prompt/doc/resume_vision.txt       |  86 ++++  (新檔、忠實轉錄哲學、完全重寫)
 tests/test_resume_processor.py     | 224 +++++ (新檔、14 個測試、+3 黑名單測試)
 tools/test_resume_vision.py        | 162 ++++  (新檔、structure_check v2 鬆綁 + 黑名單)
 5 files changed, +740
```

---

## 與舊 7e-1 (ffb3000、已 revert) 對照表

### ✅ 完全保留（架構穩定、邏輯正確）

| 元件 | 舊 7e-1 設計 | v2 是否保留 |
|---|---|---|
| `llm/client.py::chat_with_images` | explicit acquire/try/finally semaphore、timeout 參數、retry decorator | ✅ 100% 相同 |
| `ResumeProcessor` class 骨架 | PDFParser ABC 繼承、`__init__(llm=None)`、`parse() → process()` | ✅ |
| `_render_pages()` | PyMuPDF Matrix(2.5) + > 10MB fallback Matrix(1.5) + 寫 `page_NN.jpg` | ✅ |
| `_analyze_resume()` | 整份單次 Vision call（不分頁） | ✅ |
| Post-process 三道防線 | strip code fence / 移 14 種中英 preamble / validate `^#` | ✅ |
| 整份單次 call 設計 | 1M context 充裕、不分批 | ✅ |
| 失敗模式 | raise `PDFParseError` | ✅ |

### ❌ 完全重寫（核心精神反轉）

| 元件 | 舊 7e-1 內容 | v2 內容 | 變更理由 |
|---|---|---|---|
| **`prompt/doc/resume_vision.txt`** | 「重組主標題 `{職稱} Resume - {人名}` + `## Candidate Summary` 整合 Edu/Skills/Honors prose + 跨履歷彙整 `## Technical Skills` + 雙語以英語為主 + 強制 Working Experience」 | **「忠實轉錄」+ 主標題用人名 + 補抽 plain text ### 為唯一加工 + 保留原語言 + 邊界 case 含手冊黑名單對照表」** | baron 觀察：「專案目的是翻譯保留排版、不是摘要」；舊 7e-1 違反此哲學 |
| `_validate_vision_output()` | 強制 `## Working Experience`（warn）+ 驗 `^#` | **移除 `## Working Experience` 強制**（履歷各種變體都合法）+ **新加主標題黑名單檢查**（手冊 §3.1 / §4.5）：完全等於 'resume'/'cv'/'curriculum vitae'/'履歷'/'個人簡歷'/'履歷表' → raise；含 'CTO Resume - X' suspicious pattern → warn | 履歷可能用中文 section 名 / freelance / 學生履歷各種變體；主標題黑名單對齊既有設計手冊保證 md_restore 短路機制可接手 |
| `tools/test_resume_vision.py::structure_check()` | 強制 `## Candidate Summary` / `## Working Experience` / `## Technical Skills` 3 區段、table 容忍 2 | **移除 3 個區段強制**、table 容忍放寬到 5（履歷常用 table 列學歷）、**新加主標題黑名單檢查**、回傳 (h1, h2, h3) 統計 | 同上 |
| `tests/test_resume_processor.py` | 11 個（含 `test_validate_no_working_experience_warns`） | **14 個**：移除 `test_validate_no_working_experience_warns`、新加 3 個黑名單測試（`test_validate_resume_title_blacklist_exact_raises` / `test_validate_resume_title_recomposed_warns` / `test_validate_resume_title_real_name_passes`） | v2 邏輯反轉 |

---

## 與既有設計手冊 v2 對接點

| 手冊條款 | v2 實作 |
|---|---|
| §3.1 TITLE_BLACKLIST_EXACT 含 `{resume, cv, curriculum vitae, 履歷, 個人簡歷, 履歷表}` | `RESUME_TITLE_BLACKLIST` frozenset 1:1 對應；prompt 「主標題規則」段明列禁用詞表格 + validate raise；CLI structure_check 警告 |
| §4.5 candidate_name 黑名單（與 §3.1 同集合） | 同上、prompt 提及「下游 md_restore stage 會 log warning 並 fallback」 |
| §1 raw first-# = 候選人姓名 🟢（最可信來源） | prompt 「主標題規則」段明確要求第一行 `# {人名}`、人名格式保留原 PDF；6 份樣本範例對照表（DeHunt → `# Tzung-Yuan Lee (李宗原)` 等） |
| §4.1 #1: resume + 有 candidate_name → md_restore 短路用 CN | ResumeProcessor 輸出第一行 # 為純人名，md_restore stage 可正確接手做 final title |
| §4.1 #2: resume + raw 是姓名 + 沒在黑名單 → 用 raw | 同上、validate 確保 raw 不含黑名單詞 |

---

## prompt 完整內容（自包含、不只引用）

見 `prompt/doc/resume_vision.txt`，86 行。骨架：

```
你是處理「履歷 / CV」的 AI 助手...

# 核心原則（嚴格遵守）
1. 忠實轉錄（不改寫 / 不合併 / 不重組）
2. 保留原語言（中 / 英 / 雙語並列）
3. 唯一加工：補抽 plain text 公司 / 學位為 ###

# 主標題規則（對齊手冊 §3.1 + §4.5）
- 第一行 # {人名}（中 / 英 / 中英並列）
- 絕對禁止：通用詞 / 重組格式 / 職稱+人名 主標題
- 6 份樣本範例對照表（DeHunt / 黃忠偉 / Priyal_Shah / YuLun_Wu / 江元杰）

# 輸出格式（保留原 PDF section 名稱、不統一翻譯）
# 邊界 case（公司是 plain text / 自傳重複 / table / freelance / 雙語 / 浮水印 / 學生）
# 輸出限制（無 preamble / 無 code fence / 無末尾客套）
```

---

## 主標題黑名單實作細節

```python
# processor/resume_processor.py
RESUME_TITLE_BLACKLIST = frozenset({
    'resume', 'cv', 'curriculum vitae',
    '履歷', '個人簡歷', '履歷表',
})

RESUME_TITLE_SUSPICIOUS_PATTERNS = (
    ' resume -', ' resume:', ' cv -', ' cv:',
    '履歷 -', '履歷:', 'curriculum vitae',
)

def _validate_vision_output(self, text, paper_name):
    # 1. 驗 ^#
    # 2. 完全等於黑名單詞 → raise PDFParseError
    # 3. 含 suspicious pattern → log warning（不 raise）
```

行為對照：

| Vision 輸出主標題 | 行為 |
|---|---|
| `# Tzung-Yuan Lee (李宗原)` | ✅ 通過 |
| `# 黃忠偉` | ✅ 通過 |
| `# Resume` | ❌ raise PDFParseError "黑名單通用詞" |
| `# CV` | ❌ raise |
| `# 履歷` | ❌ raise |
| `# CTO Resume - Tzung-Yuan Lee` | ⚠ log warning "重組格式"（不 raise） |
| `# 行銷部經理 履歷 - 黃忠偉` | ⚠ log warning（不 raise） |

---

## 不可動清單（已遵守）

- [x] `pipeline_core.py`：未動（7e-2 才動）
- [x] `processor/doc_analyzer.py`：未動（baron Q6 決定不短路）
- [x] `processor/slides_processor.py`：未動
- [x] `processor/pdf_parser.py`（ABC）：未動
- [x] `processor/md_cleaner.py`：未動
- [x] `processor/metadata_extractor.py`：未動（4.7c 已有 `prompt/processor/metadata_resume.txt`）
- [x] 既有 `chat_with_image()`（單張）：未動
- [x] `settings.py`：未動
- [x] `tools/check_doc_type_registry.py`：未動（7e-2 才更新）
- [x] `prompt/doc/heading_fix_resume.txt`（7b 既有）：未動（v2 反而更需要、academic LLM 雙保險）
- [x] `prompt/processor/metadata_resume.txt`（4.7c step 3 既有）：未動
- [x] DB / 前端 / web_server：未動
- [x] commit / push：未動

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
# 14 passed in 5.70s

venv/bin/pytest tests/ -q
# 143 passed, 3 skipped（129 baseline post-revert + 14 新增、零回歸）
```

### 14 個單元測試（vs 舊 7e-1 11 個）

| # | 測試 | vs 舊 7e-1 |
|---|---|---|
| 1 | `test_parse_creates_md_file` | 保留 |
| 2 | `test_parse_creates_page_images` | 保留 |
| 3 | `test_render_dpi_correct` | 保留 |
| 4 | `test_vision_call_passes_images_and_model` | 保留 |
| 5 | `test_strip_code_fence_markdown` | 保留 |
| 6 | `test_strip_code_fence_plain` | 保留 |
| 7 | `test_remove_preamble_en` | 保留 |
| 8 | `test_remove_preamble_zh` | 保留 |
| 9 | `test_validate_no_heading_raises` | 保留 |
| 10 | `test_failure_raises_pdfparseerror` | 保留 |
| 11 | `test_large_image_lowers_dpi` | 保留 |
| ~~舊~~ | ~~`test_validate_no_working_experience_warns`~~ | **移除（v2 鬆綁）** |
| 12 | **`test_validate_resume_title_blacklist_exact_raises`** | **新增**：8 種黑名單詞（含 casefold）都應 raise |
| 13 | **`test_validate_resume_title_recomposed_warns`** | **新增**：4 種重組 pattern 都應 warn 但不 raise |
| 14 | **`test_validate_resume_title_real_name_passes`** | **新增**：6 種合法人名格式都通過、無 warning |

---

## 下一步驗證（給 baron）

### 1. 跑 CLI 對 6 份樣本

⚠ **會打 LLM API（gemini-3.1-pro-preview）、估 $0.5-1**：

```bash
# 確認樣本已解壓
ls /tmp/phase_4_7e_samples/resume_samples/

# 跑驗證
venv/bin/python tools/test_resume_vision.py
```

輸出位置：`.claude-logs/_phase_4_7e_outputs/{paper_name}/{paper_name}.md`

### 2. 重點檢查項（v2 是否真做到「忠實轉錄」+ 主標題用人名）

| 履歷 | ✅ v2 期望 | ❌ 舊 7e-1 走偏的 |
|---|---|---|
| **DeHunt** | `# Tzung-Yuan Lee (李宗原)` + 中文 / 英文混合 section 原樣 + FOCALTECH / NOVATEK 補成 ### | `# CTO Resume - Tzung-Yuan Lee`、Candidate Summary 把 Edu/Skills 摘要 prose |
| **黃忠偉** | `# 黃忠偉` + 中文 section 名（個人資料 / 學歷 / 工作經驗 / 自傳）原樣 + 6 家公司 ### | `# 影音事業處行銷部經理 Resume - 黃忠偉` |
| **Priyal_Shah** | `# Priyal Shah (李思雅)` + SERVICES OFFERED 原樣（不強塞 Working Experience）+ 英中雙語並列保留 | `# Chinese Language Trainer Resume - Priyal Shah` |
| **YuLun_Wu** | `# 吳焴倫` + Education / Work Experience table **保留 markdown table 不拆成 ###** | `# 資深研發工程師 Resume - 吳焴倫`、學歷 table 被拆 |
| **江元杰** | `# 江元杰 (Steven Chiang)` + 補抽 2 家公司（河洛 / 大昌瑞台）為 ### | `# 機電整合研發副理 Resume - 江元杰` |
| **CV_Chinyu_Lin** | `# Chin-Yu Lin 林晉羽` + 結構漂亮 case 不被過度加工 | 過度加工為 Candidate Summary |

### 3. structure_check 自動 warnings

CLI 自動跑 v2 `structure_check()`、預期：
- **理想**：6 份全部「✓ 無 warnings」
- **可接受**：CV_Chinyu_Lin 單頁可能 `⚠ ### 僅 X 個`（合理）
- **要 prompt 迭代**：
  - 任何份出現 `❌ 主標題是黑名單通用詞` → prompt 對人名抽取規則需強化
  - 任何份出現 `⚠ 主標題含重組 pattern` → prompt 「絕對禁止重組」規則需強化
  - 任何份 `❌ 缺主標題` → vision 失準、加 few-shot 

### 4. 看到問題的處理流程

- **prompt 強度不夠**（如 Vision 仍重組 `# CTO Resume - X`）→ 改 prompt 加更激進否定範例 → 再跑 → 對齊
- **6 份 structure_check 全 ✓** + 人工目視中文 section / table / 補 ### 正確 → commit 7e-1 v2 → 進 7e-2 pipeline 整合

---

## 已知限制 / 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| Vision 仍可能輸出「Resume - X」格式 | 🟡 中 | validate raise（嚴格）+ suspicious pattern warn + prompt 含 6 樣本範例對照表 |
| Vision prompt 邊界 case 失準 | 🟡 中 | structure_check 自動偵測、迭代 1-2 輪 |
| 補抽 plain text 公司判定不準 | 🟡 中 | 7e-3 OrcStack 重新上傳 DeHunt + 江元杰 實測；可後續加 few-shot |
| 多語履歷穩定性 | 🟢 低（v2 已修） | prompt 明寫「保留原語言、不統一」 |
| Pro 預覽 latency / cost | 🟡 中 | timeout 參數預留；可改 LLM_VISION_MODEL env 切 Flash |
| 與 SlidesProcessor 模板偏離 | 🟢 低 | 高對齊度 |
| `chat_with_images()` 破壞既有調用 | 🟢 低 | 新 method、`chat_with_image()` 零改動 |
| Semaphore 永鎖 | 🟢 低（已防禦） | explicit acquire/try/finally |

---

## 7e-2 後續工作備忘

依 design plan v2 §6 + baron Q6 / Q7 決策：

```python
# pipeline_core.py
from processor.resume_processor import ResumeProcessor

# _stage_pdf_to_md
if doc_type == 'slides':
    parser = SlidesProcessor()
elif doc_type == 'resume':
    parser = ResumeProcessor()
elif doc_type in KNOWN_DOC_TYPES:
    parser = self.pdf_processor
else:
    self.logger.warning(f"未知 doc_type='{doc_type}'、fallback MinerU、known: ...")
    parser = self.pdf_processor

# md_cleaner 跳過（baron Q7）
if doc_type not in ('slides', 'resume'):
    self.md_cleaner.clean(markdown_path)

# processor/doc_analyzer.py — baron Q6 決定不短路
# → 讓 academic heading_fix LLM 再修 # 數量當雙保險
# 因此 doc_analyzer.py 不動！
```

加 `tools/check_doc_type_registry.py` 新 marker `PIPELINE_PARSER` + `KNOWN_DOC_TYPES`。
加 `tests/test_pipeline_resume_routing.py` mock 測試（routing + md_cleaner skip）。

---

## 下游 md_restore 對接驗證計畫（給 7e-3）

`processor/md_restore_processor.py::_resolve_title()` 走 v2 §4.1 三軸融合：

1. ResumeProcessor 輸出 `# Tzung-Yuan Lee (李宗原)` 進 `data['title']`
2. metadata `candidate_name` 走既有 4.7c step 3 抽取
3. md_restore `_resolve_title()` 用 §4.1 #1 路徑：
   - `doc_type == 'resume'` + `candidate_name` 存在 → 短路用 CN
   - 否則 `_resolve_title` 走 §4.1 #2：raw 是姓名 + 沒在黑名單 → 用 raw
4. final markdown title 應為人名（不是「Resume」/「CV」/ 重組格式）

7e-3 驗證項目：
- `output/1/{paper}/{paper}.md` 第一行 `# {人名}`（v2 ResumeProcessor 輸出）
- `output/1/{paper}/final_{paper}_en.md` 第一行 `# {人名}`
- `output/1/{paper}/final_{paper}_zh.md` 第一行 `# {人名}`（中譯後仍為人名、不被翻成「履歷」）
- log 看 `[md_restore] 三軸融合 title: {conf_log}` 顯示走 §4.1 #1 或 #2 路徑

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

**本地改檔完成、未 commit、未 push**——等 baron：
1. 跑 `tools/test_resume_vision.py`（cost ~$0.5-1）
2. 看 `.claude-logs/_phase_4_7e_outputs/` 內 6 份 .md
3. 確認 v2 真做到「忠實轉錄」+ 主標題用人名

確認後 commit 7e-1 v2 → 進 7e-2 pipeline 整合（baron Q6: doc_analyzer 不短路）。
