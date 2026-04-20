#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/tier0/artifact-catalog.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(CATALOG.is_file(), "artifact catalog exists")
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = payload["entries"]
    expect(len(entries) >= 10, "artifact catalog includes multiple entries")
    expect(all(entry["exists"] for entry in entries), "all cataloged entries exist")
    categories = {entry["category"] for entry in entries}
    for category in {"manifest", "documentation", "query_examples"}:
        expect(category in categories, f"artifact catalog includes category {category}")
    counts = payload["counts"]
    expect(counts["raw_files"] > 0, "catalog reports raw files")
    expect(counts["derived_files"] > 0, "catalog reports derived files")
    expect(counts["export_files"] > 0, "catalog reports export files")
    print("PASS: artifact catalog verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
