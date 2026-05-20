import json
import logging
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Optional
from utils.text_utils import load_caption_map, CONTROL_CHAR_PATTERN

logger = logging.getLogger(__name__)

# ───────────────── Phase 4.7d Commit 1：title 三軸融合（v2 §3.1 §4.1 §5 §6） ─────────────────
# 黑名單（中英 + PDF 匯出器預設值 + 履歷 label）
TITLE_BLACKLIST_EXACT = {
    # 章節 label
    "contents", "table of contents", "目錄", "目次",
    "abstract", "摘要", "summary", "executive summary",
    "introduction", "前言", "緒論", "intro",
    "references", "参考文献", "參考文獻", "bibliography",
    "acknowledgements", "acknowledgments", "致謝",
    "appendix", "附錄",
    "preface", "序",
    # PDF 匯出器預設值
    "untitled", "untitled document", "untitled1",
    "document", "document1", "document2",
    "未命名", "未命名文件",
    "powerpoint presentation", "slide 1", "slide1",
    "presentation",
    # 履歷 label
    "resume", "cv", "curriculum vitae", "履歷", "個人簡歷",
}
TITLE_BLACKLIST_PATTERN = [
    r"^第\s*\d+\s*頁$",
    r"^page\s*\d+$",
    r"^chapter\s*\d+$",
    r"^第\s*\d+\s*章$",
    r"^slide\s*\d+$",
    r"^section\s*\d+$",
    r"^\d+$",
    r"^[\d.]+$",
]
# 中文 domain token 排除字
_DOM_STOPS_CN = {"的", "與", "和", "之", "對", "在", "及", "或"}


def _title_in_blacklist(title: str) -> bool:
    """v2 §3.1：title 是否為已知雜訊（章節 label / 頁碼 / 預設值）。"""
    if not title:
        return False
    t = title.strip().casefold()
    if t in TITLE_BLACKLIST_EXACT:
        return True
    for pat in TITLE_BLACKLIST_PATTERN:
        if re.match(pat, t, re.IGNORECASE):
            return True
    return False


def _title_sim(a: str, b: str) -> bool:
    """v2 §6：相似度三段（相等 / 包含 / SequenceMatcher.ratio() >= 0.7）。"""
    if not a or not b:
        return False
    A = re.sub(r"\s+", "", a).casefold()
    B = re.sub(r"\s+", "", b).casefold()
    if A == B:
        return True
    if A in B or B in A:
        return True
    return SequenceMatcher(None, A, B).ratio() >= 0.7


def _tokenize_for_domain(s: str) -> set:
    """v2 §5.1：英文 token + 中文 2/3-gram；去停用詞。"""
    if not s:
        return set()
    tokens = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9-]*", s):
        tokens.add(m.group().casefold())
    for chunk in re.findall(r"[一-鿿]+", s):
        if len(chunk) >= 2:
            for i in range(len(chunk) - 1):
                tokens.add(chunk[i:i+2])
        if len(chunk) >= 3:
            for i in range(len(chunk) - 2):
                tokens.add(chunk[i:i+3])
    return tokens - _DOM_STOPS_CN


def _dom_match(value: str, domain: str) -> bool:
    """v2 §5.1：value 與 domain 的 token 交集 ≥ 1。domain 空則一律 False。"""
    if not domain:
        return False
    return len(_tokenize_for_domain(value) & _tokenize_for_domain(domain)) >= 1


