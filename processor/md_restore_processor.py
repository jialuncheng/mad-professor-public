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
    # 型別容錯：LLM 偶爾把 title / candidate_name 回成 list（多個候選名）
    m_title = _coerce_to_str((m.get('title') or {}).get('value'))
    m_trans = _coerce_to_str((m.get('translated_title') or {}).get('value'))
    m_source = ((m.get('title') or {}).get('source') or '')
    m_cand = _coerce_to_str((m.get('candidate_name') or {}).get('value'))

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


# ───────────────── Phase 4.7d Commit 2：全欄位融合（v2 §3.2-§3.4 + §4.2-§4.5） ─────────────────

# Authors 黑名單（v2 §3.2）：PDF 預設值 + label 文字 + PDF 工具名
AUTHORS_BLACKLIST_NORM = {
    "microsoft office user", "office user", "office",
    "administrator", "admin", "user", "guest",
    "windows user", "mac user", "default user",
    "author", "authors", "作者", "by",
    "anonymous", "unknown",
    "adobe acrobat", "microsoft word", "powerpoint",
}

# Date 黑名單（v2 §3.3）
DATE_BLACKLIST = {"1970-01-01", "0000-00-00", "1900-01-01"}
DATE_FUTURE_THRESHOLD = "2050-12-31"

# venue / journal / publisher / organization 共用 label 黑名單（v2 §3.4）
META_LABEL_BLACKLIST = {"n/a", "unknown", "tbd", "none", "null", "-"}

# DOI 格式（v2 §4.5）
DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:a-z0-9]+$", re.IGNORECASE)

# Keywords 自身 label（v2 §4.5）
KEYWORDS_STOPWORDS = {"keywords", "關鍵字", "keyword", "key words"}

# Candidate name label（v2 §3.4 / 4.5）
CANDIDATE_LABEL_BLACKLIST = {"resume", "履歷", "cv", "curriculum vitae", "個人簡歷"}


def _coerce_to_str(v) -> str:
    """metadata value 型別容錯：str/list/None/其他 → str。

    LLM 偶爾對某些欄位（如 organization）回 list（多機構名）即使 prompt
    要求 string；schema `_LIST_FIELDS` 未列入該欄、後段 `.strip()` 會炸
    AttributeError。本 helper 在 md_restore 層消化型別 drift（不動 prompt
    避免引入新型別不確定）。

    - str: strip 後回傳
    - list: 取第一個非空 str 元素 strip 後回傳；無 → 空字串
    - 其他（None / int / dict / ...）: 空字串
    """
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, list):
        for item in v:
            if isinstance(item, str) and item.strip():
                return item.strip()
        return ''
    return ''


def _author_in_blacklist(name: str) -> bool:
    if not name:
        return False
    return name.strip().casefold() in AUTHORS_BLACKLIST_NORM


def _resolve_authors(
    data: dict,
    metadata: Optional[dict],
    doc_type: Optional[str],
) -> tuple:
    """v2 §4.2 authors 決策樹。

    Returns:
        (authors_list, keep_raw_info, conf_log)
        - authors_list: 給 header 用的結構化作者陣列（可空）
        - keep_raw_info: 是否保留原 raw authors_info 段（True=保留、False=已由
          header 取代不再寫）
        - conf_log: 日誌字串
    """
    # resume 不顯示 authors（candidate_name 已是 title）
    if doc_type == 'resume':
        return ([], False, 'resume skip')

    raw_authors_info = (data.get('authors_info') or '').strip()
    m = metadata or {}
    m_authors = (m.get('authors') or {}).get('value') or []
    m_source = (m.get('authors') or {}).get('source') or ''

    if m_authors:
        all_blacklisted = all(_author_in_blacklist(str(a)) for a in m_authors)
        if all_blacklisted:
            # 整組丟、用 raw_authors_info（如有）
            return ([], bool(raw_authors_info),
                    'all-blacklisted, drop M, keep raw_info')
        cleaned = [a for a in m_authors if not _author_in_blacklist(str(a))]
        if cleaned:
            return (cleaned, False,
                    f'{m_source or "metadata"} cleaned ({len(m_authors)}->{len(cleaned)})')

    # M 空、raw_authors_info 有 → 保留 raw section
    if raw_authors_info:
        return ([], True, 'no M, keep raw_authors_info')

    return ([], False, 'no authors')


def _date_in_blacklist(date_str: str) -> bool:
    if not date_str:
        return True
    d = date_str.strip()
    if d in DATE_BLACKLIST:
        return True
    if d > DATE_FUTURE_THRESHOLD:
        return True
    return False


