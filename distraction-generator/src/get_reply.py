import base64
from textwrap import dedent
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel


def get_image_base64(image_input: str) -> str:
    if image_input.startswith("data:image"):
        return image_input.split(",")[1]
    elif all(
        c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/="
        for c in image_input.strip()
    ):
        return image_input.strip()
    else:
        with open(image_input, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


def get_reply(
    image_path: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    format: BaseModel,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
):
    client = OpenAI()
    image_base64 = get_image_base64(image_path)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": dedent(system_prompt)},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": dedent(user_prompt)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            },
        ],
        temperature=temperature,
        response_format=format,
    )

    return completion.choices[0].message
