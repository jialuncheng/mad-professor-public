import re
import logging
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)

class MarkdownCleaner:
    """清理 Markdown 文件中的雜訊字元"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def _detect_watermark_headings(lines, threshold: int = 3) -> set:
        """Phase 4.7d RAG-7a：偵測重複 heading 行（≥ threshold 次）= 浮水印候選。

        normalize: strip '#' 與空白後 casefold——不同 # 數量 / 大小寫變體
        都算同一個浮水印（如 `# XDeHunt` / `### XDeHunt` / `# xdehunt`）。

        回傳 set of normalized heading text。
        """
        counter: Counter = Counter()
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('#'):
                continue
            norm = stripped.lstrip('#').strip().casefold()
            if norm:
                counter[norm] += 1
        return {h for h, n in counter.items() if n >= threshold}

    def clean(self, markdown_path: Path) -> Path:
        """清除控制字元等雜訊"""
        try:
            text = markdown_path.read_text(encoding='utf-8')

            # Step 1：移除 MinerU 從圖表解析出的純數字行（如坡度標籤 "- 8 6 1 8 11 1 2 2 4"）
            # 特徵：只含數字、空格、小數點、百分號、負號，不含任何文字
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and re.match(r'^[-\d\s.%]+$', stripped):
                    if not re.search(r'[a-zA-Z一-鿿]', stripped):
                        self.logger.debug(f"移除圖表數字行: {repr(stripped)}")
                        continue
                cleaned_lines.append(line)

            # Phase 4.7d RAG-7a Step 2：浮水印 heading 偵測 + 整行移除
            # 整篇出現 ≥ WATERMARK_HEADING_THRESHOLD 次的 heading 視為浮水印
            # （DeHunt 履歷 XDeHunt / HDeHunt 浮水印各出現 5 處被 MinerU OCR
            #  抽成多處 markdown heading、影響後續 doc_analyzer / md_processor / RAG）
            from settings import WATERMARK_HEADING_THRESHOLD
            watermarks = self._detect_watermark_headings(
                cleaned_lines, threshold=WATERMARK_HEADING_THRESHOLD
            )
            if watermarks:
                removed_counts: dict = {}
                final_lines = []
                for line in cleaned_lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        norm = stripped.lstrip('#').strip().casefold()
                        if norm in watermarks:
                            removed_counts[norm] = removed_counts.get(norm, 0) + 1
                            continue
                    final_lines.append(line)
                for norm, count in removed_counts.items():
                    self.logger.info(
                        f"[md_cleaner] 移除浮水印 heading: {norm!r} ({count} 次)"
                    )
                cleaned_lines = final_lines

            text = '\n'.join(cleaned_lines)
            markdown_path.write_text(text, encoding='utf-8')
            self.logger.info(f"清理完成: {markdown_path}")
            return markdown_path
        except Exception as e:
            self.logger.warning(f"清理時出錯（不影響後續流程）: {str(e)}")
            return markdown_path
