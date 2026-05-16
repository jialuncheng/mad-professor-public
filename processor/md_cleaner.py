import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MarkdownCleaner:
    """清理 Markdown 文件中的雜訊字元"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def clean(self, markdown_path: Path) -> Path:
        """清除控制字元等雜訊"""
        try:
            text = markdown_path.read_text(encoding='utf-8')
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
            markdown_path.write_text(text, encoding='utf-8')
            self.logger.info(f"清理完成: {markdown_path}")
            return markdown_path
        except Exception as e:
            self.logger.warning(f"清理時出錯（不影響後續流程）: {str(e)}")
            return markdown_path
