import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class Section:
    title: str            # 完整标题（包含编号和文本）
    number: str           # 章节编号（如 "1.2.3"）
    level: int           # 层级深度（根据编号中的点数确定）
    content: List[str]   # 章节内容，每个段落作为列表的一个元素
    raw_title: str       # 不含编号的标题文本
    type: Optional[str] = None   # 章节类型,如 'abstract', 'references'
    heading_level: int = 1       # Markdown # 的數量

class MarkdownProcessor:
    """Markdown处理器：将Markdown解析为结构化JSON"""

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
        
        self.potential_title_pattern = re.compile(r'^(?!#)(\d+(?:\.\d+)*)\s+([A-Z][A-Z\s\d:]+(?:\s*[A-Z][A-Za-z\s\d:]+)*)')

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
        self.logger.debug("初始化Markdown处理器完成")
        
    def parse_section_number(self, title: str) -> tuple[str, str, int]:
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
        references = [line.strip() for line in content.split('\n') if line.strip()]
        return references

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
            content_empty = not section.get('content', [])
            children_empty = not section.get('children', [])
            references_empty = not section.get('references', [])
            if not (content_empty and children_empty and references_empty):
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

    def check_section_continuity(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    def build_hierarchy(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """用 heading_level 建立父子關係"""
        if not sections:
            return []
        
        hierarchy = []
        stack = []  # 存放 (heading_level, section_dict)
        
        for section in sections:
            section['children'] = []
            h = section.get('heading_level', 1)
            
            # 彈出所有 heading_level >= 當前的節點
            while stack and stack[-1][0] >= h:
                stack.pop()
            
            if stack:
                # 當前節點是棧頂節點的子節點
                stack[-1][1]['children'].append(section)
            else:
                # 頂層節點
                hierarchy.append(section)
            
            stack.append((h, section))
        
        return hierarchy

    def parse(self, content: str, structure: dict = None) -> Dict[str, Any]:
        lines = content.split('\n')
        result = {
            'title': '',
            'authors_info': '',
            'sections': []
        }
        
        # 如果有 structure，預處理：負面表列邏輯
        # 只有 authors/publication_info/toc/other/title 不翻譯（歸入 authors_info）
        # 其他所有類型都插入標題，確保會被翻譯
        if structure:
            SKIP_TYPES = {'authors', 'publication_info', 'toc'}
            TYPE_TO_HEADING = {
                'abstract':   '## Abstract',
                'intro_text': '## Introduction',
                'preface':    '## Preface',
            }

            lines_to_insert = []
            seen_types = set()

            for block in structure.get('structure', []):
                btype = block.get('type')
                if btype in SKIP_TYPES:
                    continue
                if btype in TYPE_TO_HEADING and btype not in seen_types:
                    lines_to_insert.append((block['start'], TYPE_TO_HEADING[btype]))
                    seen_types.add(btype)

            # 把 SKIP_TYPES 的行清空（不讓它們進入 authors_info）
            skip_line_indices = set()
            for block in structure.get('structure', []):
                if block.get('type') in SKIP_TYPES:
                    for i in range(block['start'], block['end'] + 1):
                        skip_line_indices.add(i)
            for i in skip_line_indices:
                if i < len(lines):
                    lines[i] = ''

            # 從後往前插入標題，避免行號偏移
            for insert_line, heading in sorted(lines_to_insert, key=lambda x: -x[0]):
                lines.insert(insert_line, heading)

            content = '\n'.join(lines)
            lines = content.split('\n')

        current_section = None
        current_content = []
        collecting_authors = False
        in_references = False
        authors_content = []
        has_started = False
        
        for line in lines:
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
                    title="REFERENCES",
                    number="",
                    level=1,
                    content=[],
                    raw_title="REFERENCES",
                    type='references'
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
                    authors_text = '\n'.join(authors_content).strip()
                    authors_lines = authors_text.split('\n')
                    image_lines = []
                    clean_authors_lines = []
                    for line in authors_lines:
                        if self.image_pattern.match(line) or self.figure_table_pattern.match(line):
                            image_lines.append(line)
                        else:
                            clean_authors_lines.append(line)
                    result['authors_info'] = '\n'.join(clean_authors_lines).strip()
                    collecting_authors = False
                    number, raw_title, level = self.parse_section_number(title_text)
                    current_section = Section(
                        title=title_text,
                        number=number,
                        level=level,
                        content=[],
                        raw_title=raw_title,
                        type='abstract',
                        heading_level=heading_level
                    )
                    current_content = []
                    current_content.extend(image_lines)
                    continue
                
                if collecting_authors:
                    # 如果遇到 ## 或更深的標題，強制結束作者收集
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
                        if self.abstract_pattern.match(current_section.title):
                            parsed_content = []
                            other_lines = []
                            for line in current_content:
                                if self.image_pattern.match(line) or self.figure_table_pattern.match(line):
                                    parsed_content.append(line)
                                else:
                                    other_lines.append(line)
                            if other_lines:
                                parsed_content.extend(self.parse_content(other_lines))
                            current_section.content = parsed_content
                        else:
                            current_section.content = self.parse_content(current_content)
                        result['sections'].append(vars(current_section))
                
                number, raw_title, level = self.parse_section_number(title_text)
                current_section = Section(
                    title=title_text,
                    number=number,
                    level=level,
                    content=[],
                    raw_title=raw_title,
                    heading_level=heading_level
                )
                current_content = []
                
                if self.reference_pattern.match(line):
                    in_references = True
                    current_section.type = 'references'
                    
            else:
                if collecting_authors:
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
        
        result['sections'] = self.build_hierarchy(result['sections'])
        result['sections'] = self.remove_empty_sections(result['sections'])
        
        return result

    def process(self, markdown_path: str, output_path: str) -> Path:
        try:
            markdown_path = Path(markdown_path)
            output_path = Path(output_path)
            self.logger.info(f"开始解析Markdown文件: {markdown_path}")
            content = markdown_path.read_text(encoding='utf-8')

            # 讀取結構分析 sidecar（如果存在）
            import json as json_module
            sidecar_path = markdown_path.parent / f'{markdown_path.stem}_doc_structure.json'
            structure = {}
            if sidecar_path.exists():
                structure = json_module.loads(sidecar_path.read_text(encoding='utf-8'))
                self.logger.info(f"讀取文件結構: {structure.get('document_type')}")

            result = self.parse(content, structure=structure)
            self.logger.info(f"保存解析结果到: {output_path}")
            output_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            return output_path
        except Exception as e:
            self.logger.error(f"Markdown处理失败: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    processor = MarkdownProcessor()
    try:
        json_path = processor.process("input.md", "output.json")
    except Exception as e:
        print(f"处理失败：{e}")