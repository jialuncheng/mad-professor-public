# Phase 4.7e — Resume 獨立 Pipeline 設計報告

> 基準：Plan 報告（2026-05-21_Phase_4_7e_Resume_Independent_Pipeline_plan.md）+ baron D1-D5 決策
> 方向選定：**A（含 Vision），模仿 SlidesProcessor 模板**
> 樣本：6 份履歷 + 1 份 slides，已解到 `/tmp/phase_4_7e_samples/`
> **本輪只寫設計報告、零業務檔改動**

---

## TL;DR

**結論**：依方向 A 新建 `processor/resume_processor.py`、用 PyMuPDF + Vision LLM **整份重看**、輸出結構化 markdown，繞過 MinerU + heading_fix。設計模板 100% 抄 SlidesProcessor（已驗證可行）；技術困難主要在「**Vision 多頁 PDF 單次 call 的 SDK 介面**」與「**Prompt 對多語 / 邊界 case 的穩定性**」。建議 4 commits 拆分（7e-1 ~ 7e-4），總工時 5-8h。

### 6 份履歷 MinerU 抽 heading 實測（剛在 claude-lab 端 grep 確認）

| 履歷 | 頁數 | 公司 ### 數 | 預期公司數 | 結論 |
|---|---|---|---|---|
| CV_Chinyu_Lin_2308 | 1 | 3 | 3 | ✅ 漂亮 |
| 黃忠偉 | 5 | 6（+「自傳」內又 4 重複）| 6 | ✅ 漂亮（但有重複區塊） |
| DeHunt_CTO_Tzung-Yuan_Lee | 11 | 3（VIEWTRIX / TARGETEK / ITRI） | 5（缺 FOCALTECH / NOVATEK） | ⚠ 中度失敗 |
| YuLun_Wu_CV | 3 | 0（Work Experience H2、底下無 ###） | 1+ | ❌ 完全失敗 |
| 江元杰 | 3 | 0（工作經驗 ##、底下無 ###） | 2+ | ❌ 完全失敗 |
| Priyal_Shah_CV | 10 | 0（EXPERIENCE 底下無 ###、結構奇特、中英文 2 份） | N/A | ❌ 結構奇特 |

**統計：2/6 抽對**——驗證方向 A 必要性。

### 樣本意外發現（影響設計）

1. **黃忠偉**有「工 作經歷」#H2 區塊 + 後段「自 傳」也有 4 家公司 ###（與前段重複）→ Vision 必須能識別「自傳」是補述、避免重複建 chunk
2. **Priyal_Shah** 是雙語履歷：英文版 + 完整中文翻譯版（同一份 PDF 內並列）→ Vision 必須能識別這是同一人的雙語版本、不要當兩個候選人
3. **CV_Chinyu_Lin** 1 頁就完整 → Vision 多頁支援不是硬需求
4. **DeHunt 11 頁、黃忠偉 5 頁** → 多頁 vision call 需評估 token / context 上限
5. 中文/中英混雜履歷 4/6 → prompt 必須母語感地處理

---

## 1. ResumeProcessor 介面與架構

### 1.1 類別骨架（依 SlidesProcessor `processor/slides_processor.py:54-165` 模板）