def _resolve_date(metadata: Optional[dict]) -> tuple:
    """v2 §4.3：pdf_metadata 來源永遠丟（creation_date ≠ 發表日）。
    型別容錯：LLM 偶爾回 list → 取第一個非空字串。"""
    m = metadata or {}
    m_date = _coerce_to_str((m.get('publication_date') or {}).get('value'))
    m_source = (m.get('publication_date') or {}).get('source') or ''

    if not m_date:
        return ('', 'no date')
    if m_source == 'pdf_metadata':
        return ('', 'pdf_metadata is creation_date, drop')
    if _date_in_blacklist(m_date):
        return ('', f'blacklisted: {m_date}')
    return (m_date, m_source or 'unknown')


def _resolve_venue(metadata: Optional[dict]) -> tuple:
    """v2 §4.5：journal_or_conference > publisher > organization 取第一個非空。
    pdf_metadata 來源此 3 欄一律不採。
    型別容錯：LLM 偶爾回 list（如 organization）→ 取第一個非空字串元素。"""
    m = metadata or {}
    for field in ('journal_or_conference', 'publisher', 'organization'):
        raw_v = (m.get(field) or {}).get('value')
        v = _coerce_to_str(raw_v)
        s = (m.get(field) or {}).get('source') or ''
        if not v:
            continue
        if s == 'pdf_metadata':
            continue
        if v.casefold() in META_LABEL_BLACKLIST:
            continue
        return (v, field, s)
    return ('', '', '')


def _resolve_doi(metadata: Optional[dict]) -> str:
    m = metadata or {}
    # 型別容錯：偶有 LLM 把 DOI 回成 list
    v = _coerce_to_str((m.get('doi') or {}).get('value'))
    if not v:
        return ''
    return v if DOI_REGEX.match(v) else ''


def _resolve_keywords(metadata: Optional[dict]) -> list:
    m = metadata or {}
    kws = (m.get('keywords') or {}).get('value') or []
    if not kws:
        return []
    return [k for k in kws
            if str(k).strip()
            and str(k).strip().casefold() not in KEYWORDS_STOPWORDS]


def _resolve_candidate_extras(metadata: Optional[dict],
                              doc_type: Optional[str]) -> dict:
    """resume 專用：取 organization 暫代 current_role / latest_employer。
    型別容錯：LLM 偶爾回 list → 取第一個非空字串。"""
    if doc_type != 'resume':
        return {}
    m = metadata or {}
    org = _coerce_to_str((m.get('organization') or {}).get('value'))
    if org and org.casefold() not in CANDIDATE_LABEL_BLACKLIST:
        return {'organization': org}
    return {}


# ───────────────── Phase 4.7d Commit 3：abstract 雙語注入（v2 §4.4） ─────────────────

# 哪些 doc_type 無 abstract（與 translate_processor.doc_type_no_abstract +
# resume 對齊；翻譯階段已 skip、md_restore 也跳過）
# === doc_type-registry ===
# 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
ABSTRACT_NO_DOC_TYPES = {'news', 'web', 'slides', 'resume'}


def _resolve_abstract(data: dict, doc_type: Optional[str]) -> tuple:
    """v2 §4.4：從 JSON tree 找 sections[type=='abstract'].content[0]。

    Returns:
        (abstract_en, abstract_zh, conf_log)
        - 英文取 content；中文取 translated_content；中文空則 fallback 英文
        - doc_type ∈ ABSTRACT_NO_DOC_TYPES 一律 ('', '', ...)
    """
    if doc_type in ABSTRACT_NO_DOC_TYPES:
        return ('', '', f'{doc_type} no abstract')

    sections = data.get('sections') or []
    for sec in sections:
        if sec.get('type') != 'abstract':
            continue
        contents = sec.get('content') or []
        if not contents:
            continue
        # 取第一個 dict 型 content item
        item = next((c for c in contents if isinstance(c, dict)
                     and c.get('type') == 'text'), None)
        if item is None:
            # 沒 text item 也試取第一個 dict
            item = contents[0] if isinstance(contents[0], dict) else {}
        ab_en = (item.get('content') or '').strip()
        ab_zh = (item.get('translated_content') or '').strip()
        if ab_en or ab_zh:
            return (ab_en, ab_zh or ab_en, 'found in sections')
    return ('', '', 'no abstract section')


# ───────────────── doc_type-specific header templates（v2 §B-5） ─────────────────
# === doc_type-registry ===
# 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md

def _render_header_en(
    title: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_en.md 的 header（# title + meta block + abstract）。缺項靜默省略。"""
    lines = [f"# {title}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **Organization**: {org}")
        if domain:
            lines.append(f"> **Domain**: {domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **Authors**: {', '.join(str(a) for a in authors_list)}")
    if date:
        meta_bits.append(f"> **Date**: {date}")
    if venue:
        meta_bits.append(f"> **Venue**: {venue}")
    if doi:
        meta_bits.append(f"> **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")

    if meta_bits:
        lines.extend(meta_bits)
        lines.append("")

    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)


