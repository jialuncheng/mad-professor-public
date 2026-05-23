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
import json
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# Stage A 第二來源（LLM 看第一頁）prompt：Phase 4.7c step 3 起改為 doc_type
# 分支讀外部檔（prompt/processor/metadata_{doc_type}.txt），由
# _load_stage_a_prompt 載入。未知 doc_type 一律 fallback academic。
#
# === doc_type-registry ===
# 新增 doc_type 須同步新增 prompt/processor/metadata_{doc_type}.txt 或在
# _PROMPT_BY_DOC_TYPE 顯式映射到既有檔。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
_PROMPT_BY_DOC_TYPE = {
    "academic":  "prompt/processor/metadata_academic.txt",
    "resume":    "prompt/processor/metadata_resume.txt",
    "technical": "prompt/processor/metadata_technical.txt",
    # 以下 doc_type 暫共用 academic prompt（4.7c §C-5：暫不規劃）
    "book":      "prompt/processor/metadata_academic.txt",
    "news":      "prompt/processor/metadata_academic.txt",
    "slides":    "prompt/processor/metadata_academic.txt",
    "web":       "prompt/processor/metadata_academic.txt",
}
# 走 multi-page（讀頭 N 頁文字）的 doc_type；其他僅 page 1
_MULTI_PAGE_DOC_TYPES = {"technical"}
_MULTI_PAGE_N = 3

# Schema 版本；未來改結構需 bump（JSON 欄位免 migration 的配套）
SCHEMA_VERSION = 2

# metadata 欄位列舉。Phase 4.7c step 2 新增 candidate_name：對 resume 是主資料
# （履歷沒「title」概念，要的是候選人姓名）；對其他 doc_type 永遠為 None，
# 與其他欄位對稱結構 {value, source, confidence, alternates}，scalar 非 list。
_LIST_FIELDS = {"authors", "keywords"}
_ALL_FIELDS = [
    "title", "translated_title", "authors", "publication_date", "abstract",
    # RAG-1 Phase 2 P2-1：雙語摘要管道；由 pipeline_core._stage_translate
    # 完成後從 self.translate_processor.translated_abstract 寫入。對應前端
    # Phase 1 R1 子項 F 中文模式 abstract fallback 路徑（缺欄時 fallback 英文）。
    "translated_abstract",
    "journal_or_conference", "doi", "keywords", "publisher",
    "organization", "version", "candidate_name", "domain",
    # Phase 4.7d Commit 4-2：resume 專用（其他 doc_type 永遠 None / False）
    "source_platform", "is_third_party",
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
        "source": None,        # pdf_metadata / llm_page1 / markdown_extracted / both_agree / manual
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


# ─────────────────────── Stage A 第二來源：LLM 看第一頁 ───────────────────────

_LLM_FLAT_KEYS = [
    "title", "translated_title", "authors", "publication_date", "abstract",
    "journal_or_conference", "doi", "keywords", "publisher",
    "organization", "version", "candidate_name", "domain",
    "source_platform", "is_third_party",
]


def _coerce_llm_meta(raw: dict) -> dict:
    """把 LLM 回傳 dict 正規化為固定 flat 結構（缺鍵補 None/[]）。"""
    out = {}
    for k in _LLM_FLAT_KEYS:
        v = raw.get(k)
        if k in ("authors", "keywords"):
            if isinstance(v, list):
                out[k] = [str(x).strip() for x in v if str(x).strip()]
            elif isinstance(v, str) and v.strip():
                out[k] = [v.strip()]
            else:
                out[k] = []
        else:
            if isinstance(v, str):
                v = v.strip()
                out[k] = v or None
            elif v in (None, [], {}):
                out[k] = None
            else:
                out[k] = v
    pd = date_to_iso(out.get("publication_date")) if out.get("publication_date") else None
    out["publication_date"] = pd
    return out


def _load_stage_a_prompt(doc_type: Optional[str]) -> str:
    """依 doc_type 載入對應 prompt 檔；未知/None 一律 academic。soft fail：
    讀檔失敗回 academic 內建 fallback 訊息（仍能跑、信心度降但不 break）。"""
    rel = _PROMPT_BY_DOC_TYPE.get((doc_type or "").strip() or "academic",
                                  _PROMPT_BY_DOC_TYPE["academic"])
    try:
        from pathlib import Path as _P
        base = _P(__file__).resolve().parent.parent
        return (base / rel).read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"_load_stage_a_prompt 失敗（soft，用最簡 fallback）: {rel} - {e}")
        return ("從以下第一頁文字抽 title/translated_title/authors/"
                "publication_date 等欄位，回 JSON：\n---\n{page1_text}\n---")


