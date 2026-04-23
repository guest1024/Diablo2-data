#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.catalog import load_page_catalog
from crawler.storage import write_json

CONFIG_PATH = CURRENT_DIR / 'sources.zh.json'
HEALTH_PATH = CURRENT_DIR / 'state/source-health.json'
OUT_PATH = CURRENT_DIR / 'state/source-status-report.md'
JSON_OUT = CURRENT_DIR / 'state/source-status-report.json'
MANUAL_CURATED_PATH = CURRENT_DIR / 'manual_curated_urls.json'
PARTITIONED_DIR = CURRENT_DIR / 'state/source-status'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def load_manual_curated() -> dict[str, list[str]]:
    if not MANUAL_CURATED_PATH.is_file():
        return {}
    return json.loads(MANUAL_CURATED_PATH.read_text(encoding='utf-8'))


def build_report_payload() -> dict:
    config = load_json(CONFIG_PATH)
    health = load_json(HEALTH_PATH) if HEALTH_PATH.exists() else {'sources': []}
    health_map = {row['id']: row for row in health.get('sources', [])}
    catalog = load_page_catalog(CURRENT_DIR / 'state/page_catalog.json')
    manual_curated = load_manual_curated()

    snapshot_counts: dict[str, int] = Counter()
    capture_breakdown: dict[str, Counter] = defaultdict(Counter)
    lifecycle_breakdown: dict[str, Counter] = defaultdict(Counter)
    for row in catalog.values():
        source_id = row.get('source_id', 'unknown')
        if row.get('snapshot_path'):
            snapshot_counts[source_id] += 1
        capture_breakdown[source_id][row.get('capture_status', 'unknown')] += 1
        lifecycle_breakdown[source_id][row.get('lifecycle_status', 'unknown')] += 1

    sources_payload = []
    for source in config.get('sources', []):
        source_id = source['id']
        health_row = health_map.get(source_id, {})
        sources_payload.append(
            {
                'source_id': source_id,
                'enabled': source.get('enabled', True),
                'region': source.get('region', ''),
                'transport': source.get('transport', ''),
                'observed_status': source.get('observed_status', ''),
                'saved_snapshots': snapshot_counts.get(source_id, 0),
                'manual_curated_count': len(manual_curated.get(source_id, [])),
                'capture_summary': dict(capture_breakdown.get(source_id, Counter())),
                'lifecycle_summary': dict(lifecycle_breakdown.get(source_id, Counter())),
                'last_run_status': health_row.get('status', 'n/a'),
                'notes': source.get('notes', ''),
            }
        )

    return {
        'version': config.get('version', 'unknown'),
        'sources': sources_payload,
        'summary': {
            'configured_sources': len(config.get('sources', [])),
            'sources_with_saved_snapshots': sum(1 for count in snapshot_counts.values() if count > 0),
            'total_saved_snapshots': sum(snapshot_counts.values()),
            'sources_with_manual_curated': sum(1 for urls in manual_curated.values() if urls),
        },
    }


def build_report() -> str:
    payload = build_report_payload()
    lines = [
        '# Source Status Report',
        '',
        f"- Version: `{payload['version']}`",
        f"- Report path: `{OUT_PATH.relative_to(CURRENT_DIR)}`",
        '',
        '| Source | Enabled | Region | Transport | Observed status | Saved snapshots | Manual curated | Capture summary | Lifecycle summary | Last run status | Notes |',
        '| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |',
    ]
    for source in payload['sources']:
        lines.append(
            f"| {source['source_id']} | {source['enabled']} | {source['region']} | {source['transport']} | {source['observed_status']} | {source['saved_snapshots']} | {source['manual_curated_count']} | `{source['capture_summary']}` | `{source['lifecycle_summary']}` | {source['last_run_status']} | {source['notes']} |"
        )

    summary = payload['summary']
    lines.extend([
        '',
        '## Summary',
        '',
        f"- Configured sources: `{summary['configured_sources']}`",
        f"- Sources with saved snapshots: `{summary['sources_with_saved_snapshots']}`",
        f"- Total saved snapshots: `{summary['total_saved_snapshots']}`",
        f"- Sources with manual curated overrides: `{summary['sources_with_manual_curated']}`",
        '',
    ])
    return '\n'.join(lines) + '\n'


def main() -> int:
    payload = build_report_payload()
    report = build_report()
    OUT_PATH.write_text(report, encoding='utf-8')
    write_json(JSON_OUT, payload)
    PARTITIONED_DIR.mkdir(parents=True, exist_ok=True)
    for source in payload['sources']:
        write_json(PARTITIONED_DIR / f"{source['source_id']}.json", source)
    print(report, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
