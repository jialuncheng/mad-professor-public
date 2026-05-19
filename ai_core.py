import logging
import json
import threading
from typing import AsyncGenerator, Optional, Dict, Any
from AI_professor_chat import AIProfessorChat
from rag_retriever import RagRetriever

logger = logging.getLogger(__name__)


class AICore:
    """AI 核心模組（不依賴 Qt，供 Web API 使用）"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.ai_chat = AIProfessorChat()
        self.retriever: Optional[RagRetriever] = None
        self.is_generating = False
        self._generating_lock = threading.Lock()
        self._paper_cache: Dict[str, Any] = {}

    def init_rag_retriever(self, base_path: str) -> bool:
        """初始化 RAG 檢索器"""
        try:
            self.logger.info(f"初始化 RAG 檢索器: {base_path}")
            self.retriever = RagRetriever(base_path)
            self.ai_chat.retriever = self.retriever
            self.logger.info("RAG 檢索器初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"初始化 RAG 檢索器失敗: {str(e)}")
            return False

    def add_paper_vector_store(self, paper_id: str, vector_store_path: str) -> bool:
        """新增論文向量庫"""
        if self.retriever:
            return self.retriever.add_paper(paper_id, vector_store_path)
        return False

    def set_paper_context(self, paper_id: str, paper_data: Dict[str, Any]) -> bool:
        """設定當前論文上下文"""
        return self.ai_chat.set_paper_context(paper_id, paper_data)

    def query_stream(self, query: str, paper_id: Optional[str] = None,
                     visible_content: Optional[str] = None,
                     use_web_search: bool = False):
        """
        同步 generator，逐句回傳 AI 回答。
        Web API 用 SSE 推送每個 chunk。

        Yields:
            dict: {'sentence': str, 'done': bool}
            done=True 時另帶 'grounding_sources': list[{'title','uri'}]
        """
        if not self._generating_lock.acquire(blocking=False):
            yield {'sentence': '目前有其他對話正在生成中，請稍候再試。',
                   'done': True}
            return
        try:
            self.is_generating = True

            # 取得論文上下文（一律注入；cache-miss 以無論文模式回答）
            paper_data = self._paper_cache.get(paper_id) if paper_id else None
            if paper_id and paper_data is None:
                self.logger.warning(f"paper_id {paper_id} 不在快取中，以無論文模式回答")

            for sentence in self.ai_chat.process_query_stream(
                query, visible_content, paper_id=paper_id, paper_data=paper_data,
                use_web_search=use_web_search
            ):
                if not self.is_generating:
                    break
                yield {
                    'sentence': sentence,
                    'done': False
                }

            yield {'sentence': '', 'done': True,
                   'grounding_sources': self.ai_chat.last_grounding_sources or []}

        except Exception as e:
            self.logger.error(f"query_stream 失敗: {str(e)}")
            yield {'sentence': f'抱歉，處理問題時出現錯誤: {str(e)}',
                   'done': True, 'grounding_sources': []}
        finally:
            self.is_generating = False
            self._generating_lock.release()

    def cancel(self):
        """取消當前生成"""
        self.is_generating = False

    def load_paper_cache(self, paper_id: str, rag_tree_path: str) -> bool:
        """載入論文的 RAG tree 到快取"""
        try:
            with open(rag_tree_path, 'r', encoding='utf-8') as f:
                paper_data = json.load(f)
            self._paper_cache[paper_id] = paper_data
            # 同步註冊到 retriever（取代其讀 papers_index.json）
            if self.retriever:
                self.retriever.set_rag_tree(paper_id, paper_data)
            return True
        except Exception as e:
            self.logger.error(f"載入論文快取失敗: {str(e)}")
            return False

    def remove_paper(self, paper_id: str) -> None:
        """移除該論文的所有記憶體快取（_paper_cache、retriever、當前對話上下文）"""
        if paper_id in self._paper_cache:
            del self._paper_cache[paper_id]
        if self.retriever:
            self.retriever.remove_paper(paper_id)
        if self.ai_chat.current_paper_id == paper_id:
            self.ai_chat.current_paper_id = None
            self.ai_chat.current_paper_data = None
        self.logger.info(f"已移除論文快取: {paper_id}")