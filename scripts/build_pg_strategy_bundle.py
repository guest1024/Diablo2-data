#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'docs/tier0/postgres-strategy-bundle'
DATA_DIR = OUT_DIR / 'data'
MANIFEST = OUT_DIR / 'manifest.json'
IMPORT_SQL = OUT_DIR / 'import.sql'

SQL_EXPORT = """
COPY (
    SELECT subject_id, predicate, object_id, priority, metadata::text
    FROM d2.strategy_edges
    ORDER BY subject_id, predicate, priority DESC, object_id
) TO STDOUT WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"');
"""


def docker_prefix() -> list[str]:
    import shutil
    import subprocess
    if shutil.which('docker'):
        if subprocess.run(['docker', 'info'], capture_output=True, text=True).returncode == 0:
            return []
    if shutil.which('sudo'):
        if subprocess.run(['sudo', '-n', 'docker', 'info'], capture_output=True, text=True).returncode == 0:
            return ['sudo', '-n']
    return []


def main() -> int:
    prefix = docker_prefix()
    if not prefix:
        raise SystemExit('FAIL: docker access is unavailable; cannot export strategy edges from live PG container.')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tsv_path = DATA_DIR / 'strategy_edges.tsv'

    cmd = prefix + ['docker', 'exec', '-i', 'd2-pg17', '/opt/postgresql/bin/psql', '-U', 'd2', '-d', 'd2', '-At', '-c', SQL_EXPORT]
    result = __import__('subprocess').run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout or 'FAIL: strategy edge export failed')
    tsv_path.write_text(result.stdout, encoding='utf-8')

    row_count = 0
    with tsv_path.open(encoding='utf-8', newline='') as handle:
        row_count = sum(1 for _ in csv.reader(handle, delimiter='\t', quotechar='"'))

    import_sql = f"""\\set ON_ERROR_STOP on
BEGIN;
CREATE TABLE IF NOT EXISTS d2.strategy_edge_facts (
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    priority INTEGER,
    metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    PRIMARY KEY (subject_id, predicate, object_id)
);
TRUNCATE TABLE d2.strategy_edge_facts;
\\copy d2.strategy_edge_facts (subject_id, predicate, object_id, priority, metadata) FROM '{tsv_path.resolve()}' WITH (FORMAT csv, DELIMITER E'\\t', QUOTE '"')
COMMIT;
"""
    IMPORT_SQL.write_text(import_sql, encoding='utf-8')
    MANIFEST.write_text(json.dumps({
        'rows': row_count,
        'paths': {
            'strategy_edges': str(tsv_path.relative_to(ROOT)),
            'import_sql': str(IMPORT_SQL.relative_to(ROOT)),
        },
        'source': 'd2.strategy_edges live export',
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rows': row_count}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
