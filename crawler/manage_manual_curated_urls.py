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
from crawler.storage import write_json

CONFIG_PATH = CURRENT_DIR / 'sources.zh.json'
MANUAL_PATH = MANUAL_CURATED_OVERRIDES


def load_manual(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding='utf-8'))
    return {key: list(value) for key, value in payload.items() if isinstance(value, list)}


def validate_source_id(source_id: str) -> None:
    config = load_config(CONFIG_PATH)
    valid_ids = {source.id for source in config.sources}
    if source_id not in valid_ids:
        raise SystemExit(f'Unknown source id: {source_id}')


def list_urls(source_id: str | None) -> int:
    payload = load_manual(MANUAL_PATH)
    if source_id:
        validate_source_id(source_id)
        rows = {source_id: payload.get(source_id, [])}
    else:
        rows = payload
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def add_url(source_id: str, url: str) -> int:
    validate_source_id(source_id)
    if not url.startswith(('http://', 'https://')):
        raise SystemExit('URL must start with http:// or https://')
    payload = load_manual(MANUAL_PATH)
    urls = payload.setdefault(source_id, [])
    if url not in urls:
        urls.append(url)
        write_json(MANUAL_PATH, payload)
    print(json.dumps({'source_id': source_id, 'count': len(urls), 'added': url}, ensure_ascii=False, indent=2))
    return 0


def remove_url(source_id: str, url: str) -> int:
    validate_source_id(source_id)
    payload = load_manual(MANUAL_PATH)
    urls = payload.setdefault(source_id, [])
    if url in urls:
        urls.remove(url)
        write_json(MANUAL_PATH, payload)
    print(json.dumps({'source_id': source_id, 'count': len(urls), 'removed': url}, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Manage crawler/manual_curated_urls.json entries')
    subparsers = parser.add_subparsers(dest='command', required=True)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--source')

    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('--source', required=True)
    add_parser.add_argument('--url', required=True)

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('--source', required=True)
    remove_parser.add_argument('--url', required=True)

    args = parser.parse_args(argv)
    if args.command == 'list':
        return list_urls(args.source)
    if args.command == 'add':
        return add_url(args.source, args.url)
    if args.command == 'remove':
        return remove_url(args.source, args.url)
    raise SystemExit(f'Unhandled command: {args.command}')


if __name__ == '__main__':
    raise SystemExit(main())
