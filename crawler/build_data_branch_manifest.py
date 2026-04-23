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

OUT_PATH = CURRENT_DIR / 'state/data-branch-manifest.json'


def build_manifest(latest_only: bool = True) -> dict:
    run_id = load_latest_run_id()
    include_roots = build_effective_include(latest_only, None, run_id)
    paths = tracked_paths(include_roots)
    preview = build_publish_preview(paths)
    return {
        'latest_only': latest_only,
        'run_id': run_id,
        'include_roots': include_roots,
        'preview_count': len(preview),
        'files': preview,
    }


def main() -> int:
    manifest = build_manifest(latest_only=True)
    OUT_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'run_id': manifest['run_id'], 'preview_count': manifest['preview_count'], 'output': str(OUT_PATH.relative_to(CURRENT_DIR))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
