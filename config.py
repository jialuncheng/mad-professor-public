import logging
import threading
from typing import Optional
import numpy as np
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings

# 設定常數已抽至 settings.py，此處 re-export 維持向後相容
# Phase 4.7d Commit 12-2：LLMClient 已搬到 llm/client.py、_convert_messages
# import 已不需。EmbeddingModel 仍留此檔。
from settings import TRANSLATE_MODEL, CHAT_MODEL, GEMINI_API_KEY, EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS  # noqa: F401

# === [MODEL-9-OPT C2 START] ===
# 接入統一彈性防禦框架（與 LLMClient 一致）：retry_call Full Jitter 指數退避 + 併發鎖。
from settings import EMBEDDING_MAX_CONCURRENT
from llm.retry import retry_call
# === [MODEL-9-OPT C2 END] ===


# 嵌入模型（Gemini Embedding 2，符合 LangChain Embeddings 介面）
class EmbeddingModel(Embeddings):
    """使用 Gemini Embedding 2 API，符合 LangChain Embeddings 介面"""

    _instance: Optional['EmbeddingModel'] = None
    _lock = threading.Lock()

    # === [MODEL-9-OPT C2 START] ===
    # 全域併發鎖（class-level、單例共用）：限制 Embedding API 同時併發 ≤ EMBEDDING_MAX_CONCURRENT，
    # 與 LLMClient._api_semaphore 各自獨立（避免跨模組死鎖）。@retry_call 包外層、with 包內層 →
    # 重試 sleep 前先 release（不佔鎖）。註：限併發數非 RPM 限流，僅削平突發（plan §7 OQ3）。
    _api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)
    # === [MODEL-9-OPT C2 END] ===

    def __init__(self):
        # Phase 4.7? MODEL-9: 注入共享 httpx.Client（與 LLMClient 共用底層 client）
        from llm._http_client import build_http_options
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=build_http_options(),
        )
        self.model = EMBEDDING_MODEL_NAME
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"初始化嵌入模型: {self.model} "
            f"(Gemini API + 共享 httpx.Client + MRL {EMBEDDING_OUTPUT_DIMENSIONS}維 + L2 normalize)"
        )

    @classmethod
    def get_instance(cls) -> 'EmbeddingModel':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @staticmethod
    def _l2_normalize(vec):
        """L2 正規化向量、安全處理空值 + 零向量 + float32 精度溢出。

        依 plan §3.6.3 修正 3：
        - 空 list / None 直接回原值（避免 numpy crash）
        - float32 精度下 1e-12 仍可能溢出、升到 1e-6 安全範圍
        - 零向量明確回 [0.0] * len（明確 zero vector、避免 caller 誤判 unit vector）
        - 使用 try-except 以防止 numpy array 的真值判定歧義

        Phase 4.7? MODEL-1+2: gemini-embedding-2 用 MRL 降維到 768 後預設未 normalized
        所有 embed 呼叫都必須走此 helper 確保 FAISS inner product = cosine。
        """
        if vec is None:
            return vec

        try:
            if len(vec) == 0:
                return vec
        except (TypeError, ValueError):
            return vec

        arr = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(arr)

        if norm < 1e-6:
            return [0.0] * len(vec)

        return (arr / norm).tolist()

    # === [MODEL-9-OPT C2 START] ===
    # 重構：手動 linear 退避（固定秒數 sleep 15s/30s + '429' 字串比對）全面改為 llm/retry.py 的
    # @retry_call（Full Jitter 指數退避、_RETRYABLE_TOKENS 涵蓋 429/5xx/timeout/disconnect 等）；
    # API 呼叫以 with self._api_semaphore 包裹（重試 sleep 前先 release）。
    # embed_content 參數（model/task_type/output_dimensionality/batch=32）與 _l2_normalize 一律不變
    # → 向量值逐一相同、不影響 Golden Baseline（plan §1）。

    @retry_call(retries=2, base=2.0)
    def _embed_one(self, text):
        """逐筆 embed（fallback 用）；@retry_call 統一退避。

        fallback 路徑用 retries=2（非 3）：為 _embed_batch 重試耗盡後的逐筆降級，
        避免「批次 3 次 → 每筆再 3 次」巢狀指數退避在持續 429 下尾巴過長（plan §2）。
        """
        with self._api_semaphore:
            result = self.client.models.embed_content(
                model=self.model,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
                )
            )
        return self._l2_normalize(result.embeddings[0].values)

    @retry_call(retries=3, base=2.0)
    def _embed_batch(self, batch: list) -> list:
        """批次 embed 單批（預設 32 筆）；@retry_call 統一退避。回 normalized values（保序）。

        數量不符拋 RuntimeError（非 _RETRYABLE_TOKENS）→ 不重試、由 embed_documents 退回逐筆。
        """
        with self._api_semaphore:
            result = self.client.models.embed_content(
                model=self.model,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
                )
            )
        if len(result.embeddings) != len(batch):
            raise RuntimeError(
                f"批次回傳數量不符: 期望 {len(batch)} 實得 {len(result.embeddings)}"
            )
        return [self._l2_normalize(e.values) for e in result.embeddings]

    def embed_documents(self, texts: list) -> list:
        """即時批次 embed 文字列表（用於建立向量庫）。

        依索引順序拼接，保證回傳順序與輸入完全一致；每批由 _embed_batch（@retry_call
        Full Jitter 指數退避）處理，重試耗盡或數量不符則該批退回逐筆 _embed_one，保證可靠性。
        """
        BATCH_SIZE = 32
        embeddings = []
        total = len(texts)
        for start in range(0, total, BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            batch_no = start // BATCH_SIZE + 1
            try:
                embeddings.extend(self._embed_batch(batch))
                self.logger.info(
                    f"批次 {batch_no} 完成（{len(batch)} 筆，"
                    f"{start + len(batch)}/{total}）"
                )
            except Exception as e:
                # 批次重試耗盡（429/5xx/...）或數量不符 → 退回逐筆，保證可靠性。
                # 429 可觀測點（plan §1）：結構化 extra_fields 供上線觀察命中率、調 EMBEDDING_MAX_CONCURRENT。
                self.logger.warning(
                    f"批次 {batch_no} 失敗（{str(e)}），退回逐筆模式",
                    extra={'extra_fields': {
                        'event': 'embedding_429',
                        'batch_no': batch_no,
                        'batch_size': len(batch),
                    }},
                )
                for text in batch:
                    embeddings.append(self._embed_one(text))
                self.logger.info(
                    f"批次 {batch_no} 逐筆完成（{len(batch)} 筆，"
                    f"{start + len(batch)}/{total}）"
                )
        return embeddings

    @retry_call(retries=3, base=2.0)
    def embed_query(self, text: str) -> list:
        """embed 單一查詢字串（用於搜尋）；@retry_call 統一退避。"""
        with self._api_semaphore:
            result = self.client.models.embed_content(
                model=self.model,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
                )
            )
        return self._l2_normalize(result.embeddings[0].values)

    @retry_call(retries=3, base=2.0)
    def embed_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> list:
        """embed 圖片（用於圖片向量檢索）；@retry_call 統一退避。"""
        image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
        with self._api_semaphore:
            result = self.client.models.embed_content(
                model=self.model,
                contents=[image_part],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
                )
            )
        return self._l2_normalize(result.embeddings[0].values)
    # === [MODEL-9-OPT C2 END] ===
