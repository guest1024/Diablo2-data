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
    canonical_claims_path = DERIVED / "canonical-claims.jsonl"
    taxonomy_path = DERIVED / "relation-taxonomy.json"
    manifest_path = DERIVED / "claim-normalization-manifest.json"
    report_path = DERIVED / "claim-normalization-report.md"
    canonical_entities_path = DERIVED / "canonical-entities.jsonl"

    expect(canonical_claims_path.is_file(), "canonical claims jsonl exists")
    expect(taxonomy_path.is_file(), "relation taxonomy exists")
    expect(manifest_path.is_file(), "claim normalization manifest exists")
    expect(report_path.is_file(), "claim normalization report exists")

    canonical_claims = load_jsonl(canonical_claims_path)
    canonical_entities = {row["canonical_id"] for row in load_jsonl(canonical_entities_path)}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))

    expect(len(canonical_claims) >= 16, "canonical claims count is at least 16")
    expect(manifest["canonical_claim_count"] == len(canonical_claims), "manifest canonical claim count matches")
    expect(all(row["subject_id"] in canonical_entities for row in canonical_claims), "all canonical claims point to canonical entities")
    expect(any(row["predicate_family"] == "availability" for row in canonical_claims), "availability-family claims exist")
    expect(any(row["predicate"] == "api_requires_key" for row in canonical_claims), "api_requires_key canonical claim exists")
    expect(all(row["supporting_source_count"] >= 1 for row in canonical_claims), "all canonical claims have supporting sources")
    expect("predicate_families" in taxonomy and "recommended_query_filters" in taxonomy, "taxonomy has expected top-level keys")

    print("PASS: claim normalization verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
