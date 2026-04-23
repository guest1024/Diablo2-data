#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/tier0/postgres-dict-bundle/manifest.json'
IMPORT_SQL = ROOT / 'docs/tier0/postgres-dict-bundle/import.sql'


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def main() -> int:
    expect(MANIFEST.is_file(), 'pg dict bundle manifest exists')
    expect(IMPORT_SQL.is_file(), 'pg dict bundle import.sql exists')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    import_sql = IMPORT_SQL.read_text(encoding='utf-8')
    required = {
        'term_dictionary','alias_dictionary','build_dictionary','build_dictionary_skills','item_dictionary','area_dictionary','monster_dictionary','rule_dictionary','query_pattern_dictionary','retrieval_policies','answer_constraints'
    }
    tables = manifest.get('tables', {})
    expect(required.issubset(tables.keys()), 'dict bundle contains required tables')
    for table_name, spec in tables.items():
        path = ROOT / spec['path']
        expect(path.is_file(), f'dict bundle data file exists: {table_name}')
        with path.open(encoding='utf-8', newline='') as handle:
            row_count = sum(1 for _ in csv.reader(handle, delimiter='\t', quotechar='"'))
        expect(row_count == spec['rows'], f'row count matches manifest for {table_name}')
        expect(table_name in import_sql, f'import.sql references {table_name}')
    expect(tables['term_dictionary']['rows'] >= 20, 'term dictionary has starter coverage')
    expect(tables['alias_dictionary']['rows'] >= 100, 'alias dictionary has strong coverage')
    expect(tables['build_dictionary']['rows'] >= 5, 'build dictionary has starter coverage')
    expect(tables['item_dictionary']['rows'] >= 500, 'item dictionary has substantial coverage')
    expect(tables['rule_dictionary']['rows'] >= 50, 'rule dictionary has substantial coverage')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
