import os
import requests
import logging
import zipfile
import io
import subprocess
import shutil
from pathlib import Path
from config import LLMClient
from processor.slides_processor import SlidesProcessor
from utils.heading_utils import fix_heading_levels
from utils.text_utils import CONTROL_CHAR_PATTERN

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF處理器：透過本機 MinerU API 將 PDF 轉換為 Markdown 格式"""






    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.MINERU_API_URL = os.getenv("MINERU_API_URL", "http://localhost:8000/file_parse")
        self.MINERU_HOST = os.getenv("MINERU_HOST", "")
        self.MINERU_OUTPUT_DIR = os.getenv("MINERU_OUTPUT_DIR", "")
        self.logger.debug("初始化 PDF 處理器（MinerU API 模式）")
        self.llm = LLMClient()

    def process(self, pdf_path: str, output_dir: str) -> Path:
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 判斷是否為簡報，若是則用 Vision 解析
            if SlidesProcessor.is_slides_pdf(str(pdf_path)):
                self.logger.info(f"偵測為簡報格式，使用 Vision 解析: {pdf_path}")
                slides_proc = SlidesProcessor()
                return slides_proc.process(str(pdf_path), str(output_dir))

            self.logger.info(f"呼叫 MinerU API 處理 PDF: {pdf_path}")

            with open(pdf_path, "rb") as f:
                response = requests.post(
                    self.MINERU_API_URL,
                    files={"files": (pdf_path.name, f, "application/pdf")},
                    data={
                        "return_md": "true",
                        "response_format_zip": "true",
                        "backend": "pipeline"
                    },
                    timeout=300
                )

            if response.status_code != 200:
                raise RuntimeError(f"MinerU API 回傳錯誤: {response.status_code} {response.text}")

            paper_name = pdf_path.stem

            # 解壓 ZIP 到暫存目錄
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(output_dir / "_tmp")

            # 把 Markdown 移到正確位置
            tmp_md = output_dir / "_tmp" / paper_name / "auto" / f"{paper_name}.md"
            markdown_path = output_dir / f"{paper_name}.md"
            if tmp_md.exists():
                tmp_md.rename(markdown_path)

            # 用 LLM 修正標題層級
            self._fix_heading_levels(markdown_path)

            # 清除控制字元（MinerU 解析特殊字元時可能產生）
            md_text = markdown_path.read_text(encoding='utf-8')
            md_text = CONTROL_CHAR_PATTERN.sub('', md_text)
            markdown_path.write_text(md_text, encoding='utf-8')

            # 從 mineru-lab 複製圖片
            self._copy_images(paper_name, output_dir)

            # 清理暫存目錄
            shutil.rmtree(output_dir / "_tmp", ignore_errors=True)

            if not markdown_path.exists():
                raise RuntimeError(f"找不到 Markdown 檔案: {markdown_path}")

            self.logger.info(f"Markdown 文件已保存到: {markdown_path}")
            return markdown_path

        except requests.exceptions.ConnectionError:
            raise RuntimeError("無法連接 MinerU API，請確認 MinerU 服務是否已啟動")
        except Exception as e:
            self.logger.error(f"PDF 處理失敗: {str(e)}", exc_info=True)
            raise

    def _fix_heading_levels(self, markdown_path: Path):
        """用 LLM 修正 Markdown 標題層級"""
        try:
            content = markdown_path.read_text(encoding="utf-8")

            # 只取出標題行給 LLM 判斷
            lines = content.split("\n")
            heading_lines = []
            for i, line in enumerate(lines):
                if line.startswith("#"):
                    heading_lines.append(f"行{i}: {line}")

            if not heading_lines:
                return
    
            headings_text = "\n".join(heading_lines)

            prompt = f"""以下是一篇學術論文 Markdown 的所有標題行（格式：行號: 標題內容）：

{headings_text}

請根據學術論文的結構邏輯（章節編號格式、標題語意、層級關係），判斷每個標題應該使用幾個 # 符號。

規則：
- 論文標題用 #（一個）
- 頂層章節（Abstract、Introduction、Methods、Results、Discussion、References 等，或羅馬數字 I. II. III.）用 ##（兩個）
- 子章節（阿拉伯數字 1. 2. 3. 或明顯從屬於上一層的標題）用 ###（三個）
- 子子章節用 ####（四個）

請只輸出 JSON 格式，key 為行號（數字），value 為應使用的 # 數量（1-4 的整數）：
{{"行號": #數量, ...}}

只輸出 JSON，不要任何解釋。"""

            new_text = fix_heading_levels(content, self.llm, prompt)

            markdown_path.write_text(new_text, encoding="utf-8")
            self.logger.info(f"標題層級修正完成: {markdown_path}")

        except Exception as e:
            self.logger.warning(f"標題層級修正時出錯（不影響後續流程）: {str(e)}")

    def _copy_images(self, paper_name: str, output_dir: Path):
        """從 mineru-lab 複製最新的圖片目錄"""
        try:
            result = subprocess.run(
                ["ssh", self.MINERU_HOST,
                 f"ls -t {self.MINERU_OUTPUT_DIR} | head -1"],
                capture_output=True, text=True, timeout=30
            )
            latest_task = result.stdout.strip()
            if not latest_task:
                self.logger.warning("找不到 mineru-lab 的輸出目錄")
                return

            src = f"{self.MINERU_HOST}:{self.MINERU_OUTPUT_DIR}/{latest_task}/{paper_name}/auto/images/"
            dst = str(output_dir / "images")

            scp_result = subprocess.run(
                ["scp", "-r", src, dst],
                capture_output=True, text=True, timeout=60
            )
            if scp_result.returncode == 0:
                self.logger.info(f"圖片複製成功: {dst}")
            else:
                self.logger.warning(f"圖片複製失敗: {scp_result.stderr}")
        except Exception as e:
            self.logger.warning(f"複製圖片時出錯: {str(e)}")