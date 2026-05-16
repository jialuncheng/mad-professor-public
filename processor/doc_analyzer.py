import re
import json
import logging
from pathlib import Path
from config import LLMClient

logger = logging.getLogger(__name__)

HEADING_FIX_PROMPTS = {
    'academic':  'prompt/heading_fix_academic.txt',
    'book':      'prompt/heading_fix_book.txt',
    'technical': 'prompt/heading_fix_technical.txt',
    'slides':    'prompt/heading_fix_slides.txt',
    'web':       'prompt/heading_fix_web.txt',
}

STRUCTURE_PROMPTS = {
    'academic':  'prompt/structure_academic.txt',
    'book':      'prompt/structure_book.txt',
    'technical': 'prompt/structure_technical.txt',
    'slides':    'prompt/structure_slides.txt',
    'web':       'prompt/structure_web.txt',
}

class DocAnalyzer:
    """文件結構分析器：偵測文件類型、修正標題層級、分析文件結構"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = LLMClient()

    def _read_prompt(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding='utf-8').strip()
        except Exception as e:
            self.logger.warning(f"讀取 prompt 失敗: {path} - {str(e)}")
            return ""

    def detect_type(self, markdown_path: Path) -> dict:
        """
        快速偵測文件類型，回傳偵測結果。
        回傳: {"doc_type": str, "confidence": str, "reason": str}
        """
        try:
            content = markdown_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            # 只取前 30 個非空行
            preview = '\n'.join(
                f'{i}: {line}' for i, line in enumerate(lines[:60]) if line.strip()
            )[:30]
            # 重新計算只取前30行
            non_empty = [(i, line) for i, line in enumerate(lines) if line.strip()][:30]
            preview = '\n'.join(f'{i}: {line}' for i, line in non_empty)

            prompt_template = self._read_prompt('prompt/doc_type_detect.txt')
            prompt = prompt_template.format(content=preview)

            result_text = self.llm.chat(
                [{"role": "user", "content": prompt}], stream=False
            ).strip()
            result_text = re.sub(r'```json|```', '', result_text).strip()
            result = json.loads(result_text)

            doc_type = result.get('doc_type', 'academic')
            if doc_type not in HEADING_FIX_PROMPTS:
                doc_type = 'academic'
            result['doc_type'] = doc_type

            self.logger.info(f"文件類型偵測: {doc_type} ({result.get('confidence')}) - {result.get('reason')}")
            return result

        except Exception as e:
            self.logger.warning(f"文件類型偵測失敗，預設 academic: {str(e)}")
            return {"doc_type": "academic", "confidence": "low", "reason": "偵測失敗"}

    def analyze(self, markdown_path: Path, doc_type: str) -> Path:
        """根據文件類型執行標題修正和結構分析"""
        if doc_type not in HEADING_FIX_PROMPTS:
            self.logger.warning(f"未知文件類型 {doc_type}，使用 academic")
            doc_type = 'academic'

        self._fix_heading_levels(markdown_path, doc_type)
        self._analyze_document_structure(markdown_path, doc_type)
        return markdown_path

    def _fix_heading_levels(self, markdown_path: Path, doc_type: str):
        """用 LLM 修正 Markdown 標題層級"""
        try:
            content = markdown_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            heading_lines = [f"行{i}: {line}" for i, line in enumerate(lines) if line.startswith('#')]
            if not heading_lines:
                return

            prompt_template = self._read_prompt(HEADING_FIX_PROMPTS[doc_type])
            prompt = prompt_template.format(headings='\n'.join(heading_lines))

            result_text = self.llm.chat(
                [{"role": "user", "content": prompt}], stream=False
            ).strip()
            result_text = re.sub(r'```json|```', '', result_text).strip()
            heading_map = json.loads(result_text)

            new_lines = lines.copy()
            for line_num_str, hash_count in heading_map.items():
                line_num = int(line_num_str)
                if line_num < len(lines) and lines[line_num].startswith('#'):
                    title_text = lines[line_num].lstrip('#').strip()
                    new_lines[line_num] = '#' * int(hash_count) + ' ' + title_text

            markdown_path.write_text('\n'.join(new_lines), encoding='utf-8')
            self.logger.info(f"標題層級修正完成: {markdown_path}")

        except Exception as e:
            self.logger.warning(f"標題層級修正時出錯（不影響後續流程）: {str(e)}")

    def _analyze_document_structure(self, markdown_path: Path, doc_type: str) -> dict:
        """用 LLM 分析文件前段結構"""
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
            numbered = '\n'.join(
                f'{i}: {line}' for i, line in enumerate(analysis_lines) if line.strip()
            )

            prompt_template = self._read_prompt(STRUCTURE_PROMPTS[doc_type])
            prompt = prompt_template.format(content=numbered)

            result_text = self.llm.chat(
                [{'role': 'user', 'content': prompt}], stream=False
            ).strip()
            result_text = re.sub(r'```json|```', '', result_text).strip()
            structure = json.loads(result_text)

            # 加入 document_type 欄位，供 md_processor 使用
            structure['document_type'] = doc_type

            sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
            sidecar_path.write_text(
                json.dumps(structure, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            self.logger.info(f'文件結構分析完成: {doc_type}')
            return structure

        except Exception as e:
            self.logger.warning(f'文件結構分析時出錯（不影響後續流程）: {str(e)}')
            return {}
