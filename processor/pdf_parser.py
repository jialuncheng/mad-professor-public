"""PDF → Markdown 解析的抽象介面。

設計：
- impl 端（pdf_processor / slides_processor）繼承 PDFParser
- caller 端（pipeline_core）只透過 PDFParser 介面呼叫
- 換 impl（pdfplumber / Marker / 自家解析）時主程式不必改

語意契約：
- 同步 call（與 pipeline 階段化邏輯相容）
- 失敗統一 raise PDFParseError（不要 raise impl-specific exception）
- 圖檔以 side-effect 寫入 output_dir/images/（best-effort，可缺）
- 不對 caller 暴露 impl 內部細節（task_id / ZIP / scp / API URL 等）
"""
from abc import ABC, abstractmethod
from pathlib import Path


class PDFParseError(RuntimeError):
    """PDF 解析失敗（任何 impl 都用此 type）。"""
    pass


class PDFParser(ABC):
    """PDF → Markdown 的抽象介面。"""

    @abstractmethod
    def parse(self, pdf_path: str, output_dir: str) -> Path:
        """
        Args:
            pdf_path:   本機 PDF 絕對路徑
            output_dir: 輸出資料夾（會建立 _tmp/, images/ 等子目錄）

        Returns:
            markdown_path: Path  # output_dir/{stem}.md

        Raises:
            FileNotFoundError: pdf_path 不存在
            PDFParseError:     解析服務錯誤、ZIP 損壞、超時等
        """
        raise NotImplementedError
