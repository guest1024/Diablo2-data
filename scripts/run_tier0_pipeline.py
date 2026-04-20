#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ["python3", "scripts/fetch_tier0.py", "--timeout", "8"],
    ["python3", "scripts/verify_tier0_fetch.py"],
    ["python3", "scripts/normalize_tier0.py"],
    ["python3", "scripts/verify_tier0_normalization.py"],
    ["python3", "scripts/extract_graph_seed.py"],
    ["python3", "scripts/verify_graph_seed.py"],
    ["python3", "scripts/extract_alias_seed.py"],
    ["python3", "scripts/verify_alias_seed.py"],
    ["python3", "scripts/refine_graph_seed.py"],
    ["python3", "scripts/verify_refined_graph.py"],
    ["python3", "scripts/normalize_claim_seed.py"],
    ["python3", "scripts/verify_claim_normalization.py"],
    ["python3", "scripts/build_graph_export_bundle.py"],
    ["python3", "scripts/verify_graph_export_bundle.py"],
    ["python3", "scripts/extract_version_semantics.py"],
    ["python3", "scripts/verify_version_semantics.py"],
    ["python3", "scripts/export_graph_csv.py"],
    ["python3", "scripts/verify_graph_csv_export.py"],
    ["python3", "scripts/build_artifact_checksums.py"],
    ["python3", "scripts/verify_artifact_checksums.py"],
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full Diablo II Tier 0 pipeline")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for step in STEPS:
        print(f"==> {' '.join(step)}")
        if args.dry_run:
            continue
        completed = subprocess.run(step, cwd=ROOT)
        if completed.returncode != 0:
            return completed.returncode
    print("PASS: full Tier 0 pipeline completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
