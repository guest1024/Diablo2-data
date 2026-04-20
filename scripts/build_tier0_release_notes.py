#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"
DERIVED = TIER0 / "derived"
EXPORT = TIER0 / "export"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    fetch = load(TIER0 / "fetch-manifest.json")
    normalized = load(TIER0 / "normalized-manifest.json")
    bundle = load(DERIVED / "graph-export-bundle.json")
    csv_manifest = load(EXPORT / "csv-export-manifest.json")
    version = load(DERIVED / "version-semantics-manifest.json")

    lines = [
        "# Tier 0 Release Notes",
        "",
        "## Summary",
        "",
        f"- Sources captured: `{len(fetch['sources'])}`",
        f"- Raw captures: `{len(fetch['results'])}`",
        f"- Normalized documents: `{normalized['document_count']}`",
        f"- Retrieval chunks: `{normalized['chunk_count']}`",
        f"- Graph nodes / edges / claims: `{bundle['counts']['nodes']}` / `{bundle['counts']['edges']}` / `{bundle['counts']['claims']}`",
        f"- Canonical entities / claims: `{bundle['counts']['canonical_entities']}` / `{bundle['counts']['canonical_claims']}`",
        f"- Aliases / provenance: `{bundle['counts']['aliases']}` / `{bundle['counts']['provenance']}`",
        f"- Version tags / contradiction seeds: `{version['version_tag_count']}` / `{version['contradiction_seed_count']}`",
        "",
        "## Deliverables",
        "",
        "- Tier 0 raw capture + scoped inventories",
        "- Normalized documents + retrieval chunks",
        "- Graph seed, aliases, provenance, refined graph",
        "- Canonical claims + relation taxonomy",
        "- Graph export bundle + CSV export",
        "- Neo4j import playbook + consumer guide + query recipes",
        "- Operator pipeline, stack verify, checksum verify, status snapshot, handoff docs",
        "",
        "## CSV export counts",
        "",
        *[f"- {name}: `{count}`" for name, count in csv_manifest["csv_tables"].items()],
        "",
        "## Known next-step work",
        "",
        "- Cross-source entity merge rules",
        "- Stronger contradiction modeling",
        "- Patch/version-aware claim refinement",
        "- Tier 1 source expansion",
    ]
    (TIER0 / "release-notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
