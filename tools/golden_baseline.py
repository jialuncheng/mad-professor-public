"""GOLDEN-BASELINE 黃金基準存盤與退化比對工具（旁路 CLI）。

PIPE 大改版「影子並行縱向五路絞殺」每路打通後須證明排版/譯文/RAG 0% 退化才准
Flip。本工具於改版動工前，對五路代表性文檔在**舊單體 A 軌**跑完整 11-stage，凍結
三維度產物（D1 排版雙語 Markdown / D2 翻譯 JSON / D3 RAG 召回）為不可變黃金快照，
作為日後比對的唯一基準。

本檔為 **OP-1 交付物**，僅實作 `capture` 子命令；`diff` 比對引擎屬 OP-2 交付。

設計鐵律（plan v2 §4 不可動清單）：
  - 只**唯讀調用**舊單體 `PipelineCore.process` 與 `rag_retriever.retrieve_with_context`，
    嚴禁改動其本體、簽名或檢索演算法。
  - 黃金快照一經凍結即唯讀，僅 `--force`（baron 核准）可覆寫。
  - 本工具資料全落檔案系統（`tests/golden_baseline/`），零 DB Schema 變動。

用法：
  python tools/golden_baseline.py capture <doc_type>      # 單路存盤
  python tools/golden_baseline.py capture --all            # 五路全量存盤
  python tools/golden_baseline.py capture <doc_type> --force  # 覆寫既有黃金快照
"""

import argparse
import hashlib
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 專案根目錄（worktree 根）= 本檔上兩層（tools/golden_baseline.py → 根）
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger(__name__)

# ── 路徑常數 ──
_GB_ROOT = _REPO_ROOT / "tests" / "golden_baseline"
_FIXTURES_DIR = _GB_ROOT / "fixtures"
_GOLDEN_DIR = _GB_ROOT / "golden"
_QUERIES_PATH = _GB_ROOT / "queries.json"
# capture 跑舊單體時的隔離工作區（產物中轉站，存盤後可清理；不污染業務 output/）
_CAPTURE_WORK = _GB_ROOT / "_capture_work"

# 五路代表性 doc_type（plan v2 §2 U1）
DOC_TYPES = ["academic", "book", "slides", "resume", "litedoc"]

# 黃金存盤專用 owner 哨兵（與真實使用者隔離、避免污染業務 output/ 與 DB row）
_GOLDEN_OWNER_ID = 900001

# D3 召回 top-k（對齊 retrieve_with_context 預設）
_D3_TOP_K = 5


