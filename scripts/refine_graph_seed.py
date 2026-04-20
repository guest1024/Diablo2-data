#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}::{value}"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Refine graph seed into canonical entity/support artifacts")
    parser.add_argument("--nodes", default="docs/tier0/derived/nodes.jsonl")
    parser.add_argument("--edges", default="docs/tier0/derived/edges.jsonl")
    parser.add_argument("--claims", default="docs/tier0/derived/claims.jsonl")
    parser.add_argument("--aliases", default="docs/tier0/derived/aliases.jsonl")
    parser.add_argument("--provenance", default="docs/tier0/derived/provenance.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/derived")
    args = parser.parse_args()

    output_root = ROOT / args.output_root
    nodes = load_jsonl(ROOT / args.nodes)
    edges = load_jsonl(ROOT / args.edges)
    claims = load_jsonl(ROOT / args.claims)
    aliases = load_jsonl(ROOT / args.aliases)
    provenance = load_jsonl(ROOT / args.provenance)

    node_by_id = {node["node_id"]: node for node in nodes}
    aliases_by_id: dict[str, list[str]] = defaultdict(list)
    for alias in aliases:
        aliases_by_id[alias["canonical_id"]].append(alias["alias"])

    provenance_by_claim: dict[str, list[dict]] = defaultdict(list)
    for item in provenance:
        provenance_by_claim[item["claim_id"]].append(item)

    source_support_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    entity_claims: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        entity_claims[claim["subject_id"]].append(claim)
        for prov in provenance_by_claim.get(claim["claim_id"], []):
            source_support_counts[claim["subject_id"]][prov["source_id"]] += 1

    describes_edges: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge["edge_type"] == "DESCRIBES":
            describes_edges[edge["to_id"]].append(edge["from_id"])

    canonical_entities: list[dict] = []
    support_edges: list[dict] = []
    claim_index: list[dict] = []

    for node in nodes:
        node_type = node["node_type"]
        if node_type in {"Source", "SourceDocument"}:
            continue

        node_id = node["node_id"]
        supporting_sources = source_support_counts.get(node_id, {})
        alias_values = sorted({alias for alias in aliases_by_id.get(node_id, []) if alias})
        canonical_entities.append(
            {
                "canonical_id": node_id,
                "node_type": node_type,
                "key": node.get("key"),
                "name": node.get("name"),
                "aliases": alias_values,
                "document_count": len(describes_edges.get(node_id, [])),
                "supporting_source_count": len(supporting_sources),
                "supporting_sources": sorted(supporting_sources),
                "claim_count": len(entity_claims.get(node_id, [])),
            }
        )

        for source_id, support_count in sorted(supporting_sources.items()):
            source_node_id = next(
                (candidate["node_id"] for candidate in nodes if candidate["node_type"] == "Source" and candidate.get("key") == source_id),
                None,
            )
            if not source_node_id:
                continue
            support_edges.append(
                {
                    "edge_id": make_id("support-edge", f"{source_node_id}|SUPPORTS_ENTITY|{node_id}"),
                    "from_id": source_node_id,
                    "to_id": node_id,
                    "edge_type": "SUPPORTS_ENTITY",
                    "support_count": support_count,
                }
            )

    for claim in claims:
        subject = node_by_id.get(claim["subject_id"], {})
        claim_index.append(
            {
                "claim_id": claim["claim_id"],
                "subject_id": claim["subject_id"],
                "subject_type": subject.get("node_type", "Unknown"),
                "predicate": claim["predicate"],
                "object": claim["object"],
                "source_id": claim["source_id"],
                "provenance_count": len(provenance_by_claim.get(claim["claim_id"], [])),
            }
        )

    canonical_entities.sort(key=lambda item: (item["node_type"], item["name"] or item["key"] or ""))
    claim_index.sort(key=lambda item: (item["subject_type"], item["predicate"], item["object"]))

    canonical_path = output_root / "canonical-entities.jsonl"
    support_edges_path = output_root / "support-edges.jsonl"
    claim_index_path = output_root / "claim-index.jsonl"

    canonical_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in canonical_entities) + "\n", encoding="utf-8")
    support_edges_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in support_edges) + "\n", encoding="utf-8")
    claim_index_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in claim_index) + "\n", encoding="utf-8")

    manifest = {
        "canonical_entity_count": len(canonical_entities),
        "support_edge_count": len(support_edges),
        "claim_index_count": len(claim_index),
        "paths": {
            "canonical_entities": str(canonical_path.relative_to(ROOT)),
            "support_edges": str(support_edges_path.relative_to(ROOT)),
            "claim_index": str(claim_index_path.relative_to(ROOT)),
        },
    }
    (output_root / "refined-graph-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "refined-graph-report.md").write_text(
        "# Tier 0 Refined Graph Report\n\n"
        f"- Canonical entities: `{len(canonical_entities)}`\n"
        f"- Support edges: `{len(support_edges)}`\n"
        f"- Claim index rows: `{len(claim_index)}`\n"
        f"- Canonical entities file: `{manifest['paths']['canonical_entities']}`\n"
        f"- Support edges file: `{manifest['paths']['support_edges']}`\n"
        f"- Claim index file: `{manifest['paths']['claim_index']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
