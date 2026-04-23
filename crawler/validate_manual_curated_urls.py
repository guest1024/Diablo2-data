#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.config import MANUAL_CURATED_OVERRIDES, load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate manually curated crawler URLs against configured sources')
    parser.add_argument('--config', default=str(CURRENT_DIR / 'sources.zh.json'))
    parser.add_argument('--manual-file', default=str(MANUAL_CURATED_OVERRIDES))
    args = parser.parse_args(argv)

    config = load_config(Path(args.config))
    source_ids = {source.id for source in config.sources}
    manual_path = Path(args.manual_file)

    if not manual_path.is_file():
        print(json.dumps({'valid': True, 'warning': 'manual curated file missing', 'manual_file': str(manual_path)}, ensure_ascii=False, indent=2))
        return 0

    payload = json.loads(manual_path.read_text(encoding='utf-8'))
    errors: list[str] = []
    summary: dict[str, int] = {}

    if not isinstance(payload, dict):
        raise SystemExit('manual curated file must be a JSON object mapping source_id -> [urls]')

    for source_id, urls in payload.items():
        if source_id not in source_ids:
            errors.append(f'unknown source id: {source_id}')
            continue
        if not isinstance(urls, list):
            errors.append(f'source {source_id} must map to a list of urls')
            continue
        valid_urls = 0
        seen: set[str] = set()
        for url in urls:
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                errors.append(f'invalid url for {source_id}: {url!r}')
                continue
            if url in seen:
                errors.append(f'duplicate url for {source_id}: {url}')
                continue
            seen.add(url)
            valid_urls += 1
        summary[source_id] = valid_urls

    result = {
        'valid': not errors,
        'manual_file': str(manual_path),
        'source_count': len(summary),
        'summary': summary,
        'errors': errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
