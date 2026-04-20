#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "docs" / "tier0" / "derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    aliases_path = DERIVED / "aliases.jsonl"
    provenance_path = DERIVED / "provenance.jsonl"
    manifest_path = DERIVED / "alias-seed-manifest.json"
    report_path = DERIVED / "alias-seed-report.md"
    nodes_path = DERIVED / "nodes.jsonl"
    claims_path = DERIVED / "claims.jsonl"

    expect(aliases_path.is_file(), "aliases jsonl exists")
    expect(provenance_path.is_file(), "provenance jsonl exists")
    expect(manifest_path.is_file(), "alias seed manifest exists")
    expect(report_path.is_file(), "alias seed report exists")

    aliases = load_jsonl(aliases_path)
    provenance = load_jsonl(provenance_path)
    nodes = load_jsonl(nodes_path)
    claims = load_jsonl(claims_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expect(len(aliases) > 50, "alias seed contains more than 50 aliases")
    expect(len(provenance) == len(claims), "provenance count matches claim count")
    expect(manifest["alias_count"] == len(aliases), "manifest alias count matches")
    expect(manifest["provenance_count"] == len(provenance), "manifest provenance count matches")

    canonical_ids = {node["node_id"] for node in nodes}
    expect(all(alias["canonical_id"] in canonical_ids for alias in aliases), "all aliases point to existing canonical nodes")
    expect(any(alias["alias_type"] == "slug" for alias in aliases), "slug aliases exist")
    expect(any(alias["node_type"] == "Runeword" for alias in aliases), "runeword aliases exist")

    claim_ids = {claim["claim_id"] for claim in claims}
    expect(all(item["claim_id"] in claim_ids for item in provenance), "all provenance rows point to existing claims")
    expect(all(item["evidence_url"] for item in provenance), "all provenance rows include evidence URLs")

    print("PASS: alias seed verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
