#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ["python3", "scripts/run_tier0_pipeline.py"],
    ["python3", "scripts/fetch_high_value_pages.py", "--timeout", "3"],
    ["python3", "scripts/verify_high_value_pages.py"],
    ["python3", "scripts/build_high_value_summary.py"],
    ["python3", "scripts/build_high_value_page_index.py"],
    ["python3", "scripts/build_high_value_preview.py"],
    ["python3", "scripts/extract_high_value_graph_seed.py"],
    ["python3", "scripts/build_high_value_graph_summary.py"],
    ["python3", "scripts/merge_high_value_into_main_graph.py"],
    ["python3", "scripts/build_merged_normalized.py"],
    [
        "python3",
        "scripts/extract_alias_seed.py",
        "--nodes",
        "docs/tier0/merged/nodes.jsonl",
        "--docs",
        "docs/tier0/merged/normalized/documents.jsonl",
        "--claims",
        "docs/tier0/merged/claims.jsonl",
        "--output-root",
        "docs/tier0/merged",
    ],
    [
        "python3",
        "scripts/refine_graph_seed.py",
        "--nodes",
        "docs/tier0/merged/nodes.jsonl",
        "--edges",
        "docs/tier0/merged/edges.jsonl",
        "--claims",
        "docs/tier0/merged/claims.jsonl",
        "--aliases",
        "docs/tier0/merged/aliases.jsonl",
        "--provenance",
        "docs/tier0/merged/provenance.jsonl",
        "--output-root",
        "docs/tier0/merged",
    ],
    [
        "python3",
        "scripts/normalize_claim_seed.py",
        "--claim-index",
        "docs/tier0/merged/claim-index.jsonl",
        "--canonical-entities",
        "docs/tier0/merged/canonical-entities.jsonl",
        "--edges",
        "docs/tier0/merged/edges.jsonl",
        "--aliases",
        "docs/tier0/merged/aliases.jsonl",
        "--output-root",
        "docs/tier0/merged",
    ],
    ["python3", "scripts/build_merged_graph_summary.py"],
    ["python3", "scripts/build_merged_export_bundle.py"],
    ["python3", "scripts/build_merged_sample_queries.py"],
    ["python3", "scripts/export_merged_graph_csv.py"],
    ["python3", "scripts/build_tier0_index.py"],
    ["python3", "scripts/build_tier0_status_snapshot.py"],
    ["python3", "scripts/build_artifact_matrix.py"],
    ["python3", "scripts/build_sample_queries.py"],
    ["python3", "scripts/build_tier0_release_notes.py"],
    ["python3", "scripts/build_tier0_catalog.py"],
    ["python3", "scripts/build_dataset_profile.py"],
    ["python3", "scripts/build_artifact_checksums.py"],
]


def main() -> int:
    for step in STEPS:
        print("==>", " ".join(step))
        result = subprocess.run(step, cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    print("PASS: production pipeline completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
