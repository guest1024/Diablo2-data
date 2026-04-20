#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    readme = TIER0 / "README.md"
    summary_path = TIER0 / "stack-summary.json"
    expect(readme.is_file(), "tier0 README exists")
    expect(summary_path.is_file(), "tier0 stack summary exists")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expect(summary["sources"] >= 5, "summary reports at least 5 sources")
    expect(summary["captures"] >= 15, "summary reports at least 15 captures")
    expect(summary["documents"] >= 20, "summary reports at least 20 normalized documents")
    expect(summary["chunks"] >= summary["documents"], "summary chunk count is at least document count")
    expect(summary["artifact_checksum_count"] >= 10, "summary includes checksum coverage")

    readme_text = readme.read_text(encoding="utf-8")
    for phrase in [
        "Graph export bundle",
        "Neo4j playbook",
        "run_tier0_pipeline.py",
        "verify_tier0_stack.py",
        "verify_artifact_checksums.py",
    ]:
        expect(phrase in readme_text, f"README contains '{phrase}'")

    print("PASS: tier0 index verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
