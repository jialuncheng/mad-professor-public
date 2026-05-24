# Phase 4.7e — Resume 獨立 Pipeline 評估與資料收集 Plan

> **本輪只寫分析報告 + 列 baron 需提供清單。零業務檔案改動。**
> 基準：RAG-7a + RAG-7b 本地改檔後狀態（皆未 commit）

---

## TL;DR

7a + 7b 修法解了「MinerU 已抽成 heading 的浮水印」+「LLM 把 H2 看成 H3」兩問題、但救不回**完全沒被 MinerU 認成 heading 的 plain-text 公司名**（FOCALTECH-SYSTEM / NOVATEK 仍 plain text）。Resume 走獨立 pipeline 是可行的、且 slides 已有完整「獨立 pipeline」模板可複用。

本報告：

1. 盤點 slides 既有獨立 pipeline 架構（pipeline_core 4 處 + SlidesProcessor 完整類）
2. 提出 3 個 resume 獨立 pipeline 設計候選（A / B / C，附工時 + 風險）
3. **列出 baron 需從 OrcStack 測試機提供的資料清單（A-F），附具體 copy-paste 命令**——下一步阻塞點
4. 影響評估（per 方向、列出要動的檔 + registry）
5. 7 個 open questions 待 baron 決策

**結論**：先不寫程式碼、先拿資料樣本做設計；建議方向 B（中等工時、低風險）為起手式。

---

## 1. slides 既有獨立 pipeline 盤點

### 1.1 整體流程

slides 的「獨立 pipeline」**不是完全繞過所有 stage**、而是只在 `_stage_pdf_to_md` 換 parser、後續 stage 走特殊路徑：

| Stage | academic | slides | 備註 |
|---|---|---|---|
| `pdf2md` | MinerU + md_cleaner | **SlidesProcessor**（PyMuPDF + Vision） | slides 跳過 md_cleaner |
| `analyze`（doc_analyzer） | LLM heading_fix + structure | 同 LLM，但 prompt = slides 專用 + `flat_structure=True` | 仍跑、prompt 不同 |
| `md2json`（md_processor） | 走 hierarchy | `SLIDES_DOC_TYPES` 不啟動 authors collecting | 仍跑、特殊分支 |
| `tiling` / `translate` / `image_caption` | 跑 | 跑 | 行為一致 |
| `md_restore` | 跑 | 跑 | 行為一致 |
| `extra_info` | `process()` 全跑 | **`generate_document_summary()`**（簡化 summary）| 跳過 question/公式抽取 |
| `rag` | 標準 chunk | `_SHORT_DOC_TYPES` 合併同 section | 同 news/web/resume |

### 1.2 關鍵 code 位置

```
pipeline_core.py:19          from processor.slides_processor import SlidesProcessor
pipeline_core.py:529-532     if doc_type == 'slides': parser = SlidesProcessor()
pipeline_core.py:539-540     if doc_type != 'slides': self.md_cleaner.clean(markdown_path)
pipeline_core.py:640-643     if doc_type in ('news','web','slides','resume'): generate_document_summary()
processor/doc_analyzer.py:125-127  if doc_type == 'slides': structure['flat_structure'] = True
processor/md_processor.py:263       SLIDES_DOC_TYPES = ('slides',)  # 不啟動 authors collecting
processor/rag_processor.py:15      _SHORT_DOC_TYPES = frozenset({'resume','slides','news','web'})
```

### 1.3 SlidesProcessor 架構（processor/slides_processor.py，212 行）

**繼承**：`PDFParser`（`processor/pdf_parser.py` 抽象 ABC，contract: `parse(pdf_path, output_dir) -> Path`）

**輸入**：本機 PDF 路徑 + 輸出 dir（與 PDFProcessor / MinerU 一致）

**核心解析**：
1. PyMuPDF (`fitz.open`) 開檔、迴圈每頁 (`for page_num in range(total_pages)`)
2. 判斷是否 2-up 直向（A4 含兩張投影片）→ 上下裁切
3. 每張裁切後 → `page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), clip=clip)` 轉 JPEG
4. **Vision LLM**（`SLIDE_PROMPT` 要求 JSON 三欄：title / markdown_content / figure_description）
5. 聚合為 markdown（`## {slide_title}` + image 連結 + content + figure_desc）