def _resolve_title(
    data: dict,
    metadata: Optional[dict],
    doc_type: Optional[str],
    domain: str,
    original_filename: Optional[str] = None,
    paper_uuid: Optional[str] = None,
) -> tuple:
    """三軸融合 title（v2 §4.1 25 狀況決策樹）。

    Returns:
        (title_en, title_zh, confidence_log)
    """
    raw_en = (data.get('title') or '').strip()
    raw_zh = (data.get('translated_title') or raw_en).strip()

    m = metadata or {}
    m_title = ((m.get('title') or {}).get('value') or '').strip()
    m_trans = ((m.get('translated_title') or {}).get('value') or '').strip()
    m_source = ((m.get('title') or {}).get('source') or '')
    m_cand = ((m.get('candidate_name') or {}).get('value') or '').strip()

    def _fallback():
        fb = (original_filename or '').strip()
        if fb.lower().endswith('.pdf'):
            fb = fb[:-4].strip()
        fb = fb or (paper_uuid or 'untitled')
        return (fb, fb, 'low (fallback to filename/uuid)')

    # #1 resume 短路（doc_type-specific）
    if doc_type == 'resume' and m_cand:
        return (m_cand, m_cand, 'high (resume candidate_name)')

    # #2-#3 resume 無 candidate_name → raw 是姓名
    if doc_type == 'resume' and not m_cand:
        if raw_en and not _title_in_blacklist(raw_en):
            return (raw_en, raw_zh, 'medium (resume raw=name)')
        return _fallback()

    # #4 全空 fallback
    if not raw_en and not m_title:
        return _fallback()

    # #5-#6 raw 空、metadata 有
    if not raw_en and m_title:
        if _title_in_blacklist(m_title):
            return _fallback()
        return (m_title, m_trans or m_title, 'high (metadata only)')

    # #7-#8 raw 有、metadata 空
    if raw_en and not m_title:
        if _title_in_blacklist(raw_en):
            return _fallback()
        return (raw_en, raw_zh, 'medium (raw only)')

    # 兩者皆有
    raw_bl = _title_in_blacklist(raw_en)
    sim = _title_sim(raw_en, m_title)

    # #9-#10 both_agree（雙路確認）
    if m_source == 'both_agree':
        return (m_title, m_trans or m_title, 'high (both_agree)')

    # #20 manual（保留）
    if m_source == 'manual':
        return (m_title, m_trans or m_title, 'high (manual override)')

    # #11-#13 llm_page1
    if m_source == 'llm_page1':
        if sim:
            return (m_title, m_trans or m_title, 'high (llm sim raw)')
        if raw_bl:
            return (m_title, m_trans or m_title, 'high (raw blacklisted)')
        # #13 都合法但不同 → domain 仲裁（v2 §5.2）
        arb_R = _dom_match(raw_en, domain)
        arb_M = _dom_match(m_title, domain)
        if arb_M and arb_R:
            return (m_title, m_trans or m_title, 'medium (dom both match, take M)')
        if arb_M and not arb_R:
            return (m_title, m_trans or m_title, 'medium (dom match M)')
        if arb_R and not arb_M:
            return (raw_en, raw_zh, 'medium (dom match raw)')
        logger.warning(
            f"[md_restore] title 仲裁失敗 raw={raw_en!r} M={m_title!r} "
            f"domain={domain!r}，保守取 raw"
        )
        return (raw_en, raw_zh, 'low (dom both fail, take raw)')

    # #14-#16 pdf_metadata（baron 核心觀察：99% 是垃圾預設值，raw 勝）
    if m_source == 'pdf_metadata':
        if sim:
            return (m_title, m_trans or m_title, 'medium (pdf_meta sim raw)')
        if raw_bl:
            return (m_title, m_trans or m_title, 'medium (raw blacklisted, only pdf_meta)')
        return (raw_en, raw_zh, 'medium (pdf_meta untrustworthy, take raw)')

    # #17-#19 llm_page1 (conflict with pdf_metadata)
    if 'conflict' in m_source.lower():
        if sim:
            return (m_title, m_trans or m_title, 'medium (conflict sim raw)')
        if raw_bl:
            return (m_title, m_trans or m_title, 'medium (raw blacklisted)')
        arb_R = _dom_match(raw_en, domain)
        arb_M = _dom_match(m_title, domain)
        if arb_M:
            return (m_title, m_trans or m_title, 'medium (conflict, dom match M)')
        if arb_R:
            return (raw_en, raw_zh, 'medium (conflict, dom match raw)')
        logger.warning(
            f"[md_restore] conflict 仲裁失敗 raw={raw_en!r} M={m_title!r}，保守取 raw"
        )
        return (raw_en, raw_zh, 'low (conflict, take raw)')

    # #24 未知 source 兜底
    logger.warning(f"[md_restore] 未知 metadata.title.source={m_source!r}，保守取 raw")
    return (raw_en, raw_zh, 'low (unknown source)')


