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
IMPORT_SQL = ROOT / 'docs/tier0/postgres-embedding-bundle/import.sql'


def main() -> int:
    parser = argparse.ArgumentParser(description='Load PostgreSQL embedding bundle into d2.chunks.embedding using psql.')
    parser.add_argument('--database-url', default=os.environ.get('DATABASE_URL'))
    parser.add_argument('--skip-build', action='store_true')
    args = parser.parse_args()

    ensure_psql_access()
    if not args.skip_build:
        subprocess.run([PYTHON, str(ROOT / 'scripts/build_pg_embedding_bundle.py')], check=True)
    run_psql_file(IMPORT_SQL, database_url=args.database_url)
    print('PASS: PostgreSQL embedding bundle loaded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
