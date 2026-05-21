"""ResumeProcessor — Phase 4.7e-1：履歷專用獨立 pipeline parser。

繞過 MinerU + md_cleaner + heading_fix；用 PyMuPDF 渲染每頁 + Vision LLM
整份重看，輸出結構化 markdown（主標題 # / Summary ## / 每家公司 ###
平行 / Technical Skills ##）。

模板：processor/slides_processor.py（同 PDFParser ABC、同 Vision-first 哲學）。
"""
import logging
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF

import settings
from llm.client import LLMClient
from processor.pdf_parser import PDFParser, PDFParseError

logger = logging.getLogger(__name__)

# Phase 4.7e-1：履歷 Vision prompt 路徑。檔案內容見
# prompt/doc/resume_vision.txt。
RESUME_VISION_PROMPT_PATH = Path("prompt/doc/resume_vision.txt")

# 渲染 dpi：履歷字密（日期 / 公司名小字），用 2.5 比 slides 的 2.0 更穩。
RENDER_MATRIX = fitz.Matrix(2.5, 2.5)
# Fallback：若 2.5 dpi 渲染後單張 JPEG > 10 MB，降到 1.5 重 render
RENDER_MATRIX_LOW = fitz.Matrix(1.5, 1.5)
MAX_PAGE_JPEG_BYTES = 10 * 1024 * 1024  # 10 MB

# Vision 回傳常見 preamble（即使 prompt 禁止仍可能出現、自動移除）
COMMON_PREAMBLES = (
    "以下是",
    "這是您的",
    "這是該",
    "Here is",
    "Here's",
    "Here are",
    "Below is",
    "Below are",
    "I have parsed",
    "I'll provide",
    "I will provide",
    "Sure",
    "Of course",
)


