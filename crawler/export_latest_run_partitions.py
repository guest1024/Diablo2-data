#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
STATE_DIR = CURRENT_DIR / 'state'
LATEST_RUN_PATH = STATE_DIR / 'latest-run.json'
OUT_DIR = STATE_DIR / 'latest-run'
INDEX_PATH = OUT_DIR / 'index.json'


def build_payload() -> dict:
    if not LATEST_RUN_PATH.is_file():
        return {'summary': None, 'sources': []}
    payload = json.loads(LATEST_RUN_PATH.read_text(encoding='utf-8'))
    summary = {
        'generated_at': payload.get('generated_at'),
        'run_id': payload.get('run_id'),
        'run_dir': payload.get('run_dir'),
        'probe_only': payload.get('probe_only'),
        'refresh_existing': payload.get('refresh_existing'),
        'config_path': payload.get('config_path'),
        'version': payload.get('version'),
        'page_snapshot_count': payload.get('page_snapshot_count'),
    }
    return {'summary': summary, 'sources': list(payload.get('sources', []))}


def main() -> int:
    payload = build_payload()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    partitions: list[str] = []
    for source in payload['sources']:
        source_id = source['id']
        path = OUT_DIR / f'{source_id}.json'
        path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        partitions.append(str(path.relative_to(CURRENT_DIR)))
    summary_path = OUT_DIR / 'summary.json'
    summary_path.write_text(json.dumps(payload['summary'], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    index = {
        'summary': str(summary_path.relative_to(CURRENT_DIR)),
        'partitions': partitions,
        'source_count': len(partitions),
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output_dir': str(OUT_DIR.relative_to(CURRENT_DIR)), 'source_count': len(partitions)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