class RestoreProcessor:
    """恢复处理器, 将提供的json文件还原成中英两篇md文档"""

    def __init__(self):
        """初始化恢复处理器"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _read_file(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.warning(f"读取文件 {filepath} 失败: {str(e)}")
            return ""
    def _clean_authors_info(self, authors_info: str) -> str:
        """清理作者資訊，移除上標數字、多餘符號、HTML table 和目錄"""
        import re
        # 移除控制字元（MinerU 解析特殊字元時產生的亂碼，如 \x01）
        text = CONTROL_CHAR_PATTERN.sub('', authors_info)
        # 移除 HTML table
        text = re.sub(r'<table.*?</table>', '', text, flags=re.DOTALL)
        # 移除目錄標題行
        text = re.sub(r'(?m)^Contents\s*$', '', text)
        # 移除上標數字（字母後接數字，數字後是空白、逗號、分號或行尾）
        text = re.sub(r'(\w)\d+(?=\s|,|;|$)', r'\1', text)
        # 移除 \*
        text = re.sub(r'\\\*', '', text)
        # 移除多餘空格
        text = re.sub(r' +', ' ', text)
        # 清理每行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n\n'.join(lines)

    def _write_to_md(self, filepath, content):
        """将内容写入md文件"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content + "\n\n")
    
    def _process_section(self, section, output_path_en, output_path_zh, level=1, vision_captions=None):
        """处理文档的一个章节，递归处理子章节"""
        if vision_captions is None:
            vision_captions = {}
        # 处理标题（空標題不輸出）
        title_prefix = "#" * level
        
        if section['title'].strip():
            en_title = f"{title_prefix} {section['title']}"
            self._write_to_md(output_path_en, en_title)
            
            zh_title = f"{title_prefix} {section.get('translated_title') or section['title']}"
            self._write_to_md(output_path_zh, zh_title)
        
        # 处理正文内容
        if 'content' in section and section['content']:
            # 创建一个有序的结构来存储所有内容项及其位置信息
            ordered_items = []
            
            # 使用字典来存储按索引分组的文本块
            en_text_blocks = defaultdict(list)
            zh_text_blocks = defaultdict(list)
            
            # 第一遍遍历：收集所有内容项
            for item in section['content']:
                if isinstance(item, str):  # 如果直接是字符串（参考文献等）
                    ordered_items.append({
                        'type': 'ref',
                        'content': item,
                        'index': float('inf'),  # 参考文献通常放在最后
                        'part': 0
                    })
                elif isinstance(item, dict):
                    item_type = item.get('type')
                    index = item.get('index')
                    if index is None:
                        index = id(item)  # 用物件 id 確保每個 item 獨立
                    part = item.get('part', 0)
                    
                    if item_type == 'text':
                        # 处理文本内容：先收集起来，稍后合并相同index的
                        en_content = item.get('content', '')
                        zh_content = item.get('translated_content', en_content)
                        
                        # 按索引和部分存储内容
                        en_text_blocks[index].append((part, en_content))
                        zh_text_blocks[index].append((part, zh_content))
                        
                        # 记录这个文本块的位置信息，用于最终有序处理
                        ordered_items.append({
                            'type': 'text',
                            'index': index,
                            'part': part
                        })
                    
                    elif item_type == 'formula':
                        ordered_items.append({
                            'type': 'formula',
                            'content': item.get('content', ''),
                            'index': index,
                            'part': part
                        })
                    
                    elif item_type == 'figure':
                        ordered_items.append({
                            'type': 'figure',
                            'src': item.get('src', ''),
                            'alt': item.get('alt', ''),
                            'en_caption': item.get('caption', ''),
                            'zh_caption': item.get('translated_caption', item.get('caption', '')),
                            'index': index,
                            'part': part
                        })
                    
                    elif item_type == 'table':
                        ordered_items.append({
                            'type': 'table',
                            'content': item.get('content', ''),
                            'en_caption': item.get('caption', ''),
                            'zh_caption': item.get('translated_caption', item.get('caption', '')),
                            'index': index,
                            'part': part
                        })
            
            # 按索引和部分排序所有内容
            ordered_items.sort(key=lambda x: (x['index'], x['part']))
            
            # 处理已合并的文本块索引集合
            processed_text_indices = set()
            
            # 按照排序后的顺序写入内容
            for item in ordered_items:
                if item['type'] == 'text':
                    index = item['index']
                    
                    # 如果这个索引的文本块已经处理过，跳过
                    if index in processed_text_indices:
                        continue
                    
                    # 合并并写入相同索引的文本块
                    # 对相同index的文本块按part排序
                    en_parts = sorted(en_text_blocks[index], key=lambda x: x[0])
                    zh_parts = sorted(zh_text_blocks[index], key=lambda x: x[0])
                    
                    # 合并相同index的文本块
                    en_content = ' '.join([part[1] for part in en_parts])
                    zh_content = ' '.join([part[1] for part in zh_parts])
                    
                    # 写入合并后的内容
                    import re
                    en_content = re.sub(r'\n(?!\n)', '\n\n', en_content)
                    zh_content = re.sub(r'\n(?!\n)', '\n\n', zh_content)
                    if en_content.strip():
                        self._write_to_md(output_path_en, en_content)
                    if zh_content.strip():
                        self._write_to_md(output_path_zh, zh_content)

                    
                    # 标记这个索引已处理
                    processed_text_indices.add(index)
                
                elif item['type'] == 'formula':
                    # 处理公式（公式在中英文文档中保持一致）
                    if item.get('content', '').strip():
                        self._write_to_md(output_path_en, item['content'])
                        self._write_to_md(output_path_zh, item['content'])
                
                elif item['type'] == 'figure':
                    src = item['src']
                    src_filename = Path(src).name

                    # 英文图片说明
                    en_figure = f"![{item['alt']}]({src})"
                    if item['en_caption']:
                        en_figure += f"\n\n*{item['en_caption']}*"
                    elif src_filename in vision_captions:
                        en_figure += f"\n\n*{vision_captions[src_filename]}*"
                    self._write_to_md(output_path_en, en_figure)

                    # 中文图片说明
                    zh_figure = f"![{item['alt']}]({src})"
                    if item['zh_caption']:
                        zh_figure += f"\n\n*{item['zh_caption']}*"
                    elif src_filename in vision_captions:
                        zh_figure += f"\n\n*{vision_captions[src_filename]}*"
                    self._write_to_md(output_path_zh, zh_figure)
                
                elif item['type'] == 'table':
                    # 表格内容在中英文文档中保持一致
                    if item.get('content', '').strip():
                        self._write_to_md(output_path_en, item['content'])
                        self._write_to_md(output_path_zh, item['content'])
                    
                    # 处理表格标题
                    if item['en_caption']:
                        self._write_to_md(output_path_en, f"*{item['en_caption']}*")
                        
                        self._write_to_md(output_path_zh, f"*{item['zh_caption']}*")
                
                elif item['type'] == 'ref':
                    # 参考文献保持原样
                    if item.get('content', '').strip():
                        self._write_to_md(output_path_en, item['content'])
                        self._write_to_md(output_path_zh, item['content'])
        
        # 递归处理子章节
        if 'children' in section and section['children']:
            for child in section['children']:
                self._process_section(child, output_path_en, output_path_zh, level + 1, vision_captions)
    
    def process(self, input_path: str, output_path_en: str, output_path_zh: str,
                images_info_path: str = None,
                metadata: Optional[dict] = None,
                doc_type: Optional[str] = None,
                domain: str = '',
                original_filename: Optional[str] = None,
                paper_uuid: Optional[str] = None) -> tuple:
        """
        读取 input.json，恢复成中英文两篇md文档
        1. 中文用翻译部分；如果没有翻译则保留英文原文

        Phase 4.7d Commit 1：title 改走三軸融合（v2 §4.1 25 狀況決策樹）。
        新增 metadata/doc_type/domain/original_filename/paper_uuid 參數；
        皆有預設值，舊 caller 不傳則退回「只看 data['title']」舊行為。
        """
        try:
            input_path = Path(input_path)
            output_path_en = Path(output_path_en)
            output_path_zh = Path(output_path_zh)
            
            # 确保输出目录存在
            output_path_en.parent.mkdir(parents=True, exist_ok=True)
            output_path_zh.parent.mkdir(parents=True, exist_ok=True)
            
            # 清空输出文件
            open(output_path_en, 'w', encoding='utf-8').close()
            open(output_path_zh, 'w', encoding='utf-8').close()
            
            self.logger.info(f"开始处理JSON文件: {input_path}")

            # 載入 Vision caption（補充 MinerU 沒有的圖片說明）
            vision_captions = load_caption_map(images_info_path) if images_info_path else {}

            with input_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Phase 4.7d Commit 1：title 三軸融合（v2 §4.1）。舊 caller
            # 不傳 metadata/doc_type/domain 時 _resolve_title 退回「raw only」分支、
            # 行為與舊版等效。
            title_en, title_zh, conf_log = _resolve_title(
                data, metadata, doc_type, domain, original_filename, paper_uuid
            )
            self.logger.info(
                f"[md_restore] 三軸融合 title: {conf_log}"
            )
            self.logger.info(
                f"  raw_en={data.get('title')!r} -> final_en={title_en!r}"
            )
            self.logger.info(
                f"  raw_zh={data.get('translated_title')!r} -> final_zh={title_zh!r}"
            )
            self._write_to_md(output_path_en, f"# {title_en}")
            self._write_to_md(output_path_zh, f"# {title_zh}")
            
            # 处理作者信息
            if 'authors_info' in data:
                authors = self._clean_authors_info(data['authors_info'])
                if authors:
                    self._write_to_md(output_path_en, authors)
                    self._write_to_md(output_path_zh, authors)
            
            # 处理各个章节
            for section in data['sections']:
                self._process_section(section, output_path_en, output_path_zh, level=2, vision_captions=vision_captions)
            
            self.logger.info(f"恢复完成，结果已保存到: {output_path_en} 和 {output_path_zh}")
            return output_path_en, output_path_zh
        except Exception as e:
            self.logger.error(f"JSON处理失败: {str(e)}", exc_info=True)
            raise