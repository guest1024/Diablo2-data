#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUICKSTART = ROOT / "docs/tier0/QUICKSTART.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(QUICKSTART.is_file(), "quickstart exists")
    text = QUICKSTART.read_text(encoding="utf-8")
    for phrase in [
        "run_tier0_pipeline.py",
        "verify_tier0_stack.py",
        "verify_artifact_checksums.py",
        "graph-export-bundle.json",
        "csv-export-manifest.json",
        "sample-queries.json",
    ]:
        expect(phrase in text, f"quickstart contains '{phrase}'")
    print("PASS: quickstart verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
