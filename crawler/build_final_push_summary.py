#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
OUT_PATH = CURRENT_DIR / 'state/final-push-summary.md'
READINESS = CURRENT_DIR / 'state/data-branch-readiness.json'
PREFLIGHT = CURRENT_DIR / 'state/preflight-report.json'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def main() -> int:
    readiness = load_json(READINESS)
    preflight = load_json(PREFLIGHT)
    ready = readiness.get('ready', False)
    warnings = readiness.get('warnings', [])
    run_id = preflight.get('latest_run_id')
    relation_count = preflight.get('snapshot_relation_count')
    remote_probe = preflight.get('remote_probe', {})
    branch_exists = remote_probe.get('branch_exists')

    lines = [
        '# Final Data Branch Push Summary',
        '',
        f'- ready: `{ready}`',
        f'- latest_run_id: `{run_id}`',
        f'- snapshot_relation_count: `{relation_count}`',
        f'- remote_data_branch_exists: `{branch_exists}`',
        '',
        '## Current warnings',
        '',
    ]
    if warnings:
        for warning in warnings:
            lines.append(f'- {warning}')
    else:
        lines.append('- none')

    lines.extend([
        '',
        '## Recommended next command',
        '',
        'Preview only:',
        '```bash',
        'python3 scripts/first_data_branch_push.py',
        '```',
        '',
        'Real push:',
        '```bash',
        'python3 scripts/first_data_branch_push.py --real-push',
        '```',
        '',
        '## Recommendation',
        '',
    ])

    if ready and warnings:
        lines.append('工程链路已经 ready，但仍有 warning。你可以先接受 warning 并执行首次真实推送，或先处理 warning 再推。')
    elif ready:
        lines.append('工程链路已完全 ready，可直接进行首次真实 data 分支推送。')
    else:
        lines.append('工程链路尚未 ready，建议先完成 preflight / readiness 中未通过的检查项。')

    OUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_PATH.read_text(encoding='utf-8'), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
