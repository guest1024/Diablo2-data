#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.catalog import load_page_catalog
from crawler.reporting import build_catalog_summary, filter_catalog_rows, render_catalog_markdown

DEFAULT_CATALOG = CURRENT_DIR / "state/page_catalog.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report crawler snapshot catalog and URL->snapshot mappings")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--source")
    parser.add_argument("--capture-status")
    parser.add_argument("--lifecycle-status")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--all-rows", action="store_true", help="include rows without snapshot_path")
    args = parser.parse_args(argv)

    catalog = load_page_catalog(Path(args.catalog))
    rows = filter_catalog_rows(
        catalog,
        source_id=args.source,
        capture_status=args.capture_status,
        lifecycle_status=args.lifecycle_status,
        snapshot_only=not args.all_rows,
    )
    summary = build_catalog_summary(rows)

    if args.format == "json":
        print(json.dumps({"summary": summary, "rows": rows[: args.limit]}, ensure_ascii=False, indent=2))
    else:
        print(render_catalog_markdown(summary, rows, limit=args.limit), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
