import logging
import json
import os
import re
from typing import List, Dict, Any, Generator, Tuple
from config import LLMClient

AI_CHARACTER_PROMPT_PATH = "prompt/ai/ai_character_prompt.txt"
AI_EXPLAIN_PROMPT_PATH = "prompt/ai/ai_explain_prompt.txt"
AI_ROUTER_PROMPT_PATH = "prompt/ai/ai_router_prompt.txt"

class AIProfessorChat:
    """AI對話助手 - 學術論文智能問答系統"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.conversation_history = []
        self.current_paper_id = None
        self.current_paper_data = None
        self.retriever = None
        self.llm_client = None
        try:
            self.llm_client = LLMClient()
            self.logger.info("AI對話助手初始化完成")
        except Exception as e:
            self.logger.error(f"初始化AI對話組件失敗: {str(e)}")

    def _read_file(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.warning(f"讀取文件 {filepath} 失敗: {str(e)}")
            return ""

    def set_paper_context(self, paper_id: str, paper_data: Dict[str, Any]) -> bool:
        try:
            self.current_paper_id = paper_id
            self.current_paper_data = paper_data
            self.logger.info(f"已設置論文上下文: {paper_id}")
            return True
        except Exception as e:
            self.logger.error(f"設置論文上下文失敗: {str(e)}")
            return False

    def process_query_stream(self, query: str, visible_content: str = None) -> Generator[str, None, None]:
        """流式處理用戶查詢，逐句 yield 回答"""
        try:
            if not self.llm_client:
                yield "AI服務尚未初始化，請稍後再試。"
                return

            # 加入對話歷史
            if not (self.conversation_history and
                    self.conversation_history[-1]["role"] == "user" and
                    self.conversation_history[-1]["content"] == query):
                self.conversation_history.append({"role": "user", "content": query})

            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            # 決策
            decision = self._make_decision(query)
            self.logger.info(f"決策結果: {decision}")

            function_name = decision.get('function', 'direct_answer')
            optimized_query = decision.get('query', query)

            # 取得上下文
            context_info = ""
            if function_name == 'page_content_analysis' and visible_content:
                context_info = f"以下是頁面當前顯示的內容:\n\n{visible_content}"
            elif function_name == 'macro_retrieval' and self.current_paper_data:
                context_info = self._get_macro_context(optimized_query)
            elif function_name == 'rag_retrieval' and self.current_paper_id:
                context_info = self._get_rag_context(optimized_query)

            # 準備訊息
            final_messages = self._prepare_final_messages(
                query=query,
                context_info=context_info,
                function_name=function_name
            )

            # 串流回答
            full_response = ""
            for sentence in self.llm_client.chat_stream_by_sentence(
                messages=final_messages, temperature=0.7
            ):
                full_response += sentence
                yield sentence

            self.conversation_history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            self.logger.error(f"處理查詢失敗: {str(e)}")
            yield f"抱歉，處理問題時出現錯誤: {str(e)}"

    def _validate_decision(self, decision_data: Dict) -> bool:
        required_fields = ["function", "query"]
        if not all(f in decision_data for f in required_fields):
            return False
        valid_functions = ["direct_answer", "page_content_analysis", "macro_retrieval", "rag_retrieval"]
        return decision_data["function"] in valid_functions

    def _make_decision(self, query: str) -> Dict[str, str]:
        default = {"function": "direct_answer", "query": query}
        try:
            router_prompt = self._read_file(AI_ROUTER_PROMPT_PATH)
            has_paper = self.current_paper_id is not None and self.current_paper_data is not None
            paper_status = "有論文加載" if has_paper else "無論文加載"
            paper_title = ""
            if has_paper:
                paper_title = self.current_paper_data.get('translated_title', '') or self.current_paper_data.get('title', '')

            formatted_history = ""
            if len(self.conversation_history) > 1:
                recent = self.conversation_history[:-1][-4:]
                formatted_history = "\n".join(
                    f"{'用戶' if m['role']=='user' else '導師'}: {m['content']}"
                    for m in recent
                )

            decision_prompt = router_prompt.format(
                query=query,
                paper_status=paper_status,
                paper_title=paper_title,
                conversation_history=formatted_history
            )

            messages = [{"role": "user", "content": decision_prompt}]
            decision_data = None

            for attempt in range(2):
                response = self.llm_client.chat(messages=messages, temperature=0.7, stream=False)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if not json_match:
                    continue
                try:
                    decision_data = json.loads(json_match.group(0))
                    if self._validate_decision(decision_data):
                        break
                except json.JSONDecodeError:
                    continue

            if not has_paper and decision_data:
                decision_data["function"] = "direct_answer"

            if decision_data and self._validate_decision(decision_data):
                return {"function": decision_data["function"], "query": decision_data["query"]}
            return default

        except Exception as e:
            self.logger.error(f"決策失敗: {str(e)}")
            return default

    def _get_macro_context(self, query: str) -> str:
        try:
            if not self.current_paper_data:
                return ""
            parts = []
            title = self.current_paper_data.get('translated_title', '') or self.current_paper_data.get('title', '')
            if title:
                parts.append(f"# {title}")
            if self.current_paper_data.get('summary'):
                parts.append(f"## 總摘要\n{self.current_paper_data['summary']}")
            if self.current_paper_data.get('sections'):
                parts.append("## 章節概要")
                for section in self.current_paper_data['sections']:
                    sec_title = section.get('translated_title', '') or section.get('title', '')
                    sec_summary = section.get('summary', '')
                    if sec_title:
                        text = f"### {sec_title}"
                        if sec_summary:
                            text += f"\n{sec_summary}"
                        parts.append(text)
            return "\n\n".join(parts)
        except Exception as e:
            self.logger.error(f"取得宏觀上下文失敗: {str(e)}")
            return ""

    def _get_rag_context(self, query: str) -> str:
        try:
            if not self.current_paper_id or not query or not self.retriever:
                return ""
            if not self.retriever.is_ready():
                return ""
            context, _ = self.retriever.retrieve_with_context(
                query=query, paper_id=self.current_paper_id, top_k=5
            )
            return context
        except Exception as e:
            self.logger.error(f"RAG檢索失敗: {str(e)}")
            return ""

    def _prepare_final_messages(self, query: str, context_info: str, function_name: str = None) -> List[Dict]:
        character_prompt = self._read_file(AI_CHARACTER_PROMPT_PATH)
        explain_prompt = self._read_file(AI_EXPLAIN_PROMPT_PATH)

        title = ""
        if self.current_paper_data:
            title = self.current_paper_data.get('translated_title', '') or self.current_paper_data.get('title', '')
        else:
            title = "無論文"

        explain_prompt = explain_prompt.format(title=title)
        system_message = f"{character_prompt}\n{explain_prompt}"

        messages = [{"role": "system", "content": system_message}]

        if len(self.conversation_history) > 1:
            messages.extend(self.conversation_history[:-1])

        final_query = f"用戶問題：{query}"

        if context_info:
            context_type = {
                "page_content_analysis": "當前頁面內容",
                "macro_retrieval": "論文概要",
                "rag_retrieval": "相關論文段落"
            }.get(function_name, "參考資訊")
            final_query += f"\n\n{context_type}:\n{context_info}"

        messages.append({"role": "user", "content": final_query})
        return messages