```python
# processor/resume_processor.py
import logging
import json
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
import settings
from llm.client import LLMClient
from utils.text_utils import strip_json_fence
from processor.pdf_parser import PDFParser, PDFParseError  # noqa: F401

logger = logging.getLogger(__name__)

RESUME_VISION_PROMPT = """..."""   # 見 §2


class ResumeProcessor(PDFParser):
    """履歷 PDF 處理器：PyMuPDF 渲染 + Vision LLM 整份重看，
    輸出標準化 markdown（公司 ###、Summary ##、主標題 #）。
    繞過 MinerU + md_cleaner + heading_fix。"""

    def __init__(self, llm=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = llm if llm is not None else LLMClient.get_instance()

    def parse(self, pdf_path: str, output_dir: str) -> Path:
        """Implements PDFParser.parse()."""
        return self.process(pdf_path, output_dir)

    def process(self, pdf_path: str, output_dir: str) -> Path:
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        paper_name = pdf_path.stem
        markdown_path = output_dir / f"{paper_name}.md"

        # 1. PyMuPDF render 每頁 → JPEG bytes
        doc = fitz.open(str(pdf_path))
        page_images: list[bytes] = []
        for i in range(len(doc)):
            mat = fitz.Matrix(2.5, 2.5)   # 履歷文字密、用 2.5 dpi
            pix = doc[i].get_pixmap(matrix=mat)
            jpg = pix.tobytes("jpeg")
            page_images.append(jpg)
            (images_dir / f"page_{i+1:02d}.jpg").write_bytes(jpg)
        doc.close()

        # 2. Vision LLM 整份重看（單次 call 含所有頁面）
        markdown = self._analyze_resume(page_images, paper_name)

        # 3. 寫檔
        markdown_path.write_text(markdown, encoding='utf-8')
        self.logger.info(f"Vision 解析履歷完成: {markdown_path}")
        return markdown_path

    def _analyze_resume(self, page_images: list[bytes], paper_name: str) -> str:
        """單次 LLM call 傳所有頁面圖片 + RESUME_VISION_PROMPT。
        重點：需 LLMClient.chat_with_images()（複數）—— 目前
        chat_with_image() 只支援單張、需 7e-1 補擴 method（見 §3.4）。"""
        try:
            result = self.llm.chat_with_images(
                messages=[{"role": "user", "content": RESUME_VISION_PROMPT}],
                images=[(img, "image/jpeg") for img in page_images],
                model=settings.LLM_VISION_MODEL
            )
            return result.strip()
        except Exception as e:
            self.logger.error(f"Vision 履歷解析失敗 {paper_name}: {e}")
            raise PDFParseError(f"Vision resume parse failed: {e}") from e
```

### 1.2 關鍵設計決策（評估後選定）

| 決策點 | 選項 | 採用 | 理由 |
|---|---|---|---|
| **call 粒度** | 單次（所有頁面）vs 每頁一 call vs 分批合併 | **單次** | 履歷結構連貫、需 LLM 看全局判主標題 / 最近職稱；slides 是每頁獨立才用 per-page。實測 11 頁（DeHunt）為最大、Gemini 2.0 Flash 1M context 充分 |
| **輸出格式** | structured output（JSON schema）vs prompt 約束 markdown | **prompt 約束 markdown** | SlidesProcessor 用 JSON 然後 caller 拼 markdown；本案直出 markdown 更簡單、減一層 JSON parse 失敗風險；對齊既有 MinerU 輸出格式 |
| **render dpi** | 1.5 / 2.0 / 2.5 / 3.0 | **2.5** | slides 用 2.0 適合圖文混合；履歷字密、再高一階確保 OCR-via-vision 看清楚日期 / 公司名小字 |
| **圖片走哪管道傳 Vision** | `chat_with_image()`（單張）vs **新加 `chat_with_images()`（複數）** | **新加 method** | 既有 `llm/client.py:192` 只支援單張圖；Gemini SDK `types.Part.from_bytes` 可塞多張、需擴介面（見 §3.4 工程動作）|
| **side product** | 不存 vs 存 page_NN.jpg | **存** | 對齊 SlidesProcessor 行為（`images/slide_NN.jpg`）、有助 debug / 未來 image_caption stage 不破 |
| **失敗策略** | best-effort 寫部分 vs raise PDFParseError | **raise** | 履歷整份結構強耦合、抓不到就讓 pipeline 知道 fail；不像 slides 可以「丟掉一頁繼續」 |

### 1.3 與 SlidesProcessor 對齊度

| 面向 | SlidesProcessor | ResumeProcessor | 差異原因 |
|---|---|---|---|
| 繼承 | `PDFParser` | `PDFParser` | 同 |
| 入口 | `parse(pdf, dir) -> Path` | 同 | contract 強制 |
| 渲染 | PyMuPDF Matrix(2.0) | PyMuPDF Matrix(2.5) | 履歷字密 |
| LLM | per-page `chat_with_image` | one-shot `chat_with_images` | 結構連貫 |
| 輸出 | `output_dir/{stem}.md` | 同 | 下游一致 |
| images dir | `slide_NN.jpg` | `page_NN.jpg` | 對齊 |
| 失敗模式 | warn + skip 該頁 | raise | 履歷強耦合 |

---

## 2. Vision LLM Prompt 草案（最核心）⭐

### 2.1 完整 prompt（建議檔名 `prompt/doc/resume_vision.txt`）

