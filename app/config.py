from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def env_first(*keys: str, default: str = "") -> str:
    for key in keys:
        value = os.environ.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return default


@dataclass(frozen=True)
class Settings:
    llm_base_url: str = env_first("LLM_BASE_URL", "BASE_URL")
    llm_model: str = env_first("LLM_MODEL", "MODEL", default="gpt-5.4")
    llm_api_key: str = env_first("LLM_API_KEY", "OPENAI_API_KEY")
    llm_timeout_seconds: float = float(env_first("LLM_TIMEOUT_SECONDS", default="45"))
    query_analyzer_llm_enabled: bool = env_first("QUERY_ANALYZER_LLM_ENABLED", default="false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    chroma_persist_dir: str = env_first("CHROMA_PERSIST_DIR", default=".data/chroma")
    graph_data_dir: str = env_first("GRAPH_DATA_DIR", default="docs/tier0/merged")
    bilingual_term_map_path: str = env_first("BILINGUAL_TERM_MAP_PATH", default="docs/tier0/bilingual-term-map.json")


settings = Settings()
