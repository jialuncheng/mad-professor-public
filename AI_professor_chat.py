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
    """文件閱讀 AI 對話模組（stateless 改造中）。

    Stage A：將狀態（conversation_history / grounding_sources）外部化，
    self 只保留服務（LLMClient / Retriever / prompt 路徑）。

    Stage B（規劃）：抽離為獨立 package。屆時：
      - prompt 改 caller 注入字串（不再讀檔）
      - LLMClient / Retriever 走 Protocol 介面
      - 介面不出現任何 mad-professor 特定型別
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.retriever = None
        self.llm_client = None
        try:
            self.llm_client = LLMClient.get_instance()
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

    def process_query_stream(self, query: str, visible_content: str = None,
                             owner_id: int = None,
                             paper_id: str = None, paper_data: Dict[str, Any] = None,
                             conversation_history: List[Dict] = None,
                             use_web_search: bool = False) -> Generator[Dict[str, Any], None, None]:
        """流式處理用戶查詢，逐 chunk yield（Stage A：history 為參數、grounding 由 yield 帶出）。

        Yields:
            {'type': 'sentence', 'text': str}   串流中每句
            {'type': 'done', 'reply': str,      串流結束
             'grounding_sources': list}
        """
        try:
            effective_paper_id = paper_id
            effective_paper_data = paper_data

            if not self.llm_client:
                yield {'type': 'sentence', 'text': "AI服務尚未初始化，請稍後再試。"}
                yield {'type': 'done', 'reply': '', 'grounding_sources': []}
                return

            # 本地對話歷史（不動 caller 的 list）；append 當前 query + 滑動窗 max 10
            working_history = list(conversation_history or [])
            if not (working_history and
                    working_history[-1]["role"] == "user" and
                    working_history[-1]["content"] == query):
                working_history.append({"role": "user", "content": query})
            if len(working_history) > 10:
                working_history = working_history[-10:]

            # 決策
            decision = self._make_decision(query, working_history,
                                           effective_paper_id, effective_paper_data)
            self.logger.info(f"決策結果: {decision}")

            function_name = decision.get('function', 'direct_answer')
            optimized_query = decision.get('query', query)

            # 取得上下文
            context_info = ""
            if function_name == 'page_content_analysis' and visible_content:
                context_info = f"以下是頁面當前顯示的內容:\n\n{visible_content}"
            elif function_name == 'macro_retrieval' and effective_paper_data:
                context_info = self._get_macro_context(optimized_query, effective_paper_data)
            elif function_name == 'rag_retrieval' and effective_paper_id:
                context_info = self._get_rag_context(optimized_query, owner_id, effective_paper_id)

            # 準備訊息
            final_messages = self._prepare_final_messages(
                query=query,
                context_info=context_info,
                function_name=function_name,
                conversation_history=working_history,
                paper_id=effective_paper_id,
                paper_data=effective_paper_data
            )

            # 串流回答
            full_response = ""
            for sentence in self.llm_client.chat_stream_by_sentence(
                messages=final_messages, temperature=0.7,
                use_web_search=use_web_search
            ):
                full_response += sentence
                yield {'type': 'sentence', 'text': sentence}

            # 串流結束後，從 LLMClient 取回本次 grounding 來源（side-channel）
            grounding = getattr(
                self.llm_client, '_last_grounding_sources', None
            ) or []

            yield {'type': 'done', 'reply': full_response,
                   'grounding_sources': grounding}

        except Exception as e:
            self.logger.error(f"處理查詢失敗: {str(e)}")
            yield {'type': 'sentence', 'text': f"抱歉，處理問題時出現錯誤: {str(e)}"}
            yield {'type': 'done', 'reply': '', 'grounding_sources': []}

    def _validate_decision(self, decision_data: Dict) -> bool:
        required_fields = ["function", "query"]
        if not all(f in decision_data for f in required_fields):
            return False
        valid_functions = ["direct_answer", "page_content_analysis", "macro_retrieval", "rag_retrieval"]
        return decision_data["function"] in valid_functions

    def _make_decision(self, query: str, conversation_history: List[Dict] = None,
                       paper_id: str = None, paper_data: Dict[str, Any] = None) -> Dict[str, str]:
        default = {"function": "direct_answer", "query": query}
        try:
            router_prompt = self._read_file(AI_ROUTER_PROMPT_PATH)
            has_paper = paper_id is not None and paper_data is not None
            paper_status = "有文件加載" if has_paper else "無文件加載"
            paper_title = ""
            if has_paper:
                paper_title = paper_data.get('translated_title', '') or paper_data.get('title', '')

            history = conversation_history or []
            formatted_history = ""
            if len(history) > 1:
                recent = history[:-1][-4:]
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

    def _get_macro_context(self, query: str, paper_data: Dict[str, Any] = None) -> str:
        try:
            if not paper_data:
                return ""
            parts = []
            title = paper_data.get('translated_title', '') or paper_data.get('title', '')
            if title:
                parts.append(f"# {title}")
            if paper_data.get('summary'):
                parts.append(f"## 總摘要\n{paper_data['summary']}")
            if paper_data.get('sections'):
                parts.append("## 章節概要")
                for section in paper_data['sections']:
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

    def _get_rag_context(self, query: str, owner_id: int = None,
                          paper_id: str = None) -> str:
        try:
            if not paper_id or not query or not self.retriever or owner_id is None:
                return ""
            if not self.retriever.is_ready():
                return ""
            context = self.retriever.retrieve_with_context(
                owner_id=owner_id, query=query, paper_id=paper_id, top_k=5
            )
            return context or ""
        except Exception as e:
            self.logger.error(f"RAG檢索失敗: {str(e)}")
            return ""

    def _prepare_final_messages(self, query: str, context_info: str, function_name: str = None,
                                conversation_history: List[Dict] = None,
                                paper_id: str = None, paper_data: Dict[str, Any] = None) -> List[Dict]:
        character_prompt = self._read_file(AI_CHARACTER_PROMPT_PATH)
        explain_prompt = self._read_file(AI_EXPLAIN_PROMPT_PATH)

        title = ""
        if paper_data:
            title = paper_data.get('translated_title', '') or paper_data.get('title', '')
        else:
            title = "無文件"

        explain_prompt = explain_prompt.format(title=title)

        # 注入 domain（沿用 translate_processor.py:233-235 範式：caller 端條件附加）
        if paper_data:
            domain = paper_data.get('_domain', '')
            if domain:
                character_prompt = character_prompt + f"\n\n當前文件主題：{domain}"
                explain_prompt = explain_prompt + f"\n\n當前文件主題：{domain}"

        system_message = f"{character_prompt}\n{explain_prompt}"

        messages = [{"role": "system", "content": system_message}]

        history = conversation_history or []
        if len(history) > 1:
            messages.extend(history[:-1])

        final_query = f"用戶問題：{query}"

        if context_info:
            context_type = {
                "page_content_analysis": "當前頁面內容",
                "macro_retrieval": "文件概要",
                "rag_retrieval": "相關文件段落"
            }.get(function_name, "參考資訊")
            final_query += f"\n\n{context_type}:\n{context_info}"

        messages.append({"role": "user", "content": final_query})
        return messages
