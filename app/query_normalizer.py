from __future__ import annotations

import json
from pathlib import Path

from .config import ROOT, settings


class QueryNormalizer:
    def __init__(self, term_map_path: Path | None = None) -> None:
        self.term_map_path = term_map_path or (ROOT / settings.bilingual_term_map_path)
        self.term_map = self._load_term_map()

    def _load_term_map(self) -> dict[str, dict[str, object]]:
        if not self.term_map_path.exists():
            return {}
        data = json.loads(self.term_map_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data

    def expand(self, query: str) -> dict[str, object]:
        normalized = " ".join(query.split())
        expansions: list[str] = []
        matched_terms: list[str] = []
        preferred_terms: list[str] = []
        canonical_hints: list[str] = []
        preferred_title_contains: list[str] = []
        preferred_text_contains: list[str] = []
        preferred_source_ids: list[str] = []
        discouraged_source_ids: list[str] = []
        lowered = normalized.lower()

        for term, payload in self.term_map.items():
            if term.lower() not in lowered:
                continue
            matched_terms.append(term)
            if isinstance(payload, dict):
                canonical_hint = str(payload.get("canonical_hint", "")).strip()
                if canonical_hint and canonical_hint not in preferred_terms:
                    preferred_terms.append(canonical_hint)
                if canonical_hint and canonical_hint not in canonical_hints:
                    canonical_hints.append(canonical_hint)
                aliases = payload.get("aliases", [])
                for value in payload.get("preferred_title_contains", []) or []:
                    text = " ".join(str(value).split())
                    if text and text not in preferred_title_contains:
                        preferred_title_contains.append(text)
                for value in payload.get("preferred_text_contains", []) or []:
                    text = " ".join(str(value).split())
                    if text and text not in preferred_text_contains:
                        preferred_text_contains.append(text)
                for value in payload.get("preferred_source_ids", []) or []:
                    text = str(value).strip()
                    if text and text not in preferred_source_ids:
                        preferred_source_ids.append(text)
                for value in payload.get("discouraged_source_ids", []) or []:
                    text = str(value).strip()
                    if text and text not in discouraged_source_ids:
                        discouraged_source_ids.append(text)
            else:
                aliases = []
            for alias in aliases:
                alias = " ".join(str(alias).split())
                if alias and alias.lower() not in lowered and alias not in expansions:
                    expansions.append(alias)
                if alias and alias not in preferred_terms:
                    preferred_terms.append(alias)

        expanded_query = " ".join([normalized] + expansions).strip()
        return {
            "original_query": query,
            "normalized_query": normalized,
            "expanded_query": expanded_query,
            "matched_terms": matched_terms,
            "expansions": expansions,
            "preferred_terms": preferred_terms,
            "canonical_hints": canonical_hints,
            "preferred_title_contains": preferred_title_contains,
            "preferred_text_contains": preferred_text_contains,
            "preferred_source_ids": preferred_source_ids,
            "discouraged_source_ids": discouraged_source_ids,
        }
