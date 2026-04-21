#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def main() -> int:
    curated_docs = load_jsonl(ROOT / "docs/tier0/curated/documents.jsonl")
    curated_chunks = load_jsonl(ROOT / "docs/tier0/curated/chunks.jsonl")
    routing = json.loads((ROOT / "docs/tier0/verification/routing-matrix.json").read_text(encoding="utf-8"))
    term_map = json.loads((ROOT / "docs/tier0/bilingual-term-map.json").read_text(encoding="utf-8"))

    docs_by_doc_id = {row["metadata"]["doc_id"]: row for row in curated_docs}
    chunks_by_doc_id = {row["metadata"]["doc_id"]: row for row in curated_chunks}

    expect(len(curated_docs) == len(curated_chunks), "curated documents and chunks counts match")
    expect(set(docs_by_doc_id) == set(chunks_by_doc_id), "curated documents and chunks share identical doc ids")

    for doc_id, doc in docs_by_doc_id.items():
        chunk = chunks_by_doc_id[doc_id]
        expect(doc["metadata"]["title"] == chunk["metadata"]["title"], f"title aligned for {doc_id}")
        expect(doc["metadata"]["source_id"] == "curated-anchor", f"document source_id is curated-anchor for {doc_id}")
        expect(chunk["metadata"]["source_id"] == "curated-anchor", f"chunk source_id is curated-anchor for {doc_id}")

    curated_titles = {row["metadata"]["title"] for row in curated_docs}
    curated_cases = [row for row in routing["cases"] if row["lane"] == "curated"]
    expect(len(curated_cases) >= len(curated_docs), "routing matrix covers at least as many curated queries as curated docs")
    for row in curated_cases:
        expect(row["source_id"] == "curated-anchor", f"routing source is curated-anchor for {row['query']}")
        expect(row["title"] in curated_titles, f"routing title exists in curated docs for {row['query']}")

    normalized_aliases = {key.lower(): key for key in term_map}
    required_aliases = ["SOJ", "CTA", "ULC", "MF", "DClone", "USC"]
    for alias in required_aliases:
        expect(alias.lower() in normalized_aliases, f"term map contains alias {alias}")

    report = {
        "curated_documents": len(curated_docs),
        "curated_chunks": len(curated_chunks),
        "curated_routing_cases": len(curated_cases),
        "term_map_entries": len(term_map),
        "required_aliases": required_aliases,
    }
    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "curated-surface-alignment.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Curated Surface Alignment",
        "",
        f"- curated documents: `{report['curated_documents']}`",
        f"- curated chunks: `{report['curated_chunks']}`",
        f"- curated routing cases: `{report['curated_routing_cases']}`",
        f"- term map entries: `{report['term_map_entries']}`",
        f"- required aliases checked: `{', '.join(required_aliases)}`",
    ]
    (out_dir / "curated-surface-alignment.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
