#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load all PostgreSQL assets in order: schema bundle, dict bundle, embeddings, strategy facts."
    )
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--with-vector", action="store_true", help="Also apply optional pgvector schema file before loading.")
    parser.add_argument("--skip-build", action="store_true", help="Skip bundle rebuild and only load current artifacts.")
    args = parser.parse_args()

    commands = [
        [PYTHON, str(ROOT / "scripts/load_postgres_bundle.py")],
        [PYTHON, str(ROOT / "scripts/load_pg_dict_bundle.py")],
        [PYTHON, str(ROOT / "scripts/load_pg_embedding_bundle.py")],
        [PYTHON, str(ROOT / "scripts/load_pg_strategy_bundle.py")],
    ]

    for command in commands:
        if args.database_url:
            command.extend(["--database-url", args.database_url])
        if args.skip_build:
            if command[-1].endswith("load_postgres_bundle.py") or "load_postgres_bundle.py" in command[1]:
                command.append("--skip-bundle-build")
            elif "load_pg_dict_bundle.py" in command[1]:
                command.append("--skip-bundle-build")
            else:
                command.append("--skip-build")
        if args.with_vector and "load_postgres_bundle.py" in command[1]:
            command.append("--with-vector")

        print("==>", " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)

    print("PASS: all PostgreSQL assets loaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