```
你是處理「履歷 / Curriculum Vitae」的 AI 助手。請看完這份履歷的所有頁面、
抽取結構化 markdown，方便後續 RAG 檢索。

# 輸出格式（嚴格遵守）

# {職稱} Resume - {人名}

## Candidate Summary

候選人摘要、整合所有「非工作經歷」資訊寫成 2-5 段 prose（不另開 ## 區段）：
- Education / Degrees / 學歷
- Languages / 語言能力
- Honors / Awards / 獲獎
- Certifications / 證照
- Personal Info（國籍 / 居住地等與職業相關者）
- 個人特質描述 / 自傳

## Working Experience

### {公司全名} - {職稱} ({期間 YYYY/MM - YYYY/MM 或 YYYY/MM - PRESENT})

職責、成就、用到的技術 / 工具 / 程式語言、產品 / 客戶 / 規模……
（保留原 PDF 所有實質內容、保留條列 / 段落結構）

### {公司2 全名} - {職稱2} ({期間2})

...

### {公司3 全名} - {職稱3} ({期間3})

...

## Technical Skills

從整份履歷彙整、列出技術 / 工具 / 程式語言 / 領域知識：
- skill 1
- skill 2
- ...

# 主標題規則（# 那行）

- 格式：「{職稱} Resume - {人名}」
- 「職稱」用候選人**最新 / 最高階**的職位（通常是 Working Experience 第一筆）
- 範例：「CTO Resume - Tzung-Yuan Lee」「Senior PM CV - Priyal Shah」
- 若履歷完全無職稱（純學生 CV）→ 用「Candidate Resume - {人名}」
- 人名保持原 PDF 寫法（中文用中文、英文用英文；中英並列保留並列）

# Working Experience 規則

- 每家公司獨立一個 ###（H3），**絕對平行**、不互為子節
- 公司全名（若有中英並列、保留：「中文名 (English name)」）
- 職稱寫在公司名後、用 " - " 分隔
- 期間用括號包起：(YYYY/MM - YYYY/MM) 或 (YYYY/MM - PRESENT)
- 時序排列：**最新在上**（與業界 CV 慣例一致）
- 即使 PDF 某些公司名是 plain text 沒被特別標出（如純粗體 / 純大寫）、
  仍要識別並補成 ###
- 履歷後段若有「自傳 / About Me」內又重複列出公司（如黃忠偉履歷案例）：
  **不要重複建 ###**、將自傳補述合併進對應公司的職責描述內

# Candidate Summary 規則（依 D2 合併原則）

- 整合所有「非工作經歷」資訊、不獨立成 ## 區段
- 用 prose 段落（不要硬轉成條列）
- 「Education / Skills / Honors / Languages」這些資訊融進 prose
- 不複製 Working Experience 內容（避免重複）

# Technical Skills 規則（依 D3 跨文件 RAG 用）

- 純條列、易掃描
- 從履歷各處彙整（不限於 Skills section）：
  - Working Experience 內提到的技術
  - Skills / 擅長工具 等 section 列舉的技能
  - 程式語言 / 框架 / 工具 / 領域知識
- 與 Working Experience 內容**可重複**（這裡是 skills index）
- 條列順序：硬技能優先（程式語言 / 工具）、軟技能在後

# 邊界 case

- **純圖檔履歷**（PDF 無可選取文字、純圖）：仍要從 vision 看出結構
- **無典型 Working Experience section**（如 Priyal_Shah_CV 列 SERVICES OFFERED + 自由業描述）：
  把所有經歷描述合進 Working Experience、用「Freelance - {專業領域}」當公司名
- **同 PDF 含雙語版本**（如 Priyal_Shah_CV 英 + 中並列）：
  視為同一份履歷、用主要語言版本當主體；另一語言關鍵詞合進 Summary 不重複建區段
- **推薦信 / 求職信內容**（出現在履歷尾頁）：不抽進輸出
- **公司 logo 字 / 浮水印**（如 DeHunt 履歷的 XDeHunt / HDeHunt）：不抽進輸出
- **學生履歷**（無工作經歷）：Working Experience section 仍保留、底下放「### 學術專案 / Internship」等近似條目；主標題用「Candidate Resume - {人名}」

# 輸出限制

- 只輸出 markdown、不要其他文字 / 解釋
- 從 # 主標題那行開始
- 不要用 ```markdown ... ``` 之類 code fence 包裹
- 不要在末尾加總結 / 註釋
```

