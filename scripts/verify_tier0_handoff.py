#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/tier0/HANDOFF.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(HANDOFF.is_file(), "tier0 handoff exists")
    text = HANDOFF.read_text(encoding="utf-8")
    for phrase in [
        "run_tier0_pipeline.py",
        "verify_tier0_stack.py",
        "graph-export-bundle.json",
        "neo4j-import-playbook.md",
        "artifact-checksums.json",
        "Recommended next Tier 1 work",
    ]:
        expect(phrase in text, f"handoff contains '{phrase}'")
    print("PASS: tier0 handoff verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
