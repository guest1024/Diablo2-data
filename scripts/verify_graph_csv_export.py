#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "docs" / "tier0" / "export"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    return max(0, len(rows) - 1)


def main() -> int:
    manifest_path = EXPORT / "csv-export-manifest.json"
    expect(manifest_path.is_file(), "csv export manifest exists")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for name, relative in manifest["files"].items():
        path = ROOT / relative
        expect(path.is_file(), f"{name} csv exists")
        row_count = count_csv_rows(path)
        expect(row_count == manifest["csv_tables"][name], f"{name} row count matches manifest")
        expect(row_count > 0, f"{name} csv has positive row count")

    print("PASS: graph csv export verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
