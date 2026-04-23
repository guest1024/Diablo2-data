#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.storage import write_json, write_partitioned_jsonl

HEALTH_PATH = CURRENT_DIR / 'state/source-health.json'
OUT_DIR = CURRENT_DIR / 'state/source-health'
INDEX_PATH = OUT_DIR / 'index.json'


def build_rows() -> list[dict]:
    if not HEALTH_PATH.is_file():
        return []
    payload = json.loads(HEALTH_PATH.read_text(encoding='utf-8'))
    return list(payload.get('sources', []))


def main() -> int:
    rows = build_rows()
    written = write_partitioned_jsonl(OUT_DIR, rows, 'id')
    write_json(
        INDEX_PATH,
        {
            'rows': len(rows),
            'partitions': [str(path.relative_to(CURRENT_DIR)) for path in sorted(written)],
            'source_health': str(HEALTH_PATH.relative_to(CURRENT_DIR)),
        },
    )
    print(json.dumps({'rows': len(rows), 'partitions': len(written), 'output_dir': str(OUT_DIR.relative_to(CURRENT_DIR))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
