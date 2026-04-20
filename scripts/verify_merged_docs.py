#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    quickstart = MERGED / "QUICKSTART.md"
    handoff = MERGED / "HANDOFF.md"
    expect(quickstart.is_file(), "merged quickstart exists")
    expect(handoff.is_file(), "merged handoff exists")

    quickstart_text = quickstart.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    for phrase in [
        "export-bundle.json",
        "summary.md",
        "sample-queries.json",
        "nodes: `925`",
        "chunks: `8155`",
    ]:
        expect(phrase in quickstart_text, f"quickstart contains '{phrase}'")

    for phrase in [
        "Primary entrypoints",
        "export-bundle.json",
        "CONSUMER-GUIDE.md",
        "QUICKSTART.md",
        "sample-queries.json",
        "Current counts",
    ]:
        expect(phrase in handoff_text, f"handoff contains '{phrase}'")

    print("PASS: merged docs verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
