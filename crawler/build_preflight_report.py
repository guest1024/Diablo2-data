#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.check_data_branch_readiness import build_readiness

OUT_PATH = CURRENT_DIR / 'state/preflight-report.json'


def build_report() -> dict:
    readiness = build_readiness()
    latest_run = json.loads((CURRENT_DIR / 'state/latest-run.json').read_text(encoding='utf-8'))
    manual_probe_path = CURRENT_DIR / 'state/manual-curated-probe.json'
    manual_probe = json.loads(manual_probe_path.read_text(encoding='utf-8')) if manual_probe_path.is_file() else None
    remote_probe_path = CURRENT_DIR / 'state/data-branch-remote-probe.json'
    remote_probe = json.loads(remote_probe_path.read_text(encoding='utf-8')) if remote_probe_path.is_file() else None
    relations_path = CURRENT_DIR / 'state/snapshot-relations.jsonl'
    relation_count = len(relations_path.read_text(encoding='utf-8').splitlines()) if relations_path.is_file() else 0
    return {
        'latest_run_id': latest_run.get('run_id'),
        'page_snapshot_count': latest_run.get('page_snapshot_count'),
        'snapshot_relation_count': relation_count,
        'manual_probe': manual_probe,
        'remote_probe': remote_probe,
        'readiness': readiness,
    }


def main() -> int:
    report = build_report()
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
