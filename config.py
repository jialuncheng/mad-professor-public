import logging
import threading
from typing import Optional
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings

# 設定常數已抽至 settings.py，此處 re-export 維持向後相容
# Phase 4.7d Commit 12-2：LLMClient 已搬到 llm/client.py、_convert_messages
# import 已不需。EmbeddingModel 仍留此檔。
from settings import TRANSLATE_MODEL, CHAT_MODEL, GEMINI_API_KEY, EMBEDDING_MODEL_NAME  # noqa: F401


# 嵌入模型（Gemini Embedding 2，符合 LangChain Embeddings 介面）
class EmbeddingModel(Embeddings):
    """使用 Gemini Embedding 2 API，符合 LangChain Embeddings 介面"""

    _instance: Optional['EmbeddingModel'] = None
    _lock = threading.Lock()

    def __init__(self):
        # Phase 4.7? MODEL-9: 注入共享 httpx.Client（與 LLMClient 共用底層 client）
        from llm._http_client import build_http_options
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=build_http_options(),
        )
        self.model = EMBEDDING_MODEL_NAME
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化嵌入模型: {self.model}（Gemini API + 共享 httpx.Client）")

    @classmethod
    def get_instance(cls) -> 'EmbeddingModel':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _embed_one(self, text):
        """逐筆 embed（fallback 用），保留原 429 retry 行為"""
        import time
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
                return result.embeddings[0].values
            except Exception as e:
                if '429' in str(e) and attempt < 2:
                    wait = 15 * (attempt + 1)
                    self.logger.warning(f"Rate limit，等待 {wait} 秒後重試...")
                    time.sleep(wait)
                else:
                    raise

    def embed_documents(self, texts: list) -> list:
        """即時批次 embed 文字列表（用於建立向量庫）。

        依索引順序拼接，保證回傳順序與輸入完全一致；
        每批保留 429 retry；非 429（或數量不符）該批退回逐筆。
        """
        import time
        BATCH_SIZE = 32
        embeddings = []
        total = len(texts)
        for start in range(0, total, BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            batch_no = start // BATCH_SIZE + 1
            for attempt in range(3):
                try:
                    result = self.client.models.embed_content(
                        model=self.model,
                        contents=batch,
                        config=types.EmbedContentConfig(
                            task_type="RETRIEVAL_DOCUMENT",
                            output_dimensionality=768
                        )
                    )
                    if len(result.embeddings) != len(batch):
                        raise RuntimeError(
                            f"批次回傳數量不符: 期望 {len(batch)} 實得 {len(result.embeddings)}"
                        )
                    embeddings.extend(e.values for e in result.embeddings)
                    self.logger.info(
                        f"批次 {batch_no} 完成（{len(batch)} 筆，"
                        f"{start + len(batch)}/{total}）"
                    )
                    break
                except Exception as e:
                    if '429' in str(e) and attempt < 2:
                        wait = 15 * (attempt + 1)
                        self.logger.warning(f"Rate limit，等待 {wait} 秒後重試...")
                        time.sleep(wait)
                        continue
                    # 非 429（或重試耗盡）→ 該批退回逐筆，保證可靠性
                    self.logger.warning(
                        f"批次 {batch_no} 失敗（{str(e)}），退回逐筆模式"
                    )
                    for text in batch:
                        embeddings.append(self._embed_one(text))
                    self.logger.info(
                        f"批次 {batch_no} 逐筆完成（{len(batch)} 筆，"
                        f"{start + len(batch)}/{total}）"
                    )
                    break
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
