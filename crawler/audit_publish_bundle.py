#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.push_crawler_to_data_branch import build_effective_include, build_publish_preview, load_latest_run_id, tracked_paths

OUT_PATH = CURRENT_DIR / 'state/publish-audit.json'


def build_audit(latest_only: bool = True) -> dict:
    run_id = load_latest_run_id()
    includes = build_effective_include(latest_only, None, run_id)
    paths = tracked_paths(includes)
    preview = build_publish_preview(paths)
    audit = {
        'latest_only': latest_only,
        'run_id': run_id,
        'include_roots': [str(path.relative_to(PROJECT_ROOT)) for path in paths],
        'preview_count': len(preview),
        'preview_head': preview[:50],
        'required_files_present': {
            'latest_run': (CURRENT_DIR / 'state/latest-run.json').is_file(),
            'page_catalog': (CURRENT_DIR / 'state/page_catalog.json').is_file(),
            'snapshot_relations': (CURRENT_DIR / 'state/snapshot-relations.jsonl').is_file(),
            'source_status': (CURRENT_DIR / 'state/source-status-report.md').is_file(),
            'manual_backlog': (CURRENT_DIR / 'state/manual-curated-backlog.md').is_file(),
        },
    }
    return audit


def main() -> int:
    audit = build_audit(latest_only=True)
    OUT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