### 2.2 prompt 設計依據對照

| Prompt 段落 | 對應 baron 決策 |
|---|---|
| 主標題格式 `{職稱} Resume - {人名}` | D4 |
| Candidate Summary 整合 Edu / Skills / Honors | D2 |
| 每家公司 ### | D1 |
| Technical Skills 獨立區段 | D3（跨文件 RAG 用 skills 當 key） |
| 純圖檔履歷邊界 case | D5（vision-first） |

### 2.3 prompt 已知潛在弱點（需 7e-1 實測迭代）

| 弱點 | 樣本 case | 建議解法 |
|---|---|---|
| 多語履歷處理 | Priyal_Shah（英中並列）、黃忠偉（中文為主含英文職稱）、江元杰（純中文）| 7e-1 實跑、看 Vision 是否自動處理；若不穩、加 `prompt 偵測主要語言 → 用該語言寫 Summary` |
| 「自傳」重複公司 | 黃忠偉履歷 | prompt 已明說「不要重複建 ###」、仍需實測 |
| 無 Working Experience 結構 | Priyal_Shah、YuLun_Wu | 「Freelance - 領域」fallback 條款；若仍亂、加 few-shot |
| 學生 / 無職稱履歷 | (未在樣本內、Q7) | 「Candidate Resume」fallback |
| LLM 漏頁 | DeHunt 11 頁 | 7e-3 時對所有樣本 diff 原 PDF vs Vision 輸出 |

---

## 3. pipeline_core / doc_analyzer 整合點（具體 diff）

### 3.1 `pipeline_core.py` — 4 處改動（仿 slides）

```python
# Line 19（import）
from processor.slides_processor import SlidesProcessor
+from processor.resume_processor import ResumeProcessor


# Line 526-542（_stage_pdf_to_md）
def _stage_pdf_to_md(self, pdf_path, paper_dir, paper_name, output_paths):
    doc_type = output_paths.get('_confirmed_doc_type', 'academic')

    if doc_type == 'slides':
        self.logger.info(f"{self.paper_info.get('paper_id')} 簡報類型，使用 Vision 解析")
        parser = SlidesProcessor()
+    elif doc_type == 'resume':
+        self.logger.info(f"{self.paper_info.get('paper_id')} 履歷類型，使用 Vision 解析")
+        parser = ResumeProcessor()
    else:
        parser = self.pdf_processor

    markdown_path = parser.parse(str(pdf_path), str(paper_dir))

-    if doc_type != 'slides':
+    if doc_type not in ('slides', 'resume'):
        self.md_cleaner.clean(markdown_path)

    return markdown_path


# Line 640（_stage_extra_info）— 不動，'resume' 已在 tuple 內
if doc_type in ('news', 'web', 'slides', 'resume'):
    return self.extra_info_processor.generate_document_summary(...)
```

### 3.2 `processor/doc_analyzer.py` — 短路 resume（保險：兩個 stage 都短路）

```python
def _fix_heading_levels(self, markdown_path: Path, doc_type: str):
+    # Phase 4.7e：resume 走 ResumeProcessor、已輸出正確 # 結構，跳過 LLM heading fix
+    if doc_type == 'resume':
+        self.logger.info(f"[analyze] {doc_type} 走 ResumeProcessor，跳過 heading fix")
+        return
    # ... 原邏輯（讀 prompt、call LLM、寫回）


def _analyze_document_structure(self, markdown_path: Path, doc_type: str) -> dict:
+    # Phase 4.7e：resume 走 ResumeProcessor、不需 LLM structure；
+    # 仍寫最小 sidecar 避免下游讀 _doc_structure.json 失敗
+    if doc_type == 'resume':
+        sidecar = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
+        minimal = {
+            "structure": [],
+            "document_type": "resume",
+            "flat_structure": True,
+        }
+        sidecar.write_text(json.dumps(minimal, ensure_ascii=False, indent=2), encoding='utf-8')
+        self.logger.info(f"[analyze] {doc_type} 寫最小 sidecar: {sidecar}")
+        return minimal
    # ... 原邏輯
```

> 為何不直接在 `analyze()` 入口 early return？保險：兩個 sub-stage 各自短路、未來若 `analyze()` 加新 sub-step（如 metadata 補強）也不會誤跑 resume 路徑。

