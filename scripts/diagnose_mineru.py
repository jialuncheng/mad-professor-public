"""MinerU 互動路徑 dry-run 診斷（不呼叫真實 MinerU）。

用 monkeypatch 假造 requests.post 的回應，餵給 PDFProcessor.process()，
觀察四種情境下：是否 raise、是否產出 markdown、是否取得 images、log 內容。
重點不是「修」，而是「看現行碼在每種 MinerU 回應下實際怎麼反應」，
用來對照 OrcStack 觀察到的 fact（task_id 抓到但 GCP 無對應目錄）。

跑法：  python scripts/diagnose_mineru.py
不需網路、不碰真實 MinerU、不寫 DB。
"""
import io
import os
import sys
import zipfile
import logging
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import processor.pdf_processor as ppmod
from processor.pdf_processor import PDFProcessor


# ── 假 Response（只實作 pdf_processor 用到的介面）──
class FakeResp:
    def __init__(self, status_code=200, headers=None, content=b"", text=""):
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content
        self.text = text


def make_zip(include_md=True, include_images=True, inner="original") -> bytes:
    """產生 MinerU 風格 ZIP：<inner>/auto/<inner>.md + <inner>/auto/images/*。

    inner = MinerU 端據「上傳檔名 stem」命名的目錄。本系統一律上傳
    original.pdf，故正常情況 inner='original'。
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        if include_md:
            z.writestr(f"{inner}/auto/{inner}.md",
                       "# Title\n\nbody ﬁ ligature\n")
        if include_images:
            # 兩張假圖（非真 JPEG，僅證明「ZIP 內就有圖」）
            z.writestr(f"{inner}/auto/images/fig1.jpg", b"\xff\xd8\xff\xe0FAKE1")
            z.writestr(f"{inner}/auto/images/fig2.jpg", b"\xff\xd8\xff\xe0FAKE2")
    return buf.getvalue()


# ── log 捕捉 ──
class CaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append((record.levelname, record.getMessage()))


def run_scenario(name, desc, resp_factory, *, mineru_output_dir_state):
    """mineru_output_dir_state: 'missing' | 'empty' | 'has_task'"""
    print("=" * 72)
    print(f"情境 {name}: {desc}")
    print("-" * 72)

    tmp = Path(tempfile.mkdtemp(prefix=f"diag_{name}_"))
    out_dir = tmp / "out"
    out_dir.mkdir(parents=True)

    # 假 PDF（內容不重要，process 只檢查 exists 並 open 後丟給 requests）
    pdf = tmp / "original.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    # 模擬本地模式（MINERU_HOST 空）+ MINERU_OUTPUT_DIR 的三種狀態，
    # 對應「GCP 上有/無 task_id 目錄」
    mo_root = tmp / "mineru_output"
    os.environ["MINERU_HOST"] = ""
    if mineru_output_dir_state == "missing":
        os.environ["MINERU_OUTPUT_DIR"] = str(mo_root)  # 不建立 → 不存在
    elif mineru_output_dir_state == "empty":
        mo_root.mkdir()
        os.environ["MINERU_OUTPUT_DIR"] = str(mo_root)
    elif mineru_output_dir_state == "has_task":
        task_dir = mo_root / "TASKID-FAKE" / "original" / "auto" / "images"
        task_dir.mkdir(parents=True)
        (task_dir / "server_side.jpg").write_bytes(b"\xff\xd8server")
        os.environ["MINERU_OUTPUT_DIR"] = str(mo_root)

    cap = CaptureHandler()
    plog = logging.getLogger("processor.pdf_processor")
    plog.addHandler(cap)
    plog.setLevel(logging.DEBUG)

    orig_post = ppmod.requests.post
    ppmod.requests.post = lambda *a, **k: resp_factory()

    raised = None
    md_path = None
    try:
        proc = PDFProcessor()
        md_path = proc.process(str(pdf), str(out_dir))
    except Exception as e:
        raised = f"{type(e).__name__}: {e}"
    finally:
        ppmod.requests.post = orig_post
        plog.removeHandler(cap)

    images_dir = out_dir / "images"
    img_files = (sorted(p.name for p in images_dir.iterdir())
                 if images_dir.is_dir() else [])
    md_ok = bool(md_path and Path(md_path).exists())

    print(f"  raise            : {raised or '無'}")
    print(f"  markdown 產出    : {'有 ('+Path(md_path).name+')' if md_ok else '無'}")
    print(f"  out/images 目錄  : {'存在' if images_dir.is_dir() else '不存在'}")
    print(f"  out/images 內容  : {img_files or '(空)'}")
    # ZIP 內是否本就含圖（拆 _tmp 前的事實）——用 resp 再算一次
    try:
        with zipfile.ZipFile(io.BytesIO(resp_factory().content)) as z:
            zip_imgs = [n for n in z.namelist() if "/images/" in n]
    except Exception:
        zip_imgs = []
    print(f"  ZIP 內原本就含圖: {zip_imgs or '(無或非ZIP)'}")
    print("  log:")
    for lvl, msg in cap.records:
        print(f"    [{lvl}] {msg}")
    print()


def main():
    zip_full = make_zip(True, True)          # md + images 都在 ZIP
    zip_empty = b"PK\x05\x06" + b"\x00" * 18  # 合法但空的 ZIP（無任何檔）

    run_scenario(
        "a", "MinerU 回 200 + 完整 ZIP（md+images），server 端也有 task 目錄",
        lambda: FakeResp(200, {"x-mineru-task-id": "TASKID-FAKE"}, zip_full),
        mineru_output_dir_state="has_task",
    )
    run_scenario(
        "b", "MinerU 回 200 + 空 ZIP（疑似：API 通但實際沒解析出東西）",
        lambda: FakeResp(200, {"x-mineru-task-id": "TASKID-FAKE"}, zip_empty),
        mineru_output_dir_state="has_task",
    )
    run_scenario(
        "c", "MinerU 回 500（明確失敗）",
        lambda: FakeResp(500, {}, b"", "internal error"),
        mineru_output_dir_state="empty",
    )
    run_scenario(
        "d", "MinerU 回 200 + 完整 ZIP，但 server 端無對應 task 目錄"
             "（= OrcStack 現況：task_id 抓到、GCP 無此目錄）",
        lambda: FakeResp(200, {"x-mineru-task-id": "6a30a9b8-FAKE"}, zip_full),
        mineru_output_dir_state="empty",
    )

    print("=" * 72)
    print(textwrap.dedent("""\
        判讀重點：
        - 情境 d 應顯示「markdown 有、out/images 空、ZIP 內原本就含圖」。
          這證明：MinerU 回的 ZIP 本身就帶 images，但 process() 解壓後
          只搬 .md、rmtree 掉 _tmp，改去 server 端 {task_id} 路徑 scp，
          一旦 server 端無該目錄 → 圖片全失（即使手上 ZIP 有圖）。
        - 情境 b（空 ZIP）會在 tmp_md.exists() False → markdown_path
          不存在 → read_text 觸發例外 → process() raise（pipeline 中止）。
        - 情境 c（500）在 status!=200 直接 RuntimeError raise。
        - x-mineru-task-id 是否為 MinerU 真實 header 需 OrcStack 實證
          （見報告 F 節指令）。"""))


if __name__ == "__main__":
    main()
