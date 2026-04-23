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
    ROOT / "sql/postgres/001_core_schema.sql",
    ROOT / "sql/postgres/003_views.sql",
]
OPTIONAL_VECTOR = ROOT / "sql/postgres/002_optional_vector.sql"
IMPORT_SQL = ROOT / "docs/tier0/postgres-bundle/import.sql"


def main() -> int:
    parser = argparse.ArgumentParser(description="Load the generated Diablo II PostgreSQL bundle using psql.")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"), help="PostgreSQL connection URL. Falls back to DATABASE_URL.")
    parser.add_argument("--with-vector", action="store_true", help="Also run the optional pgvector extension script.")
    parser.add_argument("--skip-bundle-build", action="store_true", help="Skip rebuilding docs/tier0/postgres-bundle before loading.")
    args = parser.parse_args()

    ensure_psql_access()

    if not args.skip_bundle_build:
        subprocess.run([PYTHON, str(ROOT / "scripts/build_postgres_bundle.py")], check=True)

    if not IMPORT_SQL.is_file():
        raise SystemExit(f"FAIL: missing import SQL bundle: {IMPORT_SQL}")

    for schema_file in SCHEMA_FILES:
        run_psql_file(schema_file, database_url=args.database_url)
    if args.with_vector:
        run_psql_file(OPTIONAL_VECTOR, database_url=args.database_url)
    run_psql_file(IMPORT_SQL, database_url=args.database_url)
    print("PASS: PostgreSQL bundle loaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
