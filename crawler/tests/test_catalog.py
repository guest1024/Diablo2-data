from __future__ import annotations

import unittest

from crawler.catalog import classify_page, normalize_catalog_entry, page_key, update_page_catalog


class CatalogTests(unittest.TestCase):
    def test_page_key_is_stable(self) -> None:
        self.assertEqual(page_key("91d2", "https://a.com/x"), "91d2::https://a.com/x")

    def test_normalize_catalog_entry_infers_capture_status(self) -> None:
        entry = normalize_catalog_entry({"lifecycle_status": "frozen", "snapshot_path": "snapshots/a.html"})
        self.assertEqual(entry["capture_status"], "saved")

    def test_classify_page_new_updated_unchanged(self) -> None:
        catalog = {
            "91d2::https://a.com/x": {"sha256": "abc"},
        }
        self.assertEqual(classify_page(catalog, "91d2", "https://a.com/new", "123"), "new")
        self.assertEqual(classify_page(catalog, "91d2", "https://a.com/x", "def"), "updated")
        self.assertEqual(classify_page(catalog, "91d2", "https://a.com/x", "abc"), "unchanged")

    def test_update_page_catalog_preserves_first_seen_and_snapshot_path(self) -> None:
        catalog = {
            "91d2::https://a.com/x": {
                "first_seen_at": "2026-04-22T00:00:00+00:00",
                "sha256": "abc",
                "snapshot_path": "snapshots/91d2/x.html",
            }
        }
        updated = update_page_catalog(
            catalog,
            [
                {
                    "source_id": "91d2",
                    "source_label": "91D2",
                    "url": "https://a.com/x",
                    "title": "Title",
                    "http_status": 200,
                    "sha256": "def",
                    "lifecycle_status": "updated",
                }
            ],
            run_id="run-2",
            seen_at="2026-04-23T00:00:00+00:00",
        )
        self.assertEqual(updated["91d2::https://a.com/x"]["first_seen_at"], "2026-04-22T00:00:00+00:00")
        self.assertEqual(updated["91d2::https://a.com/x"]["last_run_id"], "run-2")
        self.assertEqual(updated["91d2::https://a.com/x"]["snapshot_path"], "snapshots/91d2/x.html")


if __name__ == "__main__":
    unittest.main()
