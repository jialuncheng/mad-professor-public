import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores.faiss import FAISS
from config import EmbeddingModel

logger = logging.getLogger(__name__)


class RagRetriever:
    """RAG 檢索器，用於從向量庫中檢索相關內容"""

    def __init__(self, base_path: str = None):
        self.vector_stores: Dict[str, FAISS] = {}
        self.paper_vector_paths: Dict[str, str] = {}
        self.rag_trees: Dict[str, Dict] = {}
        self.base_path = base_path

        if base_path:
            self._preload_index(base_path)

    def _preload_index(self, base_path: str):
        """同步載入所有論文的向量庫路徑索引"""
        try:
            index_path = Path(base_path) / "papers_index.json"
            if not index_path.exists():
                logger.warning(f"論文索引不存在: {index_path}")
                return
            with open(index_path, 'r', encoding='utf-8') as f:
                papers_index = json.load(f)
            for paper in papers_index:
                paper_id = paper.get('id')
                vector_store_path = paper.get('paths', {}).get('rag_vector_store')
                if paper_id and vector_store_path:
                    self.paper_vector_paths[paper_id] = str(Path(base_path) / vector_store_path)
            logger.info(f"预加载了 {len(self.paper_vector_paths)} 篇论文的向量库路径")
        except Exception as e:
            logger.error(f"預載論文索引失敗: {str(e)}")

    def add_paper(self, paper_id: str, vector_store_path: str) -> bool:
        """新增論文向量庫"""
        try:
            self.paper_vector_paths[paper_id] = vector_store_path
            logger.info(f"添加新论文向量库: {paper_id} -> {vector_store_path}")
            vector_store = self.load_vector_store(vector_store_path)
            if vector_store:
                self.vector_stores[paper_id] = vector_store
                logger.info(f"成功加载新论文 {paper_id} 的向量库")
                return True
            return False
        except Exception as e:
            logger.error(f"添加新论文 {paper_id} 失敗: {str(e)}")
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
                allow_dangerous_deserialization=True
            )
            logger.info(f"成功加载向量库: {vector_store_path}")
            return store
        except Exception as e:
            logger.error(f"載入向量庫失敗: {str(e)}")
            return None

    def _get_vector_store(self, paper_id: str) -> Optional[FAISS]:
        """取得向量庫（lazy load）"""
        if paper_id in self.vector_stores:
            return self.vector_stores[paper_id]
        if paper_id in self.paper_vector_paths:
            store = self.load_vector_store(self.paper_vector_paths[paper_id])
            if store:
                self.vector_stores[paper_id] = store
                return store
        return None

    def load_rag_tree(self, paper_id: str) -> Dict:
        """載入論文的 RAG tree"""
        if paper_id in self.rag_trees:
            return self.rag_trees[paper_id]
        try:
            if not self.base_path:
                return {}
            index_path = Path(self.base_path) / "papers_index.json"
            if not index_path.exists():
                return {}
            with open(index_path, 'r', encoding='utf-8') as f:
                papers_index = json.load(f)
            rag_tree_path = None
            for paper in papers_index:
                if paper.get('id') == paper_id:
                    rag_tree_path = paper.get('paths', {}).get('rag_tree')
                    break
            if not rag_tree_path:
                return {}
            full_path = Path(self.base_path) / rag_tree_path
            if not full_path.exists():
                return {}
            with open(full_path, 'r', encoding='utf-8') as f:
                rag_tree = json.load(f)
            self.rag_trees[paper_id] = rag_tree
            return rag_tree
        except Exception as e:
            logger.error(f"載入 RAG tree 失敗: {str(e)}")
            return {}

    def is_ready(self) -> bool:
        """檢查是否已有向量庫路徑"""
        return bool(self.paper_vector_paths)

    def remove_paper(self, paper_id: str) -> None:
        """移除該論文的向量快取（FAISS 實例、路徑映射、rag_tree）"""
        self.vector_stores.pop(paper_id, None)
        self.paper_vector_paths.pop(paper_id, None)
        self.rag_trees.pop(paper_id, None)
        logger.info(f"已移除論文向量快取: {paper_id}")

    def retrieve_with_context(self, query: str, paper_id: str, top_k: int = 5) -> str:
        """從向量庫檢索相關內容，回傳結構化字串"""
        if not self.is_ready():
            return ""

        vector_store = self._get_vector_store(paper_id)
        if not vector_store:
            return ""

        try:
            rag_tree = self.load_rag_tree(paper_id)
            if not rag_tree:
                return ""

            docs_with_scores = vector_store.similarity_search_with_score(query=query, k=top_k)
            filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.6]

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
                                return f"{title} > {child_title}"
                    return title
            return f"章節 {path}"
        except Exception:
            return f"章節 {path}"
