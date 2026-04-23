#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.catalog import load_page_catalog
from crawler.storage import write_json

CONFIG_PATH = CURRENT_DIR / 'sources.zh.json'
MANUAL_PATH = CURRENT_DIR / 'manual_curated_urls.json'
OUT_PATH = CURRENT_DIR / 'state/manual-curated-backlog.md'
JSON_OUT = CURRENT_DIR / 'state/manual-curated-backlog.json'

SUGGESTED_ACTIONS = {
    'rogue_camp_163': '优先人工收集 1~3 条凯恩之角/罗格营地静态攻略帖 URL，再用 validate/probe 校验后写入 manual_curated_urls.json。',
    'news_blizzard_zh_tw': '若需要补繁中官方故事/专题页，可直接手工加入 article URL。',
    'ttbn_cn': '当前连接重置，建议先人工确认可访问页面，再补静态资料页 URL。',
    'bahamut_d2r': '通过代理打开哈啦板后，挑选置顶/精华攻略帖 URL 手工录入。',
    'ptt_diablo': '人工筛选高质量 M.*.A.html 文章，再加入 manual_curated_urls.json。',
    'tieba_d2r': '人工从贴吧帖子页复制 /p/<id> 形式 URL，避免列表页 403。',
    'tieba_d2': '人工从贴吧帖子页复制 /p/<id> 形式 URL，避免列表页 403。',
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def build_backlog_payload() -> dict:
    config = load_json(CONFIG_PATH)
    manual = load_json(MANUAL_PATH)
    catalog = load_page_catalog(CURRENT_DIR / 'state/page_catalog.json')

    snapshot_counts: dict[str, int] = {}
    for row in catalog.values():
        if row.get('snapshot_path'):
            source_id = row.get('source_id', 'unknown')
            snapshot_counts[source_id] = snapshot_counts.get(source_id, 0) + 1

    rows = []
    for source in config.get('sources', []):
        source_id = source['id']
        saved_count = snapshot_counts.get(source_id, 0)
        manual_count = len(manual.get(source_id, [])) if isinstance(manual.get(source_id, []), list) else 0
        transport = source.get('transport', '')
        enabled = source.get('enabled', True)
        reason_parts: list[str] = []
        if saved_count == 0:
            reason_parts.append('no saved snapshots yet')
        if transport in {'requires-proxy', 'manual-403', 'probe-only'}:
            reason_parts.append(f'transport={transport}')
        if source_id == 'rogue_camp_163':
            reason_parts.append('forum entry page still returns prompt/seed-only in current environment')
        if not reason_parts:
            continue
        rows.append(
            {
                'source_id': source_id,
                'enabled': enabled,
                'transport': transport,
                'saved_snapshots': saved_count,
                'manual_curated_count': manual_count,
                'reason': '; '.join(reason_parts),
                'suggested_action': SUGGESTED_ACTIONS.get(source_id, '人工补充高质量静态页 URL。'),
            }
        )

    return {
        'rows': rows,
        'summary': {
            'sources_needing_manual_curated': len(rows),
            'manual_curated_file': str(MANUAL_PATH.relative_to(CURRENT_DIR)),
        },
    }


def build_backlog_report() -> str:
    payload = build_backlog_payload()
    lines = [
        '# Manual Curated Backlog',
        '',
        'Weak / blocked sources that likely need manual curated URL seeding are listed below.',
        '',
        '| Source | Enabled | Transport | Saved snapshots | Manual curated count | Why it needs help | Suggested action |',
        '| --- | --- | --- | ---: | ---: | --- | --- |',
    ]
    for row in payload['rows']:
        lines.append(
            f"| {row['source_id']} | {row['enabled']} | {row['transport']} | {row['saved_snapshots']} | {row['manual_curated_count']} | {row['reason']} | {row['suggested_action']} |"
        )

    summary = payload['summary']
    lines.extend([
        '',
        '## Summary',
        '',
        f"- Sources currently needing manual curated attention: `{summary['sources_needing_manual_curated']}`",
        f"- Manual curated override file: `{summary['manual_curated_file']}`",
        '',
    ])
    return '\n'.join(lines) + '\n'


def main() -> int:
    payload = build_backlog_payload()
    report = build_backlog_report()
    OUT_PATH.write_text(report, encoding='utf-8')
    write_json(JSON_OUT, payload)
    print(report, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
