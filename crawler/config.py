from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crawler.models import CrawlerConfig


REQUIRED_SOURCE_KEYS = {
    "id",
    "label",
    "weight",
    "region",
    "transport",
    "observed_on",
    "observed_status",
    "home_url",
}
MANUAL_CURATED_OVERRIDES = Path(__file__).resolve().parent / 'manual_curated_urls.json'


def validate_config(payload: dict) -> None:
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("config.sources must be a non-empty list")

    seen_ids: set[str] = set()
    for source in sources:
        missing = REQUIRED_SOURCE_KEYS - set(source)
        if missing:
            raise ValueError(f"source missing required keys: {sorted(missing)}")
        source_id = source["id"]
        if source_id in seen_ids:
            raise ValueError(f"duplicate source id: {source_id}")
        seen_ids.add(source_id)


def _merge_manual_curated_urls(payload: dict[str, Any], override_path: Path) -> dict[str, Any]:
    if not override_path.is_file():
        return payload

    overrides = json.loads(override_path.read_text(encoding='utf-8'))
    sources_by_id = {source['id']: source for source in payload.get('sources', [])}
    for source_id, urls in overrides.items():
        if source_id not in sources_by_id or not isinstance(urls, list):
            continue
        source = sources_by_id[source_id]
        existing = list(source.get('curated_urls', []))
        for url in urls:
            if isinstance(url, str) and url and url not in existing:
                existing.append(url)
        source['curated_urls'] = existing
    return payload


def load_config(path: Path) -> CrawlerConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload = _merge_manual_curated_urls(payload, MANUAL_CURATED_OVERRIDES)
    validate_config(payload)
    return CrawlerConfig.from_dict(payload)
