#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/tier0/postgres-strategy-bundle/manifest.json'
IMPORT_SQL = ROOT / 'docs/tier0/postgres-strategy-bundle/import.sql'


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def main() -> int:
    expect(MANIFEST.is_file(), 'pg strategy bundle manifest exists')
    expect(IMPORT_SQL.is_file(), 'pg strategy import.sql exists')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    tsv = ROOT / manifest['paths']['strategy_edges']
    expect(tsv.is_file(), 'strategy edges TSV exists')
    with tsv.open(encoding='utf-8', newline='') as handle:
        row_count = sum(1 for _ in csv.reader(handle, delimiter='\t', quotechar='"'))
    expect(row_count == manifest['rows'], 'strategy edge row count matches manifest')
    expect(row_count >= 10, 'strategy edge bundle has starter coverage')
    text = IMPORT_SQL.read_text(encoding='utf-8')
    expect('CREATE TABLE IF NOT EXISTS d2.strategy_edge_facts' in text, 'strategy import creates strategy_edge_facts table')
    expect('\\copy d2.strategy_edge_facts' in text, 'strategy import loads strategy_edge_facts data')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