**輸出**：標準 `output_dir/{paper_name}.md`（與 MinerU 對齊、後續 stage 不知差別）

**側產物**：`output_dir/images/slide_{n}.jpg`

**輔助靜態方法**：`is_slides_pdf(pdf_path)` — 抓前 3 頁判橫向

### 1.4 設計哲學總結（給 resume 套用）

- **獨立 pipeline ≠ 全繞過**、只取代 parser、後續 stage 套特殊路徑
- 用 `PDFParser` ABC 解耦、caller 端 (`pipeline_core`) 只認介面
- 輸出格式必須與 MinerU 對齊（`output_dir/{stem}.md`）、否則下游壞
- 特殊規則用 `if doc_type ==` 散在各 stage（已有 7 個 registry points 統一管理）
- prompt 仍存 `prompt/doc/heading_fix_*.txt` / `structure_*.txt`、走 registry 路由

---

## 2. resume 獨立 pipeline 設計候選

### 方向 A：完全模仿 slides — 新 ResumeProcessor + 繞過 doc_analyzer

**思路**：把履歷 PDF 當「結構強烈但 layout 變化大的圖文混合」、學 slides 用 Vision 整份重看。

**改動**：
- 新檔 `processor/resume_processor.py`（繼承 `PDFParser`）
- 內部用 PyMuPDF 渲染每頁 → Vision LLM 抽結構化 markdown（公司 / 學位 / 技能皆已 `###`）
- 或 PyMuPDF 純文字抽 + LLM 「結構化重組」一次到位
- `pipeline_core.py:529` 加 `elif doc_type == 'resume': parser = ResumeProcessor()`
- `pipeline_core.py:539` 改 `if doc_type not in ('slides', 'resume'):` 跳過 md_cleaner
- `doc_analyzer` 為 resume 加 `flat_structure=True`（或更激進：完全跳過 heading_fix）

**工時**：5-10 小時
**風險**：高（要設計 Vision prompt + 處理多頁 PDF 合併 + 不同 layout 適配）
**優勢**：根治、不再依賴 MinerU OCR 的 heading 抽取
**劣勢**：影響 7 個 registry point 中 ~3 個、回退成本高

### 方向 B：MinerU 出 .md 後、resume 專用 heading inferrer（補抽）

**思路**：MinerU 抽錯（plain text 公司名）就在後續補一層「履歷感知」LLM、補打 `###`。

**改動**：
- 新檔 `processor/resume_heading_inferrer.py`（簡單類、不繼承 PDFParser）
- `pipeline_core.py:_stage_pdf_to_md` 在 `md_cleaner.clean()` 之後、`_stage_analyze` 之前插一層：
  ```python
  if doc_type == 'resume':
      self.resume_heading_inferrer.infer(markdown_path)
  ```
- 內部：讀 .md → LLM 看純文字找「公司名 / 學位名 / 專案名」pattern → 補 `###` 行 → 寫回 .md
- doc_analyzer 的 7b 新 prompt 繼續跑（heading_fix 確認 # 數量）

**工時**：2-4 小時
**風險**：中（LLM 補 heading 可能誤判正文行為 heading、需 schema 約束）
**優勢**：增量、不動既有 stage 流、與 7a+7b 完全相容
**劣勢**：仍依賴 MinerU 不漏掉公司名「文字本身」（只是漏 heading 標記）；若 MinerU 連文字也漏（如圖片化履歷）救不回

### 方向 C：MinerU 出 .md 後、整份 markdown LLM 重組

**思路**：跳過 heading_fix（單行 # 數量決策）、用「整份 markdown → 結構化 markdown」一次 LLM call 重組。

**改動**：
- 新檔 `processor/resume_md_restructure.py`
- 取代 `_stage_analyze` 的 resume 分支：LLM 看完整 markdown + 履歷 schema → 吐結構化 markdown（每家公司 / 學位皆已 `###`、頂層分區 `##`）
- 直接生成 `_doc_structure.json` 給 md_processor
- 跳過 heading_fix LLM call（7b 的 prompt 不再用）

**工時**：3-6 小時
**風險**：中（一次 LLM call 處理整份、context 長 + 需設計穩定 schema）
**優勢**：可同時補抽 heading + 修 # 數量、把 7a+7b 兩步合成一步
**劣勢**：7b 改的 prompt 浪費；大履歷可能撞 context window；prompt 工程量大

