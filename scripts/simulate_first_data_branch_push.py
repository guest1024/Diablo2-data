#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_STEPS = [
    ["python3", "crawler/validate_manual_curated_urls.py"],
    ["python3", "crawler/probe_manual_curated_urls.py"],
    ["python3", "scripts/build_crawler_reports.py"],
    ["python3", "crawler/verify_framework.py"],
    ["python3", "scripts/push_crawler_to_data_branch.py", "--branch", "data", "--remote", "origin", "--preview-only", "--latest-only"],
]
REAL_PUSH_STEP = ["python3", "scripts/push_crawler_to_data_branch.py", "--branch", "data", "--remote", "origin", "--latest-only"]


def main() -> int:
    parser = argparse.ArgumentParser(description='Simulate the first real data-branch push workflow')
    parser.add_argument('--real-push', action='store_true', help='execute the final data-branch push instead of stopping after preview')
    args = parser.parse_args()

    steps = list(BASE_STEPS)
    if args.real_push:
        steps.append(REAL_PUSH_STEP)

    for step in steps:
        print('RUN', ' '.join(step))
        subprocess.run(step, cwd=REPO_ROOT, text=True, check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
