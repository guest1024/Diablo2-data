from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def write_partitioned_jsonl(root: Path, rows: list[dict[str, Any]], partition_key: str) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        bucket = str(row.get(partition_key, 'unknown'))
        buckets.setdefault(bucket, []).append(row)
    written: list[Path] = []
    for bucket, bucket_rows in buckets.items():
        path = root / f'{bucket}.jsonl'
        write_jsonl(path, bucket_rows)
        written.append(path)
    return written


def snapshot_extension(content_type: str | None, url: str) -> str:
    lowered = (content_type or "").lower()
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".html", ".htm", ".xml", ".json", ".txt"}:
        return suffix
    if "html" in lowered:
        return ".html"
    if "xml" in lowered:
        return ".xml"
    if "json" in lowered:
        return ".json"
    if "text" in lowered:
        return ".txt"
    return ".bin"


def snapshot_id(source_id: str, url: str) -> str:
    digest = hashlib.sha1(f"{source_id}::{url}".encode("utf-8")).hexdigest()[:20]
    return f"snapshot::{source_id}::{digest}"


def save_snapshot(path_root: Path, source_id: str, url: str, content_type: str | None, body: bytes) -> tuple[str, Path]:
    snapshot_key = snapshot_id(source_id, url)
    extension = snapshot_extension(content_type, url)
    output_path = path_root / source_id / f"{snapshot_key.replace('snapshot::', '').replace('::', '--')}{extension}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(body)
    return snapshot_key, output_path
