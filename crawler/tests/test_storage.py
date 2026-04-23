from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from crawler.storage import mirrored_relative_path, normalize_snapshot_catalog_paths, save_snapshot


class StorageTests(unittest.TestCase):
    def test_save_snapshot_returns_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_id, path = save_snapshot(Path(tmpdir), "91d2", "https://example.com/a", "text/html", b"<html></html>")
            self.assertTrue(snapshot_id.startswith("snapshot::91d2::"))
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, ".html")
            self.assertIn("example.com", str(path))

    def test_mirrored_relative_path_preserves_host_and_query_signal(self) -> None:
        path = mirrored_relative_path(
            "bbs_diablo2_com_cn",
            "http://bbs.diablo2.com.cn/read.php?tid=239897",
            "text/html",
        )
        self.assertEqual(str(path), "bbs_diablo2_com_cn/bbs.diablo2.com.cn/read.php__tid-239897.html")

    def test_normalize_snapshot_catalog_paths_moves_legacy_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshots = root / "snapshots"
            legacy = snapshots / "91d2" / "91d2--legacy.html"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("<html></html>", encoding="utf-8")

            updated, moved = normalize_snapshot_catalog_paths(
                {
                    "91d2::https://example.com/path/page.html": {
                        "source_id": "91d2",
                        "url": "https://example.com/path/page.html",
                        "content_type": "text/html",
                        "snapshot_path": "snapshots/91d2/91d2--legacy.html",
                    }
                },
                crawler_root=root,
                snapshot_root=snapshots,
            )
            new_path = root / updated["91d2::https://example.com/path/page.html"]["snapshot_path"]
            self.assertTrue(new_path.is_file())
            self.assertFalse(legacy.exists())
            self.assertEqual(moved[0]["to"], "snapshots/91d2/example.com/path/page.html")


if __name__ == "__main__":
    unittest.main()
