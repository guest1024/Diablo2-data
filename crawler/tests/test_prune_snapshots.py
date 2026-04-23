from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.prune_snapshots as prune_module


class PruneSnapshotsTests(unittest.TestCase):
    def test_prune_runs_keeps_latest_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runs = Path(tmpdir) / 'runs'
            runs.mkdir()
            for name in ['20260423T010000Z', '20260423T020000Z', '20260423T030000Z']:
                (runs / name).mkdir()
            with patch.object(prune_module, 'RUNS_DIR', runs):
                removed = prune_module.prune_runs(keep=1, dry_run=True)
        self.assertEqual(removed, ['runs/20260423T010000Z', 'runs/20260423T020000Z'])

    def test_prune_catalog_without_snapshots(self) -> None:
        catalog = {
            'keep-saved': {'capture_status': 'saved', 'snapshot_path': 'snapshots/a.html'},
            'drop-filtered': {'capture_status': 'filtered', 'snapshot_path': None},
            'drop-catalog-only': {'capture_status': 'catalog-only', 'snapshot_path': None},
        }
        kept, removed = prune_module.prune_catalog_without_snapshots(catalog, dry_run=True)
        self.assertEqual(set(removed), {'drop-filtered', 'drop-catalog-only'})
        self.assertIn('keep-saved', kept)

    def test_prune_unreferenced_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshots = root / 'snapshots'
            kept = snapshots / '91d2' / 'keep.html'
            dropped = snapshots / '91d2' / 'drop.html'
            kept.parent.mkdir(parents=True)
            kept.write_text('keep', encoding='utf-8')
            dropped.write_text('drop', encoding='utf-8')
            catalog = {'k': {'snapshot_path': 'snapshots/91d2/keep.html'}}
            with patch.object(prune_module, 'CURRENT_DIR', root), patch.object(prune_module, 'SNAPSHOTS_DIR', snapshots):
                removed = prune_module.prune_unreferenced_snapshots(catalog, dry_run=True)
        self.assertEqual(removed, ['snapshots/91d2/drop.html'])


if __name__ == '__main__':
    unittest.main()
