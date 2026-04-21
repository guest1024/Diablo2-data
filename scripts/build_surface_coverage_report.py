#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.open(encoding="utf-8") if line.strip())


def main() -> int:
    term_map = json.loads((ROOT / "docs/tier0/bilingual-term-map.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "docs/tier0/verification/routing-matrix.json").read_text(encoding="utf-8"))

    curated_docs = count_jsonl(ROOT / "docs/tier0/curated/documents.jsonl")
    curated_chunks = count_jsonl(ROOT / "docs/tier0/curated/chunks.jsonl")
    chroma_docs = count_jsonl(ROOT / "docs/chroma-ready/documents.jsonl")
    chroma_chunks = count_jsonl(ROOT / "docs/chroma-ready/chunks.jsonl")

    lanes: dict[str, int] = {}
    for row in routing["cases"]:
        lanes[row["lane"]] = lanes.get(row["lane"], 0) + 1

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "term_map_entries": len(term_map),
        "curated_anchor_documents": curated_docs,
        "curated_anchor_chunks": curated_chunks,
        "chroma_ready_documents": chroma_docs,
        "chroma_ready_chunks": chroma_chunks,
        "runtime_documents": chroma_docs + curated_docs,
        "runtime_chunks": chroma_chunks + curated_chunks,
        "routing_matrix_total_queries": len(routing["cases"]),
        "routing_lanes": lanes,
    }

    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "surface-coverage-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Surface Coverage Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- bilingual term map entries: `{report['term_map_entries']}`",
        f"- curated anchor documents: `{report['curated_anchor_documents']}`",
        f"- curated anchor chunks: `{report['curated_anchor_chunks']}`",
        f"- chroma-ready documents: `{report['chroma_ready_documents']}`",
        f"- chroma-ready chunks: `{report['chroma_ready_chunks']}`",
        f"- runtime documents: `{report['runtime_documents']}`",
        f"- runtime chunks: `{report['runtime_chunks']}`",
        f"- routing matrix total queries: `{report['routing_matrix_total_queries']}`",
        "",
        "## Routing lanes",
        "",
    ]
    for lane, count in sorted(lanes.items()):
        lines.append(f"- `{lane}`: `{count}`")
    (out_dir / "surface-coverage-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
