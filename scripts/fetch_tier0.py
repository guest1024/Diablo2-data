#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; Diablo2KnowledgeBot/1.0; +https://example.invalid/bot)"


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


@dataclass
class FetchResult:
    source_id: str
    label: str
    url: str
    output_path: str
    status: str
    http_status: int | None
    content_type: str | None
    bytes_written: int
    sha256: str | None
    discovered_url_count: int
    discovered_url_sample: list[str]
    note: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def guess_extension(content_type: str | None, url: str) -> str:
    path = urlparse(url).path
    if "." in Path(path).name:
        return ""
    if not content_type:
        return ".bin"
    content_type = content_type.lower()
    if "json" in content_type:
        return ".json"
    if "xml" in content_type:
        return ".xml"
    if "html" in content_type:
        return ".html"
    if "plain" in content_type:
        return ".txt"
    return ".bin"


def content_type_from_path(path: Path) -> str | None:
    suffix = path.suffix.lower()
    return {
        ".html": "text/html",
        ".xml": "application/xml",
        ".json": "application/json",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }.get(suffix)


def slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path or '/'}"
    raw = raw.rstrip("/") or raw
    raw = raw.replace("/", "__")
    raw = re.sub(r"[^A-Za-z0-9._-]+", "-", raw)
    return raw[:180]