### 方向比較總表

| 方向 | 工時 | 風險 | 動 stage 數 | 與 7a/7b 相容 | 救不回的場景 |
|---|---|---|---|---|---|
| A（ResumeProcessor 取代 MinerU） | 5-10h | 高 | 3+ | 中（md_cleaner 不再對 resume 跑） | 純圖檔履歷 vision 也失敗 |
| B（heading inferrer 補抽） | 2-4h | 中 | 1（加 stage 中間步） | **高** | MinerU 沒抽到文字本身 |
| C（整份 markdown 重組） | 3-6h | 中 | 2（取代 heading_fix） | 低（取代 7b） | MinerU 沒抽到文字本身 |

---

## 3. 需要 baron 提供的資料清單 ⭐（**下一步阻塞點**）

> claude-lab worktree 內沒有 `output/` 也沒有 PDF 原檔（皆在 OrcStack 測試機）。
> 以下命令 baron 可在 **OrcStack 端** 跑、或把對應檔案 scp / 拖到 claude-lab worktree 內供下一輪分析。
> 建議在 worktree 內建 `.claude-logs/_phase_4_7e_samples/` 暫存（gitignored）。

### A. 履歷樣本 PDF（理想 3-5 份不同類型）

**為什麼要多份**：避免設計只 fit DeHunt 履歷；不同 layout / 模板需要不同處理策略。

**copy-paste 命令（OrcStack）**：
```bash
# 列出測試機上既有的履歷 PDF（output/ 內已上傳過的）
find output -name "*.pdf" -path "*resume*" 2>/dev/null
find output -name "*.pdf" -path "*履歷*" 2>/dev/null
# 或從 Paper.doc_type='resume' 查 DB：
sqlite3 data/mad-professor.db "SELECT id, title, original_filename FROM papers WHERE doc_type='resume';"

# 找到後傳給 claude-lab worktree：
# scp orcstack:output/1/DeHunt_.../原始檔.pdf .claude-logs/_phase_4_7e_samples/resume_1_dehunt.pdf
```

**理想樣本組合**：
- DeHunt 履歷本人（baron 自己的、已知 bug case）
- 1 份研究員 / 教授 CV（不同章節結構、含 Publications）
- 1 份開發者履歷（含 Projects / GitHub link）
- 1 份設計師 portfolio 履歷（圖文混合密度高）
- 1 份 LinkedIn export PDF（若有、layout 標準化）

### B. 對應的 MinerU 中間檔（每份 PDF 都要）

**為什麼**：看 MinerU 在哪「斷掉」（沒抽 heading / 抽錯位置 / 漏內容）—— 設計 inferrer 的關鍵輸入。

**copy-paste 命令（OrcStack，per paper）**：
```bash
PAPER_DIR="output/1/DeHunt_CTO_Tzung-Yuan_Lee"   # 替換成實際 paper 目錄
ls -la "$PAPER_DIR/"
cat "$PAPER_DIR"/*.md | head -200                # MinerU 原始 markdown（清理前）
cat "$PAPER_DIR"/*_doc_structure.json            # doc_analyzer sidecar
cat "$PAPER_DIR"/*_structured.json | head -200   # md_processor 輸出
cat "$PAPER_DIR"/_rag/*_tree.json 2>/dev/null | head -200  # RAG chunk tree
```

**打包傳輸**：
```bash
cd output/1
tar -czf /tmp/resume_samples.tgz \
    DeHunt_*/{*.md,*_doc_structure.json,*_structured.json} \
    其他履歷目錄/...
# scp 到 claude-lab worktree
```

### C. slides 既有樣本（1 份就夠、作為對比與設計模板）

**為什麼**：理解 SlidesProcessor 輸出的 markdown 風格、作為 ResumeProcessor / inferrer 的格式對齊基準。

**copy-paste 命令（OrcStack）**：
```bash
sqlite3 data/mad-professor.db "SELECT id, title FROM papers WHERE doc_type='slides' LIMIT 1;"
# 找到一個 slides paper id，例如 N
PAPER_DIR=$(ls -d output/*/[Ss]lides* 2>/dev/null | head -1 || ls -d output/1/* | grep -i slide | head -1)
ls "$PAPER_DIR/"
cat "$PAPER_DIR"/*.md | head -100
```

