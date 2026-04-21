from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import math
import re

import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import ROOT, settings
from .jsonl import load_jsonl


class HashingEmbeddingFunction:
    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def name(self) -> str:
        return "local-hashing-v1"

    @staticmethod
    def _features(text: str) -> list[str]:
        lowered = text.lower()
        ascii_tokens = [
            token
            for token in "".join(ch if ch.isalnum() else " " for ch in lowered).split()
            if len(token) >= 2
        ]
        compact = "".join(ch for ch in lowered if not ch.isspace())
        chargrams = [compact[idx : idx + 3] for idx in range(max(0, len(compact) - 2))]
        return ascii_tokens + chargrams

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in input:
            vector = [0.0] * self.dimensions
            for feature in self._features(text):
                digest = hashlib.sha1(feature.encode("utf-8")).digest()
                bucket = int.from_bytes(digest[:4], "big") % self.dimensions
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vector[bucket] += sign
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            embeddings.append([value / norm for value in vector])
        return embeddings

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: list[str] | str) -> list[list[float]] | list[float]:
        if isinstance(input, str):
            return self([input])[0]
        return self(input)


class ChromaStore:
    _ZH_STOP_CHARS = {"是", "的", "了", "吗", "呢", "啊", "和", "与", "及", "在", "用", "有"}
    _EN_STOP_TOKENS = {"what", "is", "the", "a", "an", "of", "to", "for"}

    def __init__(self, persist_dir: Path | None = None) -> None:
        self.persist_dir = persist_dir or (ROOT / settings.chroma_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.embedding_function = HashingEmbeddingFunction()
        self.raw_chunk_rows = load_jsonl(ROOT / "docs/chroma-ready/chunks.jsonl")
        curated_chunks_path = ROOT / "docs/tier0/curated/chunks.jsonl"
        if curated_chunks_path.exists():
            self.raw_chunk_rows.extend(load_jsonl(curated_chunks_path))

    @staticmethod
    def _is_low_quality_row(title: str, text: str) -> bool:
        title_l = title.strip().lower()
        text_l = text.strip().lower()
        if title_l == "sitemap":
            return True
        if text_l.startswith("</loc> <lastmod>") or "<urlset" in text_l or "</url>" in text_l[:500]:
            return True
        return False

    @staticmethod
    def _normalize_metadata_value(value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {key: self._normalize_metadata_value(value) for key, value in metadata.items()}

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        lowered = text.lower()
        ascii_tokens = [
            token
            for token in "".join(ch if ch.isalnum() else " " for ch in lowered).split()
            if len(token) >= 2
        ]
        cjk_tokens: list[str] = []
        for seq in re.findall(r"[\u4e00-\u9fff]{2,}", text):
            seq = re.sub(r"(是什么|是啥|有啥用|有什么用|怎么用|如何用)$", "", seq)
            if len(seq) >= 2:
                cjk_tokens.append(seq)
        return ascii_tokens + cjk_tokens

    def _entity_linked_search(self, entity_ids: list[str], top_k: int = 8) -> list[dict[str, Any]]:
        entity_id_set = set(entity_ids)
        if not entity_id_set:
            return []
        rows = []
        for row in self.raw_chunk_rows:
            chunk_entity_ids = set(row["metadata"].get("entity_ids", []))
            if not chunk_entity_ids.intersection(entity_id_set):
                continue
            if self._is_low_quality_row(str(row["metadata"].get("title", "")), row["content"]):
                continue
            rows.append(
                {
                    "chunk_id": row["id"],
                    "text": row["content"],
                    "metadata": row["metadata"],
                    "distance": None,
                    "retrieval_source": "entity_link",
                    "score": 10.0,
                }
            )
        return rows[:top_k]

    def _lexical_search(
        self,
        query: str,
        top_k: int = 8,
        preferred_terms: list[str] | None = None,
        preferred_title_contains: list[str] | None = None,
        preferred_text_contains: list[str] | None = None,
        preferred_source_ids: list[str] | None = None,
        discouraged_source_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        lowered = query.lower()
        preferred_terms = [term.lower() for term in (preferred_terms or []) if term]
        preferred_title_contains = [term.lower() for term in (preferred_title_contains or []) if term]
        preferred_text_contains = [term.lower() for term in (preferred_text_contains or []) if term]
        preferred_source_ids = [term for term in (preferred_source_ids or []) if term]
        discouraged_source_ids = [term for term in (discouraged_source_ids or []) if term]
        query_tokens = {
            token
            for token in self._tokenize(query)
            if token not in self._EN_STOP_TOKENS and token not in self._ZH_STOP_CHARS
        }
        scored: list[tuple[float, dict[str, Any]]] = []
        for row in self.raw_chunk_rows:
            content = row["content"]
            metadata = row["metadata"]
            title = str(metadata.get("title", ""))
            if self._is_low_quality_row(title, content):
                continue
            source_id = str(metadata.get("source_id", ""))
            keywords = " ".join(metadata.get("keywords", []))
            blob = f"{title}\n{keywords}\n{content}"
            blob_lower = blob.lower()
            title_lower = title.lower()
            score = 0.0
            if lowered and lowered in blob_lower:
                score += 4.0
            overlap = sum(1 for token in query_tokens if token in blob_lower)
            score += overlap
            exact_term_hits = sum(1 for token in query_tokens if len(token) >= 2 and token in blob_lower)
            score += exact_term_hits * 2.5
            preferred_hits = sum(1 for term in preferred_terms if term in blob_lower)
            score += preferred_hits * 5.0
            exact_preferred_phrases = [term for term in preferred_terms if len(term) >= 3 and term in blob_lower]
            score += len(exact_preferred_phrases) * 10.0
            if title and lowered and lowered in title.lower():
                score += 2.0
            if any(token in title_lower for token in query_tokens):
                score += 2.0
            if preferred_terms and any(term in title_lower for term in preferred_terms):
                score += 4.0
            if exact_preferred_phrases and any(term in title_lower for term in exact_preferred_phrases):
                score += 8.0
            if preferred_title_contains and any(term in title_lower for term in preferred_title_contains):
                score += 15.0
            if preferred_text_contains and any(term in blob_lower for term in preferred_text_contains):
                score += 12.0
            if preferred_source_ids and source_id in preferred_source_ids:
                score += 6.0
            if discouraged_source_ids and source_id in discouraged_source_ids:
                score -= 8.0
            if exact_preferred_phrases:
                authority = str(metadata.get("authority_tier", ""))
                if authority in {"official", "structured_db"}:
                    score += 3.0
                elif authority == "wiki":
                    score += 1.0
            if str(metadata.get("authority_tier", "")) == "curated":
                score += 50.0
            if score > 0:
                scored.append((score, row))

        scored.sort(key=lambda item: (-item[0], item[1]["id"]))
        return [
            {
                "chunk_id": row["id"],
                "text": row["content"],
                "metadata": row["metadata"],
                "distance": None,
                "retrieval_source": "lexical",
                "score": score,
            }
            for score, row in scored[:top_k]
        ]

    def _upsert_collection(self, name: str, rows: list[dict[str, Any]]) -> int:
        collection = self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        ids = [row["id"] for row in rows]
        documents = [row["content"] for row in rows]
        metadatas = [self._normalize_metadata(row["metadata"]) for row in rows]
        if ids:
            try:
                collection.delete(ids=ids)
            except Exception:
                pass
            batch_size = 500
            for start in range(0, len(ids), batch_size):
                end = start + batch_size
                collection.add(
                    ids=ids[start:end],
                    documents=documents[start:end],
                    metadatas=metadatas[start:end],
                )
        return collection.count()

    def ingest(self, documents_path: Path, chunks_path: Path) -> dict[str, int]:
        docs = load_jsonl(documents_path)
        chunks = load_jsonl(chunks_path)
        curated_docs_path = ROOT / "docs/tier0/curated/documents.jsonl"
        curated_chunks_path = ROOT / "docs/tier0/curated/chunks.jsonl"
        if curated_docs_path.exists():
            docs.extend(load_jsonl(curated_docs_path))
        if curated_chunks_path.exists():
            chunks.extend(load_jsonl(curated_chunks_path))
        return {
            "documents": self._upsert_collection("documents", docs),
            "chunks": self._upsert_collection("evidence_chunks", chunks),
        }

    def query_chunks(
        self,
        query: str,
        top_k: int = 8,
        entity_ids: list[str] | None = None,
        preferred_terms: list[str] | None = None,
        preferred_title_contains: list[str] | None = None,
        preferred_text_contains: list[str] | None = None,
        preferred_source_ids: list[str] | None = None,
        discouraged_source_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        collection = self.client.get_or_create_collection(
            name="evidence_chunks",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        rows: dict[str, dict[str, Any]] = {}
        for row in self._entity_linked_search(entity_ids or [], top_k=top_k):
            rows[row["chunk_id"]] = row
        try:
            if collection.count() > 0:
                result = collection.query(query_texts=[query], n_results=top_k)
                documents = result.get("documents", [[]])[0]
                metadatas = result.get("metadatas", [[]])[0]
                ids = result.get("ids", [[]])[0]
                distances = result.get("distances", [[]])[0] or [None] * len(ids)
                for idx, chunk_id in enumerate(ids):
                    title = str(metadatas[idx].get("title", "")) if idx < len(metadatas) else ""
                    text = documents[idx] if idx < len(documents) else ""
                    if self._is_low_quality_row(title, text):
                        continue
                    rows[chunk_id] = {
                        "chunk_id": chunk_id,
                        "text": documents[idx],
                        "metadata": metadatas[idx],
                        "distance": distances[idx],
                        "retrieval_source": "vector",
                    }
        except Exception:
            rows = {}

        for row in self._lexical_search(
            query,
            top_k=top_k,
            preferred_terms=preferred_terms,
            preferred_title_contains=preferred_title_contains,
            preferred_text_contains=preferred_text_contains,
            preferred_source_ids=preferred_source_ids,
            discouraged_source_ids=discouraged_source_ids,
        ):
            existing = rows.get(row["chunk_id"])
            if existing is None or existing.get("retrieval_source") == "vector":
                rows[row["chunk_id"]] = row

        combined = list(rows.values())
        def priority(row: dict[str, Any]) -> int:
            if row.get("retrieval_source") == "entity_link":
                return 0
            if row.get("retrieval_source") == "lexical" and row.get("score", 0.0) >= 3.0:
                return 1
            if row.get("retrieval_source") == "vector":
                return 2
            return 3

        combined.sort(
            key=lambda row: (
                priority(row),
                row.get("distance") is None,
                row.get("distance") if row.get("distance") is not None else 999999,
                -row.get("score", 0.0),
            )
        )
        return combined[:top_k]
