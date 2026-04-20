#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/tier0/artifact-matrix.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(MATRIX.is_file(), "artifact matrix exists")
    text = MATRIX.read_text(encoding="utf-8")
    for phrase in [
        "Fetch",
        "Normalized",
        "Graph seed",
        "Canonical graph",
        "Export CSV",
        "Integrity",
        "run_tier0_pipeline.py",
        "verify_tier0_stack.py",
        "query-recipes.md",
    ]:
        expect(phrase in text, f"artifact matrix contains '{phrase}'")
    print("PASS: artifact matrix verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
