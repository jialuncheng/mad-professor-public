import logging
import json
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from config import LLMClient

logger = logging.getLogger(__name__)

SLIDE_PROMPT = """這是一張投影片的截圖。請分析並提取以下內容：

1. 標題：投影片的主要標題（如果有）
2. 內容：投影片上的所有文字內容，保持原有的條列結構
3. 圖表描述：如果有圖表、圖片或示意圖，用一到兩句話描述其內容和學術意義

請以 JSON 格式回傳，格式如下：
{
  "title": "投影片標題（沒有則為空字串）",
  "content": "投影片的文字內容（保持原格式）",
  "figure_description": "圖表描述（沒有圖表則為空字串）"
}

只輸出 JSON，不要任何解釋。"""


class SlidesProcessor:
    """簡報 PDF 處理器：使用 PyMuPDF 渲染每頁，再用 Vision 辨識內容"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = LLMClient()

    def process(self, pdf_path: str, output_dir: str) -> Path:
        """
        將簡報 PDF 每頁渲染成圖片，用 Vision 辨識內容，
        輸出 Markdown 文件。
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paper_name = pdf_path.stem
        markdown_path = output_dir / f"{paper_name}.md"

        self.logger.info(f"開始 Vision 解析簡報: {pdf_path}")

        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        self.logger.info(f"共 {total_pages} 頁")

        lines = [f"# {paper_name.replace('_', ' ')}", ""]
        title = ""

        # 建立 images 目錄
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        for page_num in range(total_pages):
            page = doc[page_num]
            self.logger.info(f"  [{page_num + 1}/{total_pages}] 處理第 {page_num + 1} 頁")

            # 渲染頁面為圖片
            mat = fitz.Matrix(2.0, 2.0)  # 2x 解析度
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("jpeg")

            # 儲存頁面圖片
            img_filename = f"slide_{page_num + 1:02d}.jpg"
            img_path = images_dir / img_filename
            img_path.write_bytes(img_data)

            # Vision 辨識
            result = self._analyze_slide(img_data, page_num + 1)

            if not result:
                continue

            slide_title = result.get("title", "").strip()
            content = result.get("content", "").strip()
            figure_desc = result.get("figure_description", "").strip()

            # 第一頁的標題作為文件標題
            if page_num == 0 and slide_title:
                title = slide_title
                lines[0] = f"# {title}"

            # 組合成 Markdown（第一頁只用文件標題，不重複加 section 標題）
            if page_num == 0:
                pass  # 已用作文件標題
            elif slide_title:
                lines.append(f"## {slide_title}")
            else:
                lines.append(f"## 第 {page_num + 1} 頁")

            # 插入頁面圖片
            lines.append(f"![slide_{page_num + 1:02d}](images/{img_filename})")

            if content:
                lines.append(content)

            if figure_desc:
                lines.append(f"\n*圖表：{figure_desc}*")

            lines.append("")

        doc.close()

        markdown_content = "\n".join(lines)
        markdown_path.write_text(markdown_content, encoding="utf-8")
        self.logger.info(f"Vision 解析完成: {markdown_path}")

        return markdown_path

    def _analyze_slide(self, img_data: bytes, page_num: int) -> Optional[dict]:
        """用 Vision 分析單頁投影片"""
        import re
        try:
            result_text = self.llm.chat_with_image(
                messages=[{"role": "user", "content": SLIDE_PROMPT}],
                image_data=img_data,
                mime_type="image/jpeg"
            )
            result_text = re.sub(r'```json|```', '', result_text).strip()
            return json.loads(result_text)
        except Exception as e:
            self.logger.warning(f"  第 {page_num} 頁 Vision 辨識失敗: {str(e)}")
            return None

    @staticmethod
    def is_slides_pdf(pdf_path: str) -> bool:
        """
        快速判斷 PDF 是否為簡報格式。
        根據頁面寬高比判斷（簡報通常是橫向的 16:9 或 4:3）
        """
        try:
            doc = fitz.open(str(pdf_path))
            if len(doc) == 0:
                return False
            # 取前幾頁判斷
            landscape_count = 0
            check_pages = min(3, len(doc))
            for i in range(check_pages):
                page = doc[i]
                rect = page.rect
                if rect.width > rect.height:  # 橫向
                    landscape_count += 1
            doc.close()
            return landscape_count >= check_pages  # 全部都是橫向
        except Exception:
            return False
