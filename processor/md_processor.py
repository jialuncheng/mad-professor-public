import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Section:
    title: str
    number: str
    level: int
    content: List[str]
    raw_title: str
    type: Optional[str] = None
    heading_level: int = 1

class MarkdownProcessor:
    """Markdown處理器：將Markdown解析為結構化JSON"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.title_pattern = re.compile(r'^(#+)\s*(\S.*?)$')
        self.abstract_pattern = re.compile(
            r'^#+\s*(?:\d+\.)?\s*(?:ABSTRACT|Abstract|abstract|SUMMARY|Summary|summary)'
        )
        self.reference_pattern = re.compile(r'^#+\s*(?:\d+\.)?\s*(?:REFERENCES?|References?|references?)')
        self.reference_line_pattern = re.compile(r'^(?:REFERENCES?|References?|references?)(?:\s*:|\s*\.)?\s*$')
        self.section_number_pattern = re.compile(
            r'^((?:[IVXivx]+|[0-9]+(?:\.[0-9]+)*))(\.?)\s*(.*?)$'
        )
        self.potential_title_pattern = re.compile(
            r'^(?!#)(\d+(?:\.\d+)*)\s+([A-Z][A-Z\s\d:]+(?:\s*[A-Z][A-Za-z\s\d:]+)*)'
        )
        self.figure_table_pattern = re.compile(r'''
            ^(?:
                (?:Figure|Fig\.|Table|Tab\.)
                (?:\s+\(?\d+(?:\.\d+)?\)?\.?:?)
                |
                (?:IMAGE|DIAGRAM)
                (?:\s+\d+:?)
                |
                (?:Figure|Table)
                (?:\s+[IVX]+:?)
            )
            ''', re.IGNORECASE | re.VERBOSE)
        self.image_pattern = re.compile(r'^!\[.*?\]\(.*?\)')
        self.latex_block_pattern = re.compile(r'^\$\$')

    def parse_section_number(self, title: str) -> tuple:
        match = self.section_number_pattern.match(title)
        if match:
            number, dot, raw_title = match.groups()
            if re.match(r'^[IVXivx]+$', number):
                level = 1
            else:
                level = len(number.split('.'))
            return number.strip(), raw_title.strip(), level
        return '', title.strip(), 1

    def parse_references(self, content: str) -> List[str]:
        return [line.strip() for line in content.split('\n') if line.strip()]

    def parse_content(self, content: List[str]) -> List[str]:
        text = '\n'.join(content)
        paragraphs = []
        current_para = []
        in_latex_block = False
        latex_content = []
        for line in text.split('\n'):
            line = line.strip()
            if self.latex_block_pattern.match(line):
                if in_latex_block:
                    latex_content.append(line)
                    paragraphs.append('\n'.join(latex_content))
                    latex_content = []
                    in_latex_block = False
                else:
                    if current_para:
                        paragraphs.append('\n'.join(current_para).strip())
                        current_para = []
                    latex_content.append(line)
                    in_latex_block = True
                continue
            if in_latex_block:
                latex_content.append(line)
                continue
            if not line:
                if current_para:
                    paragraphs.append('\n'.join(current_para).strip())
                    current_para = []
                continue
            if self.image_pattern.match(line) or self.figure_table_pattern.match(line):
                if current_para:
                    paragraphs.append('\n'.join(current_para).strip())
                    current_para = []
                paragraphs.append(line)
                continue
            current_para.append(line)
        if current_para:
            paragraphs.append('\n'.join(current_para).strip())
        return paragraphs

    def find_missing_sections(self, content: str, current_prefix: str) -> Tuple[List[Section], List[str]]:
        missing_sections = []
        lines = content.split('\n')
        section_start_indices = []
        for i, line in enumerate(lines):
            match = self.potential_title_pattern.match(line)
            if match:
                number, title_text = match.groups()
                if number.startswith(current_prefix):
                    section_start_indices.append((i, number, title_text))
        if not section_start_indices:
            return [], self.parse_content(lines)
        original_content = self.parse_content(lines[:section_start_indices[0][0]])
        for idx in range(len(section_start_indices)):
            start_idx, number, title_text = section_start_indices[idx]
            end_idx = section_start_indices[idx + 1][0] if idx < len(section_start_indices) - 1 else len(lines)
            section_content = self.parse_content(lines[start_idx + 1:end_idx])
            number, raw_title, level = self.parse_section_number(f"{number} {title_text}")
            missing_sections.append(Section(
                title=f"{number} {title_text}",
                number=number,
                level=level,
                content=section_content,
                raw_title=raw_title
            ))
        return missing_sections, original_content

    def remove_empty_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not sections:
            return []
        result = []
        for section in sections:
            if 'children' in section:
                section['children'] = self.remove_empty_sections(section['children'])
            if not (not section.get('content') and not section.get('children') and not section.get('references')):
                result.append(section)
        return result

    def _roman_to_int(self, s: str) -> int:
        roman = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
        try:
            return int(s)
        except ValueError:
            s = s.upper()
            result = 0
            for i in range(len(s)):
                if i + 1 < len(s) and roman.get(s[i], 0) < roman.get(s[i+1], 0):
                    result -= roman.get(s[i], 0)
                else:
                    result += roman.get(s[i], 0)
            return result

    def check_section_continuity(self, sections):
        sections.sort(key=lambda x: self._roman_to_int(x['number'].split('.')[-1]))
        all_sections = sections.copy()
        section_numbers = [self._roman_to_int(s['number'].split('.')[-1]) for s in sections]
        i = 0
        while i < len(section_numbers) - 1:
            current_num = section_numbers[i]
            next_num = section_numbers[i + 1]
            if next_num - current_num > 1:
                current_section = sections[i]
                prefix = '.'.join(current_section['number'].split('.')[:-1])
                if prefix:
                    prefix += '.'
                missing_sections, updated_content = self.find_missing_sections(
                    '\n'.join(current_section['content']), prefix
                )
                if missing_sections:
                    current_section['content'] = updated_content
                    for missing_section in missing_sections:
                        missing_dict = vars(missing_section)
                        missing_dict['children'] = []
                        insert_idx = next((j for j, s in enumerate(all_sections)
                                          if s['number'] > missing_section.number), len(all_sections))
                        all_sections.insert(insert_idx, missing_dict)
                    section_numbers = [self._roman_to_int(s['number'].split('.')[-1]) for s in all_sections]
                    i = 0
                    continue
            i += 1
        return all_sections

    def build_hierarchy(self, sections):
        if not sections:
            return []
        hierarchy = []
        stack = []
        for section in sections:
            section['children'] = []
            h = section.get('heading_level', 1)
            while stack and stack[-1][0] >= h:
                stack.pop()
            if stack:
                stack[-1][1]['children'].append(section)
            else:
                hierarchy.append(section)
            stack.append((h, section))
        return hierarchy

    def parse(self, content: str, structure: dict = None) -> Dict[str, Any]:
        lines = content.split('\n')
        result = {'title': '', 'authors_info': '', 'sections': []}

        # 從 doc_analyzer 的 structure 取得 authors 行號集合
        # 只有在 authors/publication_info 類型的行才放進 authors_info
        author_lines = set()
        if structure and structure.get('structure'):
            for block in structure['structure']:
                if block.get('type') in ('authors', 'publication_info'):
                    for i in range(block['start'], block['end'] + 1):
                        author_lines.add(i)

        current_section = None
        current_content = []
        collecting_authors = False
        in_references = False
        authors_content = []
        has_started = False
        current_line_num = -1

        for line in lines:
            current_line_num += 1
            title_match = self.title_pattern.match(line)
            reference_line_match = None
            if not in_references and not title_match:
                reference_line_match = self.reference_line_pattern.match(line)

            if not has_started and not title_match:
                continue
            if line.strip().startswith('#') and not title_match:
                continue

            if reference_line_match:
                if current_section:
                    current_section.content = self.parse_content(current_content)
                    result['sections'].append(vars(current_section))
                current_section = Section(
                    title="REFERENCES", number="", level=1,
                    content=[], raw_title="REFERENCES", type='references'
                )
                reference_content = re.sub(r'^(?:REFERENCES?|References?|references?)\s*', '', line).strip()
                current_content = [reference_content] if reference_content else []
                in_references = True
                continue

            elif title_match:
                heading_level = len(title_match.group(1))
                title_text = title_match.group(2).strip()

                if not has_started:
                    result['title'] = title_text
                    collecting_authors = True
                    has_started = True
                    continue

                if self.abstract_pattern.match(line):
                    result['authors_info'] = '\n'.join(authors_content).strip()
                    collecting_authors = False
                    number, raw_title, level = self.parse_section_number(title_text)
                    current_section = Section(
                        title=title_text, number=number, level=level,
                        content=[], raw_title=raw_title, type='abstract',
                        heading_level=heading_level
                    )
                    current_content = []
                    continue

                if collecting_authors:
                    if heading_level >= 2:
                        result['authors_info'] = '\n'.join(authors_content).strip()
                        collecting_authors = False
                    else:
                        authors_content.append(title_text)
                        continue

                if current_section and not collecting_authors:
                    if in_references:
                        current_section.content = self.parse_references('\n'.join(current_content))
                        result['sections'].append(vars(current_section))
                        in_references = False
                    else:
                        current_section.content = self.parse_content(current_content)
                        result['sections'].append(vars(current_section))
                elif not collecting_authors and current_content:
                    # 第一個 section 出現前的孤立內容，建立無標題 section 承載
                    orphan = Section(
                        title='', number='', level=1,
                        content=self.parse_content(current_content),
                        raw_title='', heading_level=2
                    )
                    result['sections'].append(vars(orphan))

                number, raw_title, level = self.parse_section_number(title_text)
                current_section = Section(
                    title=title_text, number=number, level=level,
                    content=[], raw_title=raw_title, heading_level=heading_level
                )
                current_content = []
                if self.reference_pattern.match(line):
                    in_references = True
                    current_section.type = 'references'

            else:
                if collecting_authors:
                    # 有 structure：只收集 author_lines 範圍內的行
                    # 沒有 structure：收集所有行（舊邏輯）
                    if author_lines:
                        if not line.strip():
                            # 空行：不觸發結束，繼續等待
                            pass
                        elif current_line_num in author_lines:
                            authors_content.append(line)
                        else:
                            # 超出 authors 範圍，結束收集，這行當內文
                            result['authors_info'] = '\n'.join(authors_content).strip()
                            collecting_authors = False
                            current_content.append(line)
                    else:
                        authors_content.append(line)
                else:
                    current_content.append(line)

        if current_section:
            saved_titles = {s.get('title') for s in result['sections']}
            if current_section.title not in saved_titles:
                if in_references:
                    current_section.content = self.parse_references('\n'.join(current_content))
                else:
                    current_section.content = self.parse_content(current_content)
                result['sections'].append(vars(current_section))

        if structure and structure.get('flat_structure'):
            result['sections'] = self.remove_empty_sections(result['sections'])
        else:
            result['sections'] = self.build_hierarchy(result['sections'])
            result['sections'] = self.remove_empty_sections(result['sections'])

        return result

    def process(self, markdown_path: str, output_path: str) -> Path:
        try:
            markdown_path = Path(markdown_path)
            output_path = Path(output_path)
            self.logger.info(f"開始解析Markdown文件: {markdown_path}")
            content = markdown_path.read_text(encoding='utf-8')
            import json as json_module
            sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
            structure = {}
            if sidecar_path.exists():
                structure = json_module.loads(sidecar_path.read_text(encoding='utf-8'))
                self.logger.info(f"讀取文件結構: {structure.get('document_type')}")
            result = self.parse(content, structure=structure)
            self.logger.info(f"保存解析結果到: {output_path}")
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            return output_path
        except Exception as e:
            self.logger.error(f"Markdown處理失敗: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    processor = MarkdownProcessor()
    try:
        json_path = processor.process("input.md", "output.json")
    except Exception as e:
        logging.error(f"處理失敗：{e}")
