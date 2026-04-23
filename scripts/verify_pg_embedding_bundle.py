#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/tier0/postgres-embedding-bundle/manifest.json'
IMPORT_SQL = ROOT / 'docs/tier0/postgres-embedding-bundle/import.sql'


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def main() -> int:
    expect(MANIFEST.is_file(), 'pg embedding bundle manifest exists')
    expect(IMPORT_SQL.is_file(), 'pg embedding import.sql exists')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    tsv = ROOT / manifest['paths']['chunk_embeddings']
    expect(tsv.is_file(), 'chunk embedding TSV exists')
    with tsv.open(encoding='utf-8', newline='') as handle:
        row_count = sum(1 for _ in csv.reader(handle, delimiter='\t', quotechar='"'))
    expect(row_count == manifest['rows'], 'embedding row count matches manifest')
    expect(manifest['rows'] >= 8000, 'embedding bundle covers chunk corpus')
    expect(manifest['dimensions'] == 384, 'embedding dimension matches runtime baseline')
    expect('UPDATE d2.chunks' in IMPORT_SQL.read_text(encoding='utf-8'), 'import.sql updates d2.chunks embedding column')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
