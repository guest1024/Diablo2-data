from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.push_crawler_to_data_branch as publish
from scripts.push_crawler_to_data_branch import (
    build_commit_message,
    build_effective_include,
    build_publish_preview,
    tracked_paths,
)


class DataBranchPublishTests(unittest.TestCase):
    def test_build_commit_message_mentions_data_branch(self) -> None:
        message = build_commit_message('run-123')
        self.assertIn('data branch', message)
        self.assertIn('run-123', message)

    def test_tracked_paths_filters_missing_entries(self) -> None:
        paths = tracked_paths(['crawler/README.md', 'does/not/exist'])
        self.assertEqual(len(paths), 1)
        self.assertTrue(str(paths[0]).endswith('crawler/README.md'))

    def test_build_publish_preview_includes_files(self) -> None:
        preview = build_publish_preview(tracked_paths(['crawler/README.md']))
        self.assertIn('crawler/README.md', preview)

    def test_build_effective_include_latest_only(self) -> None:
        include = build_effective_include(True, None, 'run-1')
        self.assertIn('crawler/runs/run-1', include)
        self.assertNotIn('crawler/runs', include)

    def test_build_effective_include_uses_referenced_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = root / 'page_catalog.json'
            catalog.write_text(json.dumps({'a': {'snapshot_path': 'crawler/snapshots/a.html'}}), encoding='utf-8')
            with patch.object(publish, 'PAGE_CATALOG', catalog):
                include = publish.build_effective_include(True, None, 'run-1')
        self.assertIn('crawler/snapshots/a.html', include)


if __name__ == '__main__':
    unittest.main()
