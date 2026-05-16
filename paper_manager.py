import re
import json
import shutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def sanitize_paper_id(filename: str) -> str:
    """清理檔名，產生合法的 paper_id"""
    stem = Path(filename).stem
    paper_id = re.sub(r'[^\w\-]', '_', stem)
    paper_id = re.sub(r'_+', '_', paper_id).strip('_')
    return paper_id


def load_papers_index(output_dir: Path) -> list:
    """讀取 papers_index.json"""
    index_path = output_dir / "papers_index.json"
    if not index_path.exists():
        return []
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def update_papers_index(output_dir: Path, paper_id: str, title: str,
                         translated_title: str, final_paths: dict) -> None:
    """更新 papers_index.json"""
    index_path = output_dir / "papers_index.json"
    papers_index = load_papers_index(output_dir)

    path_dict = {}
    for key, path in final_paths.items():
        if path:
            try:
                path_dict[key] = str(Path(path).relative_to(output_dir))
            except ValueError:
                path_dict[key] = str(path)

    paper_entry = {
        'id': paper_id,
        'title': title,
        'translated_title': translated_title,
        'paths': path_dict
    }

    existing_index = next(
        (i for i, e in enumerate(papers_index) if e.get('id') == paper_id), -1
    )
    if existing_index >= 0:
        papers_index[existing_index] = paper_entry
    else:
        papers_index.append(paper_entry)

    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(papers_index, f, ensure_ascii=False, indent=2)

    logger.info(f"papers_index 更新完成: {paper_id}")


def delete_paper(output_dir: Path, paper_id: str) -> bool:
    """刪除論文目錄和索引記錄"""
    paper_dir = output_dir / paper_id
    if not paper_dir.exists():
        return False

    shutil.rmtree(paper_dir)

    papers_index = load_papers_index(output_dir)
    papers_index = [p for p in papers_index if p['id'] != paper_id]

    index_path = output_dir / "papers_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(papers_index, f, ensure_ascii=False, indent=2)

    logger.info(f"論文已刪除: {paper_id}")
    return True


def load_chat_history(output_dir: Path, paper_id: str) -> list:
    """讀取對話紀錄"""
    history_path = output_dir / paper_id / "chat_history.json"
    if not history_path.exists():
        return []
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_chat_history(output_dir: Path, paper_id: str, messages: list) -> None:
    """儲存對話紀錄"""
    history_path = output_dir / paper_id / "chat_history.json"
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logger.info(f"對話紀錄已儲存: {paper_id}")


def preload_vector_stores(output_dir: Path, ai_core) -> None:
    """啟動時預載所有論文的向量庫和快取"""
    papers = load_papers_index(output_dir)
    for paper in papers:
        paper_id = paper['id']
        paths = paper.get('paths', {})
        vector_store = paths.get('rag_vector_store')
        rag_tree = paths.get('rag_tree')
        if vector_store:
            full_vector_path = output_dir / vector_store
            if full_vector_path.exists():
                ai_core.add_paper_vector_store(paper_id, str(full_vector_path))
                logger.info(f"預載向量庫: {paper_id}")
        if rag_tree:
            full_tree_path = output_dir / rag_tree
            if full_tree_path.exists():
                ai_core.load_paper_cache(paper_id, str(full_tree_path))


def load_paper_resources(output_dir: Path, paper_id: str,
                          final_paths: dict, ai_core) -> None:
    """論文處理完成後，載入向量庫和快取"""
    vector_store = final_paths.get('rag_vector_store')
    rag_tree = final_paths.get('rag_tree')

    if vector_store and Path(vector_store).exists():
        ai_core.add_paper_vector_store(paper_id, str(vector_store))

    if rag_tree and Path(rag_tree).exists():
        ai_core.load_paper_cache(paper_id, str(rag_tree))

    logger.info(f"論文資源載入完成: {paper_id}")
