from anthropic import Anthropic
from ai_models.prompt import build_prompt

def anthropic_generate(text: str, config_rows: list, config: dict) -> str:
    client = Anthropic(api_key=config["api_key"])

    response = client.messages.create(
        model=config["model"],
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": build_prompt(text, config_rows)
            }
        ]
    )

    return response.content[0].text