import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from config import EmbeddingModel
from settings import RAG_SCORE_THRESHOLD

logger = logging.getLogger(__name__)


class RagRetriever:
    """RAG 檢索器，用於從向量庫中檢索相關內容"""

    def __init__(self, base_path: str = None):
        # Phase 0: 鍵改 (owner_id, paper_uuid) tuple，避免跨 owner 相同 sanitize 撞名
        self.vector_stores: Dict[Tuple[int, str], FAISS] = {}
        self.paper_vector_paths: Dict[Tuple[int, str], str] = {}
        self.rag_trees: Dict[Tuple[int, str], Dict] = {}
        self.base_path = base_path
        # 向量庫路徑與 rag_tree 由 paper_manager（DB 來源）透過
        # add_paper / set_rag_tree 註冊，不再讀 papers_index.json。

    def set_rag_tree(self, owner_id: int, paper_id: str, tree: Dict) -> None:
        """由 ai_core 載入 rag_tree 後註冊到記憶體（取代讀 papers_index.json）。"""
        if tree:
            self.rag_trees[(owner_id, paper_id)] = tree

    def add_paper(self, owner_id: int, paper_id: str, vector_store_path: str) -> bool:
        """新增論文向量庫"""
        try:
            key = (owner_id, paper_id)
            self.paper_vector_paths[key] = vector_store_path
            logger.info(f"添加新论文向量库: owner={owner_id} {paper_id} -> {vector_store_path}")
            vector_store = self.load_vector_store(vector_store_path)
            if vector_store:
                self.vector_stores[key] = vector_store
                logger.info(f"成功加载新论文 owner={owner_id} {paper_id} 的向量库")
                return True
            return False
        except Exception as e:
            logger.error(f"添加新论文 owner={owner_id} {paper_id} 失敗: {str(e)}")
            return False

    def load_vector_store(self, vector_store_path: str) -> Optional[FAISS]:
        """載入向量庫"""
        path = Path(vector_store_path)
        if not path.exists() or not (path / "index.faiss").exists():
            logger.error(f"向量庫路徑不存在: {vector_store_path}")
            return None
        try:
            store = FAISS.load_local(
                vector_store_path,
                EmbeddingModel.get_instance(),
                allow_dangerous_deserialization=True,
                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,  # 對齊建立端（rag_processor）
            )
            logger.info(f"成功加载向量库: {vector_store_path}")
            return store
        except Exception as e:
            logger.error(f"載入向量庫失敗: {str(e)}")
            return None

    def _get_vector_store(self, owner_id: int, paper_id: str) -> Optional[FAISS]:
        """取得向量庫（lazy load）"""
        key = (owner_id, paper_id)
        if key in self.vector_stores:
            return self.vector_stores[key]
        if key in self.paper_vector_paths:
            store = self.load_vector_store(self.paper_vector_paths[key])
            if store:
                self.vector_stores[key] = store
                return store
        return None

    def load_rag_tree(self, owner_id: int, paper_id: str) -> Dict:
        """回傳記憶體中的 RAG tree（由 set_rag_tree 註冊；不再讀 papers_index.json）。"""
        return self.rag_trees.get((owner_id, paper_id), {})

    def is_ready(self) -> bool:
        """檢查是否已有向量庫路徑"""
        return bool(self.paper_vector_paths)

    def remove_paper(self, owner_id: int, paper_id: str) -> None:
        """移除該論文的向量快取（FAISS 實例、路徑映射、rag_tree）"""
        key = (owner_id, paper_id)
        self.vector_stores.pop(key, None)
        self.paper_vector_paths.pop(key, None)
        self.rag_trees.pop(key, None)
        logger.info(f"已移除論文向量快取: owner={owner_id} {paper_id}")

    def retrieve_with_context(self, owner_id: int, query: str, paper_id: str, top_k: int = 5) -> str:
        """從向量庫檢索相關內容，回傳結構化字串"""
        if not self.is_ready():
            return ""

        vector_store = self._get_vector_store(owner_id, paper_id)
        if not vector_store:
            return ""

        try:
            rag_tree = self.load_rag_tree(owner_id, paper_id)
            if not rag_tree:
                return ""

            docs_with_scores = vector_store.similarity_search_with_score(query=query, k=top_k)
            # IP metric 下 score 為 inner product 值（越大越相似），與建立端
            # MAX_INNER_PRODUCT 對齊。實測 Gemini embedding 768 dim 下：
            # 相關 query top score 約 0.23-0.27，無關 query 約 0.17-0.20。
            # 門檻 0.22 可有效區分。
            # Phase 4.7d Commit 15-2：score 分布 logging（觀察門檻 0.22
            # 是否需調整；15-1 chunk 結構改後分布可能變、依此 log 校準）
            if docs_with_scores:
                _scores = [s for _, s in docs_with_scores]
                logger.info(
                    f"[retrieve] owner={owner_id} paper={paper_id} "
                    f"query={query[:40]!r} top_k={top_k} "
                    f"scores={[round(s, 3) for s in _scores]} "
                    f"above_{RAG_SCORE_THRESHOLD}={sum(1 for s in _scores if s > RAG_SCORE_THRESHOLD)}"
                )
                # Phase 4.7? MODEL-1+2 階段 B2: raw score 詳細 logging（為 RAG-3 鋪路）
                # plan §4.3 + §3.6.1 修正 1：LangChain FAISS MAX_INNER_PRODUCT 回 raw IP
                # L2 normalize 後預期 = cosine [-1, 1] 子集；具體相關區間值待實測
                logger.info(
                    f"[retrieve raw] owner={owner_id} paper={paper_id} "
                    f"min={min(_scores):.4f} max={max(_scores):.4f} "
                    f"mean={sum(_scores)/len(_scores):.4f} "
                    f"threshold={RAG_SCORE_THRESHOLD} "
                    f"raw_scores={[f'{s:.4f}' for s in _scores]}"
                )
            # Phase 4.7? MODEL-1+2 階段 B2 修正 1：閾值 env 化（plan §4.6）
            filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > RAG_SCORE_THRESHOLD]

            if not filtered_docs:
                return ""

            section_paths = []
            for doc, score in filtered_docs:
                if 'Header' in doc.metadata:
                    header_key = doc.metadata['Header']
                    if header_key in rag_tree.get('key_map', {}):
                        section_paths.append(rag_tree['key_map'][header_key])

            if not section_paths:
                return ""

            retrieved_sections = {}
            for path in section_paths:
                node = self._get_node_from_path(rag_tree, path)
                if node:
                    retrieved_sections[path] = node
                    self._add_adjacent_formulas(rag_tree, path, retrieved_sections)

            # Phase 4.7d Commit 15-2：result 標頭含 paper_title、引用源頭明確
            _paper_title = rag_tree.get('translated_title') or rag_tree.get('title') or ''
            if _paper_title:
                result_parts = [f"以下是論文《{_paper_title}》中與您問題最相關的內容:"]
            else:
                result_parts = ["以下是論文中與您問題最相關的內容:"]
            for path in sorted(retrieved_sections.keys()):
                node = retrieved_sections[path]
                section_title = self._build_section_title(rag_tree, path)
                result_parts.append(f"\n## {section_title}")

                if node.get('type') == 'text':
                    result_parts.append(node.get('translated_content', '') or node.get('content', ''))
                elif node.get('type') == 'formula':
                    result_parts.append(node.get('content', ''))
                    if 'formula_analysis' in node:
                        result_parts.append(f"公式解釋: {node['formula_analysis']}")
                elif node.get('type') in ('figure', 'table'):
                    caption = node.get('translated_caption', '') or node.get('caption', '')
                    if caption:
                        result_parts.append(caption)
                elif 'summary' in node:
                    result_parts.append(f"摘要: {node['summary']}")

            return "\n\n".join(result_parts)

        except Exception as e:
            logger.error(f"結構化檢索失敗: {str(e)}")
            return ""

    def _get_node_from_path(self, tree: Dict, path: str) -> Dict:
        try:
            if path.startswith('/'):
                path = path[1:]
            parts = path.split('/')
            node = tree
            for part in parts:
                if part.isdigit():
                    part = int(part)
                if isinstance(node, dict) and part in node:
                    node = node[part]
                elif isinstance(node, list) and isinstance(part, int) and part < len(node):
                    node = node[part]
                else:
                    return {}
            return node
        except Exception:
            return {}

    def _add_adjacent_formulas(self, tree: Dict, path: str, retrieved_sections: Dict):
        try:
            if not path or not path.startswith('/'):
                return
            parts = path.split('/')
            if len(parts) >= 5 and parts[-2] == 'content':
                current_index = int(parts[-1])
                base_path = '/'.join(parts[:-1])
                if current_index > 0:
                    prev_path = f"{base_path}/{current_index - 1}"
                    prev_node = self._get_node_from_path(tree, prev_path)
                    if prev_node.get('type') == 'formula':
                        retrieved_sections[prev_path] = prev_node
                next_path = f"{base_path}/{current_index + 1}"
                next_node = self._get_node_from_path(tree, next_path)
                if next_node and next_node.get('type') == 'formula':
                    retrieved_sections[next_path] = next_node
        except Exception:
            pass

    def _build_section_title(self, tree: Dict, path: str) -> str:
        """從 rag_tree JSON path 算 section title。
        Phase 4.7d Commit 15-2：加 paper_title 前綴、引用源頭更明確；
        AI 答覆引用此標題時可顯示「{paper_title} > {section} > {child}」。
        """
        paper_title = tree.get('translated_title') or tree.get('title') or ''
        def _with_paper(inner: str) -> str:
            return f"{paper_title} > {inner}" if paper_title else inner
        try:
            if path.startswith('/'):
                path = path[1:]
            parts = path.split('/')
            if len(parts) >= 2 and parts[0] == 'sections':
                section_index = int(parts[1])
                if 'sections' in tree and section_index < len(tree['sections']):
                    section = tree['sections'][section_index]
                    title = section.get('translated_title', '') or section.get('title', '')
                    if len(parts) >= 4 and parts[2] == 'children':
                        child_index = int(parts[3])
                        if 'children' in section and child_index < len(section['children']):
                            child = section['children'][child_index]
                            child_title = child.get('translated_title', '') or child.get('title', '')
                            if child_title:
                                return _with_paper(f"{title} > {child_title}")
                    return _with_paper(title)
            return _with_paper(f"章節 {path}")
        except Exception:
            return _with_paper(f"章節 {path}")
