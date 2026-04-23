from __future__ import annotations

import unittest

from crawler.audit_publish_bundle import build_audit


class AuditPublishBundleTests(unittest.TestCase):
    def test_build_audit_contains_required_keys(self) -> None:
        audit = build_audit(latest_only=True)
        self.assertIn('latest_only', audit)
        self.assertIn('preview_count', audit)
        self.assertIn('required_files_present', audit)


if __name__ == '__main__':
    unittest.main()
