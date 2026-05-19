"""PDF metadata 抽取與校正模組（Phase 4.2）。

Phase 4 核心基建：**先建設、不接線**。
- 本模組不被 pipeline_core / web_server / paper_manager import。
- 不寫 _metadata.json 到 disk（純函式介面，呼叫端決定如何持久化）。
- 完成後系統行為 100% 不變。

職責（Phase 4.2 範圍）：
1. 抽 PDF 嵌入式 metadata（fitz）。
2. 定義 _metadata.json 結構（schema v2：每欄位 value/source/confidence/alternates）。
3. 提供未來 Stage A/B 可呼叫的標準介面（建空結構、填 PDF metadata、第一頁文字/圖）。

信任度設計（見 Phase 4.1 設計分析）：
LLM 看第一頁 > PDF metadata > MinerU。本模組只負責 PDF metadata 與原始首頁素材，
不做 LLM 呼叫、不做仲裁。所有函式 **絕不 raise**，失敗回 None / []。
"""
from __future__ import annotations

import re
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# Schema 版本；未來改結構需 bump（JSON 欄位免 migration 的配套）
SCHEMA_VERSION = 2

# 11 個 metadata 欄位（title/translated_title 之外另有 9 個）
_LIST_FIELDS = {"authors", "keywords"}
_ALL_FIELDS = [
    "title", "translated_title", "authors", "publication_date", "abstract",
    "journal_or_conference", "doi", "keywords", "publisher",
    "organization", "version",
]

# fitz title 雜訊樣式（Word/匯出器留下的非語意 title）
_TITLE_NOISE = re.compile(
    r"(\.docx?|\.pdf|microsoft\s+word|untitled|^document\d*$|powerpoint|^slide\s)",
    re.IGNORECASE,
)


# ─────────────────────── 結構 ───────────────────────

def _empty_field(is_list: bool = False) -> dict:
    return {
        "value": [] if is_list else None,
        "source": None,        # pdf_metadata / llm_page1 / mineru / both_agree / manual
        "confidence": None,    # high / medium / low
        "alternates": {},      # 被淘汰候選，debug 用
    }


def create_empty_metadata() -> dict:
    """建立空的 metadata 結構（schema v2）。所有欄位 None/[]，_sources 全空。"""
    meta = {
        "_schema_version": SCHEMA_VERSION,
        "_stage_b_ran": False,
    }
    for f in _ALL_FIELDS:
        meta[f] = _empty_field(is_list=(f in _LIST_FIELDS))
    return meta


# ─────────────────────── 解析輔助 ───────────────────────

def date_to_iso(date_string: Optional[str]) -> Optional[str]:
    """PDF date（如 ``D:20251009144037-07'00'``）→ ISO ``YYYY-MM-DD``。

    也容許純數字串或已是 ISO 的字串。無法解析回 None（絕不 raise）。
    """
    if not date_string or not isinstance(date_string, str):
        return None
    s = date_string.strip()
    try:
        # 形如 D:YYYYMMDD...
        m = re.match(r"^D:?(\d{4})(\d{2})(\d{2})", s)
        if m:
            y, mo, d = m.groups()
        else:
            # 已是 ISO 或 YYYY-MM-DD / YYYY/MM/DD
            m2 = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
            if m2:
                y, mo, d = m2.groups()
            else:
                m3 = re.match(r"^(\d{4})(\d{2})(\d{2})$", s)
                if not m3:
                    return None
                y, mo, d = m3.groups()
        mo_i, d_i = int(mo), int(d)
        if not (1 <= mo_i <= 12 and 1 <= d_i <= 31):
            return None
        return f"{y}-{mo_i:02d}-{d_i:02d}"
    except Exception:
        return None


def parse_authors(author_str: Optional[str]) -> list:
    """PDF author 字串 → list[str]。

    支援以 ``,``、``;``、`` and ``、``&``、``、`` 分隔。去空白、去重（保序）。
    None/空 → []。絕不 raise。
    """
    if not author_str or not isinstance(author_str, str):
        return []
    try:
        parts = re.split(r"\s+and\s+|[,;&、]|\s{2,}", author_str)
        out, seen = [], set()
        for p in parts:
            name = p.strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                out.append(name)
        return out
    except Exception:
        return []


def _clean_title(raw: Optional[str]) -> Optional[str]:
    if not raw or not isinstance(raw, str):
        return None
    t = raw.strip()
    if not t or _TITLE_NOISE.search(t):
        return None
    return t


