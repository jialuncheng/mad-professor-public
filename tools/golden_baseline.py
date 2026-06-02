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
import difflib
import hashlib
import json
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
# Diff 報告輸出根（WORKFLOW_SOP §2：工具產出歸 report/）
_REPORT_DIR = _REPO_ROOT / "report" / "golden_baseline"

# 五路代表性 doc_type（plan v2 §2 U1）
DOC_TYPES = ["academic", "book", "slides", "resume", "litedoc"]

# 黃金存盤專用 owner 哨兵（與真實使用者隔離、避免污染業務 output/ 與 DB row）
_GOLDEN_OWNER_ID = 900001

# D3 召回 top-k（對齊 retrieve_with_context 預設）
_D3_TOP_K = 5

# ── Diff 退化門檻（plan v2 §7 Q2：保守起始值、實測校準後待 baron 核准寫死）──
_D2_SIM_THRESHOLD = 0.95   # D2 譯文逐 Section 相似度下限
_D3_JACCARD_THRESHOLD = 0.90  # D3 RAG 召回 top-k chunk 集合 Jaccard 重疊下限

# 凍結快照固定檔名（對齊 capture 凍結產物）
_SNAPSHOT_FILES = ["D1_zh.md", "D1_en.md", "D2_rag_tree.json", "D3_recall.json"]


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


# ════════════════════════════════════════════════════════════════════════
# OP-2：diff 三維度比對引擎（plan v2 §2.5.2 / §2 U3 / §2 U4）
# ════════════════════════════════════════════════════════════════════════

# 影子雜訊正規化：剝離 `_shadow` ID／` (測試)` 後綴／時間戳（plan v2 §2.5.2 步驟 4）
_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?")


def _normalize_text(s: str) -> str:
    """剝離已知影子雜訊（_shadow / (測試) / 時間戳），使候選與黃金可等價比對。"""
    if not s:
        return ""
    s = s.replace(" (測試)", "").replace("（測試）", "").replace("(測試)", "")
    s = s.replace("_shadow", "")
    s = _TS_RE.sub("<TS>", s)
    return s


def _build_structure_tree(md_text: str) -> Dict:
    """從 Markdown 萃取結構樹（heading 階層／table 行列／list 項數／image alt）。

    plan v2 §2 U3 D1：退化定義＝結構節點增刪或 alt 文字不符。
    """
    md = _normalize_text(md_text)
    headings: List[Tuple[int, str]] = []
    table_rows: List[int] = []   # 每行的欄位數
    list_items = 0
    images: List[str] = []
    for raw in md.splitlines():
        line = raw.strip()
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
            continue
        if line.startswith("|") and line.endswith("|") and len(line) > 1:
            table_rows.append(line.count("|") - 1)
        if re.match(r"^[-*+]\s+\S", line):
            list_items += 1
        for alt in re.findall(r"!\[([^\]]*)\]\([^)]*\)", line):
            images.append(alt.strip())
    return {
        "headings": headings,
        "table_rows": table_rows,
        "list_items": list_items,
        "images": images,
    }


def _diff_d1(golden: Dict, candidate: Dict) -> Dict:
    """D1 排版結構樹比對（zh + en 雙語）。退化＝任一結構維度有增刪/不符。"""
    deltas: List[str] = []
    for lang in ("D1_zh", "D1_en"):
        bt = _build_structure_tree(golden[lang])
        ct = _build_structure_tree(candidate[lang])
        if bt["headings"] != ct["headings"]:
            deltas.append(
                f"{lang} heading 結構不符（黃金 {len(bt['headings'])} vs 候選 {len(ct['headings'])}）"
            )
        if bt["table_rows"] != ct["table_rows"]:
            deltas.append(f"{lang} table 行列不符")
        if bt["list_items"] != ct["list_items"]:
            deltas.append(
                f"{lang} list 項數不符（{bt['list_items']} vs {ct['list_items']}）"
            )
        if bt["images"] != ct["images"]:
            deltas.append(f"{lang} image alt 不符")
    return {"degraded": bool(deltas), "deltas": deltas}


def _collect_section_texts(tree: Dict) -> List[str]:
    """遞迴收集 rag_tree sections 內所有譯文字串（保序）。"""
    out: List[str] = []

    def _walk(node):
        if isinstance(node, dict):
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for x in node:
                _walk(x)
        elif isinstance(node, str):
            out.append(node)

    _walk(tree.get("sections", tree) if isinstance(tree, dict) else tree)
    return out


