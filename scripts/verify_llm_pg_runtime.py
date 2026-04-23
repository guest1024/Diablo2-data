#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService

CASES = [
    ('我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？', ['105', 'Spirit']),
    ('我想玩锤丁，谜团底材去哪里刷最高效？', ['Mage Plate', 'Enigma']),
    ('地狱劳模火抗多少？', ['Mephisto', '75']),
]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def main() -> int:
    service = Diablo2QAService()
    for query, expected_markers in CASES:
        body = service.answer(query, use_llm=True)
        answer = body.get('answer') or ''
        expect(body.get('retrieval_backend') in {'postgres-hybrid', 'postgres-bm25', 'postgres-lexical', 'postgres-vector'}, f'LLM path uses postgres-backed retrieval for {query}')
        expect(bool(body.get('reason_summary')), f'reason_summary exists for {query}')
        expect(bool(answer.strip()), f'LLM answer exists for {query}')
        for marker in expected_markers:
            expect(marker.lower() in answer.lower(), f'LLM answer mentions {marker} for {query}')
    print(json.dumps({'verified_cases': len(CASES)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