### D. 最近一次 pipeline log（履歷 + slides 各一份）

**為什麼**：看每個 stage 實際跑了什麼 / 耗時 / 中間值（特別是 doc_analyzer 給 LLM 的 heading 行清單長啥樣、LLM 回了啥）。

**copy-paste 命令（OrcStack）**：
```bash
# 找最近處理 resume 的 log
grep -n "doc_type=resume\|履歷\|resume" logs/pipeline.log | tail -20
# 抓相關區段：先找出 paper_id 前綴，然後抽該 paper_id 的完整 log
grep "^\[paper_id=N\]" logs/pipeline.log > /tmp/resume_N_pipeline.log
# 或近 1000 行
tail -1000 logs/pipeline.log > /tmp/recent_pipeline.log
```

### E. 履歷 schema 期望（baron 設計觀，文字回答即可）⭐

**請 baron 直接在下一輪訊息回答**（不用查資料、是設計決策）：

1. **理想的履歷 chunks 是什麼粒度？**
   - 每家公司一個 chunk？
   - 每段工作職責 / 子標題一個 chunk？
   - 「Working Experience」整段一個 chunk、公司用 H1 splitter 分？
2. **Education / Skills / Honors / Publications 這些頂層分區、要不要也獨立成 chunk？**（vs 合進「履歷整體 summary」chunk）
3. **跨文件 RAG 查詢時、想用什麼當搜尋 key？**
   - 公司名（「在 NOVATEK 做過什麼」）
   - 學位 / 學校（「MIT 畢業的 candidate」）
   - 技能（「會 Verilog 的人」）
   - 三者皆要？
4. **履歷主標題的定義**：用人名（"Tzung-Yuan Lee"）還是「CTO Resume - Tzung-Yuan Lee」這種職稱組合？
5. **doc_type=resume 是否要做 vision fallback**？（純圖檔履歷、MinerU 連文字都抽不到時）

### F. PDF 解析工具盤點（次要，方便設計時參考）

**copy-paste 命令（OrcStack 或本地皆可）**：
```bash
cat requirements.txt | grep -iE "pdf|mineru|fitz"
cat pyproject.toml 2>/dev/null | grep -iE "pdf|mineru"
venv/bin/python -c "import fitz; print(fitz.__doc__[:200]); print('PyMuPDF', fitz.__version__)"
venv/bin/python -c "import pdfplumber" 2>&1   # 看有沒裝
venv/bin/python -c "import pdfminer" 2>&1
```

**已知**：`PyMuPDF==1.27.2.3`（slides 用）、MinerU API（remote service）

---

## 4. 影響評估（per 方向）

> 7 個 doc_type registry points（依 `tools/check_doc_type_registry.py`）：
> 1. `web_server.py` valid_types
> 2. `processor/doc_analyzer.py` HEADING_FIX_PROMPTS
> 3. `processor/doc_analyzer.py` STRUCTURE_PROMPTS
> 4. `processor/translate_processor.py` STYLE_HINTS（推測）
> 5. `pipeline_core.py` `extra_info_skip` tuple
> 6. `static/upload.js` 前端 dropdown（推測）
> 7. `docs/HOW_TO_ADD_DOC_TYPE.md`

### 方向 A 影響

- **新增**：`processor/resume_processor.py`、可能 `prompt/doc/resume_vision.txt`
- **改 pipeline_core.py**：`_stage_pdf_to_md` 加 elif（L529-540）、`_stage_analyze` 加 resume 跳過或特殊分支
- **改 doc_analyzer.py**：可能加 `if doc_type == 'resume': flat_structure=True`
- **改 md_processor.py**：可能把 resume 加進 `SLIDES_DOC_TYPES`（不啟動 authors collecting）
- **7a 浮水印偵測**：對 resume **不再執行**（因 ResumeProcessor 取代 MinerU、md_cleaner skip）
- **7b 履歷 heading_fix prompt**：**廢棄**（doc_analyzer 跳過 resume 或 flat_structure）
- **registry**：6 個 prompt 路徑改 / 對 resume 失效；`tools/check_doc_type_registry.py` 須更新（容忍 resume 在 HEADING_FIX_PROMPTS / STRUCTURE_PROMPTS 為 null）
- **DB / vector store / RAG retriever**：不動（仍走 `_SHORT_DOC_TYPES`）
- **前端**：不動（仍 resume option）