def _diff_d2(golden_tree: Dict, candidate_tree: Dict) -> Dict:
    """D2 譯文逐 Section 相似度（token 級 ratio）。退化＝相似度 < 門檻或 Section 數不符。"""
    b = _collect_section_texts(golden_tree)
    c = _collect_section_texts(candidate_tree)
    if len(b) != len(c):
        return {
            "degraded": True, "reason": "section_count_mismatch",
            "golden_sections": len(b), "candidate_sections": len(c),
            "min_similarity": 0.0,
        }
    sims = [
        difflib.SequenceMatcher(None, _normalize_text(x), _normalize_text(y)).ratio()
        for x, y in zip(b, c)
    ]
    min_sim = min(sims) if sims else 1.0
    mean_sim = sum(sims) / len(sims) if sims else 1.0
    return {
        "degraded": min_sim < _D2_SIM_THRESHOLD,
        "section_count": len(b),
        "min_similarity": round(min_sim, 4),
        "mean_similarity": round(mean_sim, 4),
        "threshold": _D2_SIM_THRESHOLD,
    }


def _diff_d3(golden_recall: Dict, candidate_recall: Dict) -> Dict:
    """D3 RAG 召回 Jaccard 重疊。退化＝重疊 < 門檻、query 缺漏或命中集合縮減。"""
    per_query: Dict[str, Dict] = {}
    degraded = False
    jaccards: List[float] = []
    for q, bdata in golden_recall.items():
        bset = {h["content_sha256"] for h in bdata.get("hits", [])}
        cdata = candidate_recall.get(q)
        if cdata is None:
            per_query[q] = {"degraded": True, "reason": "query_missing"}
            degraded = True
            continue
        cset = {h["content_sha256"] for h in cdata.get("hits", [])}
        inter = len(bset & cset)
        union = len(bset | cset) or 1
        jac = inter / union
        jaccards.append(jac)
        shrink = len(cset) < len(bset)
        q_degraded = jac < _D3_JACCARD_THRESHOLD or shrink
        if q_degraded:
            degraded = True
        per_query[q] = {
            "jaccard": round(jac, 4),
            "golden_hits": len(bset),
            "candidate_hits": len(cset),
            "shrink": shrink,
            "degraded": q_degraded,
        }
    return {
        "degraded": degraded,
        "min_jaccard": round(min(jaccards), 4) if jaccards else 0.0,
        "threshold": _D3_JACCARD_THRESHOLD,
        "per_query": per_query,
    }


def _aggregate_verdict(d1: Dict, d2: Dict, d3: Dict, improvement: bool) -> str:
    """三維度紅綠燈裁決（plan v2 §2.5.2 步驟 6 / §2 U4）。"""
    fails = [name for name, r in (("D1", d1), ("D2", d2), ("D3", d3)) if r["degraded"]]
    if not fails:
        return "PASS"
    return "IMPROVEMENT_PENDING_REVIEW" if improvement else "FAIL"


def _verify_manifest(snapshot_dir: Path) -> None:
    """驗證快照 manifest checksum（plan v2 §2.5.2 步驟 2 防竄改）。不符即拋例外拒比對。"""
    manifest_path = snapshot_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"快照缺 manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, expected in manifest.get("checksums", {}).items():
        actual = _sha256(snapshot_dir / name)
        if actual != expected:
            raise ValueError(f"基準被竄改、拒絕比對：{name} checksum 不符")


