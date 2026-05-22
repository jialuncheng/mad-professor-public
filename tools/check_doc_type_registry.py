"""doc_type 註冊點對齊驗證。

從 7 個註冊點抽出 doc_type 集合，比對是否完全一致；同時檢查每個註冊
點上方有 marker、且 doc_analyzer 字典指向的 prompt 檔存在。

用法（專案根目錄執行）：
    python tools/check_doc_type_registry.py
回傳 exit code：0 = 全部對齊；1 = 任一不對齊或缺檔。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER_PY = "# === doc_type-registry ==="
MARKER_JS = "// === doc_type-registry ==="


# ────────────────────── 抽取輔助 ──────────────────────
def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _extract_string_list(text: str, pattern: str) -> set[str]:
    """從文字中找 pattern（regex，須有 1 個 capture group 為整段內容），
    回傳該段中所有 '...' / "..." 字串字面之集合。
    """
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return set()
    body = m.group(1)
    return set(re.findall(r"['\"]([a-z_][a-z0-9_-]*)['\"]", body))


def _extract_dict_keys(text: str, pattern: str) -> set[str]:
    """從 pattern（含 1 個 capture group 為 dict body）內抽 key：
    支援 quoted（Python dict / JS string-keyed）與 unquoted JS shorthand。"""
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return set()
    body = m.group(1)
    # quoted: 'key': … 或 "key": …
    keys = set(re.findall(r"['\"]([a-z_][a-z0-9_-]*)['\"]\s*:", body))
    # unquoted JS shorthand: 行首縮排 + key: …（首字小寫字母，避免抓到 SVG path 等）
    keys |= set(re.findall(r"(?m)^\s*([a-z_][a-z0-9_-]*)\s*:", body))
    return keys


# ────────────────────── 7 個註冊點抽取 ──────────────────────
def points() -> dict[str, set[str]]:
    """回傳 {註冊點名稱: doc_type 集合}。"""
    web = _read("web_server.py")
    proto = _read("static/index.html")
    da = _read("processor/doc_analyzer.py")
    tr = _read("processor/translate_processor.py")
    pc = _read("pipeline_core.py")

    return {
        "web_server.valid_types":
            _extract_string_list(web, r"valid_types\s*=\s*\[(.*?)\]"),
        "static.DOC_TYPES":
            _extract_string_list(proto, r"const\s+DOC_TYPES\s*=\s*\[(.*?)\];"),
        "static.DOC_TYPE_LABELS":
            _extract_dict_keys(proto, r"const\s+DOC_TYPE_LABELS\s*=\s*\{(.*?)\};"),
        "doc_analyzer.HEADING_FIX_PROMPTS":
            _extract_dict_keys(da, r"HEADING_FIX_PROMPTS\s*=\s*\{(.*?)\}"),
        "doc_analyzer.STRUCTURE_PROMPTS":
            _extract_dict_keys(da, r"STRUCTURE_PROMPTS\s*=\s*\{(.*?)\}"),
        "translate_processor.style_hints":
            _extract_dict_keys(tr, r"style_hints\s*=\s*\{(.*?)\}"),
        # pipeline_core 的 skip tuple — 只列「跳過 extra_info」的 doc_type
        # 子集，故不要求等於全集；額外列出供 marker check + sanity 報告
        "pipeline_core.extra_info_skip":
            _extract_string_list(
                pc, r"if doc_type in\s*\((.*?)\)\s*:\s*\n\s*return self\.extra_info_processor"
            ),
        # Phase 4.7e Commit 7e-2 v2：pipeline_core 內 KNOWN_DOC_TYPES 全集
        # 必須等於 truth（web_server.valid_types）。
        "pipeline_core.KNOWN_DOC_TYPES":
            _extract_string_list(
                pc, r"KNOWN_DOC_TYPES\s*=\s*frozenset\(\{(.*?)\}\)"
            ),
        # Phase 4.7e Commit 7e-2 v2：pipeline_core 內走「獨立 parser」的
        # doc_type 子集（目前: slides + resume）；新增獨立 parser 路徑時
        # 應同步出現。不要求等於 truth、只報內容供人工確認。
        "pipeline_core.PIPELINE_PARSER":
            set(re.findall(
                r"doc_type\s*==\s*['\"]([a-z_][a-z0-9_-]*)['\"]",
                (
                    re.search(
                        r"def _stage_pdf_to_md\b.*?(?=\n    def )",
                        pc, re.DOTALL
                    ).group(0)
                    if re.search(
                        r"def _stage_pdf_to_md\b.*?(?=\n    def )", pc, re.DOTALL
                    ) else ""
                )
            )),
    }


# ────────────────────── marker 檢查 ──────────────────────
MARKER_CHECKS: list[tuple[str, str, str]] = [
    # (檔路徑, marker 樣式, 緊接其下應出現的「目標起始字串」)
    ("web_server.py", MARKER_PY, "valid_types ="),
    ("static/index.html", MARKER_JS, "const DOC_TYPES ="),
    ("static/index.html", MARKER_JS, "const DOC_TYPE_LABELS ="),
    ("processor/doc_analyzer.py", MARKER_PY, "HEADING_FIX_PROMPTS ="),
    ("processor/doc_analyzer.py", MARKER_PY, "STRUCTURE_PROMPTS ="),
    ("processor/translate_processor.py", MARKER_PY, "style_hints ="),
    ("pipeline_core.py", MARKER_PY, "if doc_type in ("),
    # Phase 4.7e Commit 7e-2 v2：pipeline_core 內 KNOWN_DOC_TYPES + parser routing
    ("pipeline_core.py", MARKER_PY, "KNOWN_DOC_TYPES = frozenset"),
    ("pipeline_core.py", MARKER_PY, "if doc_type == 'slides':"),
]


def check_markers() -> list[str]:
    """回傳缺漏 marker 的描述（空 list = 全 OK）。"""
    missing = []
    for path, marker, target in MARKER_CHECKS:
        txt = _read(path)
        # 找每個 target 起始位置，往上回看 5 行內是否有 marker
        for m in re.finditer(re.escape(target), txt):
            start = m.start()
            preceding = txt.rfind("\n", 0, start)
            # 取 marker 前 5 行（最多 ~300 字元）的回看窗
            window_start = max(0, start - 400)
            window = txt[window_start:start]
            if marker not in window:
                missing.append(f"{path}: marker '{marker}' 未緊鄰於 '{target}' 之前")
    return missing


# ────────────────────── prompt 檔存在性 ──────────────────────
def check_prompts(doc_types: set[str]) -> list[str]:
    """檢查 doc_analyzer 兩 dict 指向的所有 prompt 檔存在。"""
    missing = []
    da = _read("processor/doc_analyzer.py")
    for dict_name in ("HEADING_FIX_PROMPTS", "STRUCTURE_PROMPTS"):
        m = re.search(rf"{dict_name}\s*=\s*\{{(.*?)\}}", da, re.DOTALL)
        if not m:
            missing.append(f"無法解析 {dict_name}")
            continue
        for line in m.group(1).splitlines():
            sm = re.search(r"['\"]([a-z_][a-z0-9_-]*)['\"]\s*:\s*['\"]([^'\"]+\.txt)['\"]", line)
            if not sm:
                continue
            key, prompt_path = sm.groups()
            if not (ROOT / prompt_path).exists():
                missing.append(f"{dict_name}['{key}'] -> {prompt_path} 不存在")
    return missing


# ────────────────────── 主流程 ──────────────────────
def main() -> int:
    pts = points()
    # 主集合（用作對齊的「期望全集」）= web_server.valid_types
    truth_name = "web_server.valid_types"
    truth = pts[truth_name]
    if not truth:
        print(f"✗ 無法解析 {truth_name}", file=sys.stderr)
        return 1

    # 比對 6 個應「完全等於 truth」的註冊點
    # （extra_info_skip / PIPELINE_PARSER 例外，是子集）
    must_equal = [
        "static.DOC_TYPES",
        "static.DOC_TYPE_LABELS",
        "doc_analyzer.HEADING_FIX_PROMPTS",
        "doc_analyzer.STRUCTURE_PROMPTS",
        "translate_processor.style_hints",
        "pipeline_core.KNOWN_DOC_TYPES",
    ]
    mismatches: list[str] = []
    for name in must_equal:
        s = pts[name]
        missing = truth - s
        extra = s - truth
        if missing or extra:
            parts = []
            if missing:
                parts.append(f"missing: {sorted(missing)}")
            if extra:
                parts.append(f"extra: {sorted(extra)}")
            mismatches.append(f"  {name}: {' | '.join(parts)}")

    # extra_info_skip 應為 truth 的子集（不必等）
    skip = pts["pipeline_core.extra_info_skip"]
    skip_invalid = skip - truth
    if skip_invalid:
        mismatches.append(
            f"  pipeline_core.extra_info_skip: 含未在 valid_types 的鍵 {sorted(skip_invalid)}"
        )

    # Phase 4.7e Commit 7e-2 v2：PIPELINE_PARSER 為 truth 子集（不必等）
    parsers = pts["pipeline_core.PIPELINE_PARSER"]
    parser_invalid = parsers - truth
    if parser_invalid:
        mismatches.append(
            f"  pipeline_core.PIPELINE_PARSER: 含未在 valid_types 的鍵 {sorted(parser_invalid)}"
        )

    marker_missing = check_markers()
    prompt_missing = check_prompts(truth)

    # 報告
    if mismatches:
        print("✗ DOC_TYPE MISALIGNMENT:")
        print(f"  {truth_name}: {sorted(truth)}")
        for line in mismatches:
            print(line)
    else:
        print(f"✓ All doc_types aligned across {len(must_equal) + 1} registry points (+2 subsets):")
        print(f"  {', '.join(sorted(truth))}")
        print(f"  pipeline_core.extra_info_skip (subset): "
              f"{', '.join(sorted(skip))}")
        print(f"  pipeline_core.PIPELINE_PARSER (subset, 獨立 parser): "
              f"{', '.join(sorted(parsers))}")

    if marker_missing:
        print("\n✗ MARKER MISSING:")
        for line in marker_missing:
            print(f"  {line}")
    else:
        print(f"✓ All {len(MARKER_CHECKS)} markers present")

    if prompt_missing:
        print("\n✗ PROMPT FILES MISSING:")
        for line in prompt_missing:
            print(f"  {line}")
    else:
        print("✓ All required prompts exist")

    ok = not (mismatches or marker_missing or prompt_missing)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
