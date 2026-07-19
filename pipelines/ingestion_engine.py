# === [PIPE-INGEST C1] ===
"""共用攝入組裝引擎（PIPE-INGEST）。

B 軌文字攝入家族共用之「cleaned markdown 全文 + 前段結構判型 → 標題抽取 / meta 行分離 /
行級分塊 / section 層級樹」組裝機制，取代對 A 軌組裝鏈（md_processor / json_processor）之借用。

設計原則（PIPE-INGEST plan v4 §2.1、比照 section_engine 設計紀律）：
- **純函式 + 注入**：文體差異（meta 判型集 `meta_types` 等）一律由呼叫端參數注入；
  本模組**不寫死任何文體字面量**，亦不 import 任何 A 軌 processor、不讀 PipelineContext。
- **title 不丟**：文件標題（首個 ``#`` 行）以獨立欄位交付，不再於組裝時被隱匿丟棄。
- **meta 分離不受行連續性限制**：判型 blocks 逐塊獨立標記，非 meta 行夾雜不使後續判型作廢。
- **figure 帶可重建 content**：``![alt](src)`` 以 ``content`` 鍵交付，穿透下游 raw slot 契約。
- **接縫基準凍結**：section title＝markdown heading 原文文字零加工（原文標題 path 基準零位移）；
  輸出 schema 與 TilingProcessor 現行輸入（processed.json）相容、索引欄由 tiling 自補。
- **soft-fail**：判型缺失 / 格式不符 / 行號越界 → 退化為「無 meta 分離」（不阻斷、僅回現況行為）。
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 預設 meta 判型集（前段結構判型 schema 之型別 token、非文體名；呼叫端可覆寫注入）
DEFAULT_META_TYPES: Tuple[str, ...] = ("title", "authors", "publication_info")

# 行級樣式（語意對齊既有分塊器、零 import）
_HEADING_RE = re.compile(r"^(#+)\s*(\S.*?)\s*$")
_FIGURE_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>.*?)\)")
_TABLE_RE = re.compile(r"^<html><body><table>.*?</table></body></html>$")
_FORMULA_RE = re.compile(r"^\s*\${2}(?P<formula>.*?)\${2}\s*$", re.DOTALL)
_FIGURE_CAPTION_RE = re.compile(
    r"""
    ^(?:
        (?:Figure|Fig\.)                       # Figure 或 Fig.
        (?:\s+\(?\d+(?:\.\d+)?\)?\.?:?)        # (1), 1:, 1., (1.1), 1.1: 等
        |
        (?:IMAGE|DIAGRAM)                      # IMAGE 或 DIAGRAM
        (?:\s+\d+:?)                           # 1:, 1
        |
        (?:Figure)                             # Figure
        (?:\s+[IVX]+:?)                        # I:, II, III, IV 等
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ──────────────────────────────────────────────────────────────────────────
# 標題抽取
# ──────────────────────────────────────────────────────────────────────────
def extract_title(lines: List[str]) -> Tuple[str, Optional[int]]:
    """取首個 ``#`` heading 行為文件標題，回 (title 文字, 行號)；無則 ('', None)。"""
    for i, line in enumerate(lines):
        if line.startswith("#"):
            m = _HEADING_RE.match(line)
            if m:
                return m.group(2).strip(), i
    return "", None


# ──────────────────────────────────────────────────────────────────────────
# meta 行分離（判型注入、不受行連續性限制、soft-fail）
# ──────────────────────────────────────────────────────────────────────────
def mark_meta_lines(
    lines: List[str],
    structure: Optional[Dict[str, Any]],
    meta_types: Tuple[str, ...],
    title_idx: Optional[int],
) -> Tuple[Dict[str, List[str]], List[bool]]:
    """依前段結構判型標記 meta 行，回 (meta {型別: [行文字]}, 各行 is_meta flags)。

    - 判型 blocks（``structure["structure"]`` 之 ``{start,end,type}``）**逐塊獨立標記**：
      非 meta 行夾雜於兩 meta block 之間，不使後續判型作廢（廢除連續性假設）。
    - ``type == "title"`` 之 block 一律標 meta（與 ``title_idx`` 行同置，防標題回聲入內文）。
    - soft-fail：structure None / 無 ``structure`` 鍵 / 非 list / 任一 block 行號越界或
      格式不符 → 回 ``({}, 僅 title 行為 True)``（無 meta 分離、title 仍不入內文）。
    """
    flags = [False] * len(lines)
    if title_idx is not None and 0 <= title_idx < len(lines):
        flags[title_idx] = True
    fallback = ({}, list(flags))

    blocks = structure.get("structure") if isinstance(structure, dict) else None
    if not isinstance(blocks, list) or not blocks:
        if structure:
            logger.warning(
                "[PIPE-INGEST] 前段結構判型缺失或格式不符、跳過 meta 分離（soft-fail）"
            )
        return fallback

    # 先整批驗證行號（任一越界 → 整體 soft-fail，不做半套分離）
    try:
        spans: List[Tuple[int, int, str]] = []
        for block in blocks:
            btype = str(block.get("type") or "")
            start, end = int(block["start"]), int(block["end"])
            if start < 0 or end < start or end >= len(lines):
                logger.warning(
                    "[PIPE-INGEST] 判型行號越界（start=%d end=%d lines=%d）、"
                    "跳過 meta 分離（soft-fail）", start, end, len(lines),
                )
                return fallback
            spans.append((start, end, btype))
    except Exception as exc:  # noqa: BLE001 — 判型格式異常一律 soft-fail
        logger.warning(
            "[PIPE-INGEST] 判型解析失敗、跳過 meta 分離（soft-fail）: %s", exc,
            exc_info=True,
        )
        return fallback

    meta: Dict[str, List[str]] = {}
    for start, end, btype in spans:
        if btype != "title" and btype not in meta_types:
            continue
        for i in range(start, end + 1):
            s = lines[i].strip()
            if s and not flags[i]:
                meta.setdefault(btype, []).append(s)
            flags[i] = True
    return meta, flags


# ──────────────────────────────────────────────────────────────────────────
# 行級分塊（語意對齊既有分塊器；figure 補 content 鍵）
# ──────────────────────────────────────────────────────────────────────────
def split_blocks(lines: List[str]) -> List[Dict[str, Any]]:
    """單次自上而下掃描，將行序列拆為 formula / figure / table / text blocks（保序）。

    與既有分塊器語意等價之差異點（皆為凍結契約之刻意行為）：
    - figure block **必帶** ``content=f"![alt](src)"``（可重建 markdown、穿透 raw slot）。
    - 空白行不產空 text block（下游合併語意不變）。
    """
    blocks: List[Dict[str, Any]] = []
    n = len(lines)
    used = [False] * n
    i = 0
    while i < n:
        if used[i]:
            i += 1
            continue
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        # 1) 行間公式
        m_formula = _FORMULA_RE.match(stripped)
        if m_formula:
            body = m_formula.group("formula").strip()
            blocks.append({"type": "formula", "content": f"$$ {body} $$"})
            used[i] = True
            i += 1
            continue

        # 2) 圖片（帶 content 重建 + 上下行 caption 關聯）
        m_img = _FIGURE_RE.match(stripped)
        if m_img:
            used[i] = True
            alt, src = m_img.group("alt"), m_img.group("src")
            fig_block: Dict[str, Any] = {
                "type": "figure",
                "src": src,
                "alt": alt,
                "content": f"![{alt}]({src})",
            }
            caption, cap_idx = _find_caption(lines, i, used)
            if caption and cap_idx is not None:
                fig_block["caption"] = caption
                used[cap_idx] = True
            blocks.append(fig_block)
            i += 1
            continue

        # 3) HTML 表格
        if _TABLE_RE.match(stripped):
            blocks.append({"type": "table", "content": stripped})
            used[i] = True
            i += 1
            continue

        # 4) 一般文字（跳過未關聯之 caption 樣式行與空白行）
        if stripped and not _FIGURE_CAPTION_RE.match(stripped):
            blocks.append({"type": "text", "content": line})
        used[i] = True
        i += 1
    return blocks


def _find_caption(
    lines: List[str], current_index: int, used: List[bool]
) -> Tuple[str, Optional[int]]:
    """圖說查找：優先上一行、次查下一行（同既有分塊器語意）。"""
    if current_index - 1 >= 0 and not used[current_index - 1]:
        prev = lines[current_index - 1].strip()
        if _FIGURE_CAPTION_RE.match(prev):
            return prev, current_index - 1
    if current_index + 1 < len(lines) and not used[current_index + 1]:
        nxt = lines[current_index + 1].strip()
        if _FIGURE_CAPTION_RE.match(nxt):
            return nxt, current_index + 1
    return "", None


# ──────────────────────────────────────────────────────────────────────────
# section 層級樹組裝
# ──────────────────────────────────────────────────────────────────────────
def build_sections(
    lines: List[str], meta_flags: List[bool]
) -> List[Dict[str, Any]]:
    """依 heading 層級將非 meta 行組裝為 section 樹（processed 相容 schema）。

    - heading 行（``#`` 開頭、非 meta）起新 section：``{"title","level","content","children"}``；
      ``title``＝heading 原文文字**零加工**、``level``＝井號數。
    - 首個 heading 前之孤立內容 → 無標題容器 section（``title=''``、level=1）。
    - 層級棧組裝父子：level 較深者入前一淺層 section 之 ``children``。
    - 各 section 之 ``content``＝該節點自身行經 :func:`split_blocks` 之 block 清單。
    """
    hierarchy: List[Dict[str, Any]] = []
    stack: List[Tuple[int, Dict[str, Any]]] = []
    current: Optional[Dict[str, Any]] = None
    buffer: List[str] = []

    def flush() -> None:
        nonlocal buffer
        if current is not None:
            current["content"] = split_blocks(buffer)
        elif any(ln.strip() for ln in buffer):
            orphan = {
                "title": "", "level": 1,
                "content": split_blocks(buffer), "children": [],
            }
            hierarchy.append(orphan)
        buffer = []

    def attach(section: Dict[str, Any], level: int) -> None:
        while stack and stack[-1][0] >= level:
            stack.pop()
        if stack:
            stack[-1][1]["children"].append(section)
        else:
            hierarchy.append(section)
        stack.append((level, section))

    for i, line in enumerate(lines):
        if meta_flags[i]:
            continue
        m = _HEADING_RE.match(line) if line.startswith("#") else None
        if m:
            flush()
            level = len(m.group(1))
            current = {
                "title": m.group(2).strip(), "level": level,
                "content": [], "children": [],
            }
            attach(current, level)
        else:
            buffer.append(line)
    flush()
    return hierarchy


# ──────────────────────────────────────────────────────────────────────────
# 頂層入口
# ──────────────────────────────────────────────────────────────────────────
def assemble(
    markdown_text: str,
    structure: Optional[Dict[str, Any]] = None,
    *,
    meta_types: Tuple[str, ...] = DEFAULT_META_TYPES,
) -> Dict[str, Any]:
    """cleaned markdown 全文 + 前段結構判型 → ``{"title", "meta", "sections"}``。

    - ``title``：首個 ``#`` heading 文字（不入 sections、供呼叫端消費）。
    - ``meta``：``{判型型別: [行文字]}``（分離自內文；soft-fail 時為 ``{}``）。
    - ``sections``：processed 相容 section 樹（TilingProcessor 直接可餵、
      ``index``/``part`` 等索引欄由 tiling 自補、引擎不產）。
    """
    lines = (markdown_text or "").split("\n")
    title, title_idx = extract_title(lines)
    meta, flags = mark_meta_lines(lines, structure, tuple(meta_types), title_idx)
    sections = build_sections(lines, flags)
    logger.info(
        "[PIPE-INGEST] assemble 完成 title=%r meta_types=%d sections=%d",
        title, len(meta), len(sections),
    )
    return {"title": title, "meta": meta, "sections": sections}
# === [PIPE-INGEST C1 END] ===
