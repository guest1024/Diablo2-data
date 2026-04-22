from __future__ import annotations

from typing import Any
import re

from .config import settings
from .llm_client import analyze_query as analyze_query_with_llm
from .query_normalizer import QueryNormalizer


class QueryAnalyzer:
    _CONNECTOR_PATTERNS = ("和", "以及", "还是", "区别", "对比", "并且", "同时")
    _INTENT_RULES = [
        ("comparison", ("区别", "对比", "还是", "哪个好", "compare", "vs")),
        ("farming", ("哪里刷", "在哪刷", "掉什么", "掉落", "drop", "farm")),
        ("location", ("怎么走", "在哪", "哪里", "位置", "路线", "path")),
        ("crafting_base", ("底材", "base", "材料", "几孔", "多少孔", "符文", "runeword", "recipe")),
        ("usage", ("有什么用", "有啥用", "适合干什么", "用途", "作用", "used for")),
        ("build", ("练法", "build", "流派", "加点", "配装")),
        ("definition", ("是什么", "是啥", "what is")),
    ]
    _INTENT_SUFFIX_ZH = {
        "definition": "是什么",
        "farming": "掉落来源 刷取场景",
        "location": "位置 路线",
        "crafting_base": "底材 制作要求",
        "usage": "用途 适用场景",
        "build": "练法 配装",
        "comparison": "区别 对比",
        "fact_lookup": "核心事实",
    }
    _INTENT_SUFFIX_EN = {
        "definition": "what is it",
        "farming": "drop source farm location",
        "location": "location path",
        "crafting_base": "base requirement sockets",
        "usage": "usage use case",
        "build": "build gear skill setup",
        "comparison": "difference comparison",
        "fact_lookup": "key facts",
    }
    _DOMAIN_FACETS = {
        "crafting_base": [
            "Scythe",
            "Polearm",
            "Monarch",
            "Paladin Shield",
            "军团圣盾",
            "圣骑盾",
            "底材",
            "几孔",
            "4孔",
            "4 socket",
            "sockets",
            "米山",
        ],
        "farming": [
            "Mephisto",
            "Andariel",
            "Baal",
            "Diablo",
            "Countess",
            "劳模",
            "女伯爵",
            "掉落",
            "哪里刷",
            "farm",
        ],
        "location": [
            "River of Flame",
            "Lost City",
            "Catacombs Level 4",
            "Durance of Hate Level 3",
            "Tamoe Highland",
            "封印",
            "路线",
            "怎么走",
            "入口",
        ],
        "usage": [
            "Battle Orders",
            "Mercenary",
            "caster",
            "刷底材",
            "刷符文",
            "刷怪",
            "用途",
            "适合",
        ],
        "build": [
            "ES",
            "Energy Shield",
            "Memory",
            "Infinity Scythe",
            "Infinity",
            "Scythe",
            "预buff",
            "自持",
            "配装",
            "练法",
        ],
    }
    _GENERIC_FACETS = [
        "ES",
        "Memory",
        "Infinity",
        "Infinity Scythe",
        "Scythe",
        "Polearm",
        "Monarch",
        "Mephisto",
        "Andariel",
        "River of Flame",
        "Lost City",
        "Tamoe Highland",
        "Battle Orders",
        "Mercenary",
        "Hell Bovine",
        "Cow King",
        "劳模",
        "牛场",
        "古代通道",
        "封印",
        "预buff",
        "自持",
        "底材",
        "几孔",
        "刷底材",
        "刷符文",
    ]
    _DRIFT_TERMS = {
        "definition": {"底材", "几孔", "哪里刷", "掉落", "练法", "配装", "路线", "用途"},
        "crafting_base": {"哪里刷", "掉落", "练法", "配装", "路线"},
        "farming": {"底材", "几孔", "练法", "配装"},
        "location": {"底材", "几孔", "练法", "配装", "掉落"},
        "usage": {"底材", "几孔", "掉落", "路线"},
        "build": {"底材", "几孔", "掉落", "路线"},
    }

    def __init__(self, normalizer: QueryNormalizer | None = None) -> None:
        self.normalizer = normalizer or QueryNormalizer()

    def analyze(self, query: str, *, use_llm: bool = False) -> dict[str, Any]:
        base = self.normalizer.expand(query)
        normalized = str(base["normalized_query"])
        language = self._detect_language(normalized)
        intent = self._detect_intent(normalized)
        primary_surface = self._pick_primary_surface(normalized, base)
        complexity = self._detect_complexity(normalized, intent)
        salient_facets = self._extract_salient_facets(normalized, intent, primary_surface, base)
        rewritten_queries = self._build_rewritten_queries(normalized, base, primary_surface, intent, salient_facets)
        subquestions = self._build_subquestions(normalized, primary_surface, intent, complexity, salient_facets)

        analysis = {
            "original_query": query,
            "normalized_query": normalized,
            "expanded_query": base["expanded_query"],
            "language": language,
            "intent": intent,
            "complexity": complexity,
            "needs_decomposition": complexity != "simple",
            "matched_terms": list(base.get("matched_terms", [])),
            "matched_entries": list(base.get("matched_entries", [])),
            "preferred_terms": list(base.get("preferred_terms", [])),
            "canonical_hints": list(base.get("canonical_hints", [])),
            "preferred_title_contains": list(base.get("preferred_title_contains", [])),
            "preferred_text_contains": list(base.get("preferred_text_contains", [])),
            "preferred_source_ids": list(base.get("preferred_source_ids", [])),
            "discouraged_source_ids": list(base.get("discouraged_source_ids", [])),
            "entity_query": primary_surface or normalized,
            "salient_facets": salient_facets,
            "rewritten_queries": rewritten_queries,
            "subquestions": subquestions,
            "used_llm": False,
        }

        if use_llm and settings.query_analyzer_llm_enabled and self._should_use_llm(normalized, intent, complexity):
            llm_payload = self._analyze_with_llm(analysis)
            if llm_payload:
                analysis = self._merge_llm_analysis(analysis, llm_payload)

        analysis["retrieval_plan"] = self._build_retrieval_plan(analysis)
        analysis["retrieval_queries"] = [row["query"] for row in analysis["retrieval_plan"]]
        return analysis

    @staticmethod
    def _detect_language(query: str) -> str:
        has_cjk = bool(re.search(r"[\u4e00-\u9fff]", query))
        has_latin = bool(re.search(r"[A-Za-z]", query))
        if has_cjk and has_latin:
            return "mixed"
        if has_cjk:
            return "zh"
        if has_latin:
            return "en"
        return "unknown"

    def _detect_intent(self, query: str) -> str:
        lowered = query.lower()
        usage_patterns = ("有什么用", "有啥用", "适合干什么", "用途", "作用", "适合")
        crafting_hard_signals = ("几孔", "多少孔", "runeword", "符文之语", "monarch", "polearm", "scythe", "材料")
        if any(pattern in lowered for pattern in usage_patterns) and not any(signal in lowered for signal in crafting_hard_signals):
            return "usage"
        for intent, patterns in self._INTENT_RULES:
            if any(pattern in lowered for pattern in patterns):
                return intent
        return "fact_lookup"

    def _detect_complexity(self, query: str, intent: str) -> str:
        if intent == "comparison":
            return "complex"
        if any(token in query for token in self._CONNECTOR_PATTERNS):
            return "complex"
        if intent in {"farming", "location", "crafting_base", "usage", "build"}:
            return "medium"
        if len(query) >= 18:
            return "medium"
        return "simple"

    def _pick_primary_surface(self, query: str, base: dict[str, Any]) -> str:
        entries = list(base.get("matched_entries", []))
        hints = [str(value).strip() for value in base.get("canonical_hints", []) if str(value).strip()]
        if not entries:
            return hints[0] if hints else str(base.get("normalized_query", ""))

        query_l = query.lower()
        candidate_aliases: list[str] = []
        for entry in entries:
            candidate_aliases.extend(str(alias).strip() for alias in entry.get("aliases", []) if str(alias).strip())
            hint = str(entry.get("canonical_hint", "")).strip()
            if hint:
                candidate_aliases.append(hint)

        preference_rules = [
            (("盾", "shield"), lambda alias: "shield" in alias.lower()),
            (("符文之语", "runeword"), lambda alias: "runeword" in alias.lower()),
            (("戒指", "ring"), lambda alias: "ring" in alias.lower()),
            (("位置", "路线", "area", "location"), lambda alias: any(token in alias.lower() for token in ("level", "area", "sanctuary", "pit", "tunnels"))),
        ]
        for triggers, matcher in preference_rules:
            if any(trigger.lower() in query_l for trigger in triggers):
                for alias in candidate_aliases:
                    if matcher(alias):
                        return self._format_surface(alias)
        for alias in candidate_aliases:
            if " " in alias or alias.isascii():
                return self._format_surface(alias)
        return self._format_surface(hints[0]) if hints else str(base.get("normalized_query", ""))

    def _extract_salient_facets(
        self,
        normalized: str,
        intent: str,
        primary_surface: str,
        base: dict[str, Any],
    ) -> list[str]:
        query_lower = normalized.lower()
        banned = {
            primary_surface.lower(),
            *(str(item).strip().lower() for item in base.get("canonical_hints", []) if str(item).strip()),
            *(str(item).strip().lower() for item in base.get("matched_terms", []) if str(item).strip()),
        }
        facets: list[str] = []

        vocab = list(self._DOMAIN_FACETS.get(intent, [])) + self._GENERIC_FACETS
        for token in vocab:
            token_l = token.lower()
            if token_l in banned:
                continue
            if token_l in query_lower:
                self._push_facet(facets, token)
        for hint in list(base.get("preferred_text_contains", [])) + list(base.get("preferred_terms", [])):
            hint_text = " ".join(str(hint).split()).strip()
            if not hint_text:
                continue
            hint_lower = hint_text.lower()
            if hint_lower in banned:
                continue
            if any(token.lower() == hint_lower for token in vocab):
                self._push_facet(facets, self._format_surface(hint_text))

        phrase_pattern = re.compile(r"[A-Za-z][A-Za-z0-9+\-']*(?:\s+[A-Za-z0-9][A-Za-z0-9+\-']*){0,3}")
        for match in phrase_pattern.finditer(normalized):
            phrase = " ".join(match.group(0).split()).strip(" ,.?？！，、/\\")
            if not phrase or len(phrase) < 2:
                continue
            phrase_lower = phrase.lower()
            if phrase_lower in banned:
                continue
            if phrase_lower in {"what is", "is what", "build gear skill setup", "drop source farm location", "base requirement sockets", "location path", "usage use case", "buff", "prebuff"}:
                continue
            self._push_facet(facets, phrase)

        if ("4 孔" in normalized or "4孔" in normalized or "4 socket" in query_lower or "4 sockets" in query_lower):
            self._push_facet(facets, "4 socket")
        return facets[:4]

    @staticmethod
    def _push_facet(facets: list[str], value: str) -> None:
        normalized = " ".join(str(value).split()).strip()
        if not normalized:
            return
        key = normalized.lower()
        for existing in list(facets):
            existing_key = existing.lower()
            if existing_key == key or key in existing_key:
                return
            if existing_key in key:
                facets.remove(existing)
        facets.append(normalized)

    def _build_rewritten_queries(
        self,
        normalized: str,
        base: dict[str, Any],
        primary_surface: str,
        intent: str,
        salient_facets: list[str],
    ) -> list[str]:
        candidates: list[str] = [normalized]

        primary_surface = primary_surface.strip()
        if primary_surface and primary_surface.lower() not in normalized.lower():
            candidates.append(primary_surface)

        suffix_zh = self._INTENT_SUFFIX_ZH[intent]
        suffix_en = self._INTENT_SUFFIX_EN[intent]
        if primary_surface:
            candidates.append(f"{primary_surface} {suffix_en}".strip())
            facet_join = self._facet_join(primary_surface, salient_facets, zh=False)
            if facet_join:
                candidates.append(facet_join)
            facet_with_suffix = self._facet_join(primary_surface, salient_facets, zh=False, suffix=suffix_en)
            if facet_with_suffix:
                candidates.append(facet_with_suffix)
        for hint in base.get("canonical_hints", []):
            hint_text = str(hint).strip()
            if not hint_text:
                continue
            candidates.append(hint_text)
            candidates.append(f"{hint_text} {suffix_en}".strip())
        if base.get("matched_terms"):
            candidates.append(f"{base['matched_terms'][0]} {suffix_zh}".strip())
            zh_facet = self._facet_join(str(base["matched_terms"][0]).strip(), salient_facets, zh=True, suffix=suffix_zh)
            if zh_facet:
                candidates.append(zh_facet)
        allowed_terms = [primary_surface or normalized, *[str(item).strip() for item in base.get("matched_terms", []) if str(item).strip()]]
        return self._filter_query_candidates(candidates, intent=intent, anchor=primary_surface or normalized, allowed_terms=allowed_terms, limit=5)

    def _build_subquestions(
        self,
        normalized: str,
        primary_surface: str,
        intent: str,
        complexity: str,
        salient_facets: list[str],
    ) -> list[str]:
        anchor = primary_surface or normalized
        if complexity == "simple":
            return []
        if intent == "crafting_base":
            candidates = [
                f"{anchor} 是什么？",
                f"{anchor} 的常见底材或制作要求是什么？",
            ]
            facet = self._facet_subquestion(anchor, salient_facets, "crafting_base")
            if facet:
                candidates.append(facet)
            return self._filter_query_candidates(candidates, intent=intent, anchor=anchor, allowed_terms=[anchor], limit=3)
        if intent == "farming":
            candidates = [
                f"{anchor} 是什么？",
                f"{anchor} 的常见掉落来源或刷取场景是什么？",
            ]
            facet = self._facet_subquestion(anchor, salient_facets, "farming")
            if facet:
                candidates.append(facet)
            return self._filter_query_candidates(candidates, intent=intent, anchor=anchor, allowed_terms=[anchor], limit=3)
        if intent == "location":
            candidates = [
                f"{anchor} 指的是什么区域或对象？",
                f"{anchor} 的位置、前置路径或到达路线是什么？",
            ]
            facet = self._facet_subquestion(anchor, salient_facets, "location")
            if facet:
                candidates.append(facet)
            return self._filter_query_candidates(candidates, intent=intent, anchor=anchor, allowed_terms=[anchor], limit=3)
        if intent == "usage":
            candidates = [
                f"{anchor} 是什么？",
                f"{anchor} 的主要用途或适用场景是什么？",
            ]
            facet = self._facet_subquestion(anchor, salient_facets, "usage")
            if facet:
                candidates.append(facet)
            return self._filter_query_candidates(candidates, intent=intent, anchor=anchor, allowed_terms=[anchor], limit=3)
        if intent == "comparison":
            return self._filter_query_candidates(
                [
                    normalized,
                    f"{anchor} 的关键差异点是什么？",
                ],
                intent=intent,
                anchor=anchor,
                allowed_terms=[anchor],
                limit=3,
            )
        if intent == "build":
            candidates = [
                f"{anchor} 是什么流派或构筑？",
                f"{anchor} 的典型配装或加点是什么？",
            ]
            facet = self._facet_subquestion(anchor, salient_facets, "build")
            if facet:
                candidates.append(facet)
            return self._filter_query_candidates(candidates, intent=intent, anchor=anchor, allowed_terms=[anchor], limit=3)
        return self._filter_query_candidates([normalized], intent=intent, anchor=anchor, allowed_terms=[anchor, normalized], limit=2)

    def _should_use_llm(self, query: str, intent: str, complexity: str) -> bool:
        if complexity == "complex":
            return True
        if complexity == "medium" and intent in {"crafting_base", "farming", "location", "usage", "comparison", "build"}:
            return True
        return len(query) >= 20

    def _analyze_with_llm(self, analysis: dict[str, Any]) -> dict[str, Any] | None:
        prompt = (
            "请把下面的 Diablo II 查询分析成稳定检索用 JSON。\n"
            "要求：\n"
            "1. rewritten_queries 最多 4 条，必须保守、贴近原问题；\n"
            "2. rewritten_queries 和 subquestions 必须保留主实体，不要把主实体换成别的 build / boss / item；\n"
            "3. subquestions 最多 3 条，只在确有必要时输出；\n"
            "4. 不要臆造游戏事实；\n"
            "5. reasoning_summary 只用一句话。\n\n"
            f"query={analysis['original_query']}\n"
            f"normalized_query={analysis['normalized_query']}\n"
            f"intent={analysis['intent']}\n"
            f"canonical_hints={analysis['canonical_hints']}\n"
            f"matched_terms={analysis['matched_terms']}\n"
            f"salient_facets={analysis['salient_facets']}\n"
            f"rule_rewrites={analysis['rewritten_queries']}\n"
            f"rule_subquestions={analysis['subquestions']}\n"
        )
        try:
            return analyze_query_with_llm(prompt)
        except Exception:
            return None

    def _merge_llm_analysis(self, analysis: dict[str, Any], llm_payload: dict[str, Any]) -> dict[str, Any]:
        merged = dict(analysis)
        llm_intent = str(llm_payload.get("intent", "")).strip()
        if llm_intent in {rule[0] for rule in self._INTENT_RULES} | {"fact_lookup"}:
            merged["intent"] = llm_intent
        rewritten = [str(item).strip() for item in llm_payload.get("rewritten_queries", []) if str(item).strip()]
        subquestions = [str(item).strip() for item in llm_payload.get("subquestions", []) if str(item).strip()]
        anchor = str(analysis.get("entity_query") or analysis.get("normalized_query") or "").strip()
        merged["rewritten_queries"] = self._filter_query_candidates(
            list(analysis["rewritten_queries"]) + rewritten,
            intent=merged["intent"],
            anchor=anchor,
            allowed_terms=[anchor, *[str(item).strip() for item in analysis.get("matched_terms", []) if str(item).strip()]],
            limit=5,
        )
        merged["subquestions"] = self._filter_query_candidates(
            list(analysis["subquestions"]) + subquestions,
            intent=merged["intent"],
            anchor=anchor,
            allowed_terms=[anchor],
            limit=3,
        )
        merged["used_llm"] = True
        merged["llm_reasoning_summary"] = str(llm_payload.get("reasoning_summary", "")).strip()
        return merged

    def _build_retrieval_plan(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        plan: list[dict[str, Any]] = []
        original_query = str(analysis["normalized_query"]).strip()
        entity_query = str(analysis.get("entity_query", "")).strip()
        rewritten_queries = [str(item).strip() for item in analysis.get("rewritten_queries", []) if str(item).strip()]
        subquestions = [str(item).strip() for item in analysis.get("subquestions", []) if str(item).strip()]

        candidates = [
            ("original", original_query, 1.0),
            ("entity", entity_query, 1.0),
        ]
        candidates.extend((f"rewrite_{idx + 1}", query, 0.9 - idx * 0.08) for idx, query in enumerate(rewritten_queries))
        candidates.extend((f"subquestion_{idx + 1}", query, 0.72 - idx * 0.07) for idx, query in enumerate(subquestions))

        seen: set[str] = set()
        for label, query, weight in candidates:
            query = " ".join(query.split())
            if not query:
                continue
            key = query.lower()
            if key in seen:
                continue
            seen.add(key)
            plan.append({"label": label, "query": query, "weight": round(max(weight, 0.35), 2)})
            if len(plan) >= 6:
                break
        return plan

    def _filter_query_candidates(self, values: list[str], *, intent: str, anchor: str, allowed_terms: list[str], limit: int) -> list[str]:
        seen: set[str] = set()
        results: list[str] = []
        anchor_lower = anchor.lower().strip()
        allowed_keys = [str(term).strip().lower() for term in allowed_terms if str(term).strip()]
        for value in values:
            normalized = " ".join(value.split()).strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            if len(normalized) > 96:
                continue
            if anchor_lower and anchor_lower not in key and intent != "comparison":
                anchor_terms = [term.lower() for term in self._extract_anchor_terms(anchor)] + allowed_keys
                matched = any(term and term in key for term in anchor_terms)
                if not matched:
                    continue
            if intent == "definition" and any(connector in normalized for connector in self._CONNECTOR_PATTERNS):
                continue
            seen.add(key)
            results.append(normalized)
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def _extract_anchor_terms(anchor: str) -> list[str]:
        values = [" ".join(anchor.split()).strip()]
        values.extend(re.findall(r"[A-Za-z][A-Za-z0-9+\-']*(?:\s+[A-Za-z0-9][A-Za-z0-9+\-']*){0,3}", anchor))
        return [value for value in values if value]

    def _facet_join(self, anchor: str, facets: list[str], *, zh: bool, suffix: str | None = None) -> str:
        picked = [facet for facet in facets if facet.lower() not in anchor.lower()][:2]
        if not picked:
            return ""
        body = " ".join([anchor, *picked]).strip()
        if suffix:
            body = f"{body} {suffix}".strip()
        return body if not zh else body

    def _facet_subquestion(self, anchor: str, facets: list[str], intent: str) -> str:
        picked = [facet for facet in facets if facet.lower() not in anchor.lower()][:2]
        if not picked:
            return ""
        facet_text = " / ".join(picked)
        if intent == "crafting_base":
            return f"{anchor} 用 {facet_text} 做底材或孔数要求要注意什么？"
        if intent == "farming":
            return f"{anchor} 围绕 {facet_text} 的刷取或掉落线索是什么？"
        if intent == "location":
            return f"{anchor} 和 {facet_text} 相关的到达路线或入口线索是什么？"
        if intent == "usage":
            return f"{anchor} 围绕 {facet_text} 的主要用途或适用场景是什么？"
        if intent == "build":
            return f"{anchor} 在 {facet_text} 这类设定下通常怎么配装或加点？"
        return ""

    @staticmethod
    def _dedupe_texts(values: list[str], limit: int) -> list[str]:
        seen: set[str] = set()
        results: list[str] = []
        for value in values:
            normalized = " ".join(value.split()).strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            results.append(normalized)
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def _format_surface(value: str) -> str:
        text = " ".join(str(value).split()).strip()
        if not text:
            return ""
        if text.isascii() and text == text.lower():
            stopwords = {"a", "an", "and", "of", "or", "the", "to"}
            parts = text.split()
            formatted: list[str] = []
            for idx, part in enumerate(parts):
                if idx > 0 and part in stopwords:
                    formatted.append(part)
                    continue
                formatted.append(part[:1].upper() + part[1:] if part else part)
            return " ".join(formatted)
        return text
