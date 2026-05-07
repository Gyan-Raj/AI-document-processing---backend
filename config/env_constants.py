import os
from dotenv import load_dotenv

load_dotenv()

MODEL_TO_BE_USED = os.getenv("MODEL_TO_BE_USED")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS")

# DB_HOST = os.getenv("DB_HOST")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_PORT = os.getenv("DB_PORT", "3306")

ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET_KEY")
REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET_KEY")
HF_API_URL = os.getenv("HF_API_URL")
HF_TOKEN = os.getenv("HF_TOKEN")
