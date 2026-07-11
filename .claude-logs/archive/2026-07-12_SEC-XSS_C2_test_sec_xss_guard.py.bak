"""SEC-XSS 靜態守衛測試（C1 — Vendor & Load）。

防漂移四斷言：DOMPurify 自託管實體 / index.html defer 載入 /
fetch_frontend_vendor.sh 下載段落 / vendor README 登記（版本+SHA-256 指紋）。
純靜態檔案斷言、零 runtime 依賴（C2/C3 消毒接線之守衛於各該 commit 追加）。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PURIFY_JS = ROOT / "static" / "vendor" / "dompurify" / "purify.min.js"
INDEX_HTML = ROOT / "static" / "index.html"
FETCH_SH = ROOT / "tools" / "fetch_frontend_vendor.sh"
VENDOR_README = ROOT / "static" / "vendor" / "README.md"


def test_dompurify_vendored_asset_exists():
    """① 自託管實體存在且非空（npm pack dompurify 之 dist/purify.min.js）。"""
    assert PURIFY_JS.is_file(), "static/vendor/dompurify/purify.min.js 不存在"
    assert PURIFY_JS.stat().st_size > 10_000, "purify.min.js 過小、疑非完整資產"
    head = PURIFY_JS.read_text(encoding="utf-8", errors="replace")[:500]
    assert "DOMPurify" in head, "purify.min.js 內容缺 DOMPurify 識別"


def test_index_html_loads_dompurify_with_defer():
    """② index.html head 以 defer 載入 dompurify（於 marked 之後）。"""
    html = INDEX_HTML.read_text(encoding="utf-8")
    line = next(
        (l for l in html.splitlines() if "dompurify/purify.min.js" in l and "<script" in l),
        None,
    )
    assert line is not None, "index.html 缺 dompurify 載入 script"
    assert "defer" in line, "dompurify script 缺 defer（須與 marked/katex 同節奏）"
    assert html.find("marked/marked.min.js") < html.find("dompurify/purify.min.js"), (
        "dompurify 應於 marked script 之後載入"
    )


def test_fetch_vendor_script_has_dompurify_section():
    """③ fetch_frontend_vendor.sh 含 DOMPurify 下載＋校驗段落（離線部署可重現）。"""
    sh = FETCH_SH.read_text(encoding="utf-8")
    assert "DOMPURIFY_VERSION" in sh, "腳本缺 DOMPURIFY_VERSION 釘版"
    assert "dompurify@${DOMPURIFY_VERSION}" in sh, "腳本缺 npm pack dompurify 段落"
    assert "purify.min.js" in sh, "腳本缺 purify.min.js 提取"
    assert "sha256sum" in sh, "腳本缺 SHA-256 校驗輸出"


def test_vendor_readme_registers_dompurify():
    """④ vendor README 含 dompurify 分節（版本 + SHA-256 指紋、且指紋與實體相符）。"""
    md = VENDOR_README.read_text(encoding="utf-8")
    assert "dompurify" in md.lower(), "README 缺 dompurify 分節"
    assert "3.1.6" in md, "README 缺版本登記"
    import hashlib

    actual = hashlib.sha256(PURIFY_JS.read_bytes()).hexdigest()
    assert actual in md, (
        f"README 登記之 SHA-256 與實體不符（實測 {actual[:16]}…）——資產或文件漂移"
    )
