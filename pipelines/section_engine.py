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
# === [PIPE-SECTION-BASE END] ===
