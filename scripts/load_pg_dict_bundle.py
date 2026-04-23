#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = [
    ROOT / 'sql/postgres/004_dict_query_quality_schema.sql',
    ROOT / 'sql/postgres/005_dict_query_quality_views.sql',
]
IMPORT_SQL = ROOT / 'docs/tier0/postgres-dict-bundle/import.sql'


def psql_base_cmd(database_url: str | None) -> list[str]:
    cmd = ['psql', '-v', 'ON_ERROR_STOP=1']
    if database_url:
        cmd.append(database_url)
    return cmd


def run_psql_file(path: Path, database_url: str | None) -> None:
    subprocess.run(psql_base_cmd(database_url) + ['-f', str(path)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description='Load PostgreSQL dictionary/query-understanding bundle.')
    parser.add_argument('--database-url', default=os.environ.get('DATABASE_URL'))
    parser.add_argument('--skip-bundle-build', action='store_true')
    args = parser.parse_args()

    if shutil.which('psql') is None:
        raise SystemExit('FAIL: psql is not installed.')
    if not args.skip_bundle_build:
        subprocess.run(['python3', str(ROOT / 'scripts/build_pg_dict_bundle.py')], check=True)
    for schema_file in SCHEMA_FILES:
        run_psql_file(schema_file, args.database_url)
    run_psql_file(IMPORT_SQL, args.database_url)
    print('PASS: PostgreSQL dictionary bundle loaded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
