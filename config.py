import logging
from typing import Optional, List, Dict, Any, Generator
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings

# 設定常數已抽至 settings.py，此處 re-export 維持向後相容
from settings import TRANSLATE_MODEL, CHAT_MODEL, GEMINI_API_KEY, EMBEDDING_MODEL_NAME
from llm.message_utils import _convert_messages


class LLMClient:
    _instance: Optional['LLMClient'] = None

    def __new__(cls, *args, **kwargs):
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

    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.5,
             stream: bool = True, model: str = None) -> str:
        """一般對話，回傳完整字串"""
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
                    print(chunk.text, end='', flush=True)
                    full_response += chunk.text
            print()
            return full_response
        else:
            response = self.client.models.generate_content(
                model=model, contents=contents, config=config
            )
            return response.text

    def chat_stream_by_sentence(self, messages: List[Dict[str, Any]],
                                 temperature: float = 0.5,
                                 model: str = None) -> Generator[str, None, None]:
        """串流對話，逐句 yield"""
        import re
        model = model or CHAT_MODEL
        system_instruction, contents = _convert_messages(messages)

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction
        )

        cn_end_marks = '。！？'
        en_end_marks = '.!?;'
        current_sentence = ""

        for chunk in self.client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
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

    def chat_with_image(self, messages: List[Dict[str, Any]],
                        image_data: bytes, mime_type: str = "image/jpeg",
                        model: str = None) -> str:
        """帶圖片的對話（Vision）"""
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


# 嵌入模型（Gemini Embedding 2，符合 LangChain Embeddings 介面）
class EmbeddingModel(Embeddings):
    """使用 Gemini Embedding 2 API，符合 LangChain Embeddings 介面"""

    _instance: Optional['EmbeddingModel'] = None

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = EMBEDDING_MODEL_NAME
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化嵌入模型: {self.model}（Gemini API）")

    @classmethod
    def get_instance(cls) -> 'EmbeddingModel':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_documents(self, texts: list) -> list:
        """批次 embed 文字列表（用於建立向量庫）"""
        import time
        embeddings = []
        for text in texts:
            for attempt in range(3):
                try:
                    result = self.client.models.embed_content(
                        model=self.model,
                        contents=[text],
                        config=types.EmbedContentConfig(
                            task_type="RETRIEVAL_DOCUMENT",
                            output_dimensionality=768
                        )
                    )
                    embeddings.append(result.embeddings[0].values)
                    break
                except Exception as e:
                    if '429' in str(e) and attempt < 2:
                        wait = 15 * (attempt + 1)
                        self.logger.warning(f"Rate limit，等待 {wait} 秒後重試...")
                        time.sleep(wait)
                    else:
                        raise
            time.sleep(0.3)
        return embeddings

    def embed_query(self, text: str) -> list:
        """embed 單一查詢字串（用於搜尋）"""
        result = self.client.models.embed_content(
            model=self.model,
            contents=[text],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768
            )
        )
        return result.embeddings[0].values

    def embed_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> list:
        """embed 圖片（用於圖片向量檢索）"""
        image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
        result = self.client.models.embed_content(
            model=self.model,
            contents=[image_part],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )
        return result.embeddings[0].values
