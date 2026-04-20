#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Build downstream graph export bundle metadata")
    parser.add_argument("--derived-root", default="docs/tier0/derived")
    args = parser.parse_args()

    derived_root = ROOT / args.derived_root

    paths = {
        "nodes": derived_root / "nodes.jsonl",
        "edges": derived_root / "edges.jsonl",
        "claims": derived_root / "claims.jsonl",
        "chunks": derived_root / "chunks.jsonl",
        "canonical_entities": derived_root / "canonical-entities.jsonl",
        "support_edges": derived_root / "support-edges.jsonl",
        "claim_index": derived_root / "claim-index.jsonl",
        "canonical_claims": derived_root / "canonical-claims.jsonl",
        "aliases": derived_root / "aliases.jsonl",
        "provenance": derived_root / "provenance.jsonl",
    }

    counts = {name: count_jsonl(path) for name, path in paths.items()}

    schema = {
        "bundle_version": 1,
        "entity_tables": [
            "nodes",
            "canonical_entities",
            "aliases",
        ],
        "relation_tables": [
            "edges",
            "support_edges",
            "claims",
            "canonical_claims",
            "provenance",
        ],
        "retrieval_tables": [
            "chunks",
            "claim_index",
        ],
        "recommended_load_order": [
            "nodes",
            "canonical_entities",
            "aliases",
            "edges",
            "support_edges",
            "claims",
            "canonical_claims",
            "provenance",
            "chunks",
            "claim_index",
        ],
        "recommended_query_entrypoints": {
            "entity_lookup": ["canonical_entities", "aliases"],
            "source_grounding": ["provenance", "claims"],
            "retrieval": ["chunks", "claim_index"],
            "support_scoring": ["support_edges", "canonical_claims"],
        },
    }

    query_examples = [
        {
            "name": "lookup_entity_by_alias",
            "inputs": {"alias": "Spirit"},
            "pipeline": [
                "search aliases.alias == input alias",
                "resolve canonical_id",
                "join canonical_entities on canonical_id",
                "join canonical_claims on subject_id == canonical_id",
            ],
        },
        {
            "name": "inspect_api_gating_claims",
            "inputs": {"predicate_family": "availability"},
            "pipeline": [
                "filter canonical_claims.predicate_family == availability",
                "join provenance on claim ids if source evidence is needed",
            ],
        },
        {
            "name": "retrieve_source_grounded_chunks_for_entity",
            "inputs": {"canonical_id": "<entity-id>"},
            "pipeline": [
                "join claims/provenance for supporting evidence",
                "use chunks/doc_id linkage to gather retrieval text",
            ],
        },
    ]

    bundle = {
        "bundle_name": "diablo2-tier0-graph-export",
        "derived_root": str(derived_root.relative_to(ROOT)),
        "counts": counts,
        "files": {name: str(path.relative_to(ROOT)) for name, path in paths.items()},
        "schema": schema,
        "query_examples": query_examples,
    }

    manifest_path = derived_root / "graph-export-bundle.json"
    report_path = derived_root / "graph-export-bundle-report.md"
    manifest_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "# Tier 0 Graph Export Bundle Report\n\n"
        f"- Bundle: `diablo2-tier0-graph-export`\n"
        f"- Derived root: `{bundle['derived_root']}`\n"
        f"- Counts: `{counts}`\n"
        f"- Recommended load order: `{schema['recommended_load_order']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
