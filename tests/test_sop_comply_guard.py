"""SOP-COMPLY grep-gate 源碼守衛（logging SOP §3 / plan OQ5）。

C1 — Logging Hardening 防回歸：
  1. 業務程式碼 `except` 區塊內的 `logger.error(...)` **必含 `exc_info`** 參數
     （AST 靜態掃描·防止日後新增違規丟棄 traceback）。
  2. `llm/client.py` grounding 來源解析不再靜默吞例外（改 warning 留痕）。

掃描範圍（與 plan v1.1 §1 AST 清帳同基準）：
  頂層 `*.py` + `processor/` + `llm/` + `pipelines/` + `utils/`。
排除：
  - `tests/`（測試碼非業務日誌面）
  - `tools/`（CLI 工具·plan 清帳範圍外；已知殘留 `tools/regen_rag.py:252`
    屬範圍外既有債、由 baron 另行決定是否清理——刻意排除、非遺漏）
  - 非-except 守衛日誌（如 `rag_retriever.py:96`）AST 天然不掃（無 active
    exception、補 exc_info 反記 "NoneType: None"·plan OQ1）。
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_SCAN_GLOBS = ("*.py", "processor/*.py", "llm/*.py", "pipelines/*.py", "utils/*.py")


def _business_files():
    files = []
    for pattern in _SCAN_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))
    return files


def _violations(path: Path):
    """回傳該檔 except 區塊內缺 exc_info 之 logger.error 呼叫行號清單。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "error"
            ):
                base = sub.func.value
                name = (
                    base.id
                    if isinstance(base, ast.Name)
                    else (base.attr if isinstance(base, ast.Attribute) else None)
                )
                if name and "logger" in name.lower():
                    if not any(k.arg == "exc_info" for k in sub.keywords):
                        hits.append(sub.lineno)
    return hits


def test_except_block_logger_error_all_have_exc_info():
    """業務碼 except 區內 logger.error 全數含 exc_info（違規清單須為空）。"""
    report = {}
    for f in _business_files():
        hits = _violations(f)
        if hits:
            report[str(f.relative_to(ROOT))] = hits
    assert report == {}, (
        f"except 區塊內 logger.error 缺 exc_info（logging SOP §3 違規）: {report}"
    )


def test_scan_universe_covers_known_files():
    """掃描範圍自檢：C1 清帳之 9 檔皆在守衛涵蓋內（防 glob 失效致守衛空轉）。"""
    covered = {str(f.relative_to(ROOT)) for f in _business_files()}
    for expected in (
        "AI_professor_chat.py",
        "ai_core.py",
        "paper_manager.py",
        "pipeline_core.py",
        "rag_retriever.py",
        "web_server.py",
        "processor/extra_info_processor.py",
        "processor/rag_processor.py",
        "processor/resume_processor.py",
        "llm/client.py",
    ):
        assert expected in covered, f"守衛掃描範圍遺漏 {expected}"


def test_llm_client_grounding_no_silent_swallow():
    """llm/client.py grounding 解析：吞例外已改 warning(exc_info=True) 留痕。"""
    src = (ROOT / "llm" / "client.py").read_text(encoding="utf-8")
    assert "grounding source parse failed" in src
    # _collect_sources 的 except 區不再是裸 pass（AST 驗證：含 warning 呼叫）
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_collect_sources":
            handlers = [n for n in ast.walk(node) if isinstance(n, ast.ExceptHandler)]
            assert handlers, "_collect_sources 應有 except handler"
            for h in handlers:
                assert not all(isinstance(st, ast.Pass) for st in h.body), (
                    "_collect_sources except 區不得為裸 pass（靜默吞例外）"
                )
            break
    else:
        raise AssertionError("找不到 _collect_sources（llm/client.py 結構變動、守衛須同步）")
