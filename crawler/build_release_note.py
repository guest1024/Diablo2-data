#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
OUT_PATH = CURRENT_DIR / 'state/release-note.md'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def main() -> int:
    readiness = load_json(CURRENT_DIR / 'state/data-branch-readiness.json')
    preflight = load_json(CURRENT_DIR / 'state/preflight-report.json')
    manifest = load_json(CURRENT_DIR / 'state/data-branch-manifest.json')
    warnings = readiness.get('warnings', [])
    lines = [
        '# Data Branch Release Note',
        '',
        f"- latest_run_id: `{preflight.get('latest_run_id')}`",
        f"- ready: `{readiness.get('ready')}`",
        f"- remote_data_branch_exists: `{preflight.get('remote_probe', {}).get('branch_exists')}`",
        f"- snapshot_relation_count: `{preflight.get('snapshot_relation_count')}`",
        f"- preview_count: `{manifest.get('preview_count')}`",
        '',
        '## Warnings',
        '',
    ]
    if warnings:
        for warning in warnings:
            lines.append(f'- {warning}')
    else:
        lines.append('- none')
    lines.extend([
        '',
        '## Commands',
        '',
        'Preview:',
        '```bash',
        'python3 scripts/first_data_branch_push.py',
        '```',
        '',
        'Real push:',
        '```bash',
        'python3 scripts/first_data_branch_push.py --real-push',
        '```',
    ])
    OUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_PATH.read_text(encoding='utf-8'), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
