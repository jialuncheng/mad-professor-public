from dotenv import load_dotenv
import os

load_dotenv()

TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-2.0-flash")
CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "gemini-2.0-flash")
# 主題領域判斷模型（可選，未設定時 fallback 到 CHAT_MODEL）
LLM_DOMAIN_MODEL = os.getenv("LLM_DOMAIN_MODEL", CHAT_MODEL)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")

# ── 環境 ──
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ── 登入 / Session ──
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "")
