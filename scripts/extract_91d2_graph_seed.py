#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}::{value}"))


def classify_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    category = parts[0] if parts else "wiki"
    slug = parts[-1].replace(".html", "") if parts else "root"
    mapping = {
        "jiaosezhiye": "BuildGuide",
        "jichuzhishi": "ReferenceGuide",
        "jingyanxinde": "ExperienceGuide",
        "changjingditu": "AreaGuide",
        "xinshouzhiyin": "FAQGuide",
        "changjianwenti": "FAQGuide",
        "renwugonglue": "QuestGuide",
        "wupinzhuangbei": "ItemGuide",
    }
    return mapping.get(category, "ChineseGuide"), slug


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract graph seed from 91d2 high-value corpus")
    parser.add_argument("--documents", default="docs/tier0/91d2-high-value/normalized/documents.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/91d2-high-value/derived")
    args = parser.parse_args()

    docs = load_jsonl(ROOT / args.documents)
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    claims: list[dict] = []

    def upsert(node_id: str, **payload):
        nodes.setdefault(node_id, {"node_id": node_id, **payload})

    source_node_id = make_id("source", "91d2")
    upsert(source_node_id, node_type="Source", key="91d2", name="91D2")

    for doc in docs:
        doc_node_id = make_id("91d2-doc", doc["doc_id"])
        upsert(
            doc_node_id,
            node_type="SourceDocument",
            key=doc["doc_id"],
            name=doc["title"],
            source_id="91d2",
            char_count=doc["char_count"],
        )
        edges.append(
            {
                "edge_id": make_id("edge", f"{doc_node_id}|BELONGS_TO_SOURCE|{source_node_id}"),
                "from_id": doc_node_id,
                "to_id": source_node_id,
                "edge_type": "BELONGS_TO_SOURCE",
            }
        )
        entity_type, entity_key = classify_url(doc["source_url"])
        entity_node_id = make_id("91d2-entity", f"{entity_type}|{entity_key}")
        upsert(
            entity_node_id,
            node_type=entity_type,
            key=entity_key,
            name=doc["title"],
            source_id="91d2",
        )
        edges.append(
            {
                "edge_id": make_id("edge", f"{doc_node_id}|DESCRIBES|{entity_node_id}"),
                "from_id": doc_node_id,
                "to_id": entity_node_id,
                "edge_type": "DESCRIBES",
            }
        )
        claims.append(
            {
                "claim_id": make_id("claim", f"{entity_node_id}|discovered_via|{doc['source_url']}"),
                "subject_id": entity_node_id,
                "predicate": "discovered_via",
                "object": doc["source_url"],
                "source_id": "91d2",
                "evidence_doc_id": doc_node_id,
            }
        )
        claims.append(
            {
                "claim_id": make_id("claim", f"{doc_node_id}|char_count|{doc['char_count']}"),
                "subject_id": doc_node_id,
                "predicate": "char_count",
                "object": str(doc["char_count"]),
                "source_id": "91d2",
                "evidence_doc_id": doc_node_id,
            }
        )

    (output_root / "nodes.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in nodes.values()) + "\n", encoding="utf-8")
    (output_root / "edges.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in edges) + "\n", encoding="utf-8")
    (output_root / "claims.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in claims) + "\n", encoding="utf-8")
    manifest = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "claim_count": len(claims),
        "node_types": dict(Counter(node["node_type"] for node in nodes.values())),
    }
    (output_root / "graph-seed-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "graph-seed-report.md").write_text(
        "# 91D2 中文高价值图谱种子\n\n"
        f"- Nodes: `{manifest['node_count']}`\n"
        f"- Edges: `{manifest['edge_count']}`\n"
        f"- Claims: `{manifest['claim_count']}`\n"
        f"- Node types: `{manifest['node_types']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
