import logging
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import LLMClient

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MIME_TYPES = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
}

class ImageCaptionProcessor:
    """Vision 圖片說明生成器：掃描 images/ 目錄，為每張圖片生成 caption，輸出 images_info.md"""

    def __init__(self, llm=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = llm if llm is not None else LLMClient.get_instance()

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
            self.logger.warning(f"images 目錄不存在: {images_dir}，建立空的 images_info.md")
            output_path.write_text('', encoding='utf-8')
            return output_path

        image_files = sorted([
            f for f in images_dir.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ])

        if not image_files:
            self.logger.info("沒有圖片需要處理，建立空的 images_info.md")
            output_path.write_text('', encoding='utf-8')
            return output_path

        self.logger.info(f"開始處理 {len(image_files)} 張圖片")

        # 並行生成 caption，結果依 image_files 原索引回填以保證輸出順序
        captions = [""] * len(image_files)
        max_workers = min(4, len(image_files))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self._generate_caption, img_path): i
                for i, img_path in enumerate(image_files)
            }
            for future in as_completed(future_to_idx):
                i = future_to_idx[future]
                captions[i] = future.result()

        lines = []
        for idx, img_path in enumerate(image_files, 1):
            self.logger.info(f"  [{idx}/{len(image_files)}] {img_path.name}")
            src = f"images/{img_path.name}"
            lines.append(f"## {src}")
            lines.append(captions[idx - 1])
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