class ResumeProcessor(PDFParser):
    """履歷 PDF 處理器：PyMuPDF 渲染 + Vision LLM 整份重看。"""

    def __init__(self, llm=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = llm if llm is not None else LLMClient.get_instance()

    def parse(self, pdf_path: str, output_dir: str) -> Path:
        """Implements PDFParser.parse()."""
        return self.process(pdf_path, output_dir)

    def process(self, pdf_path: str, output_dir: str) -> Path:
        """渲染 PDF 每頁為 JPEG、整份送 Vision LLM、寫 markdown。

        Raises:
            FileNotFoundError: pdf_path 不存在
            PDFParseError:     Vision 失敗 / 輸出格式不合法
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        paper_name = pdf_path.stem
        markdown_path = output_dir / f"{paper_name}.md"

        self.logger.info(f"開始 Vision 解析履歷: {pdf_path}")

        page_images = self._render_pages(pdf_path, images_dir)
        self.logger.info(f"共渲染 {len(page_images)} 頁、送 Vision 整份解析")

        raw_markdown = self._analyze_resume(page_images, paper_name)
        cleaned = self._post_process_vision_output(raw_markdown, paper_name)
        self._validate_vision_output(cleaned, paper_name)

        markdown_path.write_text(cleaned, encoding="utf-8")
        self.logger.info(f"Vision 解析履歷完成: {markdown_path} ({len(cleaned)} chars)")
        return markdown_path

    def _render_pages(self, pdf_path: Path, images_dir: Path) -> List[bytes]:
        """PyMuPDF 開檔、render 每頁為 JPEG bytes，同時側產 images/page_NN.jpg。

        每頁 render 後檢查大小，若 > MAX_PAGE_JPEG_BYTES（10 MB）降到
        RENDER_MATRIX_LOW（1.5）重 render，避免 Vision API payload 超時。
        """
        page_images: List[bytes] = []
        try:
            doc = fitz.open(str(pdf_path))
            total = len(doc)
            for i in range(total):
                pix = doc[i].get_pixmap(matrix=RENDER_MATRIX)
                jpg = pix.tobytes("jpeg")
                if len(jpg) > MAX_PAGE_JPEG_BYTES:
                    self.logger.warning(
                        f"[resume] page {i + 1} render 後 "
                        f"{len(jpg) // 1024 // 1024} MB、超過 "
                        f"{MAX_PAGE_JPEG_BYTES // 1024 // 1024} MB、降低 dpi 重 render"
                    )
                    pix = doc[i].get_pixmap(matrix=RENDER_MATRIX_LOW)
                    jpg = pix.tobytes("jpeg")
                page_images.append(jpg)
                (images_dir / f"page_{i + 1:02d}.jpg").write_bytes(jpg)
            doc.close()
        except Exception as e:
            raise PDFParseError(f"PyMuPDF 渲染失敗 {pdf_path}: {e}") from e
        return page_images

    def _analyze_resume(self, page_images: List[bytes], paper_name: str) -> str:
        """單次 Vision call 把所有頁面 + prompt 一起送。"""
        prompt = self._read_prompt()
        try:
            text = self.llm.chat_with_images(
                messages=[{"role": "user", "content": prompt}],
                images=[(img, "image/jpeg") for img in page_images],
                model=settings.LLM_VISION_MODEL,
            )
        except Exception as e:
            self.logger.error(f"Vision 履歷解析失敗 {paper_name}: {e}")
            raise PDFParseError(f"Vision resume parse failed: {e}") from e

        if not text or not text.strip():
            raise PDFParseError(f"Vision 回傳空字串 {paper_name}")
        return text

    def _read_prompt(self) -> str:
        try:
            return RESUME_VISION_PROMPT_PATH.read_text(encoding="utf-8").strip()
        except Exception as e:
            raise PDFParseError(
                f"讀取 resume vision prompt 失敗 {RESUME_VISION_PROMPT_PATH}: {e}"
            ) from e

    def _post_process_vision_output(self, raw: str, paper_name: str = "") -> str:
        """清理 Vision LLM 輸出常見問題。

        順序：
        1. strip 兩端空白
        2. 拔 code fence（```markdown ... ``` 或 ``` ... ```）
        3. 移除 LLM preamble（即使 prompt 禁止仍可能出現）
        """
        text = raw.strip()

        # 1. Strip code fence
        if text.startswith("```"):
            lines = text.splitlines()
            # 拔第一行 ``` 或 ```markdown
            lines = lines[1:]
            # 拔最後一行 ```（若有）
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # 2. 移除 LLM preamble — 找第一個 # 開頭的行作為真正起點
        first_nonblank_line = next(
            (ln for ln in text.splitlines() if ln.strip()), ""
        )
        if not first_nonblank_line.startswith("#"):
            # 嘗試比對 preamble 後續就是 # 開頭內容的 case
            for prefix in COMMON_PREAMBLES:
                if first_nonblank_line.lstrip().startswith(prefix):
                    # 找第一個 # 開頭的行
                    all_lines = text.splitlines()
                    for idx, line in enumerate(all_lines):
                        if line.lstrip().startswith("#"):
                            removed = "\n".join(all_lines[:idx]).strip()
                            self.logger.warning(
                                f"[resume] {paper_name} Vision 回傳含 preamble、"
                                f"自動移除 {len(removed)} chars: {removed[:80]!r}"
                            )
                            text = "\n".join(all_lines[idx:]).strip()
                            break
                    break

        return text

    def _validate_vision_output(self, text: str, paper_name: str = "") -> None:
        """驗證 Vision 輸出結構完整性：缺主標題 raise、缺 Working Experience warn。"""
        first_nonblank = next(
            (ln for ln in text.splitlines() if ln.strip()), ""
        )
        if not first_nonblank.startswith("#"):
            raise PDFParseError(
                f"Vision 輸出第一行不是 # 開頭 {paper_name}: "
                f"first_line={first_nonblank[:80]!r}"
            )

        # warn 無 Working Experience（不 raise；學生 CV / freelance 可能無）
        if "## Working Experience" not in text:
            self.logger.warning(
                f"[resume] {paper_name} 輸出缺 '## Working Experience' 區段、"
                f"請人工審視（可能是學生 / 自由業 / Vision 失準）"
            )
