import logging
import json
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
import settings
from config import LLMClient
from utils.text_utils import strip_json_fence

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

如果該頁完全空白、只有頁碼、或只有純裝飾元素，請回傳三個欄位都是空字串：
{"title": "", "content": "", "figure_description": ""}

只輸出 JSON，不要任何解釋。"""

EMPTY_CHECK_PROMPT = """這是一張投影片的截圖。請判斷這張投影片是否為空白或幾乎沒有實質內容（例如：完全空白、只有頁碼、只有裝飾性圖案、只有背景）。

請只回答 "empty" 或 "has_content"，不要其他文字。"""


class SlidesProcessor:
    """簡報 PDF 處理器：使用 PyMuPDF 渲染每頁，再用 Vision 辨識內容"""

    def __init__(self, llm=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = llm if llm is not None else LLMClient.get_instance()

    def process(self, pdf_path: str, output_dir: str) -> Path:
        """
        將簡報 PDF 每頁渲染成圖片，用 Vision 辨識內容，
        輸出 Markdown 文件。

        裁切策略：固定上下各半（B 方案）
        適用於 2-up 印刷（A4 每頁放兩張投影片）。
        若遇到非標準格式導致裁切錯誤，改用 A 方案：
        請 Vision 判斷邊界後用 PyMuPDF 精確裁切。
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

        lines = [""]
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        slide_counter = 0  # 實際輸出的投影片編號

        for page_num in range(total_pages):
            page = doc[page_num]
            rect = page.rect
            mat = fitz.Matrix(2.0, 2.0)

            # 判斷是否需要裁切（A4 直向且寬高比 < 0.8）
            needs_split = rect.width < rect.height * 0.8

            if needs_split:
                # 上下各半裁切
                mid = rect.height / 2
                clips = [
                    fitz.Rect(0, 0, rect.width, mid),          # 上半
                    fitz.Rect(0, mid, rect.width, rect.height)  # 下半
                ]
            else:
                # 橫向頁面，整頁當一張
                clips = [rect]

            for clip_idx, clip in enumerate(clips):
                pix = page.get_pixmap(matrix=mat, clip=clip)
                img_data = pix.tobytes("jpeg")

                # 直接辨識，從結果判斷空白
                result = self._analyze_slide(img_data, slide_counter + 1)
                if not result:
                    self.logger.warning(
                        f"  頁 {page_num + 1} 子圖 {clip_idx + 1}: JSON 解析失敗，跳過"
                    )
                    continue

                slide_title = result.get("title", "").strip()
                content = result.get("content", "").strip()
                figure_desc = result.get("figure_description", "").strip()

                if not slide_title and not content and not figure_desc:
                    self.logger.info(f"slide {slide_counter + 1}: 內容皆空，跳過")
                    continue

                slide_counter += 1
                img_filename = f"slide_{slide_counter:02d}.jpg"
                img_path = images_dir / img_filename
                img_path.write_bytes(img_data)

                self.logger.info(
                    f"slide {slide_counter}: 標題={slide_title[:20]}, 內容字數={len(content)}"
                )

                if slide_title:
                    lines.append(f"## {slide_title}")
                else:
                    lines.append(f"## 第 {slide_counter} 頁")

                lines.append(f"![slide_{slide_counter:02d}](images/{img_filename})")

                if content:
                    lines.append(content)

                if figure_desc:
                    lines.append(f"\n*圖表：{figure_desc}*")

                lines.append("")

        doc.close()

        self.logger.info(f"共輸出 {slide_counter} 張投影片")
        markdown_path.write_text("\n".join(lines), encoding="utf-8")
        self.logger.info(f"Vision 解析完成: {markdown_path}")

        return markdown_path

    def _is_empty(self, img_data: bytes, page_num: int, clip_idx: int) -> bool:
        """用 Vision 判斷投影片是否為空白"""
        try:
            result = self.llm.chat_with_image(
                messages=[{"role": "user", "content": EMPTY_CHECK_PROMPT}],
                image_data=img_data,
                mime_type="image/jpeg"
            )
            return result.strip().lower() == "empty"
        except Exception as e:
            self.logger.warning(f"  空白判斷失敗 (頁{page_num}-{clip_idx}): {str(e)}")
            return False  # 判斷失敗時保守處理，不跳過

    def _analyze_slide(self, img_data: bytes, slide_num: int) -> Optional[dict]:
        """用 Vision 分析單頁投影片"""
        try:
            result_text = self.llm.chat_with_image(
                messages=[{"role": "user", "content": SLIDE_PROMPT}],
                image_data=img_data,
                mime_type="image/jpeg",
                model=settings.LLM_VISION_MODEL
            )
            result_text = strip_json_fence(result_text)
            return json.loads(result_text)
        except Exception as e:
            self.logger.warning(f"  第 {slide_num} 張 Vision 辨識失敗: {str(e)}")
            return None

    @staticmethod
    def is_slides_pdf(pdf_path: str) -> bool:
        """快速判斷 PDF 是否為簡報格式（橫向頁面）"""
        try:
            doc = fitz.open(str(pdf_path))
            if len(doc) == 0:
                return False
            landscape_count = 0
            check_pages = min(3, len(doc))
            for i in range(check_pages):
                rect = doc[i].rect
                if rect.width > rect.height:
                    landscape_count += 1
            doc.close()
            return landscape_count >= check_pages
        except Exception:
            return False
