#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs/tier0/readiness-checklist.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(CHECKLIST.is_file(), "readiness checklist exists")
    text = CHECKLIST.read_text(encoding="utf-8")
    for phrase in [
        "Data readiness",
        "Graph readiness",
        "Export readiness",
        "Operator readiness",
        "Residual Tier 1 work",
    ]:
        expect(phrase in text, f"checklist contains '{phrase}'")
    expect(text.count("[x]") >= 10, "checklist contains completed readiness items")
    expect(text.count("[ ]") >= 3, "checklist contains deferred Tier 1 items")
    print("PASS: readiness checklist verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
