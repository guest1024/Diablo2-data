from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .config import ROOT
from .jsonl import load_jsonl
from .query_normalizer import QueryNormalizer


def load_tsv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t", quotechar='"')
        rows = []
        for row in reader:
            rows.append(row)
    return rows


class QueryUnderstandingEngine:
    _QUERY_TYPE_KEYWORDS = {
        "numeric_reasoning": ["fcr", "fhr", "fbr", "档位", "%", "变量", "能上一个档", "breakpoint"],
        "multi_hop_strategy": ["最高效", "怎么刷", "去哪里", "底材", "核心装备", "build", "路线", "开荒"],
        "fact_lookup": ["是什么", "掉不掉", "在哪", "谁掉", "用途", "作用"],
    }

    def __init__(self) -> None:
        self.normalizer = QueryNormalizer()
        self.term_dictionary = self._load_term_dictionary()
        self.alias_dictionary = self._load_alias_dictionary()
        self.query_patterns = self._load_query_patterns()
        self.retrieval_policies = self._load_retrieval_policies()
        self.answer_constraints = self._load_answer_constraints()
        self.structured = self._load_structured_support()

    @staticmethod
    def _bundle_dir() -> Path:
        return ROOT / "docs/tier0/postgres-dict-bundle/data"

    def _load_term_dictionary(self) -> dict[str, dict[str, Any]]:
        path = self._bundle_dir() / "term_dictionary.tsv"
        columns = [
            "term_id",
            "canonical_term",
            "canonical_term_zh",
            "term_type",
            "domain",
            "language",
            "description",
            "source",
            "confidence",
            "active",
            "metadata",
        ]
        items: dict[str, dict[str, Any]] = {}
        for row in load_tsv(path):
            if not row:
                continue
            obj = {key: (None if value == "\\N" else value) for key, value in zip(columns, row)}
            metadata = json.loads(obj["metadata"] or "{}")
            obj["metadata"] = metadata
            items[str(obj["term_id"])] = obj
        return items

    def _load_alias_dictionary(self) -> list[dict[str, Any]]:
        path = self._bundle_dir() / "alias_dictionary.tsv"
        columns = [
            "alias_id",
            "term_id",
            "canonical_term",
            "alias",
            "alias_class",
            "language",
            "community_frequency",
            "confidence",
            "source",
            "active",
            "rewrite_priority",
            "metadata",
        ]
        rows: list[dict[str, Any]] = []
        for row in load_tsv(path):
            if not row:
                continue
            obj = {key: (None if value == "\\N" else value) for key, value in zip(columns, row)}
            obj["metadata"] = json.loads(obj["metadata"] or "{}")
            obj["rewrite_priority"] = int(obj["rewrite_priority"] or 100)
            obj["confidence"] = float(obj["confidence"] or 0.0)
            rows.append(obj)
        return rows

    def _load_query_patterns(self) -> list[dict[str, Any]]:
        path = self._bundle_dir() / "query_pattern_dictionary.tsv"
        columns = [
            "pattern_id",
            "query_type",
            "trigger_phrase",
            "intent_label",
            "expansion_policy",
            "requires_subquestions",
            "requires_numeric_guard",
            "requires_citation_verification",
            "lane_hints",
            "source",
            "active",
            "metadata",
        ]
        rows: list[dict[str, Any]] = []
        for row in load_tsv(path):
            if not row:
                continue
            obj = {key: (None if value == "\\N" else value) for key, value in zip(columns, row)}
            obj["lane_hints"] = json.loads(obj["lane_hints"] or "[]")
            obj["metadata"] = json.loads(obj["metadata"] or "{}")
            obj["requires_subquestions"] = str(obj["requires_subquestions"]).lower() == "true"
            obj["requires_numeric_guard"] = str(obj["requires_numeric_guard"]).lower() == "true"
            obj["requires_citation_verification"] = str(obj["requires_citation_verification"]).lower() == "true"
            rows.append(obj)
        return rows

    def _load_retrieval_policies(self) -> dict[str, dict[str, Any]]:
        path = self._bundle_dir() / "retrieval_policies.tsv"
        columns = [
            "policy_id",
            "policy_name",
            "query_type",
            "min_alias_lane",
            "min_bm25_lane",
            "min_vector_lane",
            "min_graph_lane",
            "require_authority_rerank",
            "require_numeric_grounding",
            "require_citation_verification",
            "metadata",
        ]
        items: dict[str, dict[str, Any]] = {}
        for row in load_tsv(path):
            if not row:
                continue
            obj = {key: (None if value == "\\N" else value) for key, value in zip(columns, row)}
            for key in ("min_alias_lane", "min_bm25_lane", "min_vector_lane", "min_graph_lane"):
                obj[key] = int(obj[key] or 0)
            for key in ("require_authority_rerank", "require_numeric_grounding", "require_citation_verification"):
                obj[key] = str(obj[key]).lower() == "true"
            obj["metadata"] = json.loads(obj["metadata"] or "{}")
            items[str(obj["query_type"])] = obj
        return items

    def _load_answer_constraints(self) -> dict[str, dict[str, Any]]:
        path = self._bundle_dir() / "answer_constraints.tsv"
        columns = [
            "constraint_id",
            "query_type",
            "must_quote_sources",
            "must_verify_numeric_claims",
            "must_disclose_conflicts",
            "forbid_uncited_facts",
            "forbid_linear_interpolation_without_rule",
            "metadata",
        ]
        items: dict[str, dict[str, Any]] = {}
        for row in load_tsv(path):
            if not row:
                continue
            obj = {key: (None if value == "\\N" else value) for key, value in zip(columns, row)}
            for key in (
                "must_quote_sources",
                "must_verify_numeric_claims",
                "must_disclose_conflicts",
                "forbid_uncited_facts",
                "forbid_linear_interpolation_without_rule",
            ):
                obj[key] = str(obj[key]).lower() == "true"
            obj["metadata"] = json.loads(obj["metadata"] or "{}")
            items[str(obj["query_type"])] = obj
        return items

    def _load_structured_support(self) -> dict[str, list[dict[str, Any]]]:
        base = ROOT / "docs/tier0/structured"
        files = {
            "breakpoints": "breakpoints.jsonl",
            "runewords": "runewords.jsonl",
            "base_items": "base-items.jsonl",
            "skills": "skills.jsonl",
            "areas": "areas.jsonl",
            "unique_items": "unique-items.jsonl",
            "monster_resistances": "monster-resistances.jsonl",
        }
        return {key: load_jsonl(base / filename) for key, filename in files.items() if (base / filename).exists()}

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.split())

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        lowered = query.lower()
        ascii_terms = [token for token in re.split(r"[^a-z0-9]+", lowered) if len(token) >= 2]
        cjk_terms = [seq for seq in re.findall(r"[\u4e00-\u9fff]{2,}", query) if len(seq) >= 2]
        return ascii_terms + cjk_terms

    @staticmethod
    def _trigram_similarity(left: str, right: str) -> float:
        def grams(text: str) -> set[str]:
            text = f"  {text.lower()}  "
            if len(text) < 3:
                return {text}
            return {text[idx : idx + 3] for idx in range(len(text) - 2)}

        left_set = grams(left)
        right_set = grams(right)
        if not left_set or not right_set:
            return 0.0
        intersection = len(left_set & right_set)
        return (2.0 * intersection) / (len(left_set) + len(right_set))

    def _detect_query_type(self, normalized_query: str, matched_patterns: list[dict[str, Any]]) -> tuple[str, str]:
        if matched_patterns:
            best = max(matched_patterns, key=lambda row: row.get("score", 0.0))
            return str(best["query_type"]), str(best["intent_label"])

        lowered = normalized_query.lower()
        if any(token in lowered for token in self._QUERY_TYPE_KEYWORDS["numeric_reasoning"]):
            return "numeric_reasoning", "numeric_guarded"
        if any(token in normalized_query for token in ["怎么刷", "最高效", "去哪里", "底材", "核心装备"]):
            return "multi_hop_strategy", "graph_strategy"
        return "fact_lookup", "default_fact"

    def _match_patterns(self, normalized_query: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        lowered = normalized_query.lower()
        terms = set(self._query_terms(normalized_query))
        for pattern in self.query_patterns:
            phrase = str(pattern.get("trigger_phrase") or "")
            phrase_terms = set(self._query_terms(phrase))
            overlap = len(terms & phrase_terms)
            substring_hits = sum(1 for token in phrase_terms if token and token in lowered)
            score = overlap + substring_hits * 0.5
            if score > 0:
                result = dict(pattern)
                result["score"] = round(score, 4)
                results.append(result)
        results.sort(key=lambda row: row.get("score", 0.0), reverse=True)
        return results

    def _match_aliases(self, normalized_query: str, base_context: dict[str, Any]) -> list[dict[str, Any]]:
        lowered = normalized_query.lower()
        results: dict[tuple[str, str], dict[str, Any]] = {}

        for row in self.alias_dictionary:
            alias = str(row.get("alias") or "").strip()
            if not alias:
                continue
            alias_lower = alias.lower()
            match_type = None
            score = 0.0
            if alias_lower in lowered:
                match_type = "substring_exact"
                score = 1.0
            elif lowered in alias_lower and len(lowered) >= 3:
                match_type = "reverse_contains"
                score = 0.72
            else:
                trigram = self._trigram_similarity(alias_lower, lowered)
                if trigram >= 0.28:
                    match_type = "trigram_fuzzy"
                    score = trigram
            if match_type is None:
                continue
            key = (str(row.get("canonical_term")), alias)
            existing = results.get(key)
            candidate = {
                **row,
                "match_type": match_type,
                "score": round(score + float(row.get("confidence") or 0.0) * 0.1, 4),
            }
            if existing is None or candidate["score"] > existing["score"]:
                results[key] = candidate

        for term in base_context.get("matched_terms", []):
            payload = self.normalizer.term_map.get(term, {})
            canonical = str(payload.get("canonical_hint") or term).strip()
            if not canonical:
                continue
            key = (canonical, term)
            results[key] = {
                "alias_id": f"term-map::{term}",
                "term_id": None,
                "canonical_term": canonical,
                "alias": term,
                "alias_class": "term_map_key",
                "language": "mixed",
                "community_frequency": None,
                "confidence": 0.99,
                "source": "bilingual-term-map",
                "active": True,
                "rewrite_priority": 5,
                "metadata": {"origin": "query_normalizer"},
                "match_type": "term_map_exact",
                "score": 1.05,
            }

        matched = list(results.values())
        matched.sort(key=lambda row: (row.get("rewrite_priority", 100), -row.get("score", 0.0), row.get("alias", "")))
        return matched[:20]

    def _build_rewrites(
        self,
        query: str,
        normalized_query: str,
        base_context: dict[str, Any],
        alias_matches: list[dict[str, Any]],
        query_type: str,
        matched_patterns: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        rewrites: list[dict[str, Any]] = []
        source_bias = {
            "preferred_title_contains": list(base_context.get("preferred_title_contains", [])),
            "preferred_text_contains": list(base_context.get("preferred_text_contains", [])),
            "preferred_source_ids": list(base_context.get("preferred_source_ids", [])),
            "discouraged_source_ids": list(base_context.get("discouraged_source_ids", [])),
        }

        identity_terms = [
            {"term_text": normalized_query, "term_role": "original", "source_table": "input", "source_key": "query", "confidence": 1.0}
        ]
        rewrites.append(
            {
                "rewrite_text": str(base_context.get("expanded_query") or normalized_query),
                "rewrite_kind": "identity",
                "rewrite_rank": 1,
                "accepted": True,
                "confidence": 0.95,
                "recall_expectation": 0.70,
                "precision_expectation": 0.85,
                "rationale": "Original normalized query with term-map expansions retained.",
                "terms": identity_terms,
                **source_bias,
            }
        )

        canonical_terms: list[str] = []
        canonical_term_entries: list[dict[str, Any]] = []
        for match in alias_matches:
            canonical = str(match.get("canonical_term") or "").strip()
            if not canonical:
                continue
            if canonical not in canonical_terms:
                canonical_terms.append(canonical)
                canonical_term_entries.append(
                    {
                        "term_text": canonical,
                        "term_role": "canonical",
                        "source_table": "dict.alias_dictionary",
                        "source_key": match.get("alias_id"),
                        "confidence": match.get("confidence"),
                    }
                )
        if canonical_terms:
            rewrite_text = " ".join([normalized_query] + canonical_terms)
            rewrites.append(
                {
                    "rewrite_text": rewrite_text,
                    "rewrite_kind": "alias_normalized",
                    "rewrite_rank": 2,
                    "accepted": True,
                    "confidence": min(0.99, 0.78 + len(canonical_terms) * 0.03),
                    "recall_expectation": 0.88,
                    "precision_expectation": 0.82,
                    "rationale": "Adds canonical entities resolved from alias/blackword matches.",
                    "terms": canonical_term_entries,
                    **source_bias,
                }
            )

        constraint_terms: list[dict[str, Any]] = []
        constraint_texts: list[str] = []
        if query_type == "numeric_reasoning":
            constraint_texts.extend(["breakpoint table", "rule lookup", "exact numeric evidence"])
            constraint_terms.extend(
                [
                    {"term_text": "breakpoint table", "term_role": "constraint", "source_table": "dict.rule_dictionary", "source_key": "breakpoint", "confidence": 0.95},
                    {"term_text": "exact numeric evidence", "term_role": "constraint", "source_table": "dict.rule_dictionary", "source_key": "numeric_guard", "confidence": 0.95},
                ]
            )
        elif query_type == "multi_hop_strategy":
            constraint_texts.extend(["build core gear", "base item", "farm area"])
            constraint_terms.extend(
                [
                    {"term_text": "build core gear", "term_role": "constraint", "source_table": "dict.build_dictionary", "source_key": "build", "confidence": 0.9},
                    {"term_text": "farm area", "term_role": "constraint", "source_table": "dict.area_dictionary", "source_key": "area", "confidence": 0.9},
                ]
            )
        if constraint_texts:
            rewrites.append(
                {
                    "rewrite_text": " ".join([normalized_query] + canonical_terms + constraint_texts),
                    "rewrite_kind": "entity_targeted",
                    "rewrite_rank": 3,
                    "accepted": True,
                    "confidence": 0.84,
                    "recall_expectation": 0.83,
                    "precision_expectation": 0.9,
                    "rationale": "Injects query-type constraints to bias retrieval toward exact evidence lanes.",
                    "terms": canonical_term_entries + constraint_terms,
                    **source_bias,
                }
            )

        if matched_patterns and any(pattern.get("requires_subquestions") for pattern in matched_patterns):
            rewrites.append(
                {
                    "rewrite_text": normalized_query,
                    "rewrite_kind": "subquestion_seed",
                    "rewrite_rank": len(rewrites) + 1,
                    "accepted": True,
                    "confidence": 0.8,
                    "recall_expectation": 0.76,
                    "precision_expectation": 0.88,
                    "rationale": "Preserves the original query as a seed for subquestion planning.",
                    "terms": canonical_term_entries,
                    **source_bias,
                }
            )

        accepted = max(rewrites, key=lambda row: (row.get("accepted", False), row.get("confidence", 0.0), row.get("precision_expectation", 0.0)))
        return rewrites, accepted

    def _build_subquestion_plan(
        self,
        query: str,
        query_type: str,
        matched_aliases: list[dict[str, Any]],
        accepted_rewrite: dict[str, Any],
        matched_patterns: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        requires_subquestions = query_type in {"numeric_reasoning", "multi_hop_strategy"} or any(
            pattern.get("requires_subquestions") for pattern in matched_patterns
        )
        if not requires_subquestions:
            return None

        canonicals = [str(row.get("canonical_term")) for row in matched_aliases[:4] if row.get("canonical_term")]
        steps: list[dict[str, Any]] = []
        if query_type == "numeric_reasoning":
            focus = canonicals[:2] or [query]
            steps = [
                {
                    "step_order": 1,
                    "subquestion_text": f"识别数值问题涉及的主体、职业或物品：{', '.join(focus)}",
                    "expected_answer_type": "entity_resolution",
                    "required_lane": "alias",
                    "dependency_steps": [],
                },
                {
                    "step_order": 2,
                    "subquestion_text": "检索对应的 breakpoint / numeric rule table。",
                    "expected_answer_type": "rule_lookup",
                    "required_lane": "numeric_table",
                    "dependency_steps": [1],
                },
                {
                    "step_order": 3,
                    "subquestion_text": "检索变量来源（装备词条、runeword roll、技能变量等）。",
                    "expected_answer_type": "structured_fact",
                    "required_lane": "rule_lookup",
                    "dependency_steps": [1],
                },
                {
                    "step_order": 4,
                    "subquestion_text": "根据表与变量做精确比较，不允许无规则插值。",
                    "expected_answer_type": "numeric_conclusion",
                    "required_lane": "graph",
                    "dependency_steps": [2, 3],
                },
            ]
        else:
            focus = canonicals[:3] or [query]
            steps = [
                {
                    "step_order": 1,
                    "subquestion_text": f"识别 build / 装备 / 场景主体：{', '.join(focus)}",
                    "expected_answer_type": "entity_resolution",
                    "required_lane": "alias",
                    "dependency_steps": [],
                },
                {
                    "step_order": 2,
                    "subquestion_text": "从 build 或核心装备出发，展开相关技能、底材、区域关系。",
                    "expected_answer_type": "graph_expansion",
                    "required_lane": "graph",
                    "dependency_steps": [1],
                },
                {
                    "step_order": 3,
                    "subquestion_text": "补充文本证据与场景效率说明。",
                    "expected_answer_type": "evidence_chunks",
                    "required_lane": "bm25",
                    "dependency_steps": [2],
                },
                {
                    "step_order": 4,
                    "subquestion_text": "合并图关系与证据文本，给出路径型结论。",
                    "expected_answer_type": "strategy_answer",
                    "required_lane": "vector",
                    "dependency_steps": [2, 3],
                },
            ]
        return {
            "plan_title": f"{query_type}::{self._normalize(query)[:80]}",
            "requires_graph_expansion": query_type == "multi_hop_strategy",
            "requires_numeric_lookup": query_type == "numeric_reasoning",
            "requires_citation_verification": True,
            "steps": steps,
            "seed_rewrite": accepted_rewrite.get("rewrite_text"),
        }

    def _select_policy(self, query_type: str) -> dict[str, Any]:
        return self.retrieval_policies.get(query_type) or self.retrieval_policies.get("fact_lookup") or {
            "policy_id": "policy::fallback",
            "policy_name": "Fallback Policy",
            "query_type": query_type,
            "min_alias_lane": 6,
            "min_bm25_lane": 8,
            "min_vector_lane": 8,
            "min_graph_lane": 4,
            "require_authority_rerank": True,
            "require_numeric_grounding": query_type == "numeric_reasoning",
            "require_citation_verification": True,
            "metadata": {"fusion_strategy": "rrf"},
        }

    def _build_retrieval_plan(self, query_type: str, policy: dict[str, Any], matched_patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
        lanes = [
            {"lane_name": "alias", "lane_priority": 1, "enabled": True, "target_k": int(policy["min_alias_lane"]), "hard_filter": {}, "metadata": {}},
            {"lane_name": "bm25", "lane_priority": 2, "enabled": True, "target_k": int(policy["min_bm25_lane"]), "hard_filter": {}, "metadata": {}},
            {"lane_name": "vector", "lane_priority": 3, "enabled": True, "target_k": int(policy["min_vector_lane"]), "hard_filter": {}, "metadata": {}},
            {"lane_name": "graph", "lane_priority": 4, "enabled": True, "target_k": int(policy["min_graph_lane"]), "hard_filter": {}, "metadata": {}},
        ]
        if query_type == "numeric_reasoning":
            lanes.append({"lane_name": "rule_lookup", "lane_priority": 2, "enabled": True, "target_k": 8, "hard_filter": {"rule_type": "numeric"}, "metadata": {"reason": "numeric_guard"}})
            lanes.append({"lane_name": "numeric_table", "lane_priority": 2, "enabled": True, "target_k": 6, "hard_filter": {"table_type": "breakpoint"}, "metadata": {"reason": "table_lookup"}})
        if query_type == "multi_hop_strategy":
            for lane in lanes:
                if lane["lane_name"] == "graph":
                    lane["target_k"] = max(lane["target_k"], 8)
                    lane["metadata"] = {"reason": "multi_hop_required"}
        lane_hints = []
        for pattern in matched_patterns:
            lane_hints.extend(pattern.get("lane_hints", []))
        if lane_hints:
            for lane in lanes:
                if lane["lane_name"] in lane_hints:
                    lane["target_k"] += 2
                    lane.setdefault("metadata", {})["hint_boosted"] = True
        lanes.sort(key=lambda row: (row["lane_priority"], row["lane_name"]))
        return lanes

    def _select_answer_constraints(self, query_type: str) -> dict[str, Any]:
        return self.answer_constraints.get(query_type) or self.answer_constraints.get("default") or {
            "constraint_id": "constraint::fallback",
            "query_type": query_type,
            "must_quote_sources": True,
            "must_verify_numeric_claims": True,
            "must_disclose_conflicts": True,
            "forbid_uncited_facts": True,
            "forbid_linear_interpolation_without_rule": True,
            "metadata": {},
        }

    @staticmethod
    def _class_hints_from_query(query: str) -> list[str]:
        lowered = query.lower()
        hints = []
        mapping = {
            'sorceress': ['法师', 'sorceress', 'sorc'],
            'paladin': ['圣骑士', 'paladin', '锤丁', 'hammerdin'],
            'amazon': ['亚马逊', 'amazon', '标马', '弓马', 'javazon', 'bowazon'],
            'necromancer': ['死灵', 'necromancer', '召唤死灵'],
            'assassin': ['刺客', 'assassin', '陷阱刺客', 'trapsin'],
            'druid': ['德鲁伊', 'druid', '狼德'],
            'barbarian': ['野蛮人', 'barbarian', 'barb'],
        }
        for label, terms in mapping.items():
            if any(term in lowered or term in query for term in terms):
                hints.append(label)
        return hints

    def _lookup_structured_support(self, query: str, query_type: str, alias_matches: list[dict[str, Any]]) -> dict[str, Any]:
        canonical_terms = [str(row.get("canonical_term") or "") for row in alias_matches if row.get("canonical_term")]
        lowered = query.lower()
        support: dict[str, Any] = {
            "breakpoints": [],
            "runewords": [],
            "base_items": [],
            "skills": [],
            "areas": [],
            "unique_items": [],
            "monster_resistances": [],
            "rules": [],
        }

        def name_matches(name: str) -> bool:
            name_lower = name.lower()
            return name_lower in lowered or any(term.lower() == name_lower or term.lower() in name_lower for term in canonical_terms)

        if query_type == "numeric_reasoning":
            class_hints = self._class_hints_from_query(query)
            for row in self.structured.get("breakpoints", []):
                entity_name = str(row.get("entity", ""))
                entity_lower = entity_name.lower()
                category_lower = str(row.get("category", "")).lower()
                class_match = not class_hints or any(hint in entity_lower for hint in class_hints)
                if class_match and (name_matches(entity_name) or any(token in lowered for token in [category_lower, "fcr", "fhr", "fbr", "档位"])):
                    support["breakpoints"].append(row)
            if class_hints and not support["breakpoints"]:
                for row in self.structured.get("breakpoints", []):
                    entity_lower = str(row.get("entity", "")).lower()
                    if any(hint in entity_lower for hint in class_hints):
                        support["breakpoints"].append(row)
            for row in self.structured.get("runewords", []):
                if name_matches(str(row.get("name", ""))):
                    support["runewords"].append(row)
        if query_type == "multi_hop_strategy":
            for key in ("runewords", "base_items", "areas", "skills"):
                for row in self.structured.get(key, []):
                    name = str(row.get("name") or row.get("entity") or "")
                    if name and name_matches(name):
                        support[key].append(row)

            # Heuristic: derive likely Enigma body-armor bases and common farm areas.
            runeword_names = {str(row.get("name", "")) for row in support.get("runewords", [])}
            if 'Enigma' in runeword_names or any('谜团' in term for term in canonical_terms):
                base_candidates = []
                for row in self.structured.get('base_items', []):
                    if row.get('item_type') != 'tors':
                        continue
                    sockets = int(row.get('max_sockets') or 0)
                    req_str = int(row.get('required_strength') or 9999)
                    if sockets < 3:
                        continue
                    if int(row.get('level') or 0) < 55:
                        continue
                    priority_name = str(row.get('name', ''))
                    priority_bonus = 0
                    if priority_name == 'Mage Plate':
                        priority_bonus = 100
                    elif priority_name == 'Dusk Shroud':
                        priority_bonus = 80
                    elif priority_name == 'Archon Plate':
                        priority_bonus = 60
                    score = priority_bonus - req_str - abs(sockets - 3) * 20
                    enriched = dict(row)
                    enriched['heuristic_reason'] = 'enigma_base_candidate'
                    enriched['heuristic_score'] = score
                    base_candidates.append(enriched)
                base_candidates.sort(key=lambda r: (-int(r.get('heuristic_score', 0)), int(r.get('required_strength') or 9999), str(r.get('name', ''))))
                support['base_items'].extend(base_candidates[:4])

                area_candidates = []
                preferred_names = {'Pit Level 1', 'Pit Level 2', 'Ancient Tunnels', 'The Secret Cow Level'}
                for row in self.structured.get('areas', []):
                    name = str(row.get('name', ''))
                    if name not in preferred_names:
                        continue
                    enriched = dict(row)
                    enriched['heuristic_reason'] = 'high_value_base_farm_area'
                    area_candidates.append(enriched)
                area_candidates.sort(key=lambda r: (-int(r.get('monster_density_hell') or 0), -int(r.get('level_hell') or 0), str(r.get('name', ''))))
                support['areas'].extend(area_candidates[:4])
        if query_type == "fact_lookup":
            for key in ("unique_items", "runewords", "areas", "monster_resistances", "skills"):
                for row in self.structured.get(key, []):
                    name = str(row.get("name") or row.get("entity") or "")
                    if name and name_matches(name):
                        support[key].append(row)

        if any(token in lowered for token in ["fcr", "fhr", "fbr", "档位"]):
            support["rules"].append({"rule_type": "numeric_guard", "message": "Must use exact breakpoint table lookup; no interpolation."})
        return {key: value[:6] for key, value in support.items() if value}

    def analyze(self, query: str) -> dict[str, Any]:
        base_context = self.normalizer.expand(query)
        normalized_query = str(base_context["normalized_query"])
        matched_patterns = self._match_patterns(normalized_query)
        query_type, intent_label = self._detect_query_type(normalized_query, matched_patterns)
        alias_matches = self._match_aliases(normalized_query, base_context)
        rewrites, accepted = self._build_rewrites(query, normalized_query, base_context, alias_matches, query_type, matched_patterns)
        subquestion_plan = self._build_subquestion_plan(query, query_type, alias_matches, accepted, matched_patterns)
        policy = self._select_policy(query_type)
        retrieval_plan = self._build_retrieval_plan(query_type, policy, matched_patterns)
        answer_constraints = self._select_answer_constraints(query_type)
        structured_support = self._lookup_structured_support(query, query_type, alias_matches)

        preferred_terms = list(dict.fromkeys(list(base_context.get("preferred_terms", [])) + [str(row.get("canonical_term")) for row in alias_matches if row.get("canonical_term")]))
        canonical_hints = list(dict.fromkeys(list(base_context.get("canonical_hints", [])) + [str(row.get("canonical_term")) for row in alias_matches[:4] if row.get("canonical_term")]))

        return {
            **base_context,
            "query_type": query_type,
            "intent_label": intent_label,
            "matched_patterns": matched_patterns,
            "matched_aliases": alias_matches,
            "rewrite_candidates": rewrites,
            "accepted_rewrite": accepted,
            "subquestion_plan": subquestion_plan,
            "retrieval_policy": policy,
            "retrieval_plan": retrieval_plan,
            "answer_constraints": answer_constraints,
            "structured_support": structured_support,
            "preferred_terms": preferred_terms,
            "canonical_hints": canonical_hints,
            "expanded_query": accepted.get("rewrite_text") or base_context.get("expanded_query") or normalized_query,
        }
