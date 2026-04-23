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
from crawler.storage import mirrored_relative_path, write_json

CATALOG_PATH = CURRENT_DIR / 'state/page_catalog.json'
OUT_DIR = CURRENT_DIR / 'state/page-records'
INDEX_PATH = OUT_DIR / 'index.json'


def build_record_rows() -> list[tuple[str, dict]]:
    catalog = load_page_catalog(CATALOG_PATH)
    return sorted(catalog.items(), key=lambda item: (item[1].get('source_id', ''), item[1].get('url', '')))


def prune_stale_record_files(keep_paths: set[Path]) -> None:
    if not OUT_DIR.is_dir():
        return
    for path in sorted(OUT_DIR.rglob('*.json'), reverse=True):
        if path == INDEX_PATH:
            continue
        if path not in keep_paths:
            path.unlink()
    for directory in sorted(OUT_DIR.rglob('*'), reverse=True):
        if directory.is_dir() and directory != OUT_DIR and not any(directory.iterdir()):
            directory.rmdir()


def main() -> int:
    rows = build_record_rows()
    keep_paths: set[Path] = set()
    source_counts: dict[str, int] = {}

    for catalog_key, row in rows:
        source_id = str(row.get('source_id') or 'unknown')
        path = OUT_DIR / mirrored_relative_path(
            source_id,
            str(row.get('url') or ''),
            row.get('content_type'),
            extension='.json',
            for_metadata=True,
        )
        keep_paths.add(path)
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
        write_json(path, {'catalog_key': catalog_key, **row})

    prune_stale_record_files(keep_paths)
    write_json(
        INDEX_PATH,
        {
            'rows': len(rows),
            'sources': source_counts,
            'partitions': [str((OUT_DIR / source_id).relative_to(CURRENT_DIR)) for source_id in sorted(source_counts)],
        },
    )
    print(
        json.dumps(
            {'rows': len(rows), 'sources': len(source_counts), 'output_dir': str(OUT_DIR.relative_to(CURRENT_DIR))},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