### 方向 B 影響

- **新增**：`processor/resume_heading_inferrer.py`、`prompt/doc/heading_inferrer_resume.txt`
- **改 pipeline_core.py**：`_stage_pdf_to_md` 在 md_cleaner 後加 `if doc_type == 'resume': inferrer.infer(...)`（2-3 行）
- **7a 浮水印偵測**：**繼續執行**（resume 仍走 MinerU）
- **7b 履歷 heading_fix prompt**：**繼續使用**（heading_fix 仍跑、補抽的 `###` 由 7b prompt 確認）
- **registry**：不動（doc_type 已存在、prompt 路徑不變）
- **DB / vector store / RAG retriever**：不動
- **前端**：不動
- **tools/check_doc_type_registry.py**：可選加第 8 個 marker `RESUME_HEADING_INFERRER`

### 方向 C 影響

- **新增**：`processor/resume_md_restructure.py`、`prompt/doc/resume_restructure.txt`
- **改 pipeline_core.py**：`_stage_analyze` 內 `if doc_type == 'resume': self.resume_md_restructure.process()`、跳 heading_fix + structure call
- **7a 浮水印偵測**：**繼續執行**
- **7b 履歷 heading_fix prompt**：**廢棄**（取代為 restructure）
- **改 doc_analyzer.py**：加 resume 短路
- **registry**：`HEADING_FIX_PROMPTS['resume']` 不再被用、但檔案保留（避免 registry check 紅）
- **DB / vector store / RAG retriever**：不動
- **前端**：不動

---

## 5. Open Questions（待 baron 決策）

| # | 問題 | 為什麼問 |
|---|---|---|
| Q1 | 走哪個方向（A / B / C）？ | 工時 / 風險 / 救回程度三權衡；建議 B 作為起手式（與 7a/7b 完全相容、可後續升級到 C） |
| Q2 | 既有用 academic prompt 的「學者 CV」會否誤判為 resume 而走獨立 pipeline？ | doc_type 由 user 在 upload 時選定、不自動偵測 → 若 user 選 academic 則不受影響；但要確認 user 教育 |
| Q3 | 既有已上傳的 resume paper（DeHunt 等）backfill 怎麼處理？ | RAG-2 backfill CLI 是否要擴成「resume 全部重跑」？或要 user 手動重上傳？ |
| Q4 | 是否同步處理 LinkedIn export / 純文字履歷？（.pdf 以外格式） | 目前 pipeline 只吃 .pdf；若 baron 要支援 .docx / .json export 是另一條 commit |
| Q5 | Skills / Software Tools / Honors 這些非工作經歷的區段、獨立 pipeline 怎麼切 chunk？ | 需 §3.E 回答指引 |
| Q6 | PDF 解析工具選擇：純 MinerU / 改用 PyMuPDF 純文字 / 改用其他？ | 影響方向 A vs B 抉擇；目前 slides 已用 PyMuPDF，方向 A 走同路 |
| Q7 | 工時預算？baron 願意付出 5-10h（方向 A）還是先 2-4h（方向 B）？ | 直接決定方向 |

---

## 6. 下一步（給 baron）

1. **本輪結束**：閱讀本報告、決定要先看哪些方向細節
2. **下一輪 baron 提供**：§3 的 A-F 資料（特別 A + B + E 最關鍵）
3. **下一輪 claude**：依 baron 提供的樣本 + schema 回答，產出方向選定 + 細部 design doc
4. **再下一輪**：實作（按選定方向、依 RAG-7 拆 commit 模式分 4.7e-1 / -2 / -3）

---

## 7. 不可動清單（已遵守）

- [x] `processor/*`（slides / md_cleaner / doc_analyzer 等）：未動
- [x] `pipeline_core.py`：未動
- [x] `prompt/doc/*`：未動
- [x] `settings.py` / `web_server.py` / DB / 前端：未動
- [x] `tools/check_doc_type_registry.py`：未動
- [x] commit / push：未動
- [x] 新增業務檔（resume_processor / inferrer / restructure）：未動
- [x] 本報告為唯一新增檔