def normalize_urls(urls: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        trimmed = url.strip()
        if not trimmed or trimmed in seen:
            continue
        seen.add(trimmed)
        ordered.append(trimmed)
    return ordered


def collect_json_urls(payload: object) -> list[str]:
    urls: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in {"url", "html_url", "download_url"} and isinstance(value, str):
                urls.append(value)
            else:
                urls.extend(collect_json_urls(value))
    elif isinstance(payload, list):
        for item in payload:
            urls.extend(collect_json_urls(item))
    return urls


def filter_discovered_urls(urls: Iterable[str], rules: dict | None) -> list[str]:
    normalized = []
    allow_prefixes = tuple(rules.get("allow_prefixes", [])) if rules else ()
    allow_hosts = set(rules.get("allow_hosts", [])) if rules else set()
    exclude_substrings = rules.get("exclude_substrings", []) if rules else []
    exclude_suffixes = tuple(rules.get("exclude_suffixes", [])) if rules else ()
    for url in normalize_urls(urls):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        clean = url.replace("http://", "https://", 1).split("#", 1)[0]
        if allow_prefixes and not clean.startswith(allow_prefixes):
            continue
        if allow_hosts and parsed.netloc not in allow_hosts:
            continue
        if any(fragment in clean for fragment in exclude_substrings):
            continue
        if exclude_suffixes and clean.lower().endswith(exclude_suffixes):
            continue
        normalized.append(clean)
    return normalize_urls(normalized)


def discover_urls(url: str, body: bytes, content_type: str | None, rules: dict | None = None) -> list[str]:
    parsed = urlparse(url)
    text = body.decode("utf-8", "ignore")
    if content_type and "xml" in content_type.lower():
        return filter_discovered_urls(re.findall(r"<loc>([^<]+)</loc>", text), rules)
    if content_type and "json" in content_type.lower():
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return []
        return filter_discovered_urls(collect_json_urls(payload), rules)
    if content_type and "html" in content_type.lower():
        parser = LinkExtractor()
        parser.feed(text)
        scoped: list[str] = []
        for link in parser.links:
            absolute = urljoin(url, link)
            abs_parsed = urlparse(absolute)
            if abs_parsed.netloc != parsed.netloc:
                continue
            if absolute not in scoped:
                scoped.append(absolute)
        return filter_discovered_urls(scoped, rules)
    if content_type and "plain" in content_type.lower():
        urls = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("http://") or line.startswith("https://"):
                urls.append(line)
        return filter_discovered_urls(urls, rules)
    return []


def fetch(url: str, timeout: int = 12) -> tuple[int, bytes, str | None]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read(), resp.headers.get("Content-Type")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def render_report(results: list[FetchResult], registry: dict, output_root: Path) -> str:
    grouped: dict[str, list[FetchResult]] = {}
    for result in results:
        grouped.setdefault(result.source_id, []).append(result)

    lines = [
        "# Tier 0 Acquisition Execution Report",
        "",
        f"- Generated at: `{now_iso()}`",
        f"- Registry: `{output_root / 'source-registry.json'}`",
        f"- Raw root: `{output_root / 'raw'}`",
        "",
        "## Summary",
        "",
        "| Source | Captures | Notes |",
        "| --- | ---: | --- |",
    ]
    for source in registry["sources"]:
        captures = grouped.get(source["id"], [])
        note = source.get("execution_note", "")
        lines.append(f"| {source['name']} | {len(captures)} | {note} |")

    lines.extend(["", "## Capture Details", ""])
    for source in registry["sources"]:
        captures = grouped.get(source["id"], [])
        lines.append(f"### {source['name']}")
        lines.append("")
        lines.append(f"- Tier: `{source['tier']}`")
        lines.append(f"- Lane: `{source['lane']}`")
        lines.append(f"- Capture mode: `{source['capture_mode']}`")
        lines.append(f"- Policy note: {source['policy_note']}")
        lines.append("")
        for item in captures:
            status = item.status if item.http_status is None else f"{item.status} ({item.http_status})"
            lines.append(f"- `{item.label}` → `{status}` → `{item.output_path}`")
            if item.note:
                lines.append(f"  - Note: {item.note}")
            if item.discovered_url_sample:
                lines.append(
                    "  - Discovered URLs sample: "
                    + ", ".join(f"`{u}`" for u in item.discovered_url_sample[:5])
                )
        lines.append("")

    lines.extend(
        [
            "## Tier 0 Execution Notes",
            "",
            "- `The Arreat Summit`: fetched core section pages for official legacy reference coverage.",
            "- `diablo2.io`: fetched sitemap plus allowed structured category roots only; avoided forum/build/article/tool/trade expansion.",
            "- `blizzhackers/d2data`: fetched public GitHub API listings plus README/raw samples to seed machine-readable ingestion.",
            "- `Diablo-2.net API`: captured the API docs page and current public error/guard behavior; live JSON item/rune endpoints now appear to require an API key.",
            "- `d2.blizzard.cn`: captured homepage, sitemap, and news index for official Chinese terminology/news seeding.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(results: list[FetchResult], registry: dict, registry_path: Path, output_root: Path) -> None:
    manifest = {
        "generated_at": now_iso(),
        "registry": str(registry_path),
        "output_root": str(output_root),
        "sources": registry["sources"],
        "results": [result.__dict__ for result in results],
    }
    write_text(output_root / "fetch-manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_text(output_root / "fetch-report.md", render_report(results, registry, output_root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Tier 0 Diablo II knowledge-base sources")
    parser.add_argument("--registry", default="docs/tier0/source-registry.json")
    parser.add_argument("--output-root", default="docs/tier0")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()

    registry_path = Path(args.registry)
    output_root = Path(args.output_root)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    selected = set(args.source)

    results: list[FetchResult] = []

    for source in registry["sources"]:
        if selected and source["id"] not in selected:
            continue

        inventory_urls: list[str] = []
        discovery_rules = source.get("discovery_rules")
        for target in source["targets"]:
            url = target["url"]
            label = target["label"]
            rel_path = target.get("path")
            preferred_output_name = rel_path or f"{slug_from_url(url)}"
            existing_guess = output_root / "raw" / source["id"] / preferred_output_name
            if existing_guess.exists():
                body = existing_guess.read_bytes()
                content_type = content_type_from_path(existing_guess)
                discovered = discover_urls(url, body, content_type, discovery_rules)
                inventory_urls.extend(discovered)
                results.append(
                    FetchResult(
                        source_id=source["id"],
                        label=label,
                        url=url,
                        output_path=str(existing_guess),
                        status="cached",
                        http_status=200,
                        content_type=content_type,
                        bytes_written=len(body),
                        sha256=hashlib.sha256(body).hexdigest(),
                        discovered_url_count=len(discovered),
                        discovered_url_sample=discovered[:15],
                        note="reused existing capture",
                    )
                )
                continue
            try:
                http_status, body, content_type = fetch(url, timeout=args.timeout)
                extension = guess_extension(content_type, url)
                output_name = rel_path or f"{slug_from_url(url)}{extension}"
                output_path = output_root / "raw" / source["id"] / output_name
                write_bytes(output_path, body)
                discovered = discover_urls(url, body, content_type, discovery_rules)
                inventory_urls.extend(discovered)
                sha256 = hashlib.sha256(body).hexdigest()
                results.append(
                    FetchResult(
                        source_id=source["id"],
                        label=label,
                        url=url,
                        output_path=str(output_path),
                        status="ok",
                        http_status=http_status,
                        content_type=content_type,
                        bytes_written=len(body),
                        sha256=sha256,
                        discovered_url_count=len(discovered),
                        discovered_url_sample=discovered[:15],
                    )
                )
            except HTTPError as exc:
                body = exc.read()
                extension = ".txt" if "text" in (exc.headers.get("Content-Type") or "").lower() else ".bin"
                output_name = rel_path or f"{slug_from_url(url)}{extension}"
                output_path = output_root / "raw" / source["id"] / output_name
                write_bytes(output_path, body)
                note = f"HTTPError {exc.code}"
                text_preview = body.decode("utf-8", "ignore")[:500]
                if "API Key Not Found" in text_preview:
                    note = "endpoint requires API key"
                results.append(
                    FetchResult(
                        source_id=source["id"],
                        label=label,
                        url=url,
                        output_path=str(output_path),
                        status="http_error",
                        http_status=exc.code,
                        content_type=exc.headers.get("Content-Type"),
                        bytes_written=len(body),
                        sha256=hashlib.sha256(body).hexdigest(),
                        discovered_url_count=0,
                        discovered_url_sample=[],
                        note=note,
                    )
                )
            except URLError as exc:
                output_name = rel_path or f"{slug_from_url(url)}.error.txt"
                output_path = output_root / "raw" / source["id"] / output_name
                write_text(output_path, str(exc))
                results.append(
                    FetchResult(
                        source_id=source["id"],
                        label=label,
                        url=url,
                        output_path=str(output_path),
                        status="url_error",
                        http_status=None,
                        content_type=None,
                        bytes_written=0,
                        sha256=None,
                        discovered_url_count=0,
                        discovered_url_sample=[],
                        note=str(exc),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                output_name = rel_path or f"{slug_from_url(url)}.error.txt"
                output_path = output_root / "raw" / source["id"] / output_name
                write_text(output_path, repr(exc))
                results.append(
                    FetchResult(
                        source_id=source["id"],
                        label=label,
                        url=url,
                        output_path=str(output_path),
                        status="error",
                        http_status=None,
                        content_type=None,
                        bytes_written=0,
                        sha256=None,
                        discovered_url_count=0,
                        discovered_url_sample=[],
                        note=repr(exc),
                    )
                )

        inventory_path = output_root / "url-inventories" / f"{source['id']}.txt"
        write_text(inventory_path, "\n".join(normalize_urls(inventory_urls)) + ("\n" if inventory_urls else ""))
        write_outputs(results, registry, registry_path, output_root)

    write_outputs(results, registry, registry_path, output_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
