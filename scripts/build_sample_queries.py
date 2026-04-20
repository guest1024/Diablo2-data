#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "docs" / "tier0" / "derived"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    aliases = load_jsonl(DERIVED / "aliases.jsonl")
    canonical_entities = {row["canonical_id"]: row for row in load_jsonl(DERIVED / "canonical-entities.jsonl")}
    canonical_claims = load_jsonl(DERIVED / "canonical-claims.jsonl")
    provenance = load_jsonl(DERIVED / "provenance.jsonl")
    chunks = load_jsonl(DERIVED / "chunks.jsonl")

    alias_map: dict[str, list[dict]] = {}
    for alias in aliases:
        alias_map.setdefault(alias["alias"].lower(), []).append(alias)

    spirit_aliases = [
        alias
        for alias in aliases
        if "spirit" in alias["alias"].lower()
    ]
    spirit_aliases.sort(key=lambda item: (item["node_type"] != "Runeword", item["alias"]))
    spirit_entities = []
    seen = set()
    for alias in spirit_aliases:
        canonical_id = alias["canonical_id"]
        if canonical_id in seen or canonical_id not in canonical_entities:
            continue
        seen.add(canonical_id)
        spirit_entities.append(canonical_entities[canonical_id])

    api_key_claims = [claim for claim in canonical_claims if claim["predicate"] == "api_requires_key"]

    def entity_claim_bundle(entity_id: str | None):
        if not entity_id:
            return [], [], []
        claims = [claim for claim in canonical_claims if claim["subject_id"] == entity_id][:10]
        prov = [item for item in provenance if item["subject_id"] == entity_id][:10]
        evidence_doc_ids = {item["evidence_doc_id"] for item in prov}
        chunk_rows = [chunk for chunk in chunks if chunk["doc_id"] in evidence_doc_ids][:10]
        return claims, prov, chunk_rows

    first_entity_id = None
    first_entity_claims = []
    first_entity_provenance = []
    first_entity_chunks = []
    candidate_ids = [row["canonical_id"] for row in spirit_entities]
    candidate_ids.extend(
        row["canonical_id"]
        for row in canonical_entities.values()
        if row["canonical_id"] not in set(candidate_ids)
    )
    for candidate_id in candidate_ids:
        claims_rows, prov_rows, chunk_rows = entity_claim_bundle(candidate_id)
        if claims_rows and prov_rows and chunk_rows:
            first_entity_id = candidate_id
            first_entity_claims = claims_rows
            first_entity_provenance = prov_rows
            first_entity_chunks = chunk_rows
            break

    payload = {
        "queries": {
            "resolve_alias_spirit": {
                "input": {"alias": "Spirit"},
                "matches": [
                    {
                        "canonical_id": row["canonical_id"],
                        "name": row.get("name"),
                        "node_type": row.get("node_type"),
                        "aliases": row.get("aliases", [])[:10],
                    }
                    for row in spirit_entities
                ],
            },
            "find_api_gated_knowledge": {
                "input": {"predicate": "api_requires_key"},
                "matches": [
                    {
                        "canonical_claim_id": claim["canonical_claim_id"],
                        "subject_id": claim["subject_id"],
                        "subject_name": claim.get("subject_name"),
                        "predicate": claim["predicate"],
                        "object": claim["object"],
                        "supporting_sources": claim["supporting_sources"],
                    }
                    for claim in api_key_claims
                ],
            },
            "grounded_lookup_first_entity": {
                "input": {"canonical_id": first_entity_id},
                "claims": first_entity_claims,
                "provenance": first_entity_provenance,
                "chunks": [
                    {
                        "chunk_id": chunk["chunk_id"],
                        "title": chunk["title"],
                        "text_preview": chunk["text"][:240],
                    }
                    for chunk in first_entity_chunks
                ],
            },
        }
    }

    (ROOT / "docs" / "tier0" / "sample-queries.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
