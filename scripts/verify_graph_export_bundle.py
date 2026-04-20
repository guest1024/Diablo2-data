#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "docs" / "tier0" / "derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    bundle_path = DERIVED / "graph-export-bundle.json"
    report_path = DERIVED / "graph-export-bundle-report.md"
    expect(bundle_path.is_file(), "graph export bundle exists")
    expect(report_path.is_file(), "graph export bundle report exists")

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    expect(bundle["bundle_name"] == "diablo2-tier0-graph-export", "bundle name matches")
    expect("schema" in bundle and "query_examples" in bundle, "bundle has schema and query examples")
    expect(len(bundle["query_examples"]) >= 3, "bundle contains at least three query examples")
    expect("recommended_load_order" in bundle["schema"], "schema includes recommended load order")
    expect("entity_lookup" in bundle["schema"]["recommended_query_entrypoints"], "schema includes query entrypoints")

    for name, relative_path in bundle["files"].items():
        expect((ROOT / relative_path).is_file(), f"bundle file exists for {name}")
        expect(bundle["counts"][name] > 0, f"bundle count for {name} is positive")

    print("PASS: graph export bundle verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
