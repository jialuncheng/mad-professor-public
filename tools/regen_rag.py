"""
tools/regen_rag.py — MODEL-8 backfill CLI（C3）

用法:
  python tools/regen_rag.py --check                  # 掃所有 paper / 印 mismatch
  python tools/regen_rag.py --check --owner 1        # 限定 owner
  python tools/regen_rag.py --paper <uuid> --owner 1 # 重 embed 單一 paper
  python tools/regen_rag.py --all                    # 全部 paper 重 embed
  python tools/regen_rag.py --all --force            # 不檢查 mismatch、強制重 embed
  python tools/regen_rag.py --all --dry-run          # 不實際執行、印會做什麼
  python tools/regen_rag.py --init                   # 一次性從 vectors/ FAISS docstore 反向導入 paper_chunks

依據:
- plan: .claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md v3 §3.4
- 含修正 4 (write_index_meta_json module-level)
- 含修正 5 (不重做 get_paper_db_id)
- 含修正 6 (cmd_init 完整 pseudo-code)
- 含 Q4 / Q5 / Q11 / Q16
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# 確保 import 路徑正確（從 tools/ 跑、import 上層）
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def cmd_check(owner_id: Optional[int] = None) -> int:
    """掃 paper_chunks + 比對當前 settings、印 mismatch 清單。

    輸出格式:
      [OK]       owner=1 paper=DeHunt_CTO_Tzung-Yuan_Lee  model=gemini-embedding-2/768
      [MISMATCH] owner=1 paper=hvdc_slides                stored=gemini-embedding-2/768 current=gemini-embedding-3/768

    Returns:
        mismatch_count（CLI exit code、給 CI 用、依 plan §3.4）
    """
    import settings
    import paper_manager

    papers = paper_manager.list_papers_with_chunks(owner_id=owner_id)

    if not papers:
        print("[INFO] paper_chunks 表內無資料、跑 --init 先導入既有 paper")
        return 0

    mismatches = 0
    for p in papers:
        is_match = (
            p['embedding_model'] == settings.EMBEDDING_MODEL_NAME
            and p['output_dimensions'] == settings.EMBEDDING_OUTPUT_DIMENSIONS
        )
        if is_match:
            print(
                f"[OK] owner={p['owner_id']} paper={p['paper_uuid']} "
                f"model={p['embedding_model']}/{p['output_dimensions']}"
            )
        else:
            print(
                f"[MISMATCH] owner={p['owner_id']} paper={p['paper_uuid']} "
                f"stored={p['embedding_model']}/{p['output_dimensions']} "
                f"current={settings.EMBEDDING_MODEL_NAME}/{settings.EMBEDDING_OUTPUT_DIMENSIONS}"
            )
            mismatches += 1

    print(f"\n[SUMMARY] {len(papers)} papers, {mismatches} mismatch(es)")
    return mismatches


def cmd_regen(paper_db_id: int, owner_id: int, paper_uuid: str,
              force: bool = False, dry_run: bool = False) -> None:
    """重 embed 單一 paper：從 paper_chunks 讀 → 新 model embed → 覆寫 vectors/。

    步驟（依 plan §3.4）:
    1. 從 paper_chunks 讀 (raw_text, metadata_json, chunk_index)
    2. 若非 force：比對 stored.embedding_model vs current；一致則 skip
    3. 重建 Document（page_content=raw_text、metadata=metadata_json 反序列化）
    4. FAISS.from_documents(...) → save_local（覆寫舊 vectors/）
    5. paper_manager.replace_paper_chunks(...) 更新 embedding_model / output_dimensions
    6. 寫新 index_meta.json
    """
    if dry_run:
        print(f"[DRY-RUN] would regen paper {paper_uuid} (owner={owner_id})")
        return

    from langchain_core.documents import Document
    from langchain_community.vectorstores.faiss import FAISS
    from langchain_community.vectorstores.utils import DistanceStrategy
    from config import EmbeddingModel
    import settings
    from processor.rag_processor import write_index_meta_json, CHUNK_FILTER_VERSION
    import paper_manager

    logger = logging.getLogger("regen_rag.regen")

    # 讀 paper_chunks
    chunks = list(paper_manager.iter_paper_chunks(paper_db_id))
    if not chunks:
        print(f"[SKIP] paper {paper_uuid} 無 paper_chunks rows（先跑 --init）")
        return

    # 非 force 時檢查 mismatch
    first = chunks[0]
    if not force:
        is_match = (
            first['embedding_model'] == settings.EMBEDDING_MODEL_NAME
            and first['output_dimensions'] == settings.EMBEDDING_OUTPUT_DIMENSIONS
        )
        if is_match:
            print(
                f"[SKIP] paper {paper_uuid} model match "
                f"(use --force to override)"
            )
            return

    # 重建 Document + 準備新 rows
    docs = []
    rows_for_db = []
    for c in chunks:
        meta = json.loads(c['metadata_json']) if c['metadata_json'] else {}
        docs.append(Document(page_content=c['raw_text'], metadata=meta))
        rows_for_db.append({
            "chunk_index": c['chunk_index'],
            "chunk_key": c['chunk_key'],
            "raw_text": c['raw_text'],
            "translated_text": c['translated_text'],
            "doc_type": c['doc_type'],
            "metadata_json": c['metadata_json'],
            # 更新為新 model
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "output_dimensions": settings.EMBEDDING_OUTPUT_DIMENSIONS,
            "chunk_filter_version": CHUNK_FILTER_VERSION,
        })

    # 重 embed + 覆寫 FAISS（distance_strategy 跟 C2 既有 _create_vector_store 一致）
    embedder = EmbeddingModel.get_instance()
    vs = FAISS.from_documents(
        documents=docs,
        embedding=embedder,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )

    vectors_dir = settings.OUTPUT_DIR / str(owner_id) / paper_uuid / 'vectors'
    vectors_dir.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(vectors_dir))

    # 更新 paper_chunks 內 embedding_model 標記
    paper_manager.replace_paper_chunks(paper_db_id, rows_for_db)

    # 寫新 index_meta.json（修正 4 module-level helper）
    write_index_meta_json(vectors_dir, len(docs), logger=logger)

    print(f"[OK] paper {paper_uuid} re-embedded ({len(docs)} chunks)")


def cmd_all(force: bool = False, dry_run: bool = False,
            owner_id: Optional[int] = None) -> None:
    """對所有 paper（或 owner 過濾後）執行 cmd_regen。

    依 Q5：單緒、避免併發寫 SQLite + embedding API rate limit。
    """
    import paper_manager

    papers = paper_manager.list_papers_with_chunks(owner_id=owner_id)
    if not papers:
        print("[INFO] paper_chunks 表內無資料、跑 --init 先導入既有 paper")
        return

    print(f"[INFO] 處理 {len(papers)} paper(s)...")
    for p in papers:
        cmd_regen(
            p['paper_db_id'], p['owner_id'], p['paper_uuid'],
            force=force, dry_run=dry_run,
        )


def cmd_init(owner_id: Optional[int] = None, dry_run: bool = False) -> None:
    """一次性把既有 paper（C1/C2 ship 前）從 vectors/ FAISS docstore 反向導入 paper_chunks。

    依 plan §3.4 修正 6 完整 pseudo-code:
    1. 掃 OUTPUT_DIR/<owner>/<paper_uuid>/vectors/ 找所有有 index.faiss 的 paper
    2. 為每個 paper 檢查 paper_chunks 是否已有 rows、有則跳過
    3. 用 FAISS.load_local 讀 docstore（含原 Document.page_content + metadata）
    4. paper_manager.replace_paper_chunks(...) 寫入
    5. 寫新 index_meta.json
    """
    from langchain_community.vectorstores.faiss import FAISS
    from config import EmbeddingModel
    import settings
    from processor.rag_processor import write_index_meta_json, CHUNK_FILTER_VERSION
    import paper_manager

    logger = logging.getLogger("regen_rag.init")
    embedder = EmbeddingModel.get_instance() if not dry_run else None

    init_count = 0
    skip_count = 0

    for vectors_dir in sorted(settings.OUTPUT_DIR.glob('*/*/vectors')):
        if not (vectors_dir / 'index.faiss').exists():
            continue

        owner_dir_name = vectors_dir.parent.parent.name
        paper_uuid = vectors_dir.parent.name

        try:
            owner_id_int = int(owner_dir_name)
        except ValueError:
            logger.warning(f"[init] skip non-int owner dir: {owner_dir_name}")
            continue

        if owner_id is not None and owner_id_int != owner_id:
            continue

        # 拿 paper_db_id（修正 5：既有 helper）
        paper_db_id = paper_manager.get_paper_db_id(owner_id_int, paper_uuid)
        if paper_db_id is None:
            logger.warning(
                f"[init] skip orphan {vectors_dir} (no paper in DB)"
            )
            continue

        # 若已有 paper_chunks rows、跳過（避免覆寫 C2 ship 後寫入的真實資料）
        existing = list(paper_manager.iter_paper_chunks(paper_db_id))
        if existing:
            logger.info(
                f"[init] skip {paper_uuid} (already has {len(existing)} chunks)"
            )
            skip_count += 1
            continue

        if dry_run:
            print(f"[DRY-RUN] would init {paper_uuid} (owner={owner_id_int})")
            init_count += 1
            continue

        # 從 FAISS docstore 反向取
        try:
            vs = FAISS.load_local(
                str(vectors_dir),
                embedder,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            logger.error(f"[init] FAISS load failed for {paper_uuid}: {e}")
            continue

        # docstore 是 InMemoryDocstore、._dict 內含 doc_id → Document 對應
        rows = []
        for i, (_doc_id, doc) in enumerate(vs.docstore._dict.items()):
            chunk_key = (doc.metadata or {}).get('Header', '') or f"chunk_{i}"
            rows.append({
                "chunk_index": i,
                "chunk_key": chunk_key[:255],
                "raw_text": doc.page_content or '',
                "translated_text": None,
                # Q16: init 場景 doc_type 已不可考、留空；未來可手寫 SQL UPDATE 跨表補
                "doc_type": "",
                "metadata_json": json.dumps(
                    doc.metadata or {}, ensure_ascii=False
                ),
                "embedding_model": settings.EMBEDDING_MODEL_NAME,
                "output_dimensions": settings.EMBEDDING_OUTPUT_DIMENSIONS,
                "chunk_filter_version": CHUNK_FILTER_VERSION,
            })

        paper_manager.replace_paper_chunks(paper_db_id, rows)
        write_index_meta_json(vectors_dir, len(rows), logger=logger)

        print(f"[OK] init {paper_uuid} ({len(rows)} chunks reverse-imported)")
        init_count += 1

    print(f"\n[SUMMARY] init={init_count}, skip={skip_count}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--check', action='store_true',
        help='掃所有 paper / 印 mismatch',
    )
    parser.add_argument(
        '--paper', metavar='UUID',
        help='重 embed 單一 paper（搭配 --owner）',
    )
    parser.add_argument(
        '--all', action='store_true',
        help='全部 paper 重 embed',
    )
    parser.add_argument(
        '--owner', type=int,
        help='限定 owner_id',
    )
    parser.add_argument(
        '--force', action='store_true',
        help='略過 mismatch 檢查、強制重 embed',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='不實際執行、印會做什麼',
    )
    parser.add_argument(
        '--init', action='store_true',
        help='從 vectors/ FAISS docstore 反向導入 paper_chunks（修正 6）',
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(cmd_check(owner_id=args.owner))
    elif args.init:
        cmd_init(owner_id=args.owner, dry_run=args.dry_run)
    elif args.paper:
        # 修正 5: 用既有 paper_manager.get_paper_db_id
        import paper_manager
        if args.owner is None:
            sys.exit("[ERROR] --paper 需搭配 --owner <id>")
        pid = paper_manager.get_paper_db_id(args.owner, args.paper)
        if pid is None:
            sys.exit(
                f"[ERROR] paper not found: owner={args.owner} uuid={args.paper}"
            )
        cmd_regen(
            pid, args.owner, args.paper,
            force=args.force, dry_run=args.dry_run,
        )
    elif args.all:
        cmd_all(force=args.force, dry_run=args.dry_run, owner_id=args.owner)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    main()
