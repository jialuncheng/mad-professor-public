# === [PIPE-SECTION-BASE] ===
"""共用 section 引擎（PIPE-SECTION-BASE）。

B 軌結構化文體（resume / litedoc / academic / technical / book）共用之「遞迴標題樹
走訪 → 逐節點摘要 / 並行翻譯 / 排版還原 / RAG section 旁路」機制，自 `resume_pipeline`
抽出為**零 doc_type 耦合**之純函式模組。

設計原則（PIPE-SECTION-BASE plan §2.5 方案 A）：
- **pure-function + 注入**：translator / llm / model / prompt 全由呼叫端參數注入；
  本模組內**不寫死任何 doc_type 字面量**，亦不讀 `PipelineContext` / `raw_metadata`。
- **接縫基準凍結**：節點 key＝**原文標題 path**（P2 產 / P3 帶 / P4 取同基準、
  RAG-ASYNC-HOTFIX-1）；抽取前後 key 零位移。
- 各文體之 route-specific（STYLE_HINTS / constraints / 門檻 / meta 欄位集）皆留呼叫端。

C1 範圍：摘要簇（標題樹走訪 + 批次節點摘要產出 / 翻譯）。C2/C3 追加翻譯與排版還原、
rag 旁路與 meta header 純格式化器。
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# 標題樹走訪（純結構、無 LLM）
# ──────────────────────────────────────────────────────────────────────────
def node_content_text(sec: Dict[str, Any]) -> str:
    """彙整單一節點之實質內文（content list → 串接字串）。"""
    parts: List[str] = []
    for item in sec.get("content", []) or []:
        if isinstance(item, dict):
            c = item.get("content", "") or ""
            if c:
                parts.append(c)
        elif isinstance(item, str) and item.strip():
            parts.append(item)
    return "\n\n".join(parts)


def collect_summary_targets(
    sections: List[Dict[str, Any]], path_prefix: str = "",
) -> List[Tuple[str, str, str]]:
    """DFS 收集有實質內文之節點 (node_key, title, content)；key 對位巢狀樹。

    node_key＝原文標題 path（接縫基準、RAG-ASYNC-HOTFIX-1）。
    可吃**任意子標題樹**（非僅 root）→ 供 PIPE-BOOK 未來組合成 rolling 摘要（plan U3.2）。
    DFS pre-order：父節點先於子節點 append。
    """
    out: List[Tuple[str, str, str]] = []
    for sec in sections or []:
        if not isinstance(sec, dict):
            continue
        title = (sec.get("title") or "").strip()
        node_key = f"{path_prefix}/{title}" if (path_prefix and title) else (title or path_prefix)
        content = node_content_text(sec)
        if title and content.strip():
            out.append((node_key, title, content))
        out.extend(collect_summary_targets(sec.get("children", []) or [], node_key))
    return out


def parse_indexed(out: Optional[str], n: int) -> Dict[int, str]:
    """解析 LLM 批次輸出 `[i] 文字` 逐行 → {i: 文字}（容錯：缺漏項自然留空、越界丟棄）。"""
    result: Dict[int, str] = {}
    for line in (out or "").splitlines():
        m = re.match(r"^\s*\[(\d+)\]\s*(.+?)\s*$", line)
        if m:
            idx = int(m.group(1))
            if 0 <= idx < n:
                result[idx] = m.group(2)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 批次節點摘要產出 / 翻譯（LLM 注入；三安全鎖：批次 / 非致命 / 可量測）
# ──────────────────────────────────────────────────────────────────────────
def generate_section_summaries(
    targets: List[Tuple[str, str, str]], *,
    llm: Any, model: str, system_prompt: str,
    input_chars_cap: int, max_chars: int,
) -> Dict[int, str]:
    """⑤ 1 次批次 LLM 產各節點原文摘要 → {index: 摘要}；失敗→{} 非致命（不阻 reading_ready）。"""
    blocks = [
        f"[{i}] {title}\n{content[:input_chars_cap]}"
        for i, (_k, title, content) in enumerate(targets)
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n\n".join(blocks)[:max_chars]},
    ]
    try:
        out = llm.chat(
            messages=messages, temperature=0.2, stream=False, model=model,
        )
        return parse_indexed(out, len(targets))
    except Exception as exc:  # noqa: BLE001 — 非致命：留空、不阻 reading_ready
        logger.warning(
            "[PIPE-SECTION-BASE] section 摘要批次生成失敗（非致命、留空）: %s", exc,
            exc_info=True,
            extra={"extra_fields": {"event": "section_summary_fallback", "stage": "generate"}},
        )
        return {}


def translate_section_summaries(
    raw_by_idx: Dict[int, str], targets: List[Tuple[str, str, str]],
    abstract: str, source_lang: str, *,
    llm: Any, model: str, system_prompt: str, max_chars: int,
) -> Dict[str, str]:
    """⑥ 1 次批次翻各節點摘要為繁中（全文摘要引導）→ {node_key: 繁中}；失敗→{} 非致命。

    source_lang zh* → 原文即繁中、不重譯。
    """
    items = [(i, s) for i, s in raw_by_idx.items() if (s or "").strip()]
    if not items:
        return {}
    if (source_lang or "").startswith("zh"):
        return {
            targets[i][0]: s.strip()
            for i, s in items if 0 <= i < len(targets)
        }
    user = (
        "全文摘要（翻譯風格與術語引導）：\n" + (abstract or "")[:500]
        + "\n\n待譯各區塊摘要（逐行保留 [編號]）：\n"
        + "\n".join(f"[{i}] {s}" for i, s in items)
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user[:max_chars]},
    ]
    try:
        out = llm.chat(
            messages=messages, temperature=0.2, stream=False, model=model,
        )
        parsed = parse_indexed(out, len(targets))
        return {
            targets[i][0]: t.strip()
            for i, t in parsed.items() if (t or "").strip() and 0 <= i < len(targets)
        }
    except Exception as exc:  # noqa: BLE001 — 非致命：留空、不阻 reading_ready
        logger.warning(
            "[PIPE-SECTION-BASE] section 摘要批次翻譯失敗（非致命、留空）: %s", exc,
            exc_info=True,
            extra={"extra_fields": {"event": "section_summary_fallback", "stage": "translate"}},
        )
        return {}


def build_section_summaries(
    sections: List[Dict[str, Any]], *,
    llm: Any, abstract: str, source_lang: str,
    summary_model: str, translate_model: str,
    summary_system_prompt: str, translate_system_prompt: str,
    input_chars_cap: int, max_chars: int,
    paper_id: Optional[str] = None,
) -> Dict[str, str]:
    """⑤ 產 + ⑥ 批次翻 section_summaries（繁中、key＝原文標題 path）。

    三安全鎖：批次（⑤⑥ 各 1 次 LLM、非 N 次）/ 非致命（失敗留空、不阻 reading_ready、不拋）/
    可量測（performance_metric phase=P2 stage=section_summary）。LLM 全在 DB 交易外。
    回 {node_key: 繁中摘要}（空節點/失敗則該 key 不入、降級為缺）。
    """
    t0 = time.perf_counter()
    targets = collect_summary_targets(sections, "")
    raw_by_idx = generate_section_summaries(
        targets, llm=llm, model=summary_model, system_prompt=summary_system_prompt,
        input_chars_cap=input_chars_cap, max_chars=max_chars,
    ) if targets else {}
    zh_by_key = translate_section_summaries(
        raw_by_idx, targets, abstract, source_lang,
        llm=llm, model=translate_model, system_prompt=translate_system_prompt,
        max_chars=max_chars,
    )
    logger.info(
        "[PIPE-SECTION-BASE] section_summaries 完成 sections=%d produced=%d translated=%d",
        len(targets), len(raw_by_idx), len(zh_by_key),
        extra={"extra_fields": {
            "event": "performance_metric",
            "phase": "P2",
            "stage": "section_summary",
            "paper_id": paper_id,
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "sections": len(targets),
            "translated": len(zh_by_key),
        }},
    )
    return zh_by_key


# === [PIPE-SECTION-BASE C2 START] 翻譯與排版還原機制 ===
from concurrent.futures import ThreadPoolExecutor  # noqa: E402 — C2 局部 import 便於審計/移除
from processor.translator import TranslateMode  # noqa: E402 — 翻譯模式 enum（翻譯契約耦合、非 doc_type）


# ──────────────────────────────────────────────────────────────────────────
# render slot 收集（純結構、不翻譯；DFS pre-order）
# ──────────────────────────────────────────────────────────────────────────
def collect_render_slots(
    sections: List[Dict[str, Any]], depth: int = 0, path_prefix: str = "",
) -> List[Dict[str, Any]]:
    """遞迴收集有序 render slot（不翻譯）。順序＝原 DFS pre-order。

    slot 型態：
    - title  ：{"kind":"title","text":標題,"level":HEADING 層級,"key":原文標題 path}
    - content：{"kind":"content","text":待翻正文}（組裝時套段落正規化）
    - raw    ：{"kind":"raw","text":原文}（formula/figure/table，不翻、passthrough）

    title slot `key`＝原文標題 path（RAG-ASYNC-HOTFIX-1、slot 翻譯前收集故 text 即原文）；
    `level`＝min(2+depth,6)（HEADING-HOTFIX-1，頂層 h2、每下潛 +1、上限 h6）。
    可吃任意子樹（plan U3.2）。
    """
    out: List[Dict[str, Any]] = []
    for sec in sections or []:
        if not isinstance(sec, dict):
            continue
        title = (sec.get("title") or "").strip()
        node_key = f"{path_prefix}/{title}" if (path_prefix and title) else (title or path_prefix)
        if title:
            out.append({
                "kind": "title", "text": title, "level": min(2 + depth, 6),
                "key": node_key,  # 原文標題 path，譯後 title 另存於組裝端 "title" 供顯示
            })
        for item in sec.get("content", []) or []:
            if isinstance(item, dict):
                itype = item.get("type")
                content = item.get("content", "") or ""
                if itype == "text":
                    out.append({"kind": "content", "text": content})
                else:
                    # formula / figure / table 等：保留原文結構、不翻
                    if content:
                        out.append({"kind": "raw", "text": content})
            else:
                # 容錯：content 為純字串 list（md_processor 原始型態）
                txt = str(item).strip()
                if txt:
                    out.append({"kind": "content", "text": txt})
        for child in sec.get("children", []) or []:
            if isinstance(child, dict):
                out.extend(collect_render_slots([child], depth + 1, node_key))
    return out


def normalize_paragraph_breaks(text: str) -> str:
    """段落邊界正規化（pipe-table-safe 單 \\n → \\n\\n）。

    一般段落單 \\n 升級 \\n\\n（製造段落空行）；pipe table 區塊（以 | 開頭連續行）rows 之間
    單 \\n 保留（否則 table 渲染破碎）。移植自 RESUME-P3 PARA-HOTFIX-1、不耦合 A 軌。
    """
    if not text:
        return text
    lines = text.split("\n")
    out_lines: List[str] = []
    in_table = False
    for line in lines:
        is_table_row = bool(re.match(r"^\s*\|", line))
        if is_table_row:
            if not in_table and out_lines and out_lines[-1].strip():
                out_lines.append("")          # 進 table 前補空行作 paragraph 邊界
            in_table = True
            out_lines.append(line)
        elif in_table:
            in_table = False
            if line.strip():
                out_lines.append("")          # table 結束補空行作分隔
            out_lines.append(line)
        else:
            out_lines.append(line)
    text = "\n".join(out_lines)
    # table 區塊外一般 paragraph：單 \n 轉 \n\n（避開 | 開頭行）
    text = re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])", "\n\n", text)
    return text


# ──────────────────────────────────────────────────────────────────────────
# 單元 / 整檔翻譯（translator 注入）
# ──────────────────────────────────────────────────────────────────────────
def translate_unit(text: str, inj: Any, tr: Any, text_type: str) -> str:
    """單元翻譯（空白略過、不浪費呼叫）。"""
    t = (text or "").strip()
    if not t:
        return text
    return tr.translate(t, inj, TranslateMode.NORMAL, text_type)


def translate_whole(full_text: str, inj: Any, tr: Any, translate: bool) -> str:
    """退化 fallback 基礎：整檔一次翻譯（單一巨 section 降級路徑）。"""
    if not translate:
        return full_text
    return tr.translate(full_text, inj, TranslateMode.NORMAL, "content")


# ──────────────────────────────────────────────────────────────────────────
# heading 退化偵測（單一巨 section 降級防護）
# ──────────────────────────────────────────────────────────────────────────
def flatten_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """遞迴攤平 sections（含 children）。"""
    out: List[Dict[str, Any]] = []
    for sec in sections or []:
        if isinstance(sec, dict):
            out.append(sec)
            out.extend(flatten_sections(sec.get("children", []) or []))
    return out


def own_text_len(sec: Dict[str, Any]) -> int:
    """單一 section **自身**（不含 children）的 text item 文字長度累加。"""
    n = 0
    for item in sec.get("content", []) or []:
        if isinstance(item, dict):
            if item.get("type") == "text":
                n += len(item.get("content", "") or "")
        else:
            n += len(str(item))
    return n


def is_heading_degraded(
    sections: List[Dict[str, Any]],
    ratio_threshold: float = 0.85,
    min_sections: int = 2,
) -> bool:
    """heading 退化判定：heading 總數 < min_sections，或單一 heading 自身文字佔比 > ratio_threshold。"""
    flat = flatten_sections(sections)
    if len(flat) < min_sections:
        return True
    sizes = [own_text_len(s) for s in flat]
    total = sum(sizes)
    if total <= 0:
        return False
    return (max(sizes) / total) > ratio_threshold


# ──────────────────────────────────────────────────────────────────────────
# 排版還原（收集 slot → 並行翻譯 → 按序組裝）
# ──────────────────────────────────────────────────────────────────────────
def restore_sections_markdown(
    sections: List[Dict[str, Any]], inj: Any, tr: Any, translate: bool, *,
    max_workers: int,
) -> Tuple[str, List[Dict[str, Any]], Dict[int, str]]:
    """逐 section：收集有序 render slot → 並行翻譯 → 按序組裝，回 (markdown, slots, zh_by_index)。

    RESUME-PERF-1：① `collect_render_slots` 序列收集有序 slot；② 受限並行翻譯
    （max_workers＝呼叫端注入、實際 API 併發再受 LLMClient._api_semaphore 限流）、`{future:index}`
    保序回填、單 unit 失敗退原文異常隔離；③ 按 slot 原序組裝（title 套 HEADING 層級、content
    套段落正規化、raw 原文）。
    **rag section 旁路**由呼叫端以回傳之 slots+zh_by_index 自建（引擎不知 rag、Zero coupling）。
    """
    slots = collect_render_slots(sections, 0, "")
    zh_by_index: Dict[int, str] = {}
    if translate:
        todo = [
            (i, slot, "title" if slot["kind"] == "title" else "content")
            for i, slot in enumerate(slots)
            if slot["kind"] in ("title", "content")
        ]
        if todo:
            with ThreadPoolExecutor(max_workers=max(1, max_workers)) as ex:
                fut_to_idx = {
                    ex.submit(translate_unit, slot["text"], inj, tr, ttype): i
                    for i, slot, ttype in todo
                }
                for fut, i in fut_to_idx.items():
                    try:
                        zh_by_index[i] = fut.result()
                    except Exception as exc:  # noqa: BLE001 — 單 unit 隔離、退原文保交付
                        zh_by_index[i] = slots[i]["text"]
                        logger.warning(
                            "[PIPE-SECTION-BASE] 單元翻譯失敗、退回原文",
                            extra={'extra_fields': {
                                'event': 'resume_translate_unit_fallback',
                                'reason': str(exc)[:200],
                            }},
                        )
    rendered: List[str] = []
    for i, slot in enumerate(slots):
        kind = slot["kind"]
        if kind == "raw":
            rendered.append(slot["text"])
            continue
        zh = zh_by_index.get(i, slot["text"]) if translate else slot["text"]
        if kind == "title":
            rendered.append(f"{'#' * slot['level']} {zh}")
        else:
            rendered.append(normalize_paragraph_breaks(zh))
    markdown = ("\n\n".join(p for p in rendered if p)).strip() + "\n"
    return markdown, slots, zh_by_index
# === [PIPE-SECTION-BASE C2 END] ===


# === [PIPE-SECTION-BASE C3 START] rag section 旁路 + meta header 純格式化器 ===
def collect_rag_sections(
    slots: List[Dict[str, Any]], zh_by_index: Dict[int, str],
    translate: bool, sink: List[Dict[str, Any]],
) -> None:
    """由（已翻譯）slots 重組扁平譯後 section 清單供 rag_indexer：title slot 起新 section，
    其後 content/raw slot 歸入該 section.content（type=text/raw）。不重譯、複用 zh_by_index。

    title section 之 `summary_key`＝原文標題 path（slot["key"]、RAG-ASYNC-HOTFIX-1）；
    P4 以此跨譯查 section_summaries（與 P2 同基準）。
    """
    cur: Optional[Dict[str, Any]] = None
    for i, slot in enumerate(slots):
        kind = slot["kind"]
        text = zh_by_index.get(i, slot["text"]) if translate else slot["text"]
        if kind == "title":
            cur = {
                "title": text, "level": slot.get("level", 2),
                # 原文標題 path（譯後 title 仍存於 "title" 供顯示）；P4 以此跨譯查 section_summaries
                "summary_key": slot.get("key", ""),
                "content": [], "children": [],
            }
            sink.append(cur)
        else:
            if cur is None:  # 容錯：標題前的內容 → 匿名容器
                cur = {"title": "", "level": 2, "content": [], "children": []}
                sink.append(cur)
            cur["content"].append(
                {"type": ("raw" if kind == "raw" else "text"), "content": text}
            )


def single_container_sections(text: str, title: str) -> List[Dict[str, Any]]:
    """is_zh / 退化 fallback：整檔為單一容器 section（size-cap 由 rag_indexer 子切）。

    `title` 由呼叫端傳入（含各文體之 fallback、引擎不讀 ctx、不寫死文體預設）。
    """
    return [{
        "title": title or "", "level": 2,
        "content": [{"type": "text", "content": text or ""}], "children": [],
    }]


def render_meta_header(
    title: str, items: List[Tuple[str, str]], sep: str = "：",
) -> str:
    """meta header **純格式化器**（Zero Schema Coupling、plan U3.1）。

    收**已抽好 + 已做語系 label 對照**之 `(Label, Value)` 清單，產 `# 標題` + 無序列表
    （每欄 `- **Label**{sep}Value`、CommonMark 規範保證各自一行）。
    **引擎零讀 `raw_metadata` / `PipelineContext`**——欄位抽取與 zh/en label 對照全留呼叫端
    （resume 取 phone/email/domain、litedoc 取 date/publisher 等，各自處理）。

    - 空 value 之欄位略過；title 空則無 `# 標題`；整包空 → 回 ''。
    """
    lines: List[str] = []
    t = (title or "").strip()
    if t:
        lines.append(f"# {t}")
        lines.append("")
    rendered = [
        f"- **{label}**{sep}{value}"
        for label, value in items if str(value).strip()
    ]
    if rendered:
        lines.extend(rendered)
        lines.append("")
    if not lines:
        return ""
    return "\n".join(lines).rstrip("\n") + "\n\n"
# === [PIPE-SECTION-BASE C3 END] ===
# === [PIPE-SECTION-BASE END] ===
