#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.catalog import load_page_catalog
from crawler.storage import write_json, write_partitioned_jsonl

CATALOG_PATH = CURRENT_DIR / 'state/page_catalog.json'
OUT_DIR = CURRENT_DIR / 'state/page-catalog'
INDEX_PATH = OUT_DIR / 'index.json'


def build_partition_rows() -> list[dict]:
    catalog = load_page_catalog(CATALOG_PATH)
    rows: list[dict] = []
    for key, row in sorted(catalog.items(), key=lambda item: (item[1].get('source_id', ''), item[1].get('url', ''))):
        rows.append({'catalog_key': key, **row})
    return rows


def main() -> int:
    rows = build_partition_rows()
    written = write_partitioned_jsonl(OUT_DIR, rows, 'source_id')
    write_json(
        INDEX_PATH,
        {
            'rows': len(rows),
            'partitions': [str(path.relative_to(CURRENT_DIR)) for path in sorted(written)],
        },
    )
    print(json.dumps({'rows': len(rows), 'partitions': len(written), 'output_dir': str(OUT_DIR.relative_to(CURRENT_DIR))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
