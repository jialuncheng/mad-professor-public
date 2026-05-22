from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-2.0-flash")
CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "gemini-2.0-flash")
# 主題領域判斷模型（可選，未設定時 fallback 到 CHAT_MODEL）
LLM_DOMAIN_MODEL = os.getenv("LLM_DOMAIN_MODEL", CHAT_MODEL)
# 後台處理模型細分（皆可選，未設定時 fallback 到 CHAT_MODEL，行為不變）
# doc_analyzer 的 heading fix / structure 分析
LLM_DOC_MODEL = os.getenv("LLM_DOC_MODEL", CHAT_MODEL)
# image_caption 與 slides 的 Vision 辨識
LLM_VISION_MODEL = os.getenv("LLM_VISION_MODEL", CHAT_MODEL)
# extra_info 章節摘要 / 問題 / 公式解析
LLM_EXTRA_INFO_MODEL = os.getenv("LLM_EXTRA_INFO_MODEL", CHAT_MODEL)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
# Phase 4.7? MODEL-1+2: MRL 降維到 768、與既有 FAISS 768 維 schema 相容
# 3072 維預設 pre-normalized、768 維降維後需手動 normalize
# （見 config.py::EmbeddingModel._l2_normalize）
EMBEDDING_OUTPUT_DIMENSIONS = int(os.getenv("EMBEDDING_OUTPUT_DIMENSIONS", "768"))
# Phase 4.7? MODEL-1+2 階段 B2：RAG 檢索分數閾值（plan §4.6、修正 1）
# 預設保留現有 0.22、env override 讓 baron 觀察 raw score 後動態調整
# 推測 L2 normalize 後可能需升到 0.35-0.45、待 RAG-3 收實測數據確認
RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.22"))

# Phase 4.7d Commit 13：LLM 全域並發上限（Semaphore in llm/client.py）。
# 太高會撞「Server disconnected」（4 paper × image_caption 4 worker ~16 條
# 連線會把 Gemini endpoint 打斷）；太低會慢。預設 6 為經驗值；env override。
LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "6"))

# Phase 4.7d RAG-7a：浮水印偵測閾值
# 整篇 markdown 內出現 ≥ N 次的 heading line 視為浮水印、整行移除
# 預設 3（DeHunt 履歷實測 XDeHunt 出現 5 處、HDeHunt 出現 5 處）
WATERMARK_HEADING_THRESHOLD = int(os.getenv("WATERMARK_HEADING_THRESHOLD", "3"))

# ── 環境 ──
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ── 登入 / Session ──
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "")

# ── 資料庫（Phase 0：僅建設，預設未接線；核心模組不 import）──
_BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{_BASE_DIR / 'data' / 'mad-professor.db'}"
)
