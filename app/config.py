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


@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "")
    llm_model: str = os.environ.get("LLM_MODEL", "gpt-5.4")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    chroma_persist_dir: str = os.environ.get("CHROMA_PERSIST_DIR", ".data/chroma")
    graph_data_dir: str = os.environ.get("GRAPH_DATA_DIR", "docs/tier0/merged")
    bilingual_term_map_path: str = os.environ.get("BILINGUAL_TERM_MAP_PATH", "docs/tier0/bilingual-term-map.json")


settings = Settings()
