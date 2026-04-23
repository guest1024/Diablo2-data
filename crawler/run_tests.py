#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

TEST_MODULES = [
    "crawler.tests.test_run_snapshot",
    "crawler.tests.test_selection",
    "crawler.tests.test_catalog",
    "crawler.tests.test_relevance",
    "crawler.tests.test_storage",
    "crawler.tests.test_reporting",
    "crawler.tests.test_config",
    "crawler.tests.test_data_branch_publish",
    "crawler.tests.test_prune_snapshots",
    "crawler.tests.test_source_status_report",
    "crawler.tests.test_validate_manual_curated_urls",
    "crawler.tests.test_manual_curated_backlog",
    "crawler.tests.test_manage_manual_curated_urls",
    "crawler.tests.test_export_snapshot_relations",
    "crawler.tests.test_audit_publish_bundle",
    "crawler.tests.test_check_data_branch_readiness",
    "crawler.tests.test_probe_manual_curated_urls",
    "crawler.tests.test_build_data_branch_manifest",
    "crawler.tests.test_probe_data_branch_remote",
    "crawler.tests.test_build_preflight_report",
    "crawler.tests.test_build_crawler_reports",
    "crawler.tests.test_preflight_data_branch_push",
    "crawler.tests.test_export_page_catalog_partitions",
    "crawler.tests.test_export_source_health_partitions",
    "crawler.tests.test_export_page_records",
    "crawler.tests.test_runner",
]


def main() -> int:
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for module in TEST_MODULES:
        suite.addTests(loader.loadTestsFromName(module))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
