import os
from openai import OpenAI


def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))


def chat_completion(model: str, messages: list, tools: list | None = None):
    client = get_client()
    resp = client.chat.completions.create(model=model, messages=messages, tools=tools or [])
    usage = getattr(resp, "usage", None)
    return resp, (
        getattr(usage, "prompt_tokens", 0) or 0,
        getattr(usage, "completion_tokens", 0) or 0,
    )


def generate_image(model: str, prompt: str):
    client = get_client()
    return client.images.generate(model=model, prompt=prompt)


