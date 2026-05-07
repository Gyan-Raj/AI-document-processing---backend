import os
from config.env_constants import (
    GROQ_API_KEY,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
)

AI_MODELS = {
    # ✅ Free — Groq gives free API access to open source models
    "GROQ_LLAMA": {
        "provider": "groq",
        # "model": "llama3-8b-8192",
        "model": "llama-3.1-8b-instant",
        "api_key": GROQ_API_KEY,
    },
    # ✅ Free — Groq also serves Mixtral
    "GROQ_MIXTRAL": {
        "provider": "groq",
        "model": "mixtral-8x7b-32768",
        "api_key": GROQ_API_KEY,
    },
    # ✅ Free tier available — Google Gemini
    "GEMINI": {
        "provider": "gemini",
        "model": "gemini-1.5-flash",
        "api_key": GEMINI_API_KEY,
    },
    # paid — keep for future
    "OPENAI": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key": OPENAI_API_KEY,
    },
    "ANTHROPIC": {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "api_key": ANTHROPIC_API_KEY,
    },
}
