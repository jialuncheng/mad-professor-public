import logging
from pathlib import Path
from typing import Optional
from config import LLMClient

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MIME_TYPES = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
}

class ImageCaptionProcessor:
    """Vision 圖片說明生成器：掃描 images/ 目錄，為每張圖片生成 caption，輸出 images_info.md"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = LLMClient()

    def process(self, images_dir: str, output_path: str) -> Optional[Path]:
        """
        掃描 images_dir 下所有圖片，用 Vision 生成 caption，
        輸出 images_info.md。

        格式：
        ## images/xxx.jpg
        caption 內容

        ## images/yyy.png
        caption 內容
        """
        images_dir = Path(images_dir)
        output_path = Path(output_path)

        if not images_dir.exists():
            self.logger.warning(f"images 目錄不存在: {images_dir}")
            return None

        image_files = sorted([
            f for f in images_dir.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ])

        if not image_files:
            self.logger.info("沒有圖片需要處理")
            return None

        self.logger.info(f"開始處理 {len(image_files)} 張圖片")

        lines = []
        for img_path in image_files:
            caption = self._generate_caption(img_path)
            src = f"images/{img_path.name}"
            lines.append(f"## {src}")
            lines.append(caption)
            lines.append("")

        output_path.write_text('\n'.join(lines), encoding='utf-8')
        self.logger.info(f"images_info.md 已生成: {output_path}（{len(image_files)} 張圖片）")
        return output_path

    def _generate_caption(self, img_path: Path) -> str:
        """用 Vision 為單張圖片生成說明"""
        try:
            img_data = img_path.read_bytes()
            mime = MIME_TYPES.get(img_path.suffix.lower(), 'image/jpeg')

            result = self.llm.chat_with_image(
                messages=[{"role": "user", "content":
                    "請用一到兩句話描述這張圖片的內容。"
                    "如果是圖表（折線圖、柱狀圖、散點圖等），說明圖表類型和主要呈現的資訊。"
                    "如果是示意圖或流程圖，說明其結構或流程。"
                    "如果是照片或顯微鏡圖，說明拍攝內容。"
                    "聚焦在學術或科學意義上，不要描述圖片風格。"}],
                image_data=img_data,
                mime_type=mime
            )
            caption = result.strip()
            self.logger.info(f"  {img_path.name}: {caption[:60]}...")
            return caption

        except Exception as e:
            self.logger.warning(f"  {img_path.name} 生成失敗: {str(e)}")
            return ""
