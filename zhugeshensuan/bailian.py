"""Compatibility helper for OpenAI-compatible model providers."""

import os

from openai import OpenAI


def get_completion(organization=None, system_prompt="", user_message="", temperature=0.7):
    provider = organization or {
        "API_KEY": os.getenv("AI_API_KEY", ""),
        "base_url": os.getenv("AI_BASE_URL", "https://api.deepseek.com"),
        "model_name": os.getenv("AI_MODEL", "deepseek-v4-flash"),
    }
    if not provider.get("API_KEY"):
        raise RuntimeError("AI_API_KEY is not configured")
    client = OpenAI(api_key=provider["API_KEY"], base_url=provider["base_url"])
    response = client.chat.completions.create(
        model=provider["model_name"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content
