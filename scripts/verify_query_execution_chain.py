#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def main() -> int:
    service = Diablo2QAService()
    cases = [
        ('劳模掉不掉军帽？', 'fact_lookup', False),
        ('我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？', 'numeric_reasoning', True),
        ('我想玩锤丁，谜团底材去哪里刷最高效？', 'multi_hop_strategy', True),
    ]
    for query, expected_type, expect_subplan in cases:
        body = service.answer(query, use_llm=False)
        trace = body['retrieval_trace']
        expect(trace['query_type'] == expected_type, f'query type detected for {query}')
        expect(bool(trace['accepted_rewrite']['rewrite_text']), f'accepted rewrite exists for {query}')
        expect(bool(trace['rewrite_candidates']), f'rewrite candidates exist for {query}')
        expect(bool(body['chunks']), f'chunks retrieved for {query}')
        expect(bool(body['resolved_entities']), f'entities resolved for {query}')
        expect(bool(body['structured_support']), f'structured support found for {query}')
        expect(bool(trace['subquestion_plan']) == expect_subplan, f'subquestion expectation matches for {query}')
    print(json.dumps({'verified_cases': len(cases)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
