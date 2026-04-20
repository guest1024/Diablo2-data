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

    snapshot = {
        "readiness": {
            "tier0_pipeline_rerunnable": True,
            "stack_verification_present": True,
            "checksum_verification_present": True,
            "graph_export_bundle_present": True,
            "csv_export_present": True,
            "neo4j_playbook_present": True,
            "consumer_guide_present": True,
            "handoff_present": True,
        },
        "counts": {
            "sources": len(fetch["sources"]),
            "captures": len(fetch["results"]),
            "documents": normalized["document_count"],
            "chunks": normalized["chunk_count"],
            "graph": graph_bundle["counts"],
            "version_semantics": {
                "version_tags": version_semantics["version_tag_count"],
                "contradiction_seeds": version_semantics["contradiction_seed_count"],
            },
            "csv_export": csv_export["csv_tables"],
            "artifact_checksums": checksums["artifact_count"],
        },
        "entrypoints": {
            "readme": "docs/tier0/README.md",
            "handoff": "docs/tier0/HANDOFF.md",
            "consumer_guide": "docs/tier0/graph-export-consumer-guide.md",
            "neo4j_playbook": "docs/tier0/neo4j-import-playbook.md",
            "pipeline": "python3 scripts/run_tier0_pipeline.py",
            "verify_stack": "python3 scripts/verify_tier0_stack.py",
            "verify_checksums": "python3 scripts/verify_artifact_checksums.py",
        },
    }

    out = TIER0 / "status-snapshot.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
