from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        return float(value.strip())
    except ValueError:
        return default


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file(ROOT / ".env.local")


@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "")
    llm_model: str = os.environ.get("LLM_MODEL", "gpt-5.4")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    llm_timeout_seconds: float = env_float("LLM_TIMEOUT_SECONDS", 90.0)
    llm_max_retries: int = env_int("LLM_MAX_RETRIES", 2)
    llm_retry_backoff_seconds: float = env_float("LLM_RETRY_BACKOFF_SECONDS", 2.0)
    llm_verifier_enabled: bool = env_bool("LLM_VERIFIER_ENABLED", True)
    llm_verifier_model: str = os.environ.get("LLM_VERIFIER_MODEL", os.environ.get("LLM_MODEL", "gpt-5.4"))
    llm_verifier_base_url: str = os.environ.get("LLM_VERIFIER_BASE_URL", os.environ.get("LLM_BASE_URL", ""))
    llm_verifier_api_key: str = os.environ.get("LLM_VERIFIER_API_KEY", os.environ.get("LLM_API_KEY", ""))
    llm_answer_repair_attempts: int = env_int("LLM_ANSWER_REPAIR_ATTEMPTS", 1)
    chroma_persist_dir: str = os.environ.get("CHROMA_PERSIST_DIR", ".data/chroma")
    graph_data_dir: str = os.environ.get("GRAPH_DATA_DIR", "docs/tier0/merged")
    bilingual_term_map_path: str = os.environ.get("BILINGUAL_TERM_MAP_PATH", "docs/tier0/bilingual-term-map.json")
    database_url: str = os.environ.get("DATABASE_URL", "")
    retrieval_backend: str = os.environ.get("RETRIEVAL_BACKEND", "auto")


settings = Settings()
