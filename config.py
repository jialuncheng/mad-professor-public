import logging
import sys
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Optional, List, Dict, Any, Generator
from google import genai
from google.genai import types
from langchain_huggingface import HuggingFaceEmbeddings

# 模型設定
TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-2.0-flash")
CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 嵌入模型配置
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

# 日誌配置
def setup_logging():
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)


def _convert_messages(messages: List[Dict[str, Any]]):
    """
    將 OpenAI 格式的 messages 轉換成 Gemini 格式。
    system message 單獨提取，其餘轉成 contents。
    回傳 (system_instruction, contents)
    """
    system_instruction = None
    contents = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "system":
            system_instruction = content
        elif role == "user":
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=content)]
            ))
        elif role == "assistant":
            contents.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text=content)]
            ))

    return system_instruction, contents


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

        # 把圖片加到最後一個 user message
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


# 嵌入模型
class EmbeddingModel:
    _instance: Optional[HuggingFaceEmbeddings] = None

    @classmethod
    def get_instance(cls) -> HuggingFaceEmbeddings:
        if cls._instance is None:
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

            logging.info(f"初始化嵌入模型: {EMBEDDING_MODEL_NAME}，使用設備: {device}")

            cls._instance = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True}
            )
        return cls._instance
