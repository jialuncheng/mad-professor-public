import requests
import logging
import zipfile
import io
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF處理器：透過本機 MinerU API 將 PDF 轉換為 Markdown 格式"""
    
    MINERU_API_URL = "http://192.168.139.94:8000/file_parse"
    MINERU_HOST = "baroncheng@192.168.139.94"
    MINERU_OUTPUT_DIR = "/home/baroncheng/output"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("初始化 PDF 處理器（MinerU API 模式）")

    def process(self, pdf_path: str, output_dir: str) -> Path:
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
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

            # 取得 task_id 用於後續複製圖片
            content_type = response.headers.get("content-type", "")
            task_id = response.headers.get("X-Task-Id") or response.headers.get("task-id")

            # 解壓 ZIP（包含 Markdown）
            paper_name = pdf_path.stem
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # ZIP 內路徑是 NPH71232/auto/NPH71232.md，解壓後需要移動
                z.extractall(output_dir / "_tmp")

            # 把 Markdown 移到正確位置
            tmp_md = output_dir / "_tmp" / paper_name / "auto" / f"{paper_name}.md"
            markdown_path = output_dir / f"{paper_name}.md"
            if tmp_md.exists():
                tmp_md.rename(markdown_path)

            # 從 mineru-lab 複製圖片
            self._copy_images(paper_name, output_dir)

            # 清理暫存目錄
            import shutil
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

    def _copy_images(self, paper_name: str, output_dir: Path):
        """從 mineru-lab 複製最新的圖片目錄"""
        try:
            # 找最新的 task 目錄
            result = subprocess.run(
                ["ssh", self.MINERU_HOST,
                 f"ls -t {self.MINERU_OUTPUT_DIR} | head -1"],
                capture_output=True, text=True, timeout=30
            )
            latest_task = result.stdout.strip()
            if not latest_task:
                self.logger.warning("找不到 mineru-lab 的輸出目錄")