import os
import requests
import logging
import zipfile
import io
import subprocess
import shutil
from pathlib import Path
from config import LLMClient

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF處理器：透過本機 MinerU API 將 PDF 轉換為 Markdown 格式"""





    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.MINERU_API_URL = os.getenv("MINERU_API_URL", "http://192.168.139.94:8000/file_parse")
        self.MINERU_HOST = os.getenv("MINERU_HOST", "baroncheng@192.168.139.94")
        self.MINERU_OUTPUT_DIR = os.getenv("MINERU_OUTPUT_DIR", "/home/baroncheng/output")
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

            paper_name = pdf_path.stem

            # 解壓 ZIP 到暫存目錄
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(output_dir / "_tmp")

            # 把 Markdown 移到正確位置
            tmp_md = output_dir / "_tmp" / paper_name / "auto" / f"{paper_name}.md"
            markdown_path = output_dir / f"{paper_name}.md"
            if tmp_md.exists():
                tmp_md.rename(markdown_path)

            # 用 LLM 修正標題層級
            self._fix_heading_levels(markdown_path)

            # 清除控制字元（MinerU 解析特殊字元時可能產生）
            import re as _re
            md_text = markdown_path.read_text(encoding='utf-8')
            md_text = _re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', md_text)
            markdown_path.write_text(md_text, encoding='utf-8')

            # 分析文件結構
            self._analyze_document_structure(markdown_path)

            # 從 mineru-lab 複製圖片
            self._copy_images(paper_name, output_dir)

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

    def _fix_heading_levels(self, markdown_path: Path):
        """用 LLM 修正 Markdown 標題層級"""
        try:
            content = markdown_path.read_text(encoding="utf-8")

            # 只取出標題行給 LLM 判斷
            lines = content.split("\n")
            heading_lines = []
            for i, line in enumerate(lines):
                if line.startswith("#"):
                    heading_lines.append(f"行{i}: {line}")

            if not heading_lines:
                return
    
            headings_text = "\n".join(heading_lines)

            prompt = f"""以下是一篇學術論文 Markdown 的所有標題行（格式：行號: 標題內容）：

{headings_text}

請根據學術論文的結構邏輯（章節編號格式、標題語意、層級關係），判斷每個標題應該使用幾個 # 符號。

規則：
- 論文標題用 #（一個）
- 頂層章節（Abstract、Introduction、Methods、Results、Discussion、References 等，或羅馬數字 I. II. III.）用 ##（兩個）
- 子章節（阿拉伯數字 1. 2. 3. 或明顯從屬於上一層的標題）用 ###（三個）
- 子子章節用 ####（四個）

請只輸出 JSON 格式，key 為行號（數字），value 為應使用的 # 數量（1-4 的整數）：
{{"行號": #數量, ...}}

只輸出 JSON，不要任何解釋。"""

            messages = [{"role": "user", "content": prompt}]
            result_text = self.llm.chat(messages, stream=False).strip()

            # 清理 JSON（移除可能的 markdown 包裹）
            import re
            result_text = re.sub(r"```json|```", "", result_text).strip()

            import json
            heading_map = json.loads(result_text)

            # 套用修正
            new_lines = lines.copy()
            for line_num_str, hash_count in heading_map.items():
                line_num = int(line_num_str)
                if line_num < len(lines) and lines[line_num].startswith("#"):
                    original = lines[line_num]
                    # 取出標題文字（去掉所有 # 和空白）
                    title_text = original.lstrip("#").strip()
                    new_lines[line_num] = "#" * int(hash_count) + " " + title_text

            markdown_path.write_text("\n".join(new_lines), encoding="utf-8")
            self.logger.info(f"標題層級修正完成: {markdown_path}")

        except Exception as e:
            self.logger.warning(f"標題層級修正時出錯（不影響後續流程）: {str(e)}")

    def _analyze_document_structure(self, markdown_path: Path) -> dict:
        """用 LLM 分析文件結構，識別標題、作者、摘要等區塊"""
        import re
        import json as json_module

        try:
            content = markdown_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            first_section_line = len(lines)
            for i, line in enumerate(lines):
                if re.match(r'^#{2,}\s+\S', line):
                    first_section_line = i
                    break

            analysis_end = min(first_section_line + 10, 500, len(lines))
            analysis_lines = lines[:analysis_end]
            # 只送非空行給 LLM，但保留原始行號
            numbered = '\n'.join(f'{i}: {line}' for i, line in enumerate(analysis_lines) if line.strip())

            prompt = f"""以下是一份文件的前段內容（格式：原始行號: 內容，空行已省略但行號保留）：

{numbered}

請分析這份文件的結構，回傳 JSON：

{{
  "document_type": "academic_paper 或 book 或 technical_doc 或 slides 或 other",
  "structure": [
    {{"start": 起始行號, "end": 結束行號, "type": "類型"}}
  ]
}}

type 可以是：title, authors, publication_info, abstract, preface, toc, section_heading, intro_text, other

只輸出 JSON，不要任何解釋。"""

            messages = [{'role': 'user', 'content': prompt}]
            result_text = self.llm.chat(messages, stream=False).strip()
            result_text = re.sub(r'```json|```', '', result_text).strip()
            structure = json_module.loads(result_text)

            sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
            sidecar_path.write_text(json_module.dumps(structure, ensure_ascii=False, indent=2), encoding='utf-8')
            self.logger.info(f'文件結構分析完成: {structure.get("document_type")}')
            return structure

        except Exception as e:
            self.logger.warning(f'文件結構分析時出錯（不影響後續流程）: {str(e)}')
            return {}

    def _copy_images(self, paper_name: str, output_dir: Path):
        """從 mineru-lab 複製最新的圖片目錄"""
        try:
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
            dst = str(output_dir / "images")

            scp_result = subprocess.run(
                ["scp", "-r", src, dst],
                capture_output=True, text=True, timeout=60
            )
            if scp_result.returncode == 0:
                self.logger.info(f"圖片複製成功: {dst}")
            else:
                self.logger.warning(f"圖片複製失敗: {scp_result.stderr}")
        except Exception as e:
            self.logger.warning(f"複製圖片時出錯: {str(e)}")