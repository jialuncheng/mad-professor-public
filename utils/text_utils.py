import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_caption_map(images_info_path: str) -> dict:
    """讀取 images_info.md，建立 src -> caption 的字典"""
    caption_map = {}
    try:
        path = Path(images_info_path)
        if not path.exists():
            return caption_map
        lines = path.read_text(encoding='utf-8').split('\n')
        current_src = None
        for line in lines:
            if line.startswith('## '):
                current_src = line[3:].strip()
            elif current_src and line.strip():
                caption_map[current_src] = line.strip()
                # 也存只有檔名的版本
                caption_map[Path(current_src).name] = line.strip()
                current_src = None
        logger.info(f"載入 caption_map: {len(caption_map)} 張圖片")
    except Exception as e:
        logger.warning(f"讀取 images_info.md 失敗: {str(e)}")
    return caption_map


CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def strip_json_fence(text: str) -> str:
    return re.sub(r'```json|```', '', text).strip()
