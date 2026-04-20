#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "docs/tier0/merged/sample-queries.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(SAMPLE.is_file(), "merged sample queries file exists")
    payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
    queries = payload["queries"]
    expect("resolve_spirit_in_merged_graph" in queries, "merged spirit lookup query exists")
    expect("find_api_gated_claims_in_merged_graph" in queries, "merged api-gated query exists")
    expect("grounded_lookup_in_merged_graph" in queries, "merged grounded lookup query exists")
    expect(len(queries["resolve_spirit_in_merged_graph"]["matches"]) >= 1, "merged spirit lookup returns matches")
    expect(len(queries["find_api_gated_claims_in_merged_graph"]["matches"]) >= 1, "merged api-gated lookup returns matches")
    grounded = queries["grounded_lookup_in_merged_graph"]
    expect(bool(grounded["input"]["subject_id"]), "merged grounded lookup has a subject id")
    expect(len(grounded["claims"]) >= 1, "merged grounded lookup returns claims")
    expect(len(grounded["chunks"]) >= 1, "merged grounded lookup returns chunks")
    print("PASS: merged sample query verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
