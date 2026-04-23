#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.config import load_config
from crawler.extractors import extract_page_fields
from crawler.models import CrawlOptions, FetchResponse
from crawler.runner import DEFAULT_CONFIG, run_crawl
from crawler.selection import discover_urls, normalize_urls, slug_url


def parse_args(argv: list[str] | None = None) -> CrawlOptions:
    parser = argparse.ArgumentParser(description="Run stable Chinese-site snapshot discovery and first-capture freezing")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--source", action="append", dest="sources", help="limit to one or more source ids")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--limit-per-source", type=int, default=2)
    parser.add_argument("--max-discover", type=int, default=12)
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--include-disabled", action="store_true")
    parser.add_argument("--refresh-existing", action="store_true", help="re-fetch already captured pages explicitly")
    args = parser.parse_args(argv)
    return CrawlOptions(
        config_path=Path(args.config).resolve(),
        timeout=args.timeout,
        limit_per_source=args.limit_per_source,
        max_discover=args.max_discover,
        probe_only=args.probe_only,
        include_disabled=args.include_disabled,
        refresh_existing=args.refresh_existing,
        source_ids=tuple(args.sources or ()),
    )


def main(argv: list[str] | None = None) -> int:
    options = parse_args(argv)
    run_crawl(options)
    return 0


__all__ = [
    "CrawlOptions",
    "FetchResponse",
    "discover_urls",
    "extract_page_fields",
    "load_config",
    "main",
    "normalize_urls",
    "parse_args",
    "slug_url",
    "run_crawl",
]


if __name__ == "__main__":
    raise SystemExit(main())
