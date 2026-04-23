#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    ["python3", "crawler/run_tests.py"],
    ["python3", "crawler/validate_manual_curated_urls.py"],
    ["python3", "crawler/probe_manual_curated_urls.py"],
    ["python3", "scripts/build_crawler_reports.py"],
    ["python3", "crawler/verify_framework.py"],
    ["python3", "scripts/push_crawler_to_data_branch.py", "--branch", "data", "--remote", "origin", "--preview-only", "--latest-only"],
]


def main() -> int:
    for step in STEPS:
        print("RUN", " ".join(step))
        subprocess.run(step, cwd=REPO_ROOT, text=True, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