def _get_multi_page_text(pdf_path, n: int = _MULTI_PAGE_N,
                        per_page_limit: int = 1500) -> Optional[str]:
    """抽 PDF 頭 n 頁原始文字，頁與頁之間以 `===== PAGE k =====` 分隔。
    每頁截至 per_page_limit 字元避免單頁炸 token。**絕不 raise**，全失敗回 None。"""
    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        if doc.page_count < 1:
            return None
        parts = []
        for i in range(min(n, doc.page_count)):
            try:
                t = (doc[i].get_text() or "").strip()
                if t:
                    parts.append(f"===== PAGE {i+1} =====\n{t[:per_page_limit]}")
            except Exception:
                continue
        if not parts:
            return None
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"_get_multi_page_text 失敗（soft）: {pdf_path} - {e}")
        return None
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def extract_metadata_from_first_page_llm(pdf_path, llm=None,
                                          doc_type: Optional[str] = None
                                          ) -> Optional[dict]:
    """用 LLM 看 PDF 第一頁（或頭 N 頁，依 doc_type）原始文字＋渲染圖抽 metadata。

    Returns flat dict（同 fitz 結構 + translated_title + candidate_name）；
    第一頁無文字 / LLM 失敗 / JSON 解析失敗 → None。**永遠 soft fail，不 raise**。

    doc_type：影響 prompt 選擇與是否多頁讀文字（Phase 4.7c step 3）。
    llm：可注入測試替身（需有 chat_with_image 或 chat）；None 時用
    config.LLMClient.get_instance()（延遲 import，避免模組載入即需金鑰）。
    """
    try:
        dt = (doc_type or "").strip() or "academic"
        if dt in _MULTI_PAGE_DOC_TYPES:
            text = _get_multi_page_text(pdf_path)
        else:
            text = get_first_page_text(pdf_path)
        if not text:
            return None
        text = text[:6000 if dt in _MULTI_PAGE_DOC_TYPES else 4000]
        img = get_first_page_render(pdf_path)
        prompt = _load_stage_a_prompt(dt).replace("{page1_text}", text)

        if llm is None:
            from llm.client import LLMClient  # 延遲 import
            import settings
            llm = LLMClient.get_instance()
            model = getattr(settings, "LLM_DOC_MODEL", None)
        else:
            model = None

        messages = [{"role": "user", "content": prompt}]
        if img is not None and hasattr(llm, "chat_with_image"):
            resp = llm.chat_with_image(
                messages=messages, image_data=img,
                mime_type="image/png", model=model,
            )
        else:
            resp = llm.chat(messages, stream=False, model=model)

        if not resp:
            return None
        from utils.text_utils import strip_json_fence
        data = json.loads(strip_json_fence(resp))
        if not isinstance(data, dict):
            return None
        return _coerce_llm_meta(data)
    except Exception as e:
        logger.warning(f"extract_metadata_from_first_page_llm 失敗（soft）: "
                        f"{pdf_path} - {e}")
        return None


