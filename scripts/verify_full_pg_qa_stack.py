#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"

CHECKS = [
    "scripts/verify_query_execution_chain.py",
    "scripts/verify_postgres_runtime_ready.py",
    "scripts/verify_api_pg_runtime.py",
    "scripts/verify_llm_reasoned_answers.py",
]


def main() -> int:
    results: list[dict[str, object]] = []
    for relative in CHECKS:
        path = ROOT / relative
        completed = subprocess.run(
            [str(PYTHON), str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        results.append(
            {
                "script": relative,
                "returncode": completed.returncode,
                "ok": completed.returncode == 0,
                "stdout_tail": completed.stdout[-1500:],
                "stderr_tail": completed.stderr[-1500:],
            }
        )
        if completed.returncode != 0:
            print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
            return completed.returncode

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
