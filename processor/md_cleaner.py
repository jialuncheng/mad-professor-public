import re
import logging
from pathlib import Path
from utils.text_utils import CONTROL_CHAR_PATTERN

logger = logging.getLogger(__name__)

class MarkdownCleaner:
    """清理 Markdown 文件中的雜訊字元"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def clean(self, markdown_path: Path) -> Path:
        """清除控制字元等雜訊"""
        try:
            text = markdown_path.read_text(encoding='utf-8')

            # 移除控制字元
            text = CONTROL_CHAR_PATTERN.sub('', text)

            # 移除 MinerU 從圖表解析出的純數字行（如坡度標籤 "- 8 6 1 8 11 1 2 2 4"）
            # 特徵：只含數字、空格、小數點、百分號、負號，不含任何文字
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and re.match(r'^[-\d\s.%]+$', stripped):
                    if not re.search(r'[a-zA-Z\u4e00-\u9fff]', stripped):
                        self.logger.debug(f"移除圖表數字行: {repr(stripped)}")
                        continue
                cleaned_lines.append(line)
            text = '\n'.join(cleaned_lines)

            markdown_path.write_text(text, encoding='utf-8')
            self.logger.info(f"清理完成: {markdown_path}")
            return markdown_path
        except Exception as e:
            self.logger.warning(f"清理時出錯（不影響後續流程）: {str(e)}")
            return markdown_path
