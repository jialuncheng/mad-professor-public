from dotenv import load_dotenv
import os

load_dotenv()

TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-2.0-flash")
CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
