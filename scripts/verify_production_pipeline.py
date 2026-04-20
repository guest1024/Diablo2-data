#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    required = [
        "docs/tier0/merged/export-bundle.json",
        "docs/tier0/merged/csv/manifest.json",
        "docs/tier0/merged/CONSUMER-GUIDE.md",
        "docs/tier0/merged/QUICKSTART.md",
        "docs/tier0/merged/HANDOFF.md",
        "docs/tier0/merged/sample-queries.json",
        "docs/tier0/high-value/summary.json",
        "docs/tier0/combined-content-stats.json",
        "docs/tier0/bilingual-graphrag-guidelines.md",
    ]
    for rel in required:
        expect((ROOT / rel).is_file(), f"{rel} exists")

    merged_bundle = json.loads((ROOT / "docs/tier0/merged/export-bundle.json").read_text(encoding="utf-8"))
    merged_csv = json.loads((ROOT / "docs/tier0/merged/csv/manifest.json").read_text(encoding="utf-8"))
    combined = json.loads((ROOT / "docs/tier0/combined-content-stats.json").read_text(encoding="utf-8"))

    expect(merged_bundle["counts"]["nodes"] >= 650, "merged bundle node count is populated")
    expect(merged_bundle["counts"]["chunks"] >= 7000, "merged bundle chunk count is populated")
    expect(merged_csv["csv_tables"]["chunks"] == merged_bundle["counts"]["chunks"], "merged csv chunk count matches merged bundle")
    expect(combined["combined_chars"] > 8000000, "combined chars exceed 8M")
    expect(combined["combined_chunk_surfaces"] > 7000, "combined chunk surfaces exceed 7k")
    print("PASS: production pipeline verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