def _sha256(path: Path) -> str:
    """計算單檔 SHA-256（plan v2 §2 U2 防竄改 manifest）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_queries(doc_type: str) -> List[str]:
    """讀取凍結的固定 query set（D3 來源）。"""
    if not _QUERIES_PATH.exists():
        raise FileNotFoundError(f"固定 query set 缺檔: {_QUERIES_PATH}")
    data = json.loads(_QUERIES_PATH.read_text(encoding="utf-8"))
    queries = data.get(doc_type)
    if not queries:
        raise ValueError(f"queries.json 內無 doc_type={doc_type!r} 的 query set")
    return queries


def _run_old_monolith(pdf_path: Path, doc_type: str) -> Path:
    """唯讀調用舊單體 A 軌 PipelineCore 跑完整 11-stage（plan v2 §2.5.1 步驟 2）。

    回傳該文檔的產物目錄（含 final_*_zh/en.md、final_*_rag_tree.json、vectors/）。
    對齊 web_server.run_pipeline L503-508 的調用模式，shadow=False（正本基準）。
    """
    from pipeline_core import PipelineCore  # 延遲載入，避免無依賴時 import 即炸

    paper_id = f"golden_{doc_type}"
    _CAPTURE_WORK.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"[golden capture] 啟動舊單體 11-stage: doc_type={doc_type} "
        f"pdf={pdf_path.name} owner={_GOLDEN_OWNER_ID} paper_id={paper_id}"
    )
    pipeline = PipelineCore()  # 唯讀調用，不傳 on_progress
    output_paths = pipeline.process(
        str(pdf_path),
        str(_CAPTURE_WORK),
        owner_id=_GOLDEN_OWNER_ID,
        existing_paths={"_confirmed_doc_type": doc_type},
        paper_id=paper_id,
        original_filename=f"{doc_type}.pdf",
    )
    if not output_paths:
        raise RuntimeError(f"舊單體回傳空產物（doc_type={doc_type}），基準不可用")

    paper_dir = _CAPTURE_WORK / str(_GOLDEN_OWNER_ID) / paper_id
    if not paper_dir.is_dir():
        raise RuntimeError(f"舊單體產物目錄不存在: {paper_dir}")
    return paper_dir


def _collect_d3_recall(paper_dir: Path, doc_type: str) -> Dict:
    """D3：對固定 query set 逐條唯讀呼叫 retrieve_with_context，記 top-k chunk+score。

    同時以唯讀方式呼叫 vector_store.similarity_search_with_score 取 chunk 識別與分值，
    供 OP-2 diff 的 Jaccard 比對。嚴禁改動 retrieve_with_context 演算法（plan v2 §4）。
    """
    from rag_retriever import RagRetriever

    paper_id = f"golden_{doc_type}"
    vectors_path = paper_dir / "vectors"
    tree_json = paper_dir / f"final_{paper_id}_rag_tree.json"
    if not (vectors_path / "index.faiss").exists():
        raise RuntimeError(f"D3 缺 FAISS 向量庫: {vectors_path}")
    if not tree_json.exists():
        raise RuntimeError(f"D3 缺 rag_tree: {tree_json}")

    retr = RagRetriever()
    retr.add_paper(_GOLDEN_OWNER_ID, paper_id, str(vectors_path))
    retr.set_rag_tree(
        _GOLDEN_OWNER_ID, paper_id,
        json.loads(tree_json.read_text(encoding="utf-8")),
    )

    queries = _load_queries(doc_type)
    recall: Dict[str, Dict] = {}
    store = retr._get_vector_store(_GOLDEN_OWNER_ID, paper_id)
    for q in queries:
        # 既有入口（回傳結構化字串）——凍結為召回基準
        context_str = retr.retrieve_with_context(
            _GOLDEN_OWNER_ID, q, paper_id, top_k=_D3_TOP_K
        )
        # 唯讀取 chunk 識別 + 分值（供 OP-2 Jaccard）
        hits = []
        if store is not None:
            for doc, score in store.similarity_search_with_score(q, k=_D3_TOP_K):
                hits.append({
                    "content_sha256": hashlib.sha256(
                        doc.page_content.encode("utf-8")
                    ).hexdigest(),
                    "metadata": doc.metadata,
                    "score": float(score),
                })
        recall[q] = {"context": context_str, "hits": hits}
    return recall


def _capture_one(doc_type: str, force: bool) -> None:
    """單路存盤：跑舊單體 → 收 D1/D2/D3 → SHA-256 → 凍結（plan v2 §2.5.1）。"""
    pdf_path = _FIXTURES_DIR / f"{doc_type}.pdf"
    # 步驟 1：固定資料集存在性（缺檔 FAIL FAST）
    if not pdf_path.exists():
        raise FileNotFoundError(f"固定資料集缺檔: {pdf_path}")

    # 步驟 5（前置）：防覆寫閘——已存在且無 --force → ABORT（保護不可變性）
    dest = _GOLDEN_DIR / doc_type
    if dest.exists() and not force:
        raise FileExistsError(
            f"黃金快照已存在、防覆寫 ABORT: {dest}（如確需重存請加 --force，須 baron 核准）"
        )

    paper_id = f"golden_{doc_type}"
    # 步驟 2：唯讀跑舊單體 11-stage
    paper_dir = _run_old_monolith(pdf_path, doc_type)

    # 步驟 3：收集三維度產物
    d1_zh = paper_dir / f"final_{paper_id}_zh.md"
    d1_en = paper_dir / f"final_{paper_id}_en.md"
    d2_tree = paper_dir / f"final_{paper_id}_rag_tree.json"
    missing = [str(p) for p in (d1_zh, d1_en, d2_tree) if not p.exists()]
    if missing:
        raise RuntimeError(f"產物不完整（D1/D2 缺漏）: {missing}")
    d3_recall = _collect_d3_recall(paper_dir, doc_type)

    # 凍結寫入（含 --force 覆寫時先清舊）
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copy2(d1_zh, dest / "D1_zh.md")
    shutil.copy2(d1_en, dest / "D1_en.md")
    shutil.copy2(d2_tree, dest / "D2_rag_tree.json")
    (dest / "D3_recall.json").write_text(
        json.dumps(d3_recall, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 步驟 4：SHA-256 → manifest.json
    frozen = ["D1_zh.md", "D1_en.md", "D2_rag_tree.json", "D3_recall.json"]
    manifest = {
        "doc_type": doc_type,
        "source_pdf": pdf_path.name,
        "source_pdf_sha256": _sha256(pdf_path),
        "checksums": {name: _sha256(dest / name) for name in frozen},
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        f"[golden capture] 凍結完成 doc_type={doc_type} → {dest} "
        f"（{len(frozen)} 檔 + manifest）"
    )


def cmd_capture(args: argparse.Namespace) -> int:
    """capture 子命令入口。"""
    targets = DOC_TYPES if args.all else [args.doc_type]
    if not args.all and args.doc_type not in DOC_TYPES:
        logger.error(f"未知 doc_type={args.doc_type!r}，合法值: {DOC_TYPES}")
        return 2

    failures: Dict[str, str] = {}
    for dt in targets:
        try:
            _capture_one(dt, force=args.force)
        except FileExistsError as e:
            # 防覆寫閘屬預期保護，明確標示但不視為崩潰
            logger.warning(f"[golden capture] {dt} ABORT: {e}")
            failures[dt] = f"ABORT(防覆寫): {e}"
        except Exception as e:
            logger.error(f"[golden capture] {dt} 失敗: {e}", exc_info=True)
            failures[dt] = str(e)

    captured = [dt for dt in targets if dt not in failures]
    logger.info(
        f"[golden capture] 完成彙總：成功 {len(captured)}/{len(targets)} "
        f"（{captured}）；失敗 {list(failures)}"
    )
    return 1 if failures else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="golden_baseline",
        description="GOLDEN-BASELINE 黃金基準存盤與退化比對工具（OP-1：capture）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cap = sub.add_parser(
        "capture", help="對五路代表性文檔在舊單體存盤三維度黃金快照"
    )
    p_cap.add_argument(
        "doc_type", nargs="?", default=None,
        help=f"單一 doc_type（{'/'.join(DOC_TYPES)}）；與 --all 二選一",
    )
    p_cap.add_argument("--all", action="store_true", help="五路全量存盤")
    p_cap.add_argument(
        "--force", action="store_true",
        help="覆寫既有黃金快照（破壞不可變性、須 baron 核准）",
    )
    p_cap.set_defaults(func=cmd_capture)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "capture" and not args.all and not args.doc_type:
        parser.error("capture 需指定 <doc_type> 或 --all")
    return args.func(args)


if __name__ == "__main__":
    from utils.logging_config import setup_logging  # logging SOP 鐵律一
    setup_logging()
    raise SystemExit(main())
