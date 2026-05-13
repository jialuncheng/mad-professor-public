import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF處理器：透過本機 MinerU API 將 PDF 轉換為 Markdown 格式"""
    
    MINERU_API_URL = "http://192.168.139.94:8000/file_parse"

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
                        "backend": "pipeline"
                    },
                    timeout=300
                )

            if response.status_code != 200:
                raise RuntimeError(f"MinerU API 回傳錯誤: {response.status_code} {response.text}")

            result = response.json()
            
            paper_name = pdf_path.stem
            markdown_path = output_dir / f"{paper_name}.md"

            md_content = result.get("md_content") or result.get("markdown") or ""
            if not md_content:
                raise RuntimeError(f"MinerU API 回傳內容為空，完整回應: {result}")

            markdown_path.write_text(md_content, encoding="utf-8")
            self.logger.info(f"Markdown 文件已保存到: {markdown_path}")
            return markdown_path

        except requests.exceptions.ConnectionError:
            raise RuntimeError("無法連接 MinerU API，請確認 MinerU 服務是否已啟動")
        except Exception as e:
            self.logger.error(f"PDF 處理失敗: {str(e)}", exc_info=True)
            raise