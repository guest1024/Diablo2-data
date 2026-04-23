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
from crawler.storage import write_json, write_jsonl, write_partitioned_jsonl

CATALOG_PATH = CURRENT_DIR / 'state/page_catalog.json'
OUT_PATH = CURRENT_DIR / 'state/snapshot-relations.jsonl'
PARTITIONED_DIR = CURRENT_DIR / 'state/snapshot-relations'
INDEX_PATH = PARTITIONED_DIR / 'index.json'


def build_snapshot_relations() -> list[dict]:
    catalog = load_page_catalog(CATALOG_PATH)
    rows: list[dict] = []
    for row in sorted(catalog.values(), key=lambda item: (item.get('source_id', ''), item.get('url', ''))):
        if not row.get('snapshot_path'):
            continue
        rows.append(
            {
                'source_id': row.get('source_id'),
                'source_label': row.get('source_label'),
                'url': row.get('url'),
                'title': row.get('title'),
                'snapshot_id': row.get('snapshot_id'),
                'snapshot_path': row.get('snapshot_path'),
                'sha256': row.get('sha256'),
                'http_status': row.get('http_status'),
                'content_type': row.get('content_type'),
                'capture_status': row.get('capture_status'),
                'lifecycle_status': row.get('lifecycle_status'),
                'first_seen_at': row.get('first_seen_at'),
                'last_seen_at': row.get('last_seen_at'),
                'last_run_id': row.get('last_run_id'),
            }
        )
    return rows


def main() -> int:
    rows = build_snapshot_relations()
    write_jsonl(OUT_PATH, rows)
    partitioned_files = write_partitioned_jsonl(PARTITIONED_DIR, rows, 'source_id')
    write_json(
        INDEX_PATH,
        {
            'rows': len(rows),
            'partitions': [str(path.relative_to(CURRENT_DIR)) for path in sorted(partitioned_files)],
            'monolithic': str(OUT_PATH.relative_to(CURRENT_DIR)),
        },
    )
    print(json.dumps({'rows': len(rows), 'output': str(OUT_PATH.relative_to(CURRENT_DIR)), 'partitions': len(partitioned_files)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
