from openai import OpenAI
from ai_models.prompt import build_prompt

def openai_generate(text: str, config_rows: list, config: dict) -> str:
    client = OpenAI(api_key=config["api_key"])

    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": "You are a risk assessment analyst. Always respond with valid JSON only."},
            {"role": "user", "content": build_prompt(text, config_rows)},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content