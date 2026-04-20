#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}::{value}"))


def normalize_alias(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = value.strip("-_/")
    return value


def slug_alias(value: str) -> str:
    value = value.replace(".shtml", "").replace(".html", "")
    value = value.replace("-", " ").replace("_", " ").replace("/", " ")
    return normalize_alias(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract alias/provenance seed artifacts from graph outputs")
    parser.add_argument("--nodes", default="docs/tier0/derived/nodes.jsonl")
    parser.add_argument("--docs", dest="documents", default="docs/tier0/normalized/documents.jsonl")
    parser.add_argument("--claims", default="docs/tier0/derived/claims.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/derived")
    args = parser.parse_args()

    nodes = load_jsonl(ROOT / args.nodes)
    documents = load_jsonl(ROOT / args.documents)
    claims = load_jsonl(ROOT / args.claims)
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    aliases: list[dict] = []
    provenance: list[dict] = []
    seen_aliases: set[tuple[str, str]] = set()

    docs_by_id = {doc["doc_id"]: doc for doc in documents}

    for node in nodes:
        node_id = node["node_id"]
        key = normalize_alias(str(node.get("key", "")))
        name = normalize_alias(str(node.get("name", "")))

        candidates = []
        if name:
            candidates.append(("title", name))
        if key and key.lower() != name.lower():
            candidates.append(("key", key))
        if key:
            slugged = slug_alias(key)
            if slugged and slugged.lower() not in {name.lower(), key.lower()}:
                candidates.append(("slug", slugged))

        for alias_type, alias_value in candidates:
            normalized = normalize_alias(alias_value)
            if not normalized:
                continue
            dedupe_key = (node_id, normalized.lower())
            if dedupe_key in seen_aliases:
                continue
            seen_aliases.add(dedupe_key)
            aliases.append(
                {
                    "alias_id": make_id("alias", f"{node_id}|{normalized.lower()}"),
                    "canonical_id": node_id,
                    "alias": normalized,
                    "alias_type": alias_type,
                    "node_type": node.get("node_type"),
                }
            )

    for claim in claims:
        evidence_doc = docs_by_id.get(claim["evidence_doc_id"])
        provenance.append(
            {
                "provenance_id": make_id("provenance", claim["claim_id"]),
                "claim_id": claim["claim_id"],
                "subject_id": claim["subject_id"],
                "predicate": claim["predicate"],
                "source_id": claim["source_id"],
                "evidence_doc_id": claim["evidence_doc_id"],
                "evidence_url": evidence_doc["source_url"] if evidence_doc else None,
                "authority_tier": evidence_doc["authority_tier"] if evidence_doc else None,
                "lane": evidence_doc["lane"] if evidence_doc else None,
            }
        )

    aliases_path = output_root / "aliases.jsonl"
    provenance_path = output_root / "provenance.jsonl"
    aliases_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in aliases) + "\n", encoding="utf-8")
    provenance_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in provenance) + "\n", encoding="utf-8")

    manifest = {
        "alias_count": len(aliases),
        "provenance_count": len(provenance),
        "paths": {
            "aliases": str(aliases_path.relative_to(ROOT)),
            "provenance": str(provenance_path.relative_to(ROOT)),
        },
    }
    (output_root / "alias-seed-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "alias-seed-report.md").write_text(
        "# Tier 0 Alias Seed Report\n\n"
        f"- Aliases: `{len(aliases)}`\n"
        f"- Provenance rows: `{len(provenance)}`\n"
        f"- Aliases file: `{manifest['paths']['aliases']}`\n"
        f"- Provenance file: `{manifest['paths']['provenance']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
