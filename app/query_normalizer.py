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

    @staticmethod
    def _clean_text(value: object) -> str:
        return " ".join(str(value).split()).strip()

    @classmethod
    def _normalized_texts(cls, values: list[object]) -> list[str]:
        return [text for text in (cls._clean_text(value) for value in values) if text]

    @staticmethod
    def _extend_unique(target: list[str], values: list[str]) -> None:
        for value in values:
            if value not in target:
                target.append(value)

    @staticmethod
    def _matched_term_payloads(
        lowered_query: str,
        term_map: dict[str, dict[str, object]],
    ) -> list[tuple[str, dict[str, object] | object]]:
        candidates: list[tuple[int, int, str, dict[str, object] | object]] = []
        for term, payload in term_map.items():
            index = lowered_query.find(term.lower())
            if index < 0:
                continue
            candidates.append((index, len(term), term, payload))

        selected: list[tuple[int, int, str, dict[str, object] | object]] = []
        for index, length, term, payload in sorted(candidates, key=lambda row: (-row[1], row[0], row[2])):
            lowered_term = term.lower()
            if any(lowered_term in existing_term.lower() for _, _, existing_term, _ in selected):
                continue
            selected.append((index, length, term, payload))

        selected.sort(key=lambda row: (row[0], -row[1], row[2]))
        return [(term, payload) for _, _, term, payload in selected]

    def expand(self, query: str) -> dict[str, object]:
        normalized = self._clean_text(query)
        expansions: list[str] = []
        matched_terms: list[str] = []
        matched_entries: list[dict[str, object]] = []
        preferred_terms: list[str] = []
        canonical_hints: list[str] = []
        preferred_title_contains: list[str] = []
        preferred_text_contains: list[str] = []
        preferred_source_ids: list[str] = []
        discouraged_source_ids: list[str] = []
        lowered = normalized.lower()

        for term, payload in self._matched_term_payloads(lowered, self.term_map):
            matched_terms.append(term)
            aliases: list[str] = []
            if isinstance(payload, dict):
                canonical_hint = self._clean_text(payload.get("canonical_hint", ""))
                aliases = self._normalized_texts(list(payload.get("aliases", []) or []))
                raw_preferred_title_contains = self._normalized_texts(list(payload.get("preferred_title_contains", []) or []))
                raw_preferred_text_contains = self._normalized_texts(list(payload.get("preferred_text_contains", []) or []))
                raw_preferred_source_ids = self._normalized_texts(list(payload.get("preferred_source_ids", []) or []))
                raw_discouraged_source_ids = self._normalized_texts(list(payload.get("discouraged_source_ids", []) or []))

                matched_entries.append(
                    {
                        "term": term,
                        "canonical_hint": canonical_hint,
                        "aliases": aliases,
                        "preferred_title_contains": raw_preferred_title_contains,
                        "preferred_text_contains": raw_preferred_text_contains,
                        "preferred_source_ids": raw_preferred_source_ids,
                        "discouraged_source_ids": raw_discouraged_source_ids,
                    }
                )
                self._extend_unique(preferred_terms, [canonical_hint] if canonical_hint else [])
                self._extend_unique(canonical_hints, [canonical_hint] if canonical_hint else [])
                if (
                    canonical_hint
                    and not any("curated anchor card" in value.lower() for value in raw_preferred_title_contains)
                ):
                    self._extend_unique(preferred_title_contains, [canonical_hint])
                self._extend_unique(preferred_title_contains, raw_preferred_title_contains)
                self._extend_unique(preferred_text_contains, raw_preferred_text_contains)
                self._extend_unique(preferred_source_ids, raw_preferred_source_ids)
                self._extend_unique(discouraged_source_ids, raw_discouraged_source_ids)

            for alias in aliases:
                if alias and alias.lower() not in lowered and alias not in expansions:
                    expansions.append(alias)
            self._extend_unique(preferred_terms, aliases)

        expanded_query = " ".join([normalized] + expansions).strip()
        return {
            "original_query": query,
            "normalized_query": normalized,
            "expanded_query": expanded_query,
            "matched_terms": matched_terms,
            "matched_entries": matched_entries,
            "expansions": expansions,
            "preferred_terms": preferred_terms,
            "canonical_hints": canonical_hints,
            "preferred_title_contains": preferred_title_contains,
            "preferred_text_contains": preferred_text_contains,
            "preferred_source_ids": preferred_source_ids,
            "discouraged_source_ids": discouraged_source_ids,
        }
