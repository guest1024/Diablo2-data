from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any
import re

from .config import ROOT, settings
from .jsonl import load_jsonl


class GraphStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or (ROOT / settings.graph_data_dir)
        self.aliases: list[dict[str, Any]] = []
        self.entities: dict[str, dict[str, Any]] = {}
        self.claims: list[dict[str, Any]] = []
        self.provenance: list[dict[str, Any]] = []
        self.chunks: list[dict[str, Any]] = []
        self.claims_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.provenance_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.chunk_by_doc: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.alias_index: dict[str, list[str]] = defaultdict(list)
        self.load()

    @staticmethod
    def _normalize_alias(text: str) -> list[str]:
        if not text:
            return []
        collapsed = " ".join(text.replace("•", " ").replace("|", " ").split())
        candidates = {collapsed, collapsed.lower()}
        trimmed = re.split(r"\s+(?:diablo\s*2|d2r|diablo2\.io|91d2|wiki)\b", collapsed, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        if trimmed:
            candidates.add(trimmed)
            candidates.add(trimmed.lower())
        head = re.split(r"\s{2,}|\s+-\s+", collapsed)[0].strip()
        if head:
            candidates.add(head)
            candidates.add(head.lower())
        return [candidate for candidate in candidates if candidate]

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        lowered = query.lower()
        ascii_terms = [token for token in re.split(r"[^a-z0-9]+", lowered) if len(token) >= 2]
        cjk_terms: list[str] = []
        for seq in re.findall(r"[\u4e00-\u9fff]{2,}", query):
            seq = re.sub(r"(是什么|是啥|有啥用|有什么用|怎么用|如何用)$", "", seq)
            if len(seq) >= 2:
                cjk_terms.append(seq)
        return ascii_terms + cjk_terms

    def load(self) -> None:
        self.aliases = load_jsonl(self.base_dir / "aliases.jsonl")
        self.entities = {row["canonical_id"]: row for row in load_jsonl(self.base_dir / "canonical-entities.jsonl")}
        self.claims = load_jsonl(self.base_dir / "canonical-claims.jsonl")
        self.provenance = load_jsonl(self.base_dir / "provenance.jsonl")
        self.chunks = load_jsonl(self.base_dir / "chunks.jsonl")

        self.claims_by_subject.clear()
        self.provenance_by_subject.clear()
        self.chunk_by_doc.clear()
        self.alias_index.clear()

        for row in self.claims:
            self.claims_by_subject[row["subject_id"]].append(row)
        for row in self.provenance:
            self.provenance_by_subject[row["subject_id"]].append(row)
        for row in self.chunks:
            self.chunk_by_doc[row["doc_id"]].append(row)
        for row in self.aliases:
            for alias in self._normalize_alias(row["alias"]):
                self.alias_index[alias].append(row["canonical_id"])
        for entity_id, entity in self.entities.items():
            for alias in self._normalize_alias(entity.get("name", "")):
                self.alias_index[alias].append(entity_id)

    def resolve_entities(
        self,
        query: str,
        limit: int = 10,
        preferred_terms: list[str] | None = None,
        canonical_hints: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        q = query.strip().lower()
        query_terms = self._query_terms(query)
        preferred_terms = [term.lower() for term in (preferred_terms or []) if term]
        canonical_hints = [term.lower() for term in (canonical_hints or []) if term]
        hits: list[tuple[float, str, str]] = []
        for alias, entity_ids in self.alias_index.items():
            score = 0.0
            if alias == q:
                score = 1.0
            elif q in alias or alias in q:
                score = 0.75
            elif any(term and term in alias for term in query_terms):
                score = 0.55
            if score and preferred_terms and any(term in alias for term in preferred_terms):
                score += 0.35
            if score and canonical_hints and any(term in alias for term in canonical_hints):
                score += 0.55
            if score:
                for entity_id in entity_ids:
                    hits.append((score, alias, entity_id))

        dedup: dict[str, dict[str, Any]] = {}
        for score, alias, entity_id in sorted(hits, reverse=True):
            if entity_id in dedup:
                continue
            entity = self.entities.get(entity_id)
            if not entity:
                continue
            entity_name = entity.get("name", "").lower()
            bonus = 0.0
            if preferred_terms and any(term in entity_name for term in preferred_terms):
                bonus += 0.25
            if canonical_hints and any(term in entity_name for term in canonical_hints):
                bonus += 0.5
            dedup[entity_id] = {
                "canonical_id": entity_id,
                "score": score + bonus,
                "match_alias": alias,
                "entity": entity,
            }
            if len(dedup) >= limit:
                break
        return list(dedup.values())

    def get_grounding(self, canonical_ids: list[str], limit_claims: int = 6, limit_provenance: int = 6) -> dict[str, Any]:
        claims: list[dict[str, Any]] = []
        provenance: list[dict[str, Any]] = []
        for canonical_id in canonical_ids:
            claims.extend(self.claims_by_subject.get(canonical_id, [])[:limit_claims])
            provenance.extend(self.provenance_by_subject.get(canonical_id, [])[:limit_provenance])
        return {"claims": claims[:limit_claims], "provenance": provenance[:limit_provenance]}

    def stats(self) -> dict[str, int]:
        return {
            "aliases": len(self.aliases),
            "entities": len(self.entities),
            "claims": len(self.claims),
            "provenance": len(self.provenance),
            "chunks": len(self.chunks),
        }
