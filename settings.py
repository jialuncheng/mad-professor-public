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

# Phase 4.7? MODEL-3 B1：短文 Fast-path Bypass 上限
# Gemini 3.5 Flash 65k 輸出解鎖、總字數 < 此值的短文整篇進 translate 不切 TextTiling
# 詳見 .claude-logs/2026-05-22_MODEL-3_短文Bypass_公式穿透_段落滑動_plan.md
TILING_BYPASS_CHAR_LIMIT = int(os.getenv("TILING_BYPASS_CHAR_LIMIT", "5000"))

# Phase 4.7? MODEL-3 修正 5: tiling_processor max_length env 化
# 對齊 TILING_BYPASS_CHAR_LIMIT / TILING_PARAGRAPH_THRESHOLD（B3 範圍）風格
# 單一 text item > 此值才走切割（與 TILING_BYPASS_CHAR_LIMIT「整篇 < N 字 bypass」不同語意）
TILING_MAX_LENGTH = int(os.getenv("TILING_MAX_LENGTH", "2500"))

# Phase 4.7? MODEL-3 B3：段落級滑動觸發閾值（書籍 / 長論文）
# 詳見 .claude-logs/2026-05-22_MODEL-3_短文Bypass_公式穿透_段落滑動_plan.md §4.3
# 總字數 > 此值 → 段落級滑動（80% 滑動窗口減少、避免 RTT 卡死）
# 否則 → 既有句子 / delimiter 級滑動
TILING_PARAGRAPH_THRESHOLD = int(os.getenv("TILING_PARAGRAPH_THRESHOLD", "30000"))

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

# Phase 4.7? MODEL-8 C1 修正 7：OUTPUT_DIR env override（依 db_analysis §5.2）
# Docker / K8s 部署時、可用 OUTPUT_DIR=/app/storage/output 集中管理（單一 Volume）
# 預設值 = _BASE_DIR / "output"、現有所有路徑解析 100% backward compat
# 詳見 .claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md §3.6
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(_BASE_DIR / "output")))