### 3.3 `tools/check_doc_type_registry.py` 更新

新增第 8 個 marker：`PIPELINE_PARSER`（pipeline_core 內 `if doc_type == ` 選 parser 的處）—— 偵測 `slides` + `resume` 都有獨立 parser、若新增 doc_type 又走獨立 parser，registry check 會提醒。

可選：另加 marker `DOC_ANALYZER_SHORTCUT`，列出哪些 doc_type 在 doc_analyzer 短路。

### 3.4 `llm/client.py` 擴 `chat_with_images()`（複數）— 7e-1 必須

既有 `chat_with_image()` 簽名（L192）只接單張：
```python
def chat_with_image(self, messages, image_data: bytes, mime_type="image/jpeg", model=None) -> str
```

新增姐妹 method 接 list：
```python
@retry_call(retries=3, base=2.0)
def chat_with_images(self, messages, images: list[tuple[bytes, str]],
                     model: str = None) -> str:
    """Vision 多張圖片版（Phase 4.7e：ResumeProcessor 用）。
    images: [(image_bytes, mime_type), ...] 順序保留。"""
    with LLMClient._api_semaphore:
        model = model or CHAT_MODEL
        system_instruction, contents = _convert_messages(messages)
        image_parts = [types.Part.from_bytes(data=img, mime_type=mt)
                       for img, mt in images]
        if contents and contents[-1].role == "user":
            contents[-1].parts.extend(image_parts)
        else:
            contents.append(types.Content(role="user", parts=image_parts))
        config = types.GenerateContentConfig(system_instruction=system_instruction)
        response = self.client.models.generate_content(
            model=model, contents=contents, config=config
        )
        return response.text
```

`chat_with_image()` **不改**（保持單張、ImageCaptionProcessor / SlidesProcessor 不破）。

### 3.5 `processor/md_processor.py` — 評估後**不動**

`SLIDES_DOC_TYPES = ('slides',)` 控制「H1 後不收集 authors」。
履歷主標題 `# {職稱} Resume - {人名}` 後直接是 `## Candidate Summary`、不會誤觸 author collecting（因為 H2 觸發 `collecting_authors = False`）。
保險起見 7e-3 實測一份履歷的 `_structured.json`、若 `authors_info` 被亂塞東西、再把 'resume' 加進 `SLIDES_DOC_TYPES`（改名為 `FLAT_DOC_TYPES`）。

---

## 4. 與 7a / 7b 既有 commits 的關係

### 4.1 RAG-7a（md_cleaner 浮水印偵測 `e2ed0e4`）

- **對 resume 不再執行**：pipeline_core L539 改為 `if doc_type not in ('slides', 'resume')`
- **對其他 doc_type 仍有用**：academic / book / news 等 MinerU OCR 仍可能抽出浮水印 heading
- **不刪 commit**、不刪 code、不改 settings 常數
- **tests/test_md_cleaner.py 6 個測試**：仍會跑（不傳 doc_type 參數、直接 `cleaner.clean(path)`）—— 不破

### 4.2 RAG-7b（resume 專用 heading_fix prompt `5c182cf`）

- **功能廢棄**：doc_analyzer 對 resume 短路、HEADING_FIX_PROMPTS['resume'] 不會被讀
- **檔案保留**：`prompt/doc/heading_fix_resume.txt` 不刪（保 registry 完整性、避免 `check_doc_type_registry.py` 報「prompt 不存在」紅）
- **加 deprecation 註解**（7e-4 完成）：
  ```python
  # processor/doc_analyzer.py
  HEADING_FIX_PROMPTS = {
      ...
      'resume':    'prompt/doc/heading_fix_resume.txt',  # Phase 4.7e DEPRECATED: ResumeProcessor 短路、此 prompt 不再使用，保留 registry 完整性
  }
  ```
  prompt 檔首加 `<!-- DEPRECATED Phase 4.7e: 由 ResumeProcessor (Vision) 取代 -->`
- **未來 4.7f / 4.8** 可考慮拔（要同步改 registry check 容忍）

### 4.3 commit 順序兼容性

7a → 7b → 7e 為線性增量；7e 不依賴 7a/7b 的「對 resume 行為」、但**依賴 7b 已新增 `'resume'` 到所有 registry**（不需再加新 doc_type）。

---

