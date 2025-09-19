import os
from dotenv import load_dotenv
load_dotenv()

# --- Global Config ---
LOGS_DIR = "./logs"
LOG_LEVEL_DEBUG = True
APPLICATION_LOG_FILE = "application.log"
UPLOAD_DIR = "./uploads"
MAX_FILE_SIZE = 1024 * 1024 * 1 # 1 Mega Byte

# --- DB Config ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

# --- LLM ---
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-2.5-flash-lite"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")