#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def main() -> int:
    normalized_manifest = json.loads((MERGED / "normalized-manifest.json").read_text(encoding="utf-8"))
    expect((MERGED / "normalized/documents.jsonl").is_file(), "merged normalized docs exist")
    expect(normalized_manifest["document_count"] >= 300, "merged normalized doc count is substantial")

    for relative in [
        "aliases.jsonl",
        "provenance.jsonl",
        "canonical-entities.jsonl",
        "support-edges.jsonl",
        "claim-index.jsonl",
        "canonical-claims.jsonl",
        "relation-taxonomy.json",
    ]:
        expect((MERGED / relative).exists(), f"merged {relative} exists")

    expect(count_jsonl(MERGED / "aliases.jsonl") > 100, "merged aliases count is populated")
    expect(count_jsonl(MERGED / "provenance.jsonl") > 100, "merged provenance count is populated")
    expect(count_jsonl(MERGED / "canonical-entities.jsonl") > 100, "merged canonical entities count is populated")
    expect(count_jsonl(MERGED / "canonical-claims.jsonl") > 50, "merged canonical claims count is populated")
    print("PASS: merged enhancement verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