## 5. chunk 粒度設計（依 D1+D2+D3）

### 5.1 預期 chunk 結構（rag_processor 走標準路徑）

`_SHORT_DOC_TYPES = frozenset({'resume', 'slides', 'news', 'web'})` 已含 resume —— `rag_processor` 會把同 section 短文合併（既有行為）。

預期輸出（DeHunt 範例）：

| Chunk | 內容 |
|---|---|
| 1 | `# CTO Resume - Tzung-Yuan Lee` + `## Candidate Summary`（含 Education / Languages / Honors / Certifications 整段 prose）|
| 2 | `## Working Experience` + `### VIEWTRIX TECHNOLOGY - Senior Manager, OLED Alg. R&D (2023/06 - 2025/08)` 整段 |
| 3 | `### TARGETEK - {職稱} (期間)` 整段 |
| 4 | `### FOCALTECH-SYSTEM - {職稱} (期間)`（**Vision 補抽出的、MinerU 漏掉**）|
| 5 | `### NOVATEK Microelectronics - {職稱} (期間)`（同上）|
| 6 | `### INDUSTRIAL TECHNOLOGY RESEARCH INSTITUTE (ITRI) - Engineer` 整段 |
| 7 | `## Technical Skills` 整段（純條列）|

### 5.2 D3 跨文件 RAG 設計

- **每個公司 chunk** 描述內含該公司用到的技術（embedding 自然含 skill 語意）
- **獨立 Technical Skills chunk** 含全部彙整（純 skill 列、跨文件 fast match）
- 查詢「會 Verilog 的 candidate」時、retrieve 會打中 Technical Skills chunk（高 score）+ 提到 Verilog 的公司 chunk（中 score）
- 不需 rag_processor 改動（既有 score 排序 + threshold 0.22 已足）

### 5.3 7e-3 驗證項目

對 6 份履歷重跑 pipeline 後、檢查：
1. `_structured.json` sections 數量 = 1（Summary）+ N（公司）+ 1（Skills）
2. `_rag_tree.json` 每 chunk 大小合理（500-1500 字、不爆 8000）
3. 跨文件查詢「Verilog / React / 行銷管理」回對的 candidate

---

## 6. 工時 commit 拆分

| Commit | 標題 | 工時 | 內容 | 風險 |
|---|---|---|---|---|
| **7e-1** | feat(resume): ResumeProcessor + Vision prompt + chat_with_images | 3-4h | 新建 `processor/resume_processor.py`、`prompt/doc/resume_vision.txt`、`llm/client.py` 加 `chat_with_images()`；單元測試（不接 pipeline）；對 6 份樣本各跑一次人工審視 | 中（prompt 迭代） |
| **7e-2** | feat(pipeline): resume 走獨立 pipeline + doc_analyzer 短路 | 1-2h | 改 `pipeline_core.py` 4 處 + `doc_analyzer.py` 2 函式短路；`tools/check_doc_type_registry.py` 加 marker；整合測試（在 OrcStack 端跑 1 份履歷確認） | 低 |
| **7e-3** | test(resume): 6 份履歷端到端驗證 + RAG 跨文件 skills 查詢 | 1-2h | OrcStack 端 backfill 6 份履歷；檢查 `_structured.json` / `_rag_tree.json`；跑跨文件 skills 查詢；diff vs 原 MinerU 輸出 | 中（可能要回頭調 prompt） |
| **7e-4**（可選） | chore(resume): 7a/7b 對 resume 廢棄標記 + docs | 30min | `heading_fix_resume.txt` deprecation header；`doc_analyzer.py` HEADING_FIX_PROMPTS['resume'] 註解；`docs/HOW_TO_ADD_DOC_TYPE.md` 補 ResumeProcessor 描述 | 低 |

**總工時**：5-8h（不含 vision call cost 與 LLM 等待）

---

## 7. Open Questions（待 baron 決策）

