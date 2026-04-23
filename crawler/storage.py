from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import parse_qsl, unquote, urlparse


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


def sanitize_path_component(value: str, fallback: str = "index") -> str:
    clean = unquote(value).strip()
    clean = re.sub(r"[^A-Za-z0-9._-]+", "-", clean)
    clean = clean.strip(".-")
    return clean[:120] or fallback


def query_suffix(query: str) -> str:
    if not query:
        return ""
    parts: list[str] = []
    for key, value in parse_qsl(query, keep_blank_values=True):
        key_part = sanitize_path_component(key, fallback="q")
        if value:
            parts.append(f"{key_part}-{sanitize_path_component(value, fallback='value')}")
        else:
            parts.append(key_part)
    if not parts:
        parts.append(sanitize_path_component(query, fallback="query"))
    return "__" + "__".join(parts)[:160]


def _mirrored_leaf_name(parsed_url, extension: str, *, for_metadata: bool) -> tuple[list[str], str]:
    raw_path = parsed_url.path or "/"
    posix_path = PurePosixPath(unquote(raw_path))
    segments = [sanitize_path_component(part) for part in posix_path.parts if part not in {"", "/", "."}]
    query_part = query_suffix(parsed_url.query)

    if not segments:
        return [], f"index{query_part}{extension}"

    last_segment = segments[-1]
    source_suffix = Path(last_segment).suffix.lower()
    if source_suffix:
        directories = segments[:-1]
        leaf_base = last_segment[:-len(source_suffix)] or "index"
        html_family = {".html", ".htm", ".shtml", ".xhtml"}
        if not for_metadata and (source_suffix == extension or (extension == ".html" and source_suffix in html_family)):
            return directories, f"{leaf_base}{query_part}{source_suffix}"
        if for_metadata or source_suffix != extension:
            leaf_base = last_segment
        return directories, f"{leaf_base}{query_part}{extension}"

    directories = segments
    return directories, f"index{query_part}{extension}"


def mirrored_relative_path(
    source_id: str,
    url: str,
    content_type: str | None,
    *,
    extension: str | None = None,
    for_metadata: bool = False,
) -> Path:
    parsed_url = urlparse(url)
    resolved_extension = extension or snapshot_extension(content_type, url)
    host = sanitize_path_component(parsed_url.netloc, fallback="unknown-host")
    directories, leaf = _mirrored_leaf_name(parsed_url, resolved_extension, for_metadata=for_metadata)
    return Path(source_id, host, *directories, leaf)


def snapshot_id(source_id: str, url: str) -> str:
    digest = hashlib.sha1(f"{source_id}::{url}".encode("utf-8")).hexdigest()[:20]
    return f"snapshot::{source_id}::{digest}"


def save_snapshot(path_root: Path, source_id: str, url: str, content_type: str | None, body: bytes) -> tuple[str, Path]:
    snapshot_key = snapshot_id(source_id, url)
    output_path = path_root / mirrored_relative_path(source_id, url, content_type)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(body)
    return snapshot_key, output_path


def normalize_snapshot_catalog_paths(
    catalog: dict[str, dict[str, Any]],
    crawler_root: Path,
    snapshot_root: Path,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    updated: dict[str, dict[str, Any]] = {}
    moved: list[dict[str, str]] = []
    for key, row in catalog.items():
        normalized = dict(row)
        snapshot_path = normalized.get("snapshot_path")
        if not snapshot_path:
            updated[key] = normalized
            continue

        desired_relative = Path("snapshots") / mirrored_relative_path(
            str(normalized.get("source_id") or "unknown"),
            str(normalized.get("url") or ""),
            normalized.get("content_type"),
        )
        desired_snapshot_path = str(desired_relative)
        current_full_path = crawler_root / snapshot_path
        desired_full_path = crawler_root / desired_relative

        if snapshot_path != desired_snapshot_path:
            desired_full_path.parent.mkdir(parents=True, exist_ok=True)
            if current_full_path.is_file() and current_full_path != desired_full_path:
                if not desired_full_path.exists():
                    shutil.move(str(current_full_path), str(desired_full_path))
                else:
                    current_full_path.unlink()
                moved.append({"from": str(snapshot_path), "to": desired_snapshot_path})
            normalized["snapshot_path"] = desired_snapshot_path
        updated[key] = normalized

    for directory in sorted(snapshot_root.rglob("*"), reverse=True):
        if directory.is_dir() and directory != snapshot_root and not any(directory.iterdir()):
            directory.rmdir()
    return updated, moved
