#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs/tier0/release-notes.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(NOTES.is_file(), "release notes exist")
    text = NOTES.read_text(encoding="utf-8")
    for phrase in [
        "Summary",
        "Deliverables",
        "CSV export counts",
        "Known next-step work",
        "Tier 0 raw capture + scoped inventories",
    ]:
        expect(phrase in text, f"release notes contain '{phrase}'")
    print("PASS: release notes verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
