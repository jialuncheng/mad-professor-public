"""Gemini LLMClient — chat adapter for the Google google-genai SDK.

Phase 4.7d Commit 12-2：從 config.py 搬出（解耦）+ 套 retry decorator（解 502）。
- chat / chat_with_image 用 @retry_call（同步、retry 5xx / 429 / timeout / ...）
- chat_stream_by_sentence 用 @retry_stream（generator、pre-yield 才重啟）
- 既有 chat_with_image 內 429 retry 內迴圈拔掉、由 decorator 統一管
- 既有 chat_stream_by_sentence grounding fallback 邏輯保留（兩層獨立）

caller 端 import path：`from llm.client import LLMClient`（取代原
`from config import LLMClient`）。signature / 例外型別 / get_instance
singleton / _last_grounding_sources side-channel 皆 1:1 等效。

EmbeddingModel 仍留 config.py（Phase 4.7d 不動）。
"""

import logging
import threading
from typing import List, Dict, Any, Generator, Optional

from google import genai
from google.genai import types

from settings import CHAT_MODEL, GEMINI_API_KEY, LLM_MAX_CONCURRENT
from llm.message_utils import _convert_messages
from llm.retry import retry_call, retry_stream


class LLMClient:
    _instance: Optional['LLMClient'] = None
    _lock = threading.Lock()
    # Phase 4.7d Commit 13：全域 LLM 並發限制（class-level、所有 caller 共用）。
    # 4 paper 並行 × image_caption 4 worker = ~16 條連線會撞「Server
    # disconnected」；限制總並發到 LLM_MAX_CONCURRENT（預設 6）。
    # retry 時 sleep 不持有 lock（fn 外、見 llm/retry.py wrapper 結構）。
    _api_semaphore = threading.Semaphore(LLM_MAX_CONCURRENT)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LLMClient, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._initialized = True
        logging.getLogger(__name__).info("LLMClient 初始化完成（google-genai SDK）")

    @classmethod
    def get_instance(cls) -> 'LLMClient':
        return cls()

    @retry_call(retries=3, base=2.0)
    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.5,
             stream: bool = True, model: str = None) -> str:
        """一般對話，回傳完整字串"""
        # Phase 4.7d Commit 13：with semaphore 包整個 method body，
        # 限制全域並發；retry 時 sleep 在 fn 外、不持有 lock
        with LLMClient._api_semaphore:
            model = model or CHAT_MODEL
            system_instruction, contents = _convert_messages(messages)

            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )

            if stream:
                full_response = ""
                for chunk in self.client.models.generate_content_stream(
                    model=model, contents=contents, config=config
                ):
                    if chunk.text:
                        full_response += chunk.text
                return full_response
            else:
                response = self.client.models.generate_content(
                    model=model, contents=contents, config=config
                )
                return response.text

    @retry_stream(retries=3, base=2.0)
    def chat_stream_by_sentence(self, messages: List[Dict[str, Any]],
                                 temperature: float = 0.5,
                                 model: str = None,
                                 use_web_search: bool = False) -> Generator[str, None, None]:
        """串流對話，逐句 yield。

        use_web_search=True 時啟用 Gemini Google Search grounding，並把來源
        寫入 self._last_grounding_sources（list[{'title','uri'}]）；關閉時為
        None，以明確區分「沒開搜網」與「開了但無結果（空陣列）」。
        模型不支援或 API 出錯且尚未產出任何句子時，退回無 tool 重試一次。

        Phase 4.7d Commit 13：with semaphore 包整個 generator body，包含
        yield。lock 持有期 = generator lifetime（caller 拉完 / 例外 / GC
        才釋放）；retry 時 sleep 在 wrapper 內、不持有 lock。
        """
        with LLMClient._api_semaphore:
            import re
            model = model or CHAT_MODEL
            system_instruction, contents = _convert_messages(messages)

            self._last_grounding_sources = [] if use_web_search else None

            def _build_config(with_search):
                kwargs = dict(temperature=temperature,
                              system_instruction=system_instruction)
                if with_search:
                    kwargs['tools'] = [types.Tool(google_search=types.GoogleSearch())]
                return types.GenerateContentConfig(**kwargs)

            def _collect_sources(chunk):
                # grounding_metadata 掛在 chunk.candidates[0]，不在 chunk.text；
                # 取最後一個非空結果覆寫(串流尾段才完整)。
                try:
                    cand = (chunk.candidates or [None])[0]
                    meta = getattr(cand, 'grounding_metadata', None)
                    gchunks = getattr(meta, 'grounding_chunks', None) if meta else None
                    if not gchunks:
                        return
                    found = []
                    for g in gchunks:
                        web = getattr(g, 'web', None)
                        if web and getattr(web, 'uri', None):
                            found.append({
                                'title': getattr(web, 'title', '') or web.uri,
                                'uri': web.uri,
                            })
                    if found:
                        self._last_grounding_sources = found
                except Exception:
                    pass

            cn_end_marks = '。！？'
            en_end_marks = '.!?;'

            def _run(with_search):
                current_sentence = ""
                for chunk in self.client.models.generate_content_stream(
                    model=model, contents=contents, config=_build_config(with_search)
                ):
                    if with_search:
                        _collect_sources(chunk)
                    if not chunk.text:
                        continue

                    content = chunk.text
                    current_sentence += content

                    if any(char in cn_end_marks for char in content):
                        sentence = current_sentence.strip()
                        if sentence and len(sentence) >= 10:
                            yield sentence
                            current_sentence = ""

                    elif any(char in en_end_marks for char in content):
                        matches = list(re.finditer(r'[.!?;][\s\n]', current_sentence))
                        if matches:
                            last_match = matches[-1]
                            end_position = last_match.end() - 1
                            sentence = current_sentence[:end_position].strip()
                            remaining = current_sentence[end_position:].strip()
                            if sentence and len(sentence) >= 10:
                                yield sentence
                                current_sentence = remaining

                if current_sentence.strip():
                    yield current_sentence.strip()

            if not use_web_search:
                yield from _run(False)
                return

            yielded_any = False
            try:
                for sentence in _run(True):
                    yielded_any = True
                    yield sentence
            except Exception as e:
                if yielded_any:
                    raise
                logging.getLogger(__name__).warning(
                    f"Google Search grounding 失敗，退回無搜尋重試一次: {e}"
                )
                self._last_grounding_sources = []
                yield from _run(False)

    @retry_call(retries=3, base=2.0)
    def chat_with_image(self, messages: List[Dict[str, Any]],
                        image_data: bytes, mime_type: str = "image/jpeg",
                        model: str = None) -> str:
        """帶圖片的對話（Vision）。

        Phase 4.7d Commit 12-2：原 for attempt in range(3) + '429' 字串
        擋的內迴圈拔掉，retry 由 @retry_call decorator 統一管（涵蓋 5xx /
        429 / timeout 等所有 transient 例外）。
        Phase 4.7d Commit 13：with semaphore 包整個 method body。
        """
        with LLMClient._api_semaphore:
            model = model or CHAT_MODEL
            system_instruction, contents = _convert_messages(messages)

            image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
            if contents and contents[-1].role == "user":
                contents[-1].parts.append(image_part)
            else:
                contents.append(types.Content(
                    role="user",
                    parts=[image_part]
                ))

            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )

            response = self.client.models.generate_content(
                model=model, contents=contents, config=config
            )
            return response.text