def _load_snapshot(snapshot_dir: Path) -> Dict:
    """讀取快照三維度產物（golden 格式：D1_zh/D1_en/D2_rag_tree/D3_recall）。"""
    missing = [f for f in _SNAPSHOT_FILES if not (snapshot_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"快照缺檔 {missing} @ {snapshot_dir}")
    return {
        "D1_zh": (snapshot_dir / "D1_zh.md").read_text(encoding="utf-8"),
        "D1_en": (snapshot_dir / "D1_en.md").read_text(encoding="utf-8"),
        "D2": json.loads((snapshot_dir / "D2_rag_tree.json").read_text(encoding="utf-8")),
        "D3": json.loads((snapshot_dir / "D3_recall.json").read_text(encoding="utf-8")),
    }


def _render_report_md(report: Dict) -> str:
    """人類可讀 Diff 報告（plan v2 §2 U3 雙格式輸出）。"""
    v = report["verdict"]
    icon = {"PASS": "🟢", "FAIL": "🔴", "IMPROVEMENT_PENDING_REVIEW": "🟡"}.get(v, "❔")
    lines = [
        f"# GOLDEN-BASELINE Diff 報告 — {report['doc_type']}",
        "",
        f"- **裁決（verdict）**：{icon} {v}",
        f"- **候選來源**：`{report['candidate']}`",
        f"- **時間**：{report['timestamp']}",
        "",
        "## D1 排版結構樹",
        f"- 退化：{'是' if report['d1']['degraded'] else '否'}",
    ]
    for d in report["d1"]["deltas"]:
        lines.append(f"  - {d}")
    lines += [
        "",
        "## D2 譯文相似度",
        f"- 退化：{'是' if report['d2']['degraded'] else '否'}"
        f"（min_sim={report['d2'].get('min_similarity')} / 門檻 {report['d2'].get('threshold')}）",
        "",
        "## D3 RAG 召回 Jaccard",
        f"- 退化：{'是' if report['d3']['degraded'] else '否'}"
        f"（min_jaccard={report['d3'].get('min_jaccard')} / 門檻 {report['d3'].get('threshold')}）",
    ]
    for q, r in report["d3"].get("per_query", {}).items():
        lines.append(f"  - `{q[:30]}…` → {r}")
    return "\n".join(lines) + "\n"


def _diff_one(doc_type: str, candidate_dir: Path, improvement: bool, ts: str) -> Dict:
    """單路比對：checksum 校驗 → 載入 → 三維度 Diff → 裁決 → 雙格式報告。"""
    golden_dir = _GOLDEN_DIR / doc_type
    if not golden_dir.exists():
        raise FileNotFoundError(
            f"無黃金基準可比、請先 capture: {golden_dir}"
        )
    _verify_manifest(golden_dir)  # 竄改 → 拋例外拒比對

    golden = _load_snapshot(golden_dir)
    candidate = _load_snapshot(candidate_dir)

    d1 = _diff_d1(golden, candidate)
    d2 = _diff_d2(golden["D2"], candidate["D2"])
    d3 = _diff_d3(golden["D3"], candidate["D3"])
    verdict = _aggregate_verdict(d1, d2, d3, improvement)

    report = {
        "doc_type": doc_type,
        "verdict": verdict,
        "candidate": str(candidate_dir),
        "timestamp": ts,
        "d1": d1, "d2": d2, "d3": d3,
    }
    out_dir = _REPORT_DIR / f"{doc_type}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "diff_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "diff_report.md").write_text(_render_report_md(report), encoding="utf-8")
    logger.info(
        f"[golden diff] {doc_type} verdict={verdict} → {out_dir}"
    )
    return report


def cmd_diff(args: argparse.Namespace) -> int:
    """diff 子命令入口（plan v2 §2.5.2）。"""
    if args.doc_type not in DOC_TYPES:
        logger.error(f"未知 doc_type={args.doc_type!r}，合法值: {DOC_TYPES}")
        return 2
    candidate_dir = Path(args.candidate)
    if not candidate_dir.is_dir():
        logger.error(f"候選快照目錄不存在: {candidate_dir}")
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        report = _diff_one(args.doc_type, candidate_dir, args.improvement, ts)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"[golden diff] {args.doc_type} 比對中止: {e}", exc_info=True)
        return 2
    # PASS / IMPROVEMENT → 0（不阻擋）；FAIL → 1（紅燈阻擋 Flip）
    return 1 if report["verdict"] == "FAIL" else 0


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

    p_diff = sub.add_parser(
        "diff", help="比對候選快照 vs 黃金快照，輸出三維度退化裁決與雙格式報告"
    )
    p_diff.add_argument(
        "doc_type", help=f"doc_type（{'/'.join(DOC_TYPES)}）"
    )
    p_diff.add_argument(
        "--candidate", required=True,
        help="候選快照目錄（golden 格式：D1_zh/D1_en/D2_rag_tree/D3_recall）；"
             "自比對歸零可指向 tests/golden_baseline/golden/<doc_type>",
    )
    p_diff.add_argument(
        "--improvement", action="store_true",
        help="標記已知改善：FAIL 改判 IMPROVEMENT_PENDING_REVIEW（待 baron 複核）",
    )
    p_diff.set_defaults(func=cmd_diff)
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
