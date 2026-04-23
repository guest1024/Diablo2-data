from __future__ import annotations

import hashlib
import re
from urllib.parse import urljoin, urlparse

from crawler.extractors import LinkExtractor
from crawler.http_client import decode_bytes
from crawler.models import FetchResponse, SourceConfig


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug_url(url: str) -> str:
    parsed = urlparse(url)
    base = f"{parsed.netloc}{parsed.path}"
    if parsed.query:
        base += f"__{parsed.query}"
    base = base.rstrip("/") or parsed.netloc
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base)
    return base[:180].strip("-") or "page"


def normalize_urls(urls: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        clean = url.strip()
        if not clean:
            continue
        clean = clean.split("#", 1)[0]
        if clean.startswith("//"):
            clean = f"https:{clean}"
        if clean not in seen:
            seen.add(clean)
            ordered.append(clean)
    return ordered


def discover_urls(source: SourceConfig, seed_url: str, response: FetchResponse, max_discover: int) -> list[str]:
    if not response.body:
        return []

    text = decode_bytes(response.body, response.content_type, source.encoding_hints)
    content_type = (response.content_type or "").lower()
    discovered: list[str] = []

    if "html" in content_type:
        parser = LinkExtractor()
        parser.feed(text)
        discovered.extend(urljoin(seed_url, href) for href in parser.links)
    elif "xml" in content_type:
        discovered.extend(re.findall(r"<loc>([^<]+)</loc>", text))
    else:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(("http://", "https://")):
                discovered.append(line)

    include_patterns = [re.compile(pattern) for pattern in source.discovery.include]
    exclude_patterns = [re.compile(pattern) for pattern in source.discovery.exclude]
    home_host = urlparse(source.home_url).netloc
    filtered: list[str] = []

    for url in normalize_urls(discovered):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        if source.discovery.same_host and parsed.netloc != home_host:
            continue
        if include_patterns and not any(pattern.search(url) for pattern in include_patterns):
            continue
        if any(pattern.search(url) for pattern in exclude_patterns):
            continue
        filtered.append(url)
        if len(filtered) >= max_discover:
            break
    return filtered


def score_candidate(url: str, source: SourceConfig, curated_urls: set[str]) -> int:
    lowered = url.lower()
    score = 0
    if url in curated_urls and source.selection.prefer_curated:
        score += 1000
    for keyword in source.selection.preferred_keywords:
        if keyword.lower() in lowered:
            score += 25
    for keyword in source.selection.denied_keywords:
        if keyword.lower() in lowered:
            score -= 50
    return score


def select_candidates(
    source: SourceConfig,
    discovered_urls: list[str],
    limit: int,
    fetch_multiplier: int = 4,
) -> list[str]:
    curated = normalize_urls(list(source.curated_urls))
    discovered = normalize_urls(discovered_urls)
    merged = normalize_urls([*curated, *discovered])
    curated_set = set(curated)
    ranked = sorted(enumerate(merged), key=lambda item: (-score_candidate(item[1], source, curated_set), item[0]))
    fetch_limit = min(len(ranked), max(limit * fetch_multiplier, limit))
    return [url for _, url in ranked[:fetch_limit]]