# ─────────────────────── PDF 抽取 ───────────────────────

def extract_pdf_metadata(pdf_path) -> dict:
    """從 PDF 嵌入式 metadata（fitz）抽取。**絕不 raise**，失敗欄位 None/[]。

    Returns dict:
        title, authors(list), publication_date(YYYY-MM-DD|None),
        creation_date(YYYY-MM-DD|None；製檔日，未必=發表日),
        subject, keywords(list), organization, creator, producer
    """
    result = {
        "title": None,
        "authors": [],
        "publication_date": None,
        "creation_date": None,
        "subject": None,
        "keywords": [],
        "organization": None,
        "creator": None,
        "producer": None,
    }
    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        md = doc.metadata or {}
        result["title"] = _clean_title(md.get("title"))
        result["authors"] = parse_authors(md.get("author"))
        result["subject"] = (md.get("subject") or "").strip() or None
        kw = (md.get("keywords") or "").strip()
        result["keywords"] = (
            [k.strip() for k in re.split(r"[,;、]", kw) if k.strip()] if kw else []
        )
        result["creator"] = (md.get("creator") or "").strip() or None
        result["producer"] = (md.get("producer") or "").strip() or None
        cdate = date_to_iso(md.get("creationDate"))
        result["creation_date"] = cdate
        # PDF metadata 無「發表日」概念；creationDate 僅作低信任候選
        result["publication_date"] = cdate
        # organization：PDF metadata 無此欄；保留 None，交由後續 LLM 階段判斷
    except Exception as e:
        logger.warning(f"extract_pdf_metadata 失敗（soft）: {pdf_path} - {e}")
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
    return result


def get_first_page_text(pdf_path) -> Optional[str]:
    """抽 PDF 第一頁原始文字（保留換行）。無文字/失敗回 None。絕不 raise。"""
    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        if doc.page_count < 1:
            return None
        text = doc[0].get_text() or ""
        text = text.strip()
        return text or None
    except Exception as e:
        logger.warning(f"get_first_page_text 失敗（soft）: {pdf_path} - {e}")
        return None
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def get_first_page_render(pdf_path, dpi: int = 150) -> Optional[bytes]:
    """抽 PDF 第一頁渲染圖（PNG bytes，給 Vision LLM）。失敗回 None。絕不 raise。"""
    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        if doc.page_count < 1:
            return None
        scale = dpi / 72.0
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale))
        return pix.tobytes("png")
    except Exception as e:
        logger.warning(f"get_first_page_render 失敗（soft）: {pdf_path} - {e}")
        return None
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


# ─────────────────────── 填入結構 ───────────────────────

def _set_field(meta: dict, field: str, value, source: str, confidence: str):
    """先到先得：已有非空 value 則不覆寫，但一律記入 alternates。"""
    f = meta[field]
    is_list = field in _LIST_FIELDS
    has_value = bool(f["value"]) if is_list else (f["value"] is not None)
    incoming_nonempty = bool(value) if is_list else (value is not None)
    if incoming_nonempty:
        f["alternates"][source] = value
    if not has_value and incoming_nonempty:
        f["value"] = value
        f["source"] = source
        f["confidence"] = confidence


def fill_from_pdf_metadata(metadata: dict, pdf_meta: dict) -> dict:
    """把 fitz PDF metadata 填進 metadata 結構（source='pdf_metadata'）。

    信任度（依 Phase 4.1）：author=high（PDF metadata 通常正確）、
    title=medium（常被 Word 匯出污染）、publication_date=medium（製檔日≠發表日）、
    keywords=medium。不覆寫已有 value（先到先得），但寫入 alternates 供後續仲裁。
    """
    try:
        _set_field(metadata, "title", pdf_meta.get("title"),
                   "pdf_metadata", "medium")
        _set_field(metadata, "authors", pdf_meta.get("authors") or [],
                   "pdf_metadata", "high")
        _set_field(metadata, "publication_date",
                   pdf_meta.get("publication_date"),
                   "pdf_metadata", "medium")
        _set_field(metadata, "keywords", pdf_meta.get("keywords") or [],
                   "pdf_metadata", "medium")
        _set_field(metadata, "organization", pdf_meta.get("organization"),
                   "pdf_metadata", "low")
    except Exception as e:
        logger.warning(f"fill_from_pdf_metadata 失敗（soft）: {e}")
    return metadata
