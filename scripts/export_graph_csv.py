#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def join_list(value: object) -> str:
    if isinstance(value, list):
        return "|".join(str(item) for item in value)
    return str(value or "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export graph bundle artifacts to Neo4j-friendly CSV")
    parser.add_argument("--derived-root", default="docs/tier0/derived")
    parser.add_argument("--output-root", default="docs/tier0/export")
    args = parser.parse_args()

    derived = ROOT / args.derived_root
    output = ROOT / args.output_root

    canonical_entities = load_jsonl(derived / "canonical-entities.jsonl")
    aliases = load_jsonl(derived / "aliases.jsonl")
    canonical_claims = load_jsonl(derived / "canonical-claims.jsonl")
    support_edges = load_jsonl(derived / "support-edges.jsonl")
    provenance = load_jsonl(derived / "provenance.jsonl")
    chunks = load_jsonl(derived / "chunks.jsonl")

    entity_rows = [
        {
            "canonical_id": row["canonical_id"],
            "node_type": row["node_type"],
            "key": row.get("key", ""),
            "name": row.get("name", ""),
            "aliases": join_list(row.get("aliases", [])),
            "document_count": row.get("document_count", 0),
            "supporting_source_count": row.get("supporting_source_count", 0),
            "supporting_sources": join_list(row.get("supporting_sources", [])),
            "claim_count": row.get("claim_count", 0),
        }
        for row in canonical_entities
    ]
    write_csv(
        output / "canonical_entities.csv",
        entity_rows,
        [
            "canonical_id",
            "node_type",
            "key",
            "name",
            "aliases",
            "document_count",
            "supporting_source_count",
            "supporting_sources",
            "claim_count",
        ],
    )

    alias_rows = [
        {
            "alias_id": row["alias_id"],
            "canonical_id": row["canonical_id"],
            "alias": row["alias"],
            "alias_type": row["alias_type"],
            "node_type": row["node_type"],
        }
        for row in aliases
    ]
    write_csv(output / "aliases.csv", alias_rows, ["alias_id", "canonical_id", "alias", "alias_type", "node_type"])

    claim_rows = [
        {
            "canonical_claim_id": row["canonical_claim_id"],
            "subject_id": row["subject_id"],
            "subject_type": row["subject_type"],
            "subject_name": row.get("subject_name", ""),
            "subject_aliases": join_list(row.get("subject_aliases", [])),
            "predicate": row["predicate"],
            "predicate_family": row["predicate_family"],
            "object": row["object"],
            "supporting_source_count": row["supporting_source_count"],
            "supporting_sources": join_list(row["supporting_sources"]),
            "claim_variant_count": row["claim_variant_count"],
        }
        for row in canonical_claims
    ]
    write_csv(
        output / "canonical_claims.csv",
        claim_rows,
        [
            "canonical_claim_id",
            "subject_id",
            "subject_type",
            "subject_name",
            "subject_aliases",
            "predicate",
            "predicate_family",
            "object",
            "supporting_source_count",
            "supporting_sources",
            "claim_variant_count",
        ],
    )

    support_rows = [
        {
            "edge_id": row["edge_id"],
            "from_id": row["from_id"],
            "to_id": row["to_id"],
            "edge_type": row["edge_type"],
            "support_count": row["support_count"],
        }
        for row in support_edges
    ]
    write_csv(output / "support_edges.csv", support_rows, ["edge_id", "from_id", "to_id", "edge_type", "support_count"])

    provenance_rows = [
        {
            "provenance_id": row["provenance_id"],
            "claim_id": row["claim_id"],
            "subject_id": row["subject_id"],
            "predicate": row["predicate"],
            "source_id": row["source_id"],
            "evidence_doc_id": row["evidence_doc_id"],
            "evidence_url": row.get("evidence_url", ""),
            "authority_tier": row.get("authority_tier", ""),
            "lane": row.get("lane", ""),
        }
        for row in provenance
    ]
    write_csv(
        output / "provenance.csv",
        provenance_rows,
        [
            "provenance_id",
            "claim_id",
            "subject_id",
            "predicate",
            "source_id",
            "evidence_doc_id",
            "evidence_url",
            "authority_tier",
            "lane",
        ],
    )

    chunk_rows = [
        {
            "chunk_id": row["chunk_id"],
            "doc_id": row["doc_id"],
            "source_id": row["source_id"],
            "source_name": row["source_name"],
            "source_url": row["source_url"],
            "label": row["label"],
            "title": row["title"],
            "lane": row["lane"],
            "authority_tier": row["authority_tier"],
            "chunk_index": row["chunk_index"],
            "char_count": row["char_count"],
            "text": row["text"],
        }
        for row in chunks
    ]
    write_csv(
        output / "chunks.csv",
        chunk_rows,
        [
            "chunk_id",
            "doc_id",
            "source_id",
            "source_name",
            "source_url",
            "label",
            "title",
            "lane",
            "authority_tier",
            "chunk_index",
            "char_count",
            "text",
        ],
    )

    manifest = {
        "csv_tables": {
            "canonical_entities": len(entity_rows),
            "aliases": len(alias_rows),
            "canonical_claims": len(claim_rows),
            "support_edges": len(support_rows),
            "provenance": len(provenance_rows),
            "chunks": len(chunk_rows),
        },
        "files": {
            "canonical_entities": str((output / "canonical_entities.csv").relative_to(ROOT)),
            "aliases": str((output / "aliases.csv").relative_to(ROOT)),
            "canonical_claims": str((output / "canonical_claims.csv").relative_to(ROOT)),
            "support_edges": str((output / "support_edges.csv").relative_to(ROOT)),
            "provenance": str((output / "provenance.csv").relative_to(ROOT)),
            "chunks": str((output / "chunks.csv").relative_to(ROOT)),
        },
    }
    (output / "csv-export-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
