import logging
import json
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
                     visible_content: Optional[str] = None):
        """
        同步 generator，逐句回傳 AI 回答。
        Web API 用 SSE 推送每個 chunk。

        Yields:
            dict: {'sentence': str, 'emotion': str, 'done': bool}
        """
        try:
            self.is_generating = True

            # 設定論文上下文
            if paper_id:
                paper_data = self._paper_cache.get(paper_id)
                if paper_data:
                    self.ai_chat.set_paper_context(paper_id, paper_data)

            for sentence in self.ai_chat.process_query_stream(
                query, visible_content
            ):
                if not self.is_generating:
                    break
                yield {
                    'sentence': sentence,
                    'done': False
                }

            yield {'sentence': '', 'emotion': 'neutral', 'done': True}

        except Exception as e:
            self.logger.error(f"query_stream 失敗: {str(e)}")
            yield {'sentence': f'抱歉，處理問題時出現錯誤: {str(e)}', 'emotion': 'neutral', 'done': True}
        finally:
            self.is_generating = False

    def cancel(self):
        """取消當前生成"""
        self.is_generating = False

    def load_paper_cache(self, paper_id: str, rag_tree_path: str) -> bool:
        """載入論文的 RAG tree 到快取"""
        try:
            with open(rag_tree_path, 'r', encoding='utf-8') as f:
                paper_data = json.load(f)
            self._paper_cache[paper_id] = paper_data
            self.ai_chat.set_paper_context(paper_id, paper_data)
            return True
        except Exception as e:
            self.logger.error(f"載入論文快取失敗: {str(e)}")
            return False