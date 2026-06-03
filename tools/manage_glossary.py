"""GLOSSARY-CORE 中央術語庫 自癒補丁 CLI（GLOSSARY-CORE C5）。

依 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C5 + plan v2 §2 U5。
對齊 tools/regen_rag.py 的 CLI / setup_logging pattern。

子命令：
  --init                       建立 GlobalGlossary 等表（create_all）。
  --test-pipeline --pdf PATH   離線閉環測試：DomainDetector.detect → normalize_to_lcc →
                               query_cascade 比對 → extract_terms → upsert_terms →
                               輸出 {stem}_glossary.json。
  --backfill-existing-papers   掃 papers 表，對每筆 domain 跑 normalize_to_lcc 升級為 LCC，
                               分批極短交易寫回（防 SQLite locked）。

日誌：CLI 入口統一 `setup_logging()`（嚴禁 logging.basicConfig）。
資料庫：批次回填採分批極短交易 `with session.begin():`（database SOP）。
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logger = logging.getLogger(__name__)

# 批次回填每批筆數（極短交易邊界、防 database locked）。
_BACKFILL_BATCH_SIZE = 10


def cmd_init() -> int:
    """建立所有資料表（含 GlobalGlossary）。可重複呼叫（已存在不重建）。"""
    from db import engine
    from models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("[glossary-cli] init：資料表已就緒（create_all 冪等）")
    return 0


def cmd_test_pipeline(pdf_path: str) -> int:
    """離線閉環測試：detect → normalize_to_lcc → cascade → extract → upsert → 輸出 json。"""
    from processor.domain_detector import DomainDetector
    from processor.domain_normalizer import normalize_to_lcc
    from processor.glossary_extractor import GlossaryManager

    pdf = Path(pdf_path)
    if not pdf.exists():
        logger.error("[glossary-cli] PDF 不存在：%s", pdf_path)
        return 1

    # 1) 偵測 raw 領域
    raw_domain = DomainDetector().detect(str(pdf))
    logger.info("[glossary-cli] detect raw_domain=%r", raw_domain)

    # 2) 標準化為 LCC（消費 DOMAIN-NORM；旗標 OFF 時原樣回傳 raw）
    lcc = normalize_to_lcc(raw_domain, context_text=None)
    logger.info("[glossary-cli] normalize_to_lcc → %r", lcc)

    gm = GlossaryManager()
    # 3) 級聯查詢既有術語（比對）
    existing = gm.query_cascade("en", "zh-tw", lcc)
    logger.info("[glossary-cli] 既有術語 %d 筆", len(existing))

    # 4) 提取（此處以第一頁文字作來源樣本；無譯文時提取多半空、屬離線測試正常）
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf))
        sample = (doc[0].get_text() or "")[:3000] if len(doc) else ""
        doc.close()
    except Exception:
        logger.error("[glossary-cli] 讀取 PDF 文字失敗", exc_info=True)
        sample = ""
    pairs = gm.extract_terms(sample, sample, "en", "zh-tw", lcc)  # LLM 交易外
    logger.info("[glossary-cli] 提取術語 %d 筆", len(pairs))

    # 5) 回填（冪等）
    written = gm.upsert_terms(pairs, "en", "zh-tw", lcc)

    # 6) 輸出 {stem}_glossary.json
    out_path = pdf.with_name(f"{pdf.stem}_glossary.json")
    payload = {
        "pdf": str(pdf),
        "raw_domain": raw_domain,
        "lcc": lcc,
        "existing_terms": existing,
        "extracted_terms": [{"original": o, "translation": t} for o, t in pairs],
        "written": written,
    }
    try:
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("[glossary-cli] 輸出閉環結果 → %s", out_path)
    except Exception:
        logger.error("[glossary-cli] 輸出 json 失敗", exc_info=True)
        return 1
    return 0


def cmd_backfill_existing_papers(dry_run: bool = False) -> int:
    """掃 papers 表，對每筆 domain 跑 normalize_to_lcc 升級為 LCC，分批極短交易寫回。"""
    from sqlalchemy import select
    from db import SessionLocal
    from models import Paper
    from processor.domain_normalizer import normalize_to_lcc

    # 1) 唯讀載出待升級清單（極短交易）
    with SessionLocal() as session:
        rows = session.execute(
            select(Paper.id, Paper.domain).where(Paper.domain.isnot(None))
        ).all()
    logger.info("[glossary-cli] backfill 掃描 %d 筆 paper", len(rows))

    # 2) 交易外計算每筆 LCC（normalize_to_lcc 內部可能呼 LLM、不可在交易內）
    updates = []
    for paper_id, raw_domain in rows:
        if not raw_domain:
            continue
        lcc = normalize_to_lcc(raw_domain, context_text=None)
        if lcc and lcc != raw_domain:
            updates.append((paper_id, lcc))
    logger.info("[glossary-cli] 待升級 %d 筆（domain → LCC）", len(updates))

    if dry_run:
        for pid, lcc in updates[:50]:
            logger.info("[glossary-cli][dry-run] paper id=%s → domain=%s", pid, lcc)
        return 0

    # 3) 分批極短交易寫回（每 _BACKFILL_BATCH_SIZE 筆一個 begin()，防 database locked）
    written = 0
    for i in range(0, len(updates), _BACKFILL_BATCH_SIZE):
        batch = updates[i:i + _BACKFILL_BATCH_SIZE]
        try:
            with SessionLocal() as session:
                with session.begin():
                    for paper_id, lcc in batch:
                        obj = session.get(Paper, paper_id)
                        if obj is not None:
                            obj.domain = lcc
                            written += 1
            logger.info("[glossary-cli] 已寫回批次 %d-%d", i, i + len(batch))
        except Exception:
            logger.error("[glossary-cli] 批次 %d 寫回失敗（跳過續行）", i, exc_info=True)
    logger.info("[glossary-cli] backfill 完成、實際升級 %d 筆", written)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--init", action="store_true",
        help="建立 GlobalGlossary 等資料表（create_all）",
    )
    parser.add_argument(
        "--test-pipeline", action="store_true",
        help="離線閉環測試（搭配 --pdf）",
    )
    parser.add_argument(
        "--pdf", metavar="PATH",
        help="--test-pipeline 的輸入 PDF 路徑",
    )
    parser.add_argument(
        "--backfill-existing-papers", action="store_true",
        help="掃歷史 paper、domain 經 normalize_to_lcc 批次升級為 LCC",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="不實際寫入、僅印將執行的動作",
    )
    args = parser.parse_args()

    if args.init:
        return cmd_init()
    elif args.test_pipeline:
        if not args.pdf:
            sys.exit("[ERROR] --test-pipeline 需搭配 --pdf <path>")
        return cmd_test_pipeline(args.pdf)
    elif args.backfill_existing_papers:
        return cmd_backfill_existing_papers(dry_run=args.dry_run)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    # 對齊 LOGGING-3：CLI 統一 setup_logging（嚴禁 logging.basicConfig）
    from utils.logging_config import setup_logging
    setup_logging()
    sys.exit(main())
