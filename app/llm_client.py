from __future__ import annotations

import json
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import settings


def normalize_base_url(base_url: str) -> str:
    normalized = (base_url or "").rstrip("/")
    if normalized and not normalized.endswith("/v1"):
        normalized = f"{normalized}/v1"
    return normalized


def llm_available(api_key: str | None = None, base_url: str | None = None) -> bool:
    effective_key = (api_key or settings.llm_api_key or "").strip()
    effective_base_url = normalize_base_url(base_url or settings.llm_base_url or "")
    return bool(effective_key and effective_base_url)


def build_chat_model(
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.2,
) -> ChatOpenAI:
    return ChatOpenAI(
        model=model or settings.llm_model,
        api_key=(api_key or settings.llm_api_key or "").strip(),
        base_url=normalize_base_url(base_url or settings.llm_base_url or ""),
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
        temperature=temperature,
    )


def complete_text(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.2,
) -> str:
    if not llm_available(api_key=api_key, base_url=base_url):
        raise RuntimeError("LLM is not configured")

    last_error: Exception | None = None
    for attempt in range(1, settings.llm_max_retries + 2):
        try:
            chat = build_chat_model(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
            )
            result = chat.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            return str(result.content or "").strip()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= settings.llm_max_retries + 1:
                break
            time.sleep(settings.llm_retry_backoff_seconds * attempt)
    raise RuntimeError(f"LLM request failed after retries: {last_error}") from last_error


def _extract_first_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[idx:])
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def complete_json(
    *,
    system_prompt: str,
    user_prompt: str,
    fallback: dict[str, Any] | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.1,
) -> dict[str, Any]:
    text = complete_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
    )
    parsed = _extract_first_json_object(text)
    if parsed is not None:
        return parsed
    result = dict(fallback or {})
    result.setdefault("raw_text", text)
    result.setdefault("parse_error", True)
    return result