def _render_header_zh(
    title_zh: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_zh.md 的 header（中文 label）。缺項靜默省略。"""
    lines = [f"# {title_zh}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **機構**：{org}")
        if domain:
            lines.append(f"> **領域**：{domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **作者**：{'、'.join(str(a) for a in authors_list)}")
    if date:
        meta_bits.append(f"> **日期**：{date}")
    if venue:
        meta_bits.append(f"> **出處**：{venue}")
    if doi:
        meta_bits.append(f"> **DOI**：{doi}")
    if keywords:
        meta_bits.append(f"> **關鍵字**：{'、'.join(keywords)}")

    if meta_bits:
        lines.extend(meta_bits)
        lines.append("")

    if abstract:
        lines.append("## 摘要")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)


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
            
            # Phase 4.7d Commit 1：title 三軸融合（v2 §4.1）
            title_en, title_zh, conf_log = _resolve_title(
                data, metadata, doc_type, domain, original_filename, paper_uuid
            )
            self.logger.info(f"[md_restore] 三軸融合 title: {conf_log}")
            self.logger.info(
                f"  raw_en={data.get('title')!r} -> final_en={title_en!r}"
            )
            self.logger.info(
                f"  raw_zh={data.get('translated_title')!r} -> final_zh={title_zh!r}"
            )

            # Phase 4.7d Commit 2：全欄位融合 + doc_type-specific header（v2 §4.2-§4.5）
            dt = doc_type or 'academic'
            authors_list, keep_raw_info, auth_log = _resolve_authors(
                data, metadata, doc_type
            )
            date_val, date_log = _resolve_date(metadata)
            venue_val, venue_field, venue_src = _resolve_venue(metadata)
            doi_val = _resolve_doi(metadata)
            keywords_val = _resolve_keywords(metadata)
            candidate_extras = _resolve_candidate_extras(metadata, doc_type)
            # Phase 4.7d Commit 3：abstract 雙語注入（v2 §4.4）
            abstract_en, abstract_zh, ab_log = _resolve_abstract(data, doc_type)

            self.logger.info(
                f"[md_restore] authors: {auth_log} (n={len(authors_list)})"
            )
            self.logger.info(f"[md_restore] date: {date_log}")
            if venue_val:
                self.logger.info(
                    f"[md_restore] venue: {venue_val!r} ({venue_field}, {venue_src})"
                )
            if doi_val:
                self.logger.info(f"[md_restore] doi: {doi_val!r}")
            if keywords_val:
                self.logger.info(f"[md_restore] keywords: n={len(keywords_val)}")
            self.logger.info(f"[md_restore] abstract: {ab_log}")

            header_en = _render_header_en(
                title_en, dt, authors_list, date_val, venue_val, doi_val,
                keywords_val, candidate_extras, domain or '',
                abstract=abstract_en,
            )
            header_zh = _render_header_zh(
                title_zh, dt, authors_list, date_val, venue_val, doi_val,
                keywords_val, candidate_extras, domain or '',
                abstract=abstract_zh,
            )
            self._write_to_md(output_path_en, header_en)
            self._write_to_md(output_path_zh, header_zh)
            # Commit 3：abstract 已寫進 header → 跳過原 sections 內 abstract section 避免重複
            self._abstract_consumed = bool(abstract_en or abstract_zh)

            # 處理 raw authors_info：若 metadata 已給結構化 authors 則丟、
            # 否則保留（既有 _clean_authors_info 處理上標數字 / table 等）
            if keep_raw_info and 'authors_info' in data:
                authors = self._clean_authors_info(data['authors_info'])
                if authors:
                    self._write_to_md(output_path_en, authors)
                    self._write_to_md(output_path_zh, authors)
            
            # 处理各个章节（Commit 3：abstract section 已寫進 header → 跳過）
            for section in data['sections']:
                if (getattr(self, '_abstract_consumed', False)
                        and section.get('type') == 'abstract'):
                    self.logger.info(
                        "[md_restore] 跳過原 sections abstract（已注入 header）"
                    )
                    continue
                self._process_section(section, output_path_en, output_path_zh, level=2, vision_captions=vision_captions)
            
            self.logger.info(f"恢复完成，结果已保存到: {output_path_en} 和 {output_path_zh}")
            return output_path_en, output_path_zh
        except Exception as e:
            self.logger.error(f"JSON处理失败: {str(e)}", exc_info=True)
            raise