#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from pg_exec_utils import ensure_psql_access, run_psql_file

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
SCHEMA_FILES = [
    ROOT / 'sql/postgres/004_dict_query_quality_schema.sql',
    ROOT / 'sql/postgres/005_dict_query_quality_views.sql',
]
IMPORT_SQL = ROOT / 'docs/tier0/postgres-dict-bundle/import.sql'


def main() -> int:
    parser = argparse.ArgumentParser(description='Load PostgreSQL dictionary/query-understanding bundle.')
    parser.add_argument('--database-url', default=os.environ.get('DATABASE_URL'))
    parser.add_argument('--skip-bundle-build', action='store_true')
    args = parser.parse_args()

    ensure_psql_access()
    if not args.skip_bundle_build:
        subprocess.run([PYTHON, str(ROOT / 'scripts/build_pg_dict_bundle.py')], check=True)
    for schema_file in SCHEMA_FILES:
        run_psql_file(schema_file, database_url=args.database_url)
    run_psql_file(IMPORT_SQL, database_url=args.database_url)
    print('PASS: PostgreSQL dictionary bundle loaded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
