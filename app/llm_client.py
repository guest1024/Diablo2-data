from __future__ import annotations

from openai import OpenAI

from .config import settings


def normalize_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized and not normalized.endswith("/v1"):
        normalized = f"{normalized}/v1"
    return normalized


def build_client() -> OpenAI:
    return OpenAI(
        api_key=settings.llm_api_key,
        base_url=normalize_base_url(settings.llm_base_url),
    )


def answer_question(prompt: str) -> str:
    client = build_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": "你是一个暗黑破坏神2知识助手。回答必须基于给定证据，简洁准确，并引用来源。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