| # | 問題 | 推薦答案 / 備註 |
|---|---|---|
| Q1 | Vision call 用哪個 model？slides 既有用什麼？ | slides 用 `settings.LLM_VISION_MODEL`（fallback CHAT_MODEL = gemini-2.0-flash）。推薦 resume **同用 LLM_VISION_MODEL**；若需更高精度可實測 gemini-2.0-pro。可在 7e-1 加 env 切換 |
| Q2 | 長履歷（DeHunt 11 頁）context window 評估 | Gemini 2.0 Flash 1M context；11 頁 @ 2.5 dpi JPEG 每張 ~500KB / ~330K tokens（估）—— 充裕。Priyal 10 頁同理。**結論：不需分批** |
| Q3 | 既有 6 份 resume backfill 用 RAG-2 CLI 還是手動重上傳？ | 推薦 7e-3 時手動重上傳（樣本小、避免 backfill CLI 額外 risk） |
| Q4 | 純圖檔履歷的測試 case 從哪來？ | 6 份樣本都有可選取文字、無純圖案例。建議 baron 7e-3 前準備 1 份（可手動「另存為純圖 PDF」或找掃描履歷） |
| Q5 | 多語履歷 prompt 是否需分語言版本？ | 推薦**單 prompt 處理所有語言**（7e-1 實測黃忠偉 / 江元杰 / Priyal）；若失敗再拆 `resume_vision_zh.txt` / `resume_vision_en.txt` 並依履歷主要語言路由 |
| Q6 | 7e-1 ~ 7e-4 是否同 session 完成？ | 推薦**拆 session**：7e-1 自成一輪（prompt 迭代是迭代過程、需 baron 看人工審視結果回饋）；7e-2/3/4 可同 session 或拆 |
| Q7 | 「無職稱」（學生 / 純研究 CV）主標題 fallback | prompt 已寫「Candidate Resume - {人名}」、若 baron 想要更精細（如「Student Resume - 」/「PhD Candidate CV - 」）需擴 prompt 邏輯 |

---

## 8. 風險評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| Vision call cost / latency（vs MinerU） | 🔴 高 | MinerU pdf2md 通常 30-60s、Vision 1-call 估 20-60s；cost 較高但 6 份樣本一次性 backfill < $1。長期看：履歷上傳頻率低（不像 academic paper），可接受 |
| Vision prompt 多語 / 邊界 case 失準 | 🟡 中 | 7e-1 人工審視 6 份樣本輸出、迭代 prompt 2-3 輪；保留 prompt 版本 v1/v2/v3 在 commit history 內 |
| 多頁長履歷 token 上限 | 🟡 中 | Q2 已估算充裕；若實測撞限制、退回分批策略（每 3-5 頁 1 call、最後合併） |
| `chat_with_images()` 新介面破壞既有調用 | 🟢 低 | 新增 method、不改既有 `chat_with_image()`、互不干擾 |
| 與既有 SlidesProcessor 架構相容 | 🟢 低 | 100% 同模板 |
| 回退 | 🟢 低 | revert 7e-2（pipeline 改動）即回到走 MinerU + 7a/7b 修法 |
| 7a / 7b 既有 commits 兼容 | 🟢 低 | 不刪、加 deprecation 註解 |
| `md_processor` 對 resume markdown 結構不適配 | 🟢 低 | §3.5 評估 H1→H2 已避開 author collecting；7e-3 驗證 |
| Vision 輸出非預期格式（漏 # 主標題、code fence 包裹） | 🟡 中 | prompt 明寫「不要 code fence」「從 # 開頭」；7e-1 加 simple post-process（strip code fence、確保第一行 `^#`） |

---

## 9. 不可動清單（已遵守）

- [x] `processor/*`：未動
- [x] `pipeline_core.py`：未動
- [x] `prompt/doc/*`：未動
- [x] `settings.py` / `llm/client.py`：未動
- [x] `tools/check_doc_type_registry.py` / `docs/HOW_TO_ADD_DOC_TYPE.md`：未動
- [x] commit / push：未動
- [x] 新增業務檔（resume_processor / resume_vision 等）：未動
- [x] 本報告為唯一新增檔（樣本解到 `/tmp/phase_4_7e_samples/` 也只是 read-only 分析、無 worktree 改動）

---

## 10. 下一步

1. baron 過目本 design doc、Q1-Q7 回答
2. 確認後進 **7e-1**：實作 `ResumeProcessor` + `chat_with_images()` + prompt v1、對 `/tmp/phase_4_7e_samples/` 6 份履歷各跑一次、把輸出寫到 `.claude-logs/_phase_4_7e_outputs/`、baron 人工審視
3. 7e-1 驗收 → 7e-2 pipeline 整合 → 7e-3 OrcStack 端到端 → 7e-4 docs
