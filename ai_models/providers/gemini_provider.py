from google import genai
from ai_models.prompt import build_prompt


def gemini_generate(text: str, config_rows: list, config: dict) -> str:
    genai.configure(api_key=config["api_key"])

    model = genai.GenerativeModel(
        model_name=config["model"], generation_config={"temperature": 0.1}
    )

    response = model.generate_content(build_prompt(text, config_rows))
    return response.text
