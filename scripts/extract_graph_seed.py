#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import uuid
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}::{value}"))


def title_name(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip()
    cleaned = re.sub(r"^(The Arreat Summit - |Diablo 2 Wiki\s*-?\s*)", "", cleaned, flags=re.I)
    return cleaned.strip(" -")


def classify_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if not parts or parts == [""]:
        return "WebPage", path or "root"

    if "diablo2.io" in parsed.netloc and len(parts) >= 2:
        category = parts[0]
        slug = parts[-1]
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

    if "d2.blizzard.cn" in parsed.netloc and "/news/" in path:
        return "NewsArticle", parts[-1].replace(".html", "") or "news"

    if "diablo-2.net" in parsed.netloc and (path == "api" or path.startswith("api/")):
        return "ApiEndpoint", parts[-1] or "api"

    if "github.com" in parsed.netloc or "raw.githubusercontent.com" in parsed.netloc or "api.github.com" in parsed.netloc:
        return "OpenDataResource", parts[-1] or parsed.netloc

    return "WebPage", parts[-1]


def make_claim(claims: list[dict], subject_id: str, predicate: str, value: str, source_id: str, evidence_doc_id: str) -> None:
    claims.append(
        {
            "claim_id": make_id("claim", f"{subject_id}|{predicate}|{value}|{evidence_doc_id}"),
            "subject_id": subject_id,
            "predicate": predicate,
            "object": value,
            "source_id": source_id,
            "evidence_doc_id": evidence_doc_id,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a minimal graph seed from Tier 0 normalized artifacts")
    parser.add_argument("--normalized", default="docs/tier0/normalized/documents.jsonl")
    parser.add_argument("--output-root", default="docs/tier0/derived")
    args = parser.parse_args()

    normalized_path = ROOT / args.normalized
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    docs = load_jsonl(normalized_path)
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    claims: list[dict] = []

    def upsert_node(node_id: str, **payload: str) -> None:
        if node_id in nodes:
            return
        nodes[node_id] = {"node_id": node_id, **payload}

    for doc in docs:
        source_node_id = make_id("source", doc["source_id"])
        upsert_node(
            source_node_id,
            node_type="Source",
            key=doc["source_id"],
            name=doc["source_name"],
            lane=doc["lane"],
            authority_tier=doc["authority_tier"],
        )

        upsert_node(
            doc["doc_id"],
            node_type="SourceDocument",
            key=doc["label"],
            name=doc["title"] or doc["label"],
            source_id=doc["source_id"],
            lane=doc["lane"],
            authority_tier=doc["authority_tier"],
        )
        edges.append(
            {
                "edge_id": make_id("edge", f"{doc['doc_id']}|BELONGS_TO_SOURCE|{source_node_id}"),
                "from_id": doc["doc_id"],
                "to_id": source_node_id,
                "edge_type": "BELONGS_TO_SOURCE",
            }
        )

        entity_type, entity_key = classify_url(doc["source_url"])
        if entity_type != "WebPage":
            entity_node_id = make_id("entity", f"{entity_type}|{entity_key}")
            upsert_node(
                entity_node_id,
                node_type=entity_type,
                key=entity_key,
                name=title_name(doc["title"]) or entity_key,
                source_id=doc["source_id"],
            )
            edges.append(
                {
                    "edge_id": make_id("edge", f"{doc['doc_id']}|DESCRIBES|{entity_node_id}"),
                    "from_id": doc["doc_id"],
                    "to_id": entity_node_id,
                    "edge_type": "DESCRIBES",
                }
            )
            make_claim(claims, entity_node_id, "discovered_via", doc["source_url"], doc["source_id"], doc["doc_id"])

        for discovered_url in doc.get("discovered_url_sample", []):
            discovered_type, discovered_key = classify_url(discovered_url)
            discovered_node_id = make_id("entity", f"{discovered_type}|{discovered_key}|{discovered_url}")
            upsert_node(
                discovered_node_id,
                node_type=discovered_type,
                key=discovered_key,
                name=discovered_key,
                source_id=doc["source_id"],
            )
            edges.append(
                {
                    "edge_id": make_id("edge", f"{doc['doc_id']}|DISCOVERS_URL|{discovered_node_id}"),
                    "from_id": doc["doc_id"],
                    "to_id": discovered_node_id,
                    "edge_type": "DISCOVERS_URL",
                }
            )

        make_claim(claims, doc["doc_id"], "lane", doc["lane"], doc["source_id"], doc["doc_id"])
        make_claim(claims, doc["doc_id"], "authority_tier", doc["authority_tier"], doc["source_id"], doc["doc_id"])

        lowered = doc["text"].lower()
        if "api key not found" in lowered or "api key" in lowered:
            make_claim(claims, doc["doc_id"], "api_requires_key", "true", doc["source_id"], doc["doc_id"])

    nodes_path = output_root / "nodes.jsonl"
    edges_path = output_root / "edges.jsonl"
    claims_path = output_root / "claims.jsonl"
    nodes_path.write_text("\n".join(json.dumps(node, ensure_ascii=False) for node in nodes.values()) + "\n", encoding="utf-8")
    edges_path.write_text("\n".join(json.dumps(edge, ensure_ascii=False) for edge in edges) + "\n", encoding="utf-8")
    claims_path.write_text("\n".join(json.dumps(claim, ensure_ascii=False) for claim in claims) + "\n", encoding="utf-8")

    manifest = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "claim_count": len(claims),
        "node_types": dict(Counter(node["node_type"] for node in nodes.values())),
        "edge_types": dict(Counter(edge["edge_type"] for edge in edges)),
        "paths": {
            "nodes": str(nodes_path.relative_to(ROOT)),
            "edges": str(edges_path.relative_to(ROOT)),
            "claims": str(claims_path.relative_to(ROOT)),
        },
    }
    (output_root / "graph-seed-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "graph-seed-report.md").write_text(
        "# Tier 0 Graph Seed Report\n\n"
        f"- Nodes: `{manifest['node_count']}`\n"
        f"- Edges: `{manifest['edge_count']}`\n"
        f"- Claims: `{manifest['claim_count']}`\n"
        f"- Node types: `{manifest['node_types']}`\n"
        f"- Edge types: `{manifest['edge_types']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
