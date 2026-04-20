#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"
DERIVED = TIER0 / "derived"
EXPORT = TIER0 / "export"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    fetch = load_json(TIER0 / "fetch-manifest.json")
    normalized = load_json(TIER0 / "normalized-manifest.json")
    graph_bundle = load_json(DERIVED / "graph-export-bundle.json")
    version_semantics = load_json(DERIVED / "version-semantics-manifest.json")
    csv_export = load_json(EXPORT / "csv-export-manifest.json")
    checksums = load_json(TIER0 / "artifact-checksums.json")

    summary = {
        "sources": len(fetch["sources"]),
        "captures": len(fetch["results"]),
        "documents": normalized["document_count"],
        "chunks": normalized["chunk_count"],
        "graph_counts": graph_bundle["counts"],
        "version_semantics": {
            "version_tags": version_semantics["version_tag_count"],
            "contradiction_seeds": version_semantics["contradiction_seed_count"],
        },
        "csv_tables": csv_export["csv_tables"],
        "artifact_checksum_count": checksums["artifact_count"],
    }

    (TIER0 / "stack-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Diablo II Tier 0 Stack Index",
        "",
        "This file is the operator-facing entrypoint for the current Tier 0 acquisition / GraphRAG seed stack.",
        "",
        "## Key counts",
        "",
        f"- Sources: `{summary['sources']}`",
        f"- Captures: `{summary['captures']}`",
        f"- Normalized documents: `{summary['documents']}`",
        f"- Retrieval chunks: `{summary['chunks']}`",
        f"- Artifact checksum entries: `{summary['artifact_checksum_count']}`",
        "",
        "## Main entrypoints",
        "",
        "- Fetch manifest: `docs/tier0/fetch-manifest.json`",
        "- Fetch report: `docs/tier0/fetch-report.md`",
        "- Normalized manifest: `docs/tier0/normalized-manifest.json`",
        "- Graph export bundle: `docs/tier0/derived/graph-export-bundle.json`",
        "- CSV export manifest: `docs/tier0/export/csv-export-manifest.json`",
        "- Consumer guide: `docs/tier0/graph-export-consumer-guide.md`",
        "- Neo4j playbook: `docs/tier0/neo4j-import-playbook.md`",
        "- Operator notes: `docs/tier0/pipeline-operator-notes.md`",
        "- Checksum manifest: `docs/tier0/artifact-checksums.json`",
        "",
        "## One-command operations",
        "",
        "```bash",
        "python3 scripts/run_tier0_pipeline.py",
        "python3 scripts/verify_tier0_stack.py",
        "python3 scripts/verify_artifact_checksums.py",
        "```",
        "",
        "## Graph bundle counts",
        "",
        *[f"- {name}: `{count}`" for name, count in summary["graph_counts"].items()],
        "",
        "## Version / contradiction counts",
        "",
        f"- Version tags: `{summary['version_semantics']['version_tags']}`",
        f"- Contradiction seeds: `{summary['version_semantics']['contradiction_seeds']}`",
        "",
        "## CSV export tables",
        "",
        *[f"- {name}: `{count}`" for name, count in summary["csv_tables"].items()],
        "",
        "## Machine-readable summary",
        "",
        "- `docs/tier0/stack-summary.json`",
    ]

    (TIER0 / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
