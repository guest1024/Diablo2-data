#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def main() -> int:
    bundle_path = MERGED / "export-bundle.json"
    report_path = MERGED / "export-bundle-report.md"
    expect(bundle_path.is_file(), "merged export bundle exists")
    expect(report_path.is_file(), "merged export bundle report exists")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    expect(bundle["bundle_name"] == "diablo2-tier0-merged-graph-export", "merged bundle name matches")
    expect(bundle["recommended_load_order"] == ["nodes", "edges", "claims", "chunks"], "merged bundle load order is present")
    for name, relative in bundle["paths"].items():
        path = ROOT / relative
        expect(path.is_file(), f"merged bundle file exists for {name}")
        expect(count_jsonl(path) == bundle["counts"][name], f"merged bundle count matches for {name}")
        expect(bundle["counts"][name] > 0, f"merged bundle {name} count is positive")
    print("PASS: merged export bundle verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
