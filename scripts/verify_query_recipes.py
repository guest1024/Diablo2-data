#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "docs/tier0/query-recipes.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(RECIPES.is_file(), "query recipes file exists")
    text = RECIPES.read_text(encoding="utf-8")
    for phrase in [
        "Resolve an alias to a canonical entity",
        "Get canonical claims for an entity",
        "Show provenance for a claim",
        "Find API-gated knowledge",
        "Retrieve chunks for grounded answering",
        "Version-aware lookup",
    ]:
        expect(phrase in text, f"recipes contain '{phrase}'")
    print("PASS: query recipes verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
