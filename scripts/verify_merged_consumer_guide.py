#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/tier0/merged/CONSUMER-GUIDE.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(GUIDE.is_file(), "merged consumer guide exists")
    text = GUIDE.read_text(encoding="utf-8")
    for phrase in [
        "export-bundle.json",
        "Suggested loading order",
        "Suggested query strategy",
        "nodes: `925`",
        "chunks: `8155`",
    ]:
        expect(phrase in text, f"merged consumer guide contains '{phrase}'")
    print("PASS: merged consumer guide verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
