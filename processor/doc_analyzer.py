import re
import json
import logging
from pathlib import Path
from config import LLMClient
from utils.heading_utils import fix_heading_levels
from utils.text_utils import strip_json_fence

logger = logging.getLogger(__name__)

HEADING_FIX_PROMPTS = {
    'academic':  'prompt/doc/heading_fix_academic.txt',
    'book':      'prompt/doc/heading_fix_book.txt',
    'technical': 'prompt/doc/heading_fix_technical.txt',
    'slides':    'prompt/doc/heading_fix_slides.txt',
    'web':       'prompt/doc/heading_fix_web.txt',
    'news':      'prompt/doc/heading_fix_news.txt',
}

STRUCTURE_PROMPTS = {
    'academic':  'prompt/doc/structure_academic.txt',
    'book':      'prompt/doc/structure_book.txt',
    'technical': 'prompt/doc/structure_technical.txt',
    'slides':    'prompt/doc/structure_slides.txt',
    'web':       'prompt/doc/structure_web.txt',
    'news':      'prompt/doc/structure_news.txt',
}

class DocAnalyzer:
    """文件結構分析器：偵測文件類型、修正標題層級、分析文件結構"""

    def __init__(self, llm=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = llm if llm is not None else LLMClient.get_instance()

    def _read_prompt(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding='utf-8').strip()
        except Exception as e:
            self.logger.warning(f"讀取 prompt 失敗: {path} - {str(e)}")
            return ""

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
            prompt = prompt_template.replace('{headings}', '\n'.join(heading_lines))

            new_text = fix_heading_levels(content, self.llm, prompt)

            markdown_path.write_text(new_text, encoding='utf-8')
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

            FLAT_DOC_TYPES = ('news', 'web')
            max_lines = 120 if doc_type in FLAT_DOC_TYPES else 500
            analysis_end = min(first_section_line + 10, max_lines, len(lines))
            self.logger.info(
                f"structure 分析範圍: {analysis_end} 行"
                f"（doc_type={doc_type}, 上限={max_lines}）"
            )
            analysis_lines = lines[:analysis_end]
            numbered = '\n'.join(
                f'{i}: {line}' for i, line in enumerate(analysis_lines) if line.strip()
            )

            prompt_template = self._read_prompt(STRUCTURE_PROMPTS[doc_type])
            prompt = prompt_template.replace('{content}', numbered)

            result_text = self.llm.chat(
                [{'role': 'user', 'content': prompt}], stream=False
            ).strip()
            result_text = strip_json_fence(result_text)
            structure = json.loads(result_text)

            # 加入 document_type 欄位，供 md_processor 使用
            structure['document_type'] = doc_type
            # 簡報用扁平結構，不建立父子關係
            if doc_type == 'slides':
                structure['flat_structure'] = True

            sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
            sidecar_path.write_text(
                json.dumps(structure, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            self.logger.info(f'文件結構分析完成: {doc_type}')
            return structure

        except Exception as e:
            self.logger.warning(f'文件結構分析時出錯（不影響後續流程）: {str(e)}')
            return {}
