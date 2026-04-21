#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERM_MAP_PATH = ROOT / "docs/tier0/bilingual-term-map.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(TERM_MAP_PATH.is_file(), "bilingual term map exists")
    data = json.loads(TERM_MAP_PATH.read_text(encoding="utf-8"))
    expect(isinstance(data, dict) and data, "bilingual term map is a non-empty object")

    for term, payload in data.items():
        expect(isinstance(term, str) and term.strip(), f"term key is valid: {term}")
        expect(isinstance(payload, dict), f"payload is object: {term}")
        expect(isinstance(payload.get("canonical_hint", ""), str) and payload.get("canonical_hint", "").strip(), f"canonical_hint exists: {term}")
        aliases = payload.get("aliases", [])
        expect(isinstance(aliases, list) and aliases, f"aliases exist: {term}")
        expect(all(isinstance(alias, str) and alias.strip() for alias in aliases), f"aliases are non-empty strings: {term}")

    print(f"PASS: validated {len(data)} bilingual term mappings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
