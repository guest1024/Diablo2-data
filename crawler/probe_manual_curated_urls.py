#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.config import MANUAL_CURATED_OVERRIDES, load_config
from crawler.extractors import extract_page_fields
from crawler.http_client import HttpFetcher
from crawler.models import FetchResponse

CONFIG_PATH = CURRENT_DIR / 'sources.zh.json'
MANUAL_PATH = MANUAL_CURATED_OVERRIDES
OUT_PATH = CURRENT_DIR / 'state/manual-curated-probe.json'


def load_manual_curated(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding='utf-8'))
    return {key: list(value) for key, value in payload.items() if isinstance(value, list)}


def build_probe_report(
    config_path: Path,
    manual_path: Path,
    fetch: Callable[[str], FetchResponse] | None = None,
) -> dict:
    config = load_config(config_path)
    source_map = {source.id: source for source in config.sources}
    manual = load_manual_curated(manual_path)
    fetcher = fetch or HttpFetcher(config.user_agent, timeout=12).fetch

    report_rows: list[dict] = []
    for source_id, urls in manual.items():
        source = source_map.get(source_id)
        if source is None:
            report_rows.append({'source_id': source_id, 'url_count': len(urls), 'error': 'unknown-source'})
            continue
        for url in urls:
            response = fetcher(url)
            title = ''
            if response.status == 200:
                title, _ = extract_page_fields(response.body, response.content_type, source.encoding_hints)
            report_rows.append(
                {
                    'source_id': source_id,
                    'url': url,
                    'status': response.status,
                    'content_type': response.content_type,
                    'title': title,
                    'note': response.note,
                }
            )

    ok_count = sum(1 for row in report_rows if row.get('status') == 200)
    return {
        'manual_file': str(manual_path),
        'source_count': len(manual),
        'url_count': sum(len(urls) for urls in manual.values()),
        'ok_count': ok_count,
        'rows': report_rows,
    }


def main() -> int:
    report = build_probe_report(CONFIG_PATH, MANUAL_PATH)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
