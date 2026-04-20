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


def infer_variant(doc: dict) -> str:
    url = doc["source_url"].lower()
    text = (doc.get("title", "") + "\n" + doc.get("text", "")[:4000]).lower()
    if "d2r" in text or "resurrected" in text or "reign of the warlock" in text:
        return "d2r"
    if "lod" in text or "lord of destruction" in text or "1.10" in text or "1.13" in text:
        return "lod"
    if "classic.battle.net/diablo2exp" in url:
        return "lod"
    return "unknown"


def infer_version_tokens(doc: dict) -> list[str]:
    text = (doc.get("title", "") + "\n" + doc.get("text", "")[:6000])
    found = sorted(set(re.findall(r"\b(?:1\.\d{2}|2\.\d+|2\.\d{1,2})\b", text)))
    if not found and infer_variant(doc) == "d2r":
        found = ["d2r-unspecified"]
    elif not found and infer_variant(doc) == "lod":
        found = ["lod-unspecified"]
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract version semantics and contradiction seeds from normalized docs/claims")
    parser.add_argument("--documents", default="docs/tier0/normalized/documents.jsonl")
    parser.add_argument("--canonical-claims", default="docs/tier0/derived/canonical-claims.jsonl")
    parser.add_argument("--provenance", default="docs/tier0/derived/provenance.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/derived")
    args = parser.parse_args()

    documents = load_jsonl(ROOT / args.documents)
    canonical_claims = load_jsonl(ROOT / args.canonical_claims)
    provenance = load_jsonl(ROOT / args.provenance)
    output_root = ROOT / args.output_root

    docs_by_id = {doc["doc_id"]: doc for doc in documents}
    version_tags: list[dict] = []
    contradiction_seeds: list[dict] = []

    for doc in documents:
        variant = infer_variant(doc)
        versions = infer_version_tokens(doc)
        version_tags.append(
            {
                "version_tag_id": make_id("version-tag", doc["doc_id"]),
                "doc_id": doc["doc_id"],
                "source_id": doc["source_id"],
                "source_url": doc["source_url"],
                "variant": variant,
                "version_tokens": versions,
            }
        )

    prov_by_doc: dict[str, list[dict]] = {}
    for item in provenance:
        prov_by_doc.setdefault(item["evidence_doc_id"], []).append(item)

    for claim in canonical_claims:
        supporting = claim.get("supporting_sources", [])
        if len(supporting) <= 1:
            continue
        doc_versions = []
        for prov in provenance:
            if prov["claim_id"] == claim["canonical_claim_id"]:
                doc = docs_by_id.get(prov["evidence_doc_id"])
                if doc:
                    doc_versions.append(infer_variant(doc))
        contradiction_seeds.append(
            {
                "contradiction_seed_id": make_id("contradiction-seed", claim["canonical_claim_id"]),
                "canonical_claim_id": claim["canonical_claim_id"],
                "subject_id": claim["subject_id"],
                "predicate": claim["predicate"],
                "object": claim["object"],
                "supporting_sources": supporting,
                "observed_variants": sorted(set(doc_versions)) or ["unknown"],
                "needs_review": len(sorted(set(doc_versions))) > 1,
            }
        )

    if not contradiction_seeds:
        # still emit a minimal review seed for future pipeline continuity
        for claim in canonical_claims[:10]:
            contradiction_seeds.append(
                {
                    "contradiction_seed_id": make_id("contradiction-seed", claim["canonical_claim_id"]),
                    "canonical_claim_id": claim["canonical_claim_id"],
                    "subject_id": claim["subject_id"],
                    "predicate": claim["predicate"],
                    "object": claim["object"],
                    "supporting_sources": claim.get("supporting_sources", []),
                    "observed_variants": ["unknown"],
                    "needs_review": False,
                }
            )

    version_path = output_root / "version-tags.jsonl"
    contradiction_path = output_root / "contradiction-seeds.jsonl"
    version_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in version_tags) + "\n", encoding="utf-8")
    contradiction_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in contradiction_seeds) + "\n", encoding="utf-8")

    manifest = {
        "version_tag_count": len(version_tags),
        "contradiction_seed_count": len(contradiction_seeds),
        "paths": {
            "version_tags": str(version_path.relative_to(ROOT)),
            "contradiction_seeds": str(contradiction_path.relative_to(ROOT)),
        },
    }
    (output_root / "version-semantics-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "version-semantics-report.md").write_text(
        "# Tier 0 Version Semantics Report\n\n"
        f"- Version tags: `{len(version_tags)}`\n"
        f"- Contradiction seeds: `{len(contradiction_seeds)}`\n"
        f"- Version tags file: `{manifest['paths']['version_tags']}`\n"
        f"- Contradiction seeds file: `{manifest['paths']['contradiction_seeds']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
