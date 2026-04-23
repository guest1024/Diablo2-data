from __future__ import annotations

from dataclasses import replace
import unittest
from pathlib import Path

from crawler.models import CrawlOptions, DiscoveryRules, FetchResponse, RelevanceRules, SelectionRules, SnapshotRules, SourceConfig
from crawler.runner import build_frozen_record, process_source, should_skip_existing


def build_source() -> SourceConfig:
    return SourceConfig(
        id='91d2',
        label='91D2',
        enabled=True,
        weight=1.0,
        region='CN',
        transport='direct',
        observed_on='2026-04-23',
        observed_status='direct-ok',
        home_url='https://example.com',
        robots_url=None,
        discovery=DiscoveryRules(),
        selection=SelectionRules(),
        snapshot=SnapshotRules(immutable_after_capture=True, store_raw_content=True),
        relevance=RelevanceRules(),
    )


class RunnerTests(unittest.TestCase):
    def test_should_skip_existing_for_frozen_and_ignored_entries(self) -> None:
        source = build_source()
        options = CrawlOptions(config_path=Path('crawler/sources.zh.json'))
        self.assertTrue(should_skip_existing({'capture_status': 'saved'}, source, options))
        self.assertTrue(should_skip_existing({'capture_status': 'frozen'}, source, options))
        self.assertTrue(should_skip_existing({'capture_status': 'filtered'}, source, options))
        self.assertTrue(should_skip_existing({'capture_status': 'ignored'}, source, options))

    def test_build_frozen_record_preserves_ignored_entries(self) -> None:
        source = build_source()
        record = build_frozen_record(
            source,
            {
                'url': 'https://example.com/noise',
                'capture_status': 'ignored',
                'title': 'noise',
            },
            seen_at='2026-04-23T00:00:00+00:00',
            run_id='run-1',
        )
        self.assertEqual(record['capture_status'], 'ignored')
        self.assertEqual(record['lifecycle_status'], 'ignored')

    def test_process_source_skips_existing_pages_without_re_fetching(self) -> None:
        source = replace(build_source(), seed_urls=('https://example.com/index.html',))
        options = CrawlOptions(config_path=Path('crawler/sources.zh.json'), limit_per_source=2)
        page_catalog = {
            '91d2::https://example.com/path/page.html': {
                'source_id': '91d2',
                'url': 'https://example.com/path/page.html',
                'capture_status': 'saved',
                'snapshot_path': 'snapshots/91d2/example.com/path/page.html',
            }
        }

        class FakeFetcher:
            def __init__(self) -> None:
                self.calls: list[str] = []

            def fetch(self, url: str) -> FetchResponse:
                self.calls.append(url)
                if url == 'https://example.com/index.html':
                    return FetchResponse(
                        url=url,
                        status=200,
                        content_type='text/html',
                        body=b'<a href="/path/page.html">page</a>',
                        note=None,
                    )
                raise AssertionError(f'unexpected fetch for {url}')

        class FakeRobots:
            def can_fetch(self, robots_url: str | None, url: str) -> tuple[bool, str]:
                return True, ''

        fetcher = FakeFetcher()
        result, manifest, updates = process_source(
            source,
            options,
            fetcher,
            FakeRobots(),
            page_catalog,
            run_id='run-1',
            seen_at='2026-04-23T00:00:00+00:00',
        )

        self.assertEqual(fetcher.calls, ['https://example.com/index.html'])
        self.assertEqual(manifest['pages'], [])
        self.assertEqual(updates, [])
        self.assertEqual(result['skipped_existing_count'], 1)
        self.assertEqual(result['status'], 'captured')


if __name__ == '__main__':
    unittest.main()
