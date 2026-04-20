#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_TARGETS = [
    "docs/tier0/fetch-manifest.json",
    "docs/tier0/fetch-report.md",
    "docs/tier0/normalized-manifest.json",
    "docs/tier0/normalized-report.md",
    "docs/tier0/derived/graph-seed-manifest.json",
    "docs/tier0/derived/alias-seed-manifest.json",
    "docs/tier0/derived/refined-graph-manifest.json",
    "docs/tier0/derived/claim-normalization-manifest.json",
    "docs/tier0/derived/version-semantics-manifest.json",
    "docs/tier0/derived/graph-export-bundle.json",
    "docs/tier0/export/csv-export-manifest.json",
    "docs/tier0/graph-export-consumer-guide.md",
    "docs/tier0/neo4j-import-playbook.md",
    "docs/tier0/pipeline-operator-notes.md",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build checksum manifest for key Tier 0 artifacts")
    parser.add_argument("--output", default="docs/tier0/artifact-checksums.json")
    args = parser.parse_args()

    entries: list[dict] = []
    for relative in DEFAULT_TARGETS:
        path = ROOT / relative
        entries.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    payload = {
        "artifact_count": len(entries),
        "entries": entries,
    }
    out_path = ROOT / args.output
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
