#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "docs" / "tier0" / "sample-queries.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(SAMPLE.is_file(), "sample queries file exists")
    payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
    queries = payload["queries"]
    expect("resolve_alias_spirit" in queries, "resolve_alias_spirit example exists")
    expect("find_api_gated_knowledge" in queries, "find_api_gated_knowledge example exists")
    expect("grounded_lookup_first_entity" in queries, "grounded_lookup_first_entity example exists")
    expect(len(queries["resolve_alias_spirit"]["matches"]) >= 1, "Spirit alias resolves to at least one entity")
    expect(len(queries["find_api_gated_knowledge"]["matches"]) >= 1, "api gated query returns at least one match")
    grounded = queries["grounded_lookup_first_entity"]
    expect(bool(grounded["input"]["canonical_id"]), "grounded lookup has a canonical entity id")
    expect(len(grounded["claims"]) >= 1, "grounded lookup returns claims")
    expect(len(grounded["provenance"]) >= 1, "grounded lookup returns provenance")
    expect(len(grounded["chunks"]) >= 1, "grounded lookup returns chunks")
    print("PASS: sample query verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
