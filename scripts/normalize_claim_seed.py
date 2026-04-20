#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}::{value}"))


def relation_family(predicate: str) -> str:
    mapping = {
        "discovered_via": "provenance",
        "lane": "classification",
        "authority_tier": "classification",
        "api_requires_key": "availability",
    }
    return mapping.get(predicate, "other")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize graph claims into query-facing claim groups")
    parser.add_argument("--claim-index", default="docs/tier0/derived/claim-index.jsonl")
    parser.add_argument("--canonical-entities", default="docs/tier0/derived/canonical-entities.jsonl")
    parser.add_argument("--edges", default="docs/tier0/derived/edges.jsonl")
    parser.add_argument("--aliases", default="docs/tier0/derived/aliases.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/derived")
    args = parser.parse_args()

    output_root = ROOT / args.output_root
    claim_index = load_jsonl(ROOT / args.claim_index)
    canonical_entities = {row["canonical_id"]: row for row in load_jsonl(ROOT / args.canonical_entities)}
    edges = load_jsonl(ROOT / args.edges)
    aliases = load_jsonl(ROOT / args.aliases)

    alias_map: dict[str, list[str]] = defaultdict(list)
    for alias in aliases:
        alias_map[alias["canonical_id"]].append(alias["alias"])

    doc_to_entity: dict[str, str] = {}
    for edge in edges:
        if edge["edge_type"] == "DESCRIBES":
            doc_to_entity.setdefault(edge["from_id"], edge["to_id"])

    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in claim_index:
        subject_id = row["subject_id"]
        if subject_id not in canonical_entities and subject_id in doc_to_entity:
            subject_id = doc_to_entity[subject_id]
        if subject_id not in canonical_entities:
            continue
        projected = {**row, "subject_id": subject_id}
        grouped[(subject_id, row["predicate"], row["object"])].append(projected)

    canonical_claims: list[dict] = []
    for (subject_id, predicate, obj), rows in grouped.items():
        entity = canonical_entities.get(subject_id, {})
        supporting_sources = sorted({row["source_id"] for row in rows})
        canonical_claims.append(
            {
                "canonical_claim_id": make_id("canonical-claim", f"{subject_id}|{predicate}|{obj}"),
                "subject_id": subject_id,
                "subject_type": rows[0]["subject_type"],
                "subject_name": entity.get("name") or entity.get("key"),
                "subject_aliases": sorted(set(alias_map.get(subject_id, [])))[:20],
                "predicate": predicate,
                "predicate_family": relation_family(predicate),
                "object": obj,
                "supporting_sources": supporting_sources,
                "supporting_source_count": len(supporting_sources),
                "claim_variant_count": len(rows),
            }
        )

    canonical_claims.sort(key=lambda row: (row["subject_type"], row["subject_name"] or "", row["predicate"], row["object"]))

    taxonomy = {
        "predicate_families": {
            "provenance": ["discovered_via"],
            "classification": ["lane", "authority_tier"],
            "availability": ["api_requires_key"],
        },
        "recommended_query_filters": [
            "subject_type",
            "predicate_family",
            "supporting_source_count",
            "supporting_sources",
        ],
    }

    canonical_claims_path = output_root / "canonical-claims.jsonl"
    taxonomy_path = output_root / "relation-taxonomy.json"
    manifest_path = output_root / "claim-normalization-manifest.json"
    report_path = output_root / "claim-normalization-report.md"

    canonical_claims_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in canonical_claims) + "\n",
        encoding="utf-8",
    )
    taxonomy_path.write_text(json.dumps(taxonomy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "canonical_claim_count": len(canonical_claims),
        "predicate_family_counts": dict(Counter(row["predicate_family"] for row in canonical_claims)),
        "paths": {
            "canonical_claims": str(canonical_claims_path.relative_to(ROOT)),
            "relation_taxonomy": str(taxonomy_path.relative_to(ROOT)),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "# Tier 0 Claim Normalization Report\n\n"
        f"- Canonical claims: `{len(canonical_claims)}`\n"
        f"- Predicate family counts: `{manifest['predicate_family_counts']}`\n"
        f"- Canonical claims file: `{manifest['paths']['canonical_claims']}`\n"
        f"- Relation taxonomy file: `{manifest['paths']['relation_taxonomy']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