def fill_from_llm_page1(metadata: dict, llm_meta: Optional[dict]) -> dict:
    """把 LLM 第一頁結果填進結構，source='llm_page1'，信任度 high。

    與 fill_from_pdf_metadata 對稱（先到先得 + 一律寫 alternates）。實際
    fitz↔LLM 的取捨/衝突由 merge_stage_a 處理；此函式僅負責「單來源填入」，
    使「empty + fill_pdf」與「empty + fill_llm」兩結構可獨立建立後再 merge。
    """
    if not llm_meta:
        return metadata
    try:
        mapping = {
            "title": "title",
            "translated_title": "translated_title",
            "authors": "authors",
            "publication_date": "publication_date",
            "abstract": "abstract",
            "journal_or_conference": "journal_or_conference",
            "doi": "doi",
            "keywords": "keywords",
            "publisher": "publisher",
            "organization": "organization",
            "version": "version",
            "candidate_name": "candidate_name",
            "domain": "domain",
            "source_platform": "source_platform",
            "is_third_party": "is_third_party",
        }
        for fld in mapping:
            _set_field(metadata, fld, llm_meta.get(fld), "llm_page1", "high")
    except Exception as e:
        logger.warning(f"fill_from_llm_page1 失敗（soft）: {e}")
    return metadata


# ─────────────────────── Stage A 即時比對（雙來源先決）───────────────────────

def _norm(v):
    if isinstance(v, str):
        return re.sub(r"\s+", " ", v).strip().casefold()
    if isinstance(v, list):
        return [re.sub(r"\s+", " ", str(x)).strip().casefold() for x in v]
    return v


def _is_empty(v):
    return v is None or v == [] or v == "" or v == {}


def merge_stage_a(pdf_filled: dict, llm_filled: dict) -> dict:
    """比對「empty+fill_pdf」與「empty+fill_llm」兩結構，依雙來源先決規則合併。

    每欄位：
    - 兩者皆有且一致 → source='both_agree'、confidence='high'
    - 一有一空 → 用有的、source=該來源、confidence='high'
    - 兩者衝突 → 取 LLM（信任排序 LLM>pdf）、
      source='llm_page1 (conflict with pdf_metadata)'、confidence='medium'
    - 兩者皆空 → value None/[]、source/confidence None（等 Stage B）
    alternates：一律保留兩來源原值（debug/Stage B 用）。
    **abstract 強制空（永遠等 Stage B）**，LLM abstract 僅留 alternates。
    """
    out = create_empty_metadata()
    for fld in _ALL_FIELDS:
        is_list = fld in _LIST_FIELDS
        pv = pdf_filled.get(fld, {}).get("value")
        lv = llm_filled.get(fld, {}).get("value")
        alt = {}
        if not _is_empty(pv):
            alt["pdf_metadata"] = pv
        if not _is_empty(lv):
            alt["llm_page1"] = lv
        # 併入兩來源已存的 alternates（保留更早記錄）
        for src_struct in (pdf_filled.get(fld, {}), llm_filled.get(fld, {})):
            for k, v in (src_struct.get("alternates") or {}).items():
                alt.setdefault(k, v)

        if fld == "abstract":
            out[fld] = {"value": None, "source": None,
                        "confidence": None, "alternates": alt}
            continue

        pe, le = _is_empty(pv), _is_empty(lv)
        if pe and le:
            out[fld] = {"value": ([] if is_list else None),
                        "source": None, "confidence": None, "alternates": alt}
        elif pe and not le:
            out[fld] = {"value": lv, "source": "llm_page1",
                        "confidence": "high", "alternates": alt}
        elif le and not pe:
            out[fld] = {"value": pv, "source": "pdf_metadata",
                        "confidence": "high", "alternates": alt}
        elif _norm(pv) == _norm(lv):
            out[fld] = {"value": lv, "source": "both_agree",
                        "confidence": "high", "alternates": alt}
        else:
            out[fld] = {"value": lv,
                        "source": "llm_page1 (conflict with pdf_metadata)",
                        "confidence": "medium", "alternates": alt}
    return out


# ─────────────────────── 最小 Stage B：只補 abstract ───────────────────────

