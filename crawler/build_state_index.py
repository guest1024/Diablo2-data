#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
STATE_DIR = CURRENT_DIR / 'state'
OUT_PATH = STATE_DIR / 'index.json'


def list_files(path: Path, pattern: str = '*') -> list[str]:
    if not path.exists():
        return []
    if path.is_file():
        return [str(path.relative_to(CURRENT_DIR))]
    return [str(p.relative_to(CURRENT_DIR)) for p in sorted(path.rglob(pattern)) if p.is_file()]


def build_index() -> dict:
    return {
        'state_root': str(STATE_DIR.relative_to(CURRENT_DIR)),
        'latest_run': str((STATE_DIR / 'latest-run.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'latest-run.json').exists() else None,
        'reports': {
            'catalog_report': str((STATE_DIR / 'catalog-report.md').relative_to(CURRENT_DIR)) if (STATE_DIR / 'catalog-report.md').exists() else None,
            'source_status_report': str((STATE_DIR / 'source-status-report.md').relative_to(CURRENT_DIR)) if (STATE_DIR / 'source-status-report.md').exists() else None,
            'manual_curated_backlog': str((STATE_DIR / 'manual-curated-backlog.md').relative_to(CURRENT_DIR)) if (STATE_DIR / 'manual-curated-backlog.md').exists() else None,
            'publish_audit': str((STATE_DIR / 'publish-audit.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'publish-audit.json').exists() else None,
            'data_branch_manifest': str((STATE_DIR / 'data-branch-manifest.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'data-branch-manifest.json').exists() else None,
            'data_branch_readiness': str((STATE_DIR / 'data-branch-readiness.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'data-branch-readiness.json').exists() else None,
            'preflight_report': str((STATE_DIR / 'preflight-report.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'preflight-report.json').exists() else None,
            'remote_probe': str((STATE_DIR / 'data-branch-remote-probe.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'data-branch-remote-probe.json').exists() else None,
            'final_push_summary': str((STATE_DIR / 'final-push-summary.md').relative_to(CURRENT_DIR)) if (STATE_DIR / 'final-push-summary.md').exists() else None,
            'release_note': str((STATE_DIR / 'release-note.md').relative_to(CURRENT_DIR)) if (STATE_DIR / 'release-note.md').exists() else None,
        },
        'partitions': {
            'snapshot_relations': list_files(STATE_DIR / 'snapshot-relations'),
            'page_catalog': list_files(STATE_DIR / 'page-catalog'),
            'source_health': list_files(STATE_DIR / 'source-health'),
            'source_status': list_files(STATE_DIR / 'source-status'),
            'latest_run': list_files(STATE_DIR / 'latest-run'),
            'page_records': list_files(STATE_DIR / 'page-records'),
        },
        'single_files': {
            'page_catalog': str((STATE_DIR / 'page_catalog.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'page_catalog.json').exists() else None,
            'source_health': str((STATE_DIR / 'source-health.json').relative_to(CURRENT_DIR)) if (STATE_DIR / 'source-health.json').exists() else None,
            'snapshot_relations': str((STATE_DIR / 'snapshot-relations.jsonl').relative_to(CURRENT_DIR)) if (STATE_DIR / 'snapshot-relations.jsonl').exists() else None,
        },
    }


def main() -> int:
    payload = build_index()
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(OUT_PATH.relative_to(CURRENT_DIR)), 'partition_groups': len(payload['partitions'])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
