import os
import requests
import logging
import zipfile
import io
import subprocess
import shutil
from pathlib import Path
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

            task_id = response.headers.get("x-mineru-task-id")
            if not task_id:
                self.logger.warning("MinerU 未回傳 x-mineru-task-id header")

            paper_name = pdf_path.stem

            # 解壓 ZIP 到暫存目錄
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(output_dir / "_tmp")

            # 把 Markdown 移到正確位置
            tmp_md = output_dir / "_tmp" / paper_name / "auto" / f"{paper_name}.md"
            markdown_path = output_dir / f"{paper_name}.md"
            if tmp_md.exists():
                tmp_md.rename(markdown_path)

            # 清除控制字元（MinerU 解析特殊字元時可能產生）
            md_text = markdown_path.read_text(encoding='utf-8')
            md_text = CONTROL_CHAR_PATTERN.sub('', md_text)
            markdown_path.write_text(md_text, encoding='utf-8')

            # 從 mineru-lab 複製圖片
            self._copy_images(paper_name, output_dir, task_id)

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

    def _copy_images(self, paper_name: str, output_dir: Path, task_id: str = None):
        """複製 MinerU 解析出的圖片目錄（雙模式，best-effort，永不 raise）。

        MINERU_HOST 有值 → 遠端模式：scp（無 task_id 時退回 ssh ls -t）。
        MINERU_HOST 為空 → 本地/bind-mount 模式：MINERU_OUTPUT_DIR 視為
        本機可讀路徑，用 shutil.copytree 複製（無 task_id 時取最新子目錄）。
        """
        try:
            dst = str(output_dir / "images")

            if self.MINERU_HOST:
                if task_id:
                    self.logger.info(f"MinerU task_id: {task_id}")
                    src = f"{self.MINERU_HOST}:{self.MINERU_OUTPUT_DIR}/{task_id}/{paper_name}/auto/images/"
                else:
                    self.logger.warning(
                        "無 task_id，退回 ls -t | head -1 猜目錄（多份並發時不可靠）"
                    )
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

                self.logger.info(f"scp 來源: {src}")
                scp_result = subprocess.run(
                    ["scp", "-r", src, dst],
                    capture_output=True, text=True, timeout=60
                )
                if scp_result.returncode == 0:
                    self.logger.info(f"圖片複製成功: {dst}")
                else:
                    self.logger.warning(f"圖片複製失敗: {scp_result.stderr}")
            else:
                if not self.MINERU_OUTPUT_DIR:
                    self.logger.warning("本地模式但 MINERU_OUTPUT_DIR 未設定，跳過圖片複製")
                    return

                if task_id:
                    self.logger.info(f"MinerU task_id: {task_id}（本地模式）")
                    src = Path(self.MINERU_OUTPUT_DIR) / task_id / paper_name / "auto" / "images"
                else:
                    self.logger.warning(
                        "無 task_id，本地掃最新子目錄猜目錄（多份並發時不可靠）"
                    )
                    output_root = Path(self.MINERU_OUTPUT_DIR)
                    if not output_root.is_dir():
                        self.logger.warning(f"本地 MINERU_OUTPUT_DIR 不存在: {output_root}")
                        return
                    subdirs = [d for d in output_root.iterdir() if d.is_dir()]
                    if not subdirs:
                        self.logger.warning("本地 MINERU_OUTPUT_DIR 內無子目錄")
                        return
                    latest = max(subdirs, key=lambda d: d.stat().st_mtime)
                    src = latest / paper_name / "auto" / "images"

                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    self.logger.info(f"圖片複製成功（本地）: {dst}")
                else:
                    self.logger.warning(f"找不到本地圖片目錄: {src}")
        except Exception as e:
            self.logger.warning(f"複製圖片時出錯: {str(e)}")