_ABSTRACT_HEADING = re.compile(
    r"^#{1,6}\s*(?:abstract|摘要)\s*$", re.IGNORECASE | re.MULTILINE
)
_ANY_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_ABSTRACT_LLM_PROMPT = (
    "以下是文件 MinerU 轉出的 markdown 開頭。請只擷取「摘要 / Abstract」段落的"
    "原文文字（不要標題、不要其他段落、不要解釋）。若找不到摘要，只回 NONE。\n\n"
    "---\n{md}\n---"
)


def extract_abstract_from_markdown(markdown_text, llm=None) -> Optional[str]:
    """從 MinerU markdown 抽 abstract。先規則（標題下段落），找不到才 LLM。

    回 abstract 文字 | None。**絕不 raise**。
    """
    try:
        if not markdown_text or not isinstance(markdown_text, str):
            return None
        m = _ABSTRACT_HEADING.search(markdown_text)
        if m:
            rest = markdown_text[m.end():]
            nxt = _ANY_HEADING.search(rest)
            seg = (rest[:nxt.start()] if nxt else rest).strip()
            seg = re.sub(r"\n{3,}", "\n\n", seg)
            if len(seg) >= 20:
                return seg
        # 規則找不到 → LLM 看開頭 3000 字
        head = markdown_text[:3000]
        if llm is None:
            try:
                from llm.client import LLMClient  # 延遲 import
                import settings
                llm = LLMClient.get_instance()
                model = getattr(settings, "LLM_DOC_MODEL", None)
            except Exception:
                return None
        else:
            model = None
        resp = llm.chat(
            [{"role": "user",
              "content": _ABSTRACT_LLM_PROMPT.replace("{md}", head)}],
            stream=False, model=model,
        )
        if not resp:
            return None
        resp = resp.strip()
        if not resp or resp.upper().startswith("NONE"):
            return None
        return resp
    except Exception as e:
        logger.warning(f"extract_abstract_from_markdown 失敗（soft）: {e}")
        return None


def fill_abstract_stage_b(metadata: dict, markdown_text, llm=None) -> dict:
    """最小 Stage B：只補 abstract。已有值則不覆寫；恆標記 _stage_b_ran=True。"""
    try:
        metadata["_stage_b_ran"] = True
        f = metadata.get("abstract") or {}
        if f.get("value"):
            return metadata
        ab = extract_abstract_from_markdown(markdown_text, llm=llm)
        if ab:
            metadata["abstract"] = {
                "value": ab, "source": "markdown_extracted", "confidence": "high",
                "alternates": {**f.get("alternates", {}), "markdown_extracted": ab},
            }
    except Exception as e:
        logger.warning(f"fill_abstract_stage_b 失敗（soft）: {e}")
    return metadata


def _read_rag_tree_title(rag_tree_path) -> Optional[str]:
    try:
        if not rag_tree_path:
            return None
        p = Path(rag_tree_path)
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        t = (data.get("title") or "").strip()
        return t or None
    except Exception:
        return None


def resolve_title(metadata: Optional[dict], rag_tree_path,
                  paper_uuid: str,
                  original_filename: Optional[str] = None) -> str:
    """title fallback 鏈（不會回空）：
    1. metadata['title'].value
    2. metadata['title'].alternates 任一非空
    3. rag_tree 的 title（既有邏輯）
    4. original_filename（去 .pdf 後綴；Phase 4.7c step 1）
    5. paper_uuid（最終 fallback）
    """
    try:
        if metadata:
            tf = metadata.get("title") or {}
            if tf.get("value"):
                return tf["value"]
            for v in (tf.get("alternates") or {}).values():
                if v:
                    return v if isinstance(v, str) else str(v)
        rt = _read_rag_tree_title(rag_tree_path)
        if rt:
            return rt
        if original_filename:
            ofn = original_filename.strip()
            if ofn.lower().endswith(".pdf"):
                ofn = ofn[:-4].strip()
            if ofn:
                return ofn
    except Exception as e:
        logger.warning(f"resolve_title 失敗（soft）: {e}")
    return paper_uuid
