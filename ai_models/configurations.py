import os

AI_MODELS = {
    # ✅ Free — Groq gives free API access to open source models
    "GROQ_LLAMA": {
        "provider": "groq",
        # "model": "llama3-8b-8192",
        "model": "llama-3.1-8b-instant",
        "api_key": os.getenv("GROQ_API_KEY"),
    },
    # ✅ Free — Groq also serves Mixtral
    "GROQ_MIXTRAL": {
        "provider": "groq",
        "model": "mixtral-8x7b-32768",
        "api_key": os.getenv("GROQ_API_KEY"),
    },
    # ✅ Free tier available — Google Gemini
    "GEMINI": {
        "provider": "gemini",
        "model": "gemini-1.5-flash",
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    # paid — keep for future
    "OPENAI": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    "ANTHROPIC": {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
}