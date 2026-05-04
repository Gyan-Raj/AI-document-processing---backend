from ai_models.configurations import AI_MODELS
from ai_models.providers.groq_provider import groq_generate
from ai_models.providers.openai_provider import openai_generate
from ai_models.providers.anthropic_provider import anthropic_generate
from ai_models.providers.gemini_provider import gemini_generate
from schemas.ai_summary_schema import SummaryResponse
import json
import asyncio

PROVIDER_MAP = {
    "groq": groq_generate,
    "openai": openai_generate,
    "anthropic": anthropic_generate,
    "gemini": gemini_generate,
}

async def generate_summary(text: str, config_rows: list, model_key: str) -> dict:
    if model_key not in AI_MODELS:
        raise ValueError(f"Unsupported model: {model_key}. Available: {list(AI_MODELS.keys())}")

    config = AI_MODELS[model_key]
    provider = config["provider"]

    if provider not in PROVIDER_MAP:
        raise ValueError(f"Unsupported provider: {provider}")

    generator_fn = PROVIDER_MAP[provider]

    raw_output = await asyncio.get_event_loop().run_in_executor(
        None, generator_fn, text, config_rows, config
    )

    clean = (
        raw_output.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        parsed = json.loads(clean)
        validated = SummaryResponse(**parsed)
        return {
            "data": validated.model_dump(),
            "meta": {
                "provider": provider,
                "model": config["model"],
                "generated_by": "Gyan Raj"
            }
        }
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw: {raw_output}")
    except Exception as e:
        raise ValueError(f"Response did not match schema: {e}")