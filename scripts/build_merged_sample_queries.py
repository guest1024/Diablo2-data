#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"
BASE_DERIVED = ROOT / "docs/tier0/derived"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    nodes = load_jsonl(MERGED / "nodes.jsonl")
    claims = load_jsonl(MERGED / "claims.jsonl")
    chunks = load_jsonl(MERGED / "chunks.jsonl")
    aliases = load_jsonl(BASE_DERIVED / "aliases.jsonl")
    provenance = load_jsonl(BASE_DERIVED / "provenance.jsonl")

    nodes_by_id = {node["node_id"]: node for node in nodes}

    spirit_aliases = [alias for alias in aliases if "spirit" in alias["alias"].lower()]
    spirit_alias_ids = {alias["canonical_id"] for alias in spirit_aliases}

    merged_spirit_nodes = [
        node for node in nodes
        if node["node_id"] in spirit_alias_ids
        or "spirit" in str(node.get("name", "")).lower()
        or "spirit" in str(node.get("key", "")).lower()
    ]
    merged_spirit_nodes.sort(key=lambda row: (row.get("node_type") != "Runeword", row.get("name", "")))

    api_key_claims = [claim for claim in claims if claim["predicate"] == "api_requires_key"]

    first_subject_id = None
    subject_claims = []
    subject_chunks = []
    subject_provenance = []
    for candidate in merged_spirit_nodes + list(nodes):
        candidate_id = candidate["node_id"]
        related_claims = [claim for claim in claims if claim["subject_id"] == candidate_id][:10]
        if not related_claims:
            continue
        subject_claims = related_claims
        first_subject_id = candidate_id
        subject_provenance = [row for row in provenance if row["subject_id"] == candidate_id][:10]
        subject_chunks = [chunk for chunk in chunks if chunk["doc_id"] == candidate_id or chunk["chunk_id"].startswith(candidate_id)][:10]
        if not subject_chunks and subject_provenance:
            evidence_doc_ids = {row["evidence_doc_id"] for row in subject_provenance}
            subject_chunks = [chunk for chunk in chunks if chunk["doc_id"] in evidence_doc_ids][:10]
        if subject_chunks:
            break

    payload = {
        "queries": {
            "resolve_spirit_in_merged_graph": {
                "input": {"alias": "Spirit"},
                "matches": [
                    {
                        "node_id": node["node_id"],
                        "node_type": node.get("node_type"),
                        "name": node.get("name"),
                        "key": node.get("key"),
                    }
                    for node in merged_spirit_nodes[:20]
                ],
            },
            "find_api_gated_claims_in_merged_graph": {
                "input": {"predicate": "api_requires_key"},
                "matches": api_key_claims[:20],
            },
            "grounded_lookup_in_merged_graph": {
                "input": {"subject_id": first_subject_id},
                "subject": nodes_by_id.get(first_subject_id),
                "claims": subject_claims,
                "provenance": subject_provenance,
                "chunks": [
                    {
                        "chunk_id": chunk["chunk_id"],
                        "title": chunk.get("title", ""),
                        "text_preview": chunk.get("text", "")[:240],
                    }
                    for chunk in subject_chunks
                ],
            },
        }
    }

    (MERGED / "sample-queries.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
