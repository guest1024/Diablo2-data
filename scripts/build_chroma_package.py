#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"
OUT = ROOT / "docs/chroma-ready"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def infer_language(source_id: str) -> str:
    if source_id in {"91d2", "blizzard-cn-d2"}:
        return "zh"
    if source_id in {"diablo2-io", "arreat-summit", "purediablo-d2wiki", "blizzhackers-d2data", "diablo2-net-api"}:
        return "en"
    return "mixed"


def infer_doc_type(source_id: str, source_url: str, title: str) -> str:
    url = source_url.lower()
    title_l = title.lower()
    if source_id == "diablo2-net-api":
        return "json_relation"
    if source_id == "blizzhackers-d2data":
        return "json_entity"
    if "faq" in title_l or "常见问题" in title or "xinshouzhiyin" in url or "changjianwenti" in url:
        return "faq"
    if source_id == "purediablo-d2wiki" and ("manual" in title_l or "faq" in title_l):
        return "article"
    if source_id in {"arreat-summit", "diablo2-io", "purediablo-d2wiki"}:
        return "article"
    return "article"


def infer_chunk_type(doc_type: str, title: str, source_url: str) -> str:
    title_l = title.lower()
    url = source_url.lower()
    if doc_type == "faq":
        return "qa_pair"
    if any(key in url for key in ["/runewords/", "/uniques/", "/sets/", "/base/", "/recipes/", "/monsters/", "/skills/", "/areas/", "/quests/", "/npcs/"]):
        return "entity"
    if "manual" in title_l:
        return "manual_section"
    if doc_type.startswith("json"):
        return "relation"
    return "text"


def infer_game_variant(source_id: str, title: str, text: str, source_url: str) -> str:
    blob = f"{title}\n{text[:4000]}\n{source_url}".lower()
    if "resurrected" in blob or "d2r" in blob:
        return "d2r"
    if "lord of destruction" in blob or "lod" in blob or "classic.battle.net/diablo2exp" in source_url:
        return "lod"
    return "unknown"


def infer_version_tokens(title: str, text: str) -> list[str]:
    found = sorted(set(re.findall(r"\b(?:1\.\d{2}|2\.\d+|2\.\d{1,2})\b", f"{title}\n{text[:6000]}")))
    return found


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    docs = load_jsonl(MERGED / "normalized/documents.jsonl")
    chunks = load_jsonl(MERGED / "chunks.jsonl")
    canonical_entities = {row["canonical_id"]: row for row in load_jsonl(MERGED / "canonical-entities.jsonl")}
    canonical_claims = load_jsonl(MERGED / "canonical-claims.jsonl")

    entity_ids_by_url: dict[str, list[str]] = {}
    for claim in canonical_claims:
        if claim["predicate"] != "discovered_via":
            continue
        entity_ids_by_url.setdefault(claim["object"], []).append(claim["subject_id"])

    docs_by_id = {doc["doc_id"]: doc for doc in docs}

    chroma_docs = []
    chroma_chunks = []
    for doc in docs:
        entity_ids = sorted(set(entity_ids_by_url.get(doc["source_url"], [])))
        aliases = []
        for entity_id in entity_ids:
            aliases.extend(canonical_entities.get(entity_id, {}).get("aliases", []))
        metadata = {
            "doc_id": doc["doc_id"],
            "doc_type": infer_doc_type(doc["source_id"], doc["source_url"], doc["title"]),
            "source": doc["source_url"],
            "source_id": doc["source_id"],
            "title": doc["title"],
            "language": infer_language(doc["source_id"]),
            "page": None,
            "section": None,
            "chunk_type": infer_chunk_type(infer_doc_type(doc["source_id"], doc["source_url"], doc["title"]), doc["title"], doc["source_url"]),
            "entity_ids": entity_ids,
            "keywords": sorted(set([doc["title"]] + aliases[:10])),
            "timestamp": None,
            "authority_tier": "official" if doc["source_id"] in {"arreat-summit", "blizzard-cn-d2"} else ("structured_db" if doc["source_id"] in {"diablo2-io", "blizzhackers-d2data", "diablo2-net-api"} else "wiki"),
            "game_variant": infer_game_variant(doc["source_id"], doc["title"], doc["text"], doc["source_url"]),
            "version_tokens": infer_version_tokens(doc["title"], doc["text"]),
        }
        chroma_docs.append({"id": f"doc::{doc['doc_id']}", "content": doc["text"], "metadata": metadata})

    for chunk in chunks:
        doc = docs_by_id.get(chunk["doc_id"])
        if not doc:
            continue
        entity_ids = sorted(set(entity_ids_by_url.get(chunk["source_url"], [])))
        aliases = []
        for entity_id in entity_ids:
            aliases.extend(canonical_entities.get(entity_id, {}).get("aliases", []))
        doc_type = infer_doc_type(chunk["source_id"], chunk["source_url"], chunk["title"])
        metadata = {
            "doc_id": chunk["doc_id"],
            "doc_type": doc_type,
            "source": chunk["source_url"],
            "source_id": chunk["source_id"],
            "title": chunk["title"],
            "language": infer_language(chunk["source_id"]),
            "page": None,
            "section": None,
            "chunk_type": infer_chunk_type(doc_type, chunk["title"], chunk["source_url"]),
            "entity_ids": entity_ids,
            "keywords": sorted(set([chunk["title"]] + aliases[:10])),
            "timestamp": None,
            "chunk_index": chunk["chunk_index"],
            "char_count": chunk["char_count"],
            "authority_tier": "official" if chunk["source_id"] in {"arreat-summit", "blizzard-cn-d2"} else ("structured_db" if chunk["source_id"] in {"diablo2-io", "blizzhackers-d2data", "diablo2-net-api"} else "wiki"),
            "game_variant": infer_game_variant(chunk["source_id"], chunk["title"], chunk["text"], chunk["source_url"]),
            "version_tokens": infer_version_tokens(chunk["title"], chunk["text"]),
        }
        chroma_chunks.append({"id": chunk["chunk_id"], "content": chunk["text"], "metadata": metadata})

    (OUT / "documents.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in chroma_docs) + "\n", encoding="utf-8")
    (OUT / "chunks.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in chroma_chunks) + "\n", encoding="utf-8")

    manifest = {
        "documents": len(chroma_docs),
        "chunks": len(chroma_chunks),
        "paths": {
            "documents": "docs/chroma-ready/documents.jsonl",
            "chunks": "docs/chroma-ready/chunks.jsonl",
        },
        "notes": {
            "vector_db": "ChromaDB",
            "embedding_storage": "Embeddings should be stored in Chroma collections, not in the JSONL payloads",
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# ChromaDB 就绪数据包\n\n"
        f"- Documents: `{manifest['documents']}`\n"
        f"- Chunks: `{manifest['chunks']}`\n"
        "- Vector DB: `ChromaDB`\n\n"
        "推荐导入方式：\n\n"
        "1. 读取 `documents.jsonl` / `chunks.jsonl`\n"
        "2. 提取 `id / content / metadata`\n"
        "3. 用 Chroma collection.add(ids=..., documents=..., metadatas=...) 导入\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
