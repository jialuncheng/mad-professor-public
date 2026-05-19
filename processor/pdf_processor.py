import os
import time
import requests
import logging
import zipfile
import io
import subprocess
import shutil
import unicodedata
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
        # MinerU 端輸出子目錄名（= 上傳檔名 stem）。web_server 一律存成
        # original.pdf 後才送 MinerU，故 MinerU 端固定為 "original"，與本機
        # paper_name（pdf_path.stem）解耦；可用 env 覆寫以防上游改名。
        self.MINERU_PAPER_NAME = os.getenv("MINERU_PAPER_NAME", "original")
        self.logger.debug("初始化 PDF 處理器（MinerU API 模式）")

    def process(self, pdf_path: str, output_dir: str) -> Path:
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"呼叫 MinerU API 處理 PDF: {pdf_path}")
            self.logger.info(f"[pdf_processor] 開始 pdf={pdf_path}")
            self.logger.info(
                f"[pdf_processor] POST MinerU API URL={self.MINERU_API_URL}"
            )
            _post_t0 = time.time()

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

            self.logger.info(
                f"[pdf_processor] MinerU 回應 status={response.status_code} "
                f"耗時={time.time() - _post_t0:.2f}s "
                f"content_length={len(response.content)} "
                f"task_id={response.headers.get('x-mineru-task-id')}"
            )

            if response.status_code != 200:
                raise RuntimeError(f"MinerU API 回傳錯誤: {response.status_code} {response.text}")

            task_id = response.headers.get("x-mineru-task-id")
            if not task_id:
                self.logger.warning("MinerU 未回傳 x-mineru-task-id header")

            paper_name = pdf_path.stem            # 本機輸出檔名用
            mineru_name = self.MINERU_PAPER_NAME  # MinerU 端 ZIP 內目錄/檔名（固定）

            # 解壓 ZIP 到暫存目錄
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(output_dir / "_tmp")
                self.logger.info(
                    f"[pdf_processor] ZIP 解壓完成 內容={z.namelist()}"
                )

            _tmp_root = output_dir / "_tmp"
            _tmp_files = (
                [str(p.relative_to(_tmp_root))
                 for p in sorted(_tmp_root.rglob("*")) if p.is_file()]
                if _tmp_root.exists() else []
            )
            self.logger.info(f"[pdf_processor] _tmp 內容: {_tmp_files}")

            # ZIP 內結構由 MinerU 端命名（= 上傳檔 stem，固定 original）；
            # 落地後的本機 md 檔名沿用 paper_name（不改既有下游路徑預期）
            tmp_md = output_dir / "_tmp" / mineru_name / "auto" / f"{mineru_name}.md"
            markdown_path = output_dir / f"{paper_name}.md"
            self.logger.info(
                f"[pdf_processor] markdown 搬移 from={tmp_md} "
                f"to={markdown_path} from_exists={tmp_md.exists()}"
            )
            if tmp_md.exists():
                tmp_md.rename(markdown_path)

            # 清除控制字元（MinerU 解析特殊字元時可能產生）
            md_text = markdown_path.read_text(encoding='utf-8')
            md_text = CONTROL_CHAR_PATTERN.sub('', md_text)
            # NFKC 正規化：拆解連字 ligature（ﬁ→fi, ﬂ→fl, ﬃ→ffi…）等相容字元
            md_text = unicodedata.normalize('NFKC', md_text)
            markdown_path.write_text(md_text, encoding='utf-8')

            # 從 mineru-lab 複製圖片（MinerU 端目錄名固定，與 paper_name 解耦）
            self.logger.info(
                f"[pdf_processor] 呼叫 _copy_images task_id={task_id} "
                f"dst={output_dir / 'images'}"
            )
            self._copy_images(output_dir, task_id)

            # 清理暫存目錄
            self.logger.info(f"[pdf_processor] rmtree _tmp: {output_dir / '_tmp'}")
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

    def _copy_images(self, output_dir: Path, task_id: str = None):
        """複製 MinerU 解析出的圖片目錄（雙模式，best-effort，永不 raise）。

        MinerU 端子目錄名用 self.MINERU_PAPER_NAME（固定 "original"，因
        web_server 一律以 original.pdf 送 MinerU），與本機 paper_name
        （pdf_path.stem）無關——後者僅用於本機 markdown 檔名。

        MINERU_HOST 有值 → 遠端模式：scp（無 task_id 時退回 ssh ls -t）。
        MINERU_HOST 為空 → 本地/bind-mount 模式：MINERU_OUTPUT_DIR 視為
        本機可讀路徑，用 shutil.copytree 複製（無 task_id 時取最新子目錄）。
        """
        try:
            dst = str(output_dir / "images")
            mineru_name = self.MINERU_PAPER_NAME

            if self.MINERU_HOST:
                if task_id:
                    self.logger.info(f"MinerU task_id: {task_id}")
                    src = f"{self.MINERU_HOST}:{self.MINERU_OUTPUT_DIR}/{task_id}/{mineru_name}/auto/images/"
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
                    src = f"{self.MINERU_HOST}:{self.MINERU_OUTPUT_DIR}/{latest_task}/{mineru_name}/auto/images/"

                self.logger.info(f"scp 來源: {src}")
                self.logger.info(f"[copy_images] 遠端模式 src={src} dst={dst}")
                scp_result = subprocess.run(
                    ["scp", "-r", src, dst],
                    capture_output=True, text=True, timeout=60
                )
                self.logger.info(
                    f"[copy_images] scp returncode={scp_result.returncode} "
                    f"stderr={scp_result.stderr.strip()!r} "
                    f"stdout={scp_result.stdout.strip()!r}"
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
                    src = Path(self.MINERU_OUTPUT_DIR) / task_id / mineru_name / "auto" / "images"
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
                    src = latest / mineru_name / "auto" / "images"

                self.logger.info(
                    f"[copy_images] 本地模式 src={src} exists={src.is_dir()}"
                )
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    self.logger.info(f"圖片複製成功（本地）: {dst}")
                else:
                    self.logger.warning(f"找不到本地圖片目錄: {src}")

            _dst_p = Path(dst)
            _dst_files = (
                sorted(p.name for p in _dst_p.iterdir())
                if _dst_p.is_dir() else []
            )
            self.logger.info(
                f"[copy_images] 完成 dst={dst} 內容({len(_dst_files)})="
                f"{_dst_files}"
            )
        except Exception as e:
            self.logger.warning(f"複製圖片時出錯: {str(e)}")