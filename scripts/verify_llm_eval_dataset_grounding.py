#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_llm_eval_dataset import SEED_BY_ID

DATASET_PATH = ROOT / 'docs/tier0/evals/llm-generated-query-eval-dataset.json'
REPORT_PATHS = [
    ROOT / 'docs/tier0/evals/llm-generated-query-eval-report-retrieval-only.json',
    ROOT / 'docs/tier0/evals/llm-generated-query-eval-report-llm-assisted.json',
]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'FAIL: {message}')
    print(f'PASS: {message}')


def compact(text: object) -> str:
    return ' '.join(str(text or '').split()).strip()


def main() -> int:
    expect(DATASET_PATH.exists(), 'llm-generated dataset exists')
    payload = json.loads(DATASET_PATH.read_text(encoding='utf-8'))
    cases = list(payload.get('cases', []))
    expect(len(cases) == len(SEED_BY_ID), 'dataset case count matches seed registry')

    seen_seed_ids: set[str] = set()
    for case in cases:
        seed_id = str(case.get('seed_id', '')).strip()
        expect(seed_id in SEED_BY_ID, f'{seed_id} exists in seed registry')
        expect(seed_id not in seen_seed_ids, f'{seed_id} appears only once')
        seen_seed_ids.add(seed_id)
        seed = SEED_BY_ID[seed_id]
        query = compact(case.get('query'))
        expect(bool(query), f'{seed_id} query is non-empty')

        required_terms = [compact(item) for item in seed.get('required_query_terms_any', []) if compact(item)]
        if required_terms:
            expect(any(term.lower() in query.lower() for term in required_terms), f'{seed_id} query keeps required grounding term')

        required_phrases = [compact(item) for item in seed.get('required_phrase_any', []) if compact(item)]
        if required_phrases:
            expect(any(term.lower() in query.lower() for term in required_phrases), f'{seed_id} query keeps required phrase')

        avoid_terms = [compact(item) for item in seed.get('avoid_terms', []) if compact(item)]
        expect(not any(term.lower() in query.lower() for term in avoid_terms), f'{seed_id} query avoids forbidden drift terms')

        contexts = list(case.get('source_contexts', []))
        expect(bool(contexts), f'{seed_id} keeps source_contexts')
        expect(bool(case.get('reference_titles')), f'{seed_id} keeps reference_titles')
        expect(bool(case.get('reference_keywords')), f'{seed_id} keeps reference_keywords')
        expect(bool(case.get('reference_source_ids')), f'{seed_id} keeps reference_source_ids')

        for idx, ctx in enumerate(contexts, start=1):
            prefix = f'{seed_id} source_context[{idx}]'
            expect(str(ctx.get('dataset')) in {'curated', 'chroma'}, f'{prefix} dataset is valid')
            expect(bool(compact(ctx.get('chunk_id'))), f'{prefix} keeps chunk_id')
            expect(bool(compact(ctx.get('source_id'))), f'{prefix} keeps source_id')
            expect(bool(compact(ctx.get('title'))), f'{prefix} keeps title')
            expect(bool(compact(ctx.get('reference_excerpt'))), f'{prefix} keeps reference_excerpt')

    expect(seen_seed_ids == set(SEED_BY_ID), 'all registered seeds are present in dataset')

    for report_path in REPORT_PATHS:
        expect(report_path.exists(), f'{report_path.name} exists')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        summary = dict(report.get('summary', {}))
        passed = int(summary.get('passed', 0))
        total = int(summary.get('total', 0))
        expect(total == len(SEED_BY_ID), f'{report_path.name} total matches dataset size')
        expect(passed == total, f'{report_path.name} is fully green')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
