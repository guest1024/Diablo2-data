from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from crawler.storage import save_snapshot


class StorageTests(unittest.TestCase):
    def test_save_snapshot_returns_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_id, path = save_snapshot(Path(tmpdir), "91d2", "https://example.com/a", "text/html", b"<html></html>")
            self.assertTrue(snapshot_id.startswith("snapshot::91d2::"))
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, ".html")


if __name__ == "__main__":
    unittest.main()
