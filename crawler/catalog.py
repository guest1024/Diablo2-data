from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def normalize_catalog_entry(entry: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(entry)
    capture_status = normalized.get("capture_status")
    lifecycle_status = normalized.get("lifecycle_status")
    snapshot_path = normalized.get("snapshot_path")

    if not capture_status:
        if snapshot_path:
            capture_status = "saved"
        elif lifecycle_status == "ignored":
            capture_status = "filtered"
        elif lifecycle_status == "frozen":
            capture_status = "frozen"
        else:
            capture_status = "catalog-only"
    if capture_status:
        normalized["capture_status"] = capture_status
    return normalized


def load_page_catalog(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {key: normalize_catalog_entry(value) for key, value in payload.items()}


def page_key(source_id: str, url: str) -> str:
    return f"{source_id}::{url}"


def get_catalog_entry(catalog: dict[str, dict[str, Any]], source_id: str, url: str) -> dict[str, Any] | None:
    return catalog.get(page_key(source_id, url))


def classify_page(catalog: dict[str, dict[str, Any]], source_id: str, url: str, sha256: str | None) -> str:
    existing = get_catalog_entry(catalog, source_id, url)
    if existing is None:
        return "new"
    if sha256 and existing.get("sha256") != sha256:
        return "updated"
    return "unchanged"


def update_page_catalog(
    catalog: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
    run_id: str,
    seen_at: str,
) -> dict[str, dict[str, Any]]:
    updated = {key: normalize_catalog_entry(value) for key, value in catalog.items()}
    for row in rows:
        key = page_key(row["source_id"], row["url"])
        existing = updated.get(key, {})
        updated[key] = normalize_catalog_entry(
            {
                "source_id": row["source_id"],
                "source_label": row.get("source_label") or existing.get("source_label"),
                "url": row["url"],
                "title": row.get("title") or existing.get("title"),
                "http_status": row.get("http_status", existing.get("http_status")),
                "content_type": row.get("content_type", existing.get("content_type")),
                "sha256": row.get("sha256") or existing.get("sha256"),
                "snapshot_id": row.get("snapshot_id") or existing.get("snapshot_id"),
                "snapshot_path": row.get("snapshot_path") or existing.get("snapshot_path"),
                "capture_status": row.get("capture_status") or existing.get("capture_status"),
                "lifecycle_status": row.get("lifecycle_status") or existing.get("lifecycle_status"),
                "first_seen_at": existing.get("first_seen_at", seen_at),
                "last_seen_at": seen_at,
                "last_run_id": run_id,
            }
        )
    return updated
