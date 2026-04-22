from __future__ import annotations

import json
import re
import time
from typing import Any

from openai import APIConnectionError, APITimeoutError, InternalServerError, OpenAI, RateLimitError

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
        timeout=settings.llm_timeout_seconds,
    )


def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.2,
    max_tokens: int | None = None,
) -> str:
    client = build_client()
    request: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        request["max_tokens"] = max_tokens

    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            response = client.chat.completions.create(**request)
            return response.choices[0].message.content or ""
        except (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError) as exc:
            last_error = exc
            if attempt >= 4:
                break
            time.sleep(min(8, 1.5 * attempt))
    if last_error is not None:
        raise last_error
    raise RuntimeError("chat_completion failed without response")


def extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    decoder = json.JSONDecoder()
    for start, char in enumerate(candidate):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(candidate[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def analyze_query(prompt: str) -> dict[str, Any] | None:
    content = chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "你是 Diablo II 检索查询分析器。"
                    "只输出一个 JSON object，不要输出解释。"
                    "JSON 只允许包含 intent, rewritten_queries, subquestions, reasoning_summary。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=800,
    )
    return extract_json_object(content)


def answer_question(prompt: str) -> str:
    return chat_completion(
        [
            {"role": "system", "content": "你是一个暗黑破坏神2知识助手。回答必须基于给定证据，简洁准确，并引用来源。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
