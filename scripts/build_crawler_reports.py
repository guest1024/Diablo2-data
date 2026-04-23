#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ["python3", "crawler/report_snapshots.py", "--limit", "50"],
    ["python3", "crawler/build_source_status_report.py"],
    ["python3", "crawler/build_manual_curated_backlog.py"],
    ["python3", "crawler/export_snapshot_relations.py"],
    ["python3", "crawler/export_page_catalog_partitions.py"],
    ["python3", "crawler/export_page_records.py"],
    ["python3", "crawler/audit_publish_bundle.py"],
    ["python3", "crawler/build_data_branch_manifest.py"],
    ["python3", "crawler/check_data_branch_readiness.py"],
]
OUTPUT_REDIRECTS = {
    ("python3", "crawler/report_snapshots.py", "--limit", "50"): REPO_ROOT / "crawler/state/catalog-report.md",
    ("python3", "crawler/build_source_status_report.py"): REPO_ROOT / "crawler/state/source-status-report.md",
    ("python3", "crawler/build_manual_curated_backlog.py"): REPO_ROOT / "crawler/state/manual-curated-backlog.md",
}


def run_command(cmd: list[str]) -> None:
    key = tuple(cmd)
    output_path = OUTPUT_REDIRECTS.get(key)
    if output_path:
        completed = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
        output_path.write_text(completed.stdout, encoding="utf-8")
        return
    subprocess.run(cmd, cwd=REPO_ROOT, text=True, check=True)


def main() -> int:
    for command in COMMANDS:
        print("RUN", " ".join(command))
        run_command(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
