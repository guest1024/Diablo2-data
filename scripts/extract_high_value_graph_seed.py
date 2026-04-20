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
    path = parsed.path.strip("/")
    parts = path.split("/")
    if "diablo2.io" in parsed.netloc and len(parts) >= 2:
        category = parts[0]
        slug = parts[-1].replace(".html", "")
        mapping = {
            "uniques": "UniqueItem",
            "runewords": "Runeword",
            "sets": "SetItem",
            "base": "BaseItem",
            "recipes": "Recipe",
            "monsters": "Monster",
            "npcs": "NPC",
            "skills": "Skill",
            "areas": "Area",
            "quests": "Quest",
            "misc": "MiscEntity",
        }
        return mapping.get(category, "WebPage"), slug
    if "classic.battle.net" in parsed.netloc and "diablo2exp" in path:
        if "/classes/" in path:
            return "Class", parts[-1].replace(".shtml", "")
        if "/skills/" in path:
            return "SkillPage", parts[-1].replace(".shtml", "")
        if "/items/" in path:
            return "ItemPage", parts[-1].replace(".shtml", "")
        if "/monsters/" in path:
            return "MonsterPage", parts[-1].replace(".shtml", "")
        if "/quests/" in path:
            return "QuestPage", parts[-1].replace(".shtml", "")
        if "/maps/" in path:
            return "AreaPage", parts[-1].replace(".shtml", "")
        return "LegacyReferencePage", parts[-1].replace(".shtml", "")
    return "WebPage", parts[-1] if parts else "root"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract graph seed from high-value normalized corpus")
    parser.add_argument("--documents", default="docs/tier0/high-value/normalized/documents.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/high-value/derived")
    args = parser.parse_args()

    docs = load_jsonl(ROOT / args.documents)
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    claims: list[dict] = []

    def upsert(node_id: str, **payload: str | int) -> None:
        nodes.setdefault(node_id, {"node_id": node_id, **payload})

    for doc in docs:
        source_node_id = make_id("source", doc["source_id"])
        upsert(source_node_id, node_type="Source", key=doc["source_id"], name=doc["source_id"])

        doc_node_id = make_id("hv-doc", doc["doc_id"])
        upsert(
            doc_node_id,
            node_type="SourceDocument",
            key=doc["doc_id"],
            name=doc["title"],
            source_id=doc["source_id"],
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
        entity_node_id = make_id("hv-entity", f"{entity_type}|{entity_key}")
        upsert(
            entity_node_id,
            node_type=entity_type,
            key=entity_key,
            name=doc["title"],
            source_id=doc["source_id"],
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
                "source_id": doc["source_id"],
                "evidence_doc_id": doc_node_id,
            }
        )
        claims.append(
            {
                "claim_id": make_id("claim", f"{doc_node_id}|char_count|{doc['char_count']}"),
                "subject_id": doc_node_id,
                "predicate": "char_count",
                "object": str(doc["char_count"]),
                "source_id": doc["source_id"],
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
        "paths": {
            "nodes": str((output_root / "nodes.jsonl").relative_to(ROOT)),
            "edges": str((output_root / "edges.jsonl").relative_to(ROOT)),
            "claims": str((output_root / "claims.jsonl").relative_to(ROOT)),
        },
    }
    (output_root / "graph-seed-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "graph-seed-report.md").write_text(
        "# High-Value Graph Seed Report\n\n"
        f"- Nodes: `{manifest['node_count']}`\n"
        f"- Edges: `{manifest['edge_count']}`\n"
        f"- Claims: `{manifest['claim_count']}`\n"
        f"- Node types: `{manifest['node_types']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
