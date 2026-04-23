#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
CONFIG = ROOT / "sources.zh.json"
STATE = ROOT / "state/latest-run.json"
HEALTH = ROOT / "state/source-health.json"
PAGE_CATALOG = ROOT / "state/page_catalog.json"
SNAPSHOT_ROOT = ROOT / "snapshots"
TEST_RUNNER = ROOT / "run_tests.py"
REPORTER = ROOT / "report_snapshots.py"
STATUS_REPORTER = ROOT / "build_source_status_report.py"
MANUAL_VALIDATOR = ROOT / "validate_manual_curated_urls.py"
MANUAL_BACKLOG = ROOT / "build_manual_curated_backlog.py"
MANUAL_MANAGER = ROOT / "manage_manual_curated_urls.py"
RELATION_EXPORTER = ROOT / "export_snapshot_relations.py"
PUBLISH_AUDITOR = ROOT / "audit_publish_bundle.py"
DATA_BRANCH_MANIFEST = ROOT / "build_data_branch_manifest.py"
READINESS_CHECKER = ROOT / "check_data_branch_readiness.py"
MANUAL_PROBER = ROOT / "probe_manual_curated_urls.py"
MANUAL_CURATED_FILE = ROOT / "manual_curated_urls.json"
DATA_BRANCH_CHECKLIST = ROOT / "DATA_BRANCH_PUSH_CHECKLIST.md"
PRUNE_SCRIPT = ROOT / "prune_snapshots.py"
OPTIONS_DOC = ROOT / "SOURCE_OPTIONS.md"
README = ROOT / "README.md"
POLICY_DOC = ROOT / "CRAWL_POLICY.md"
OPS_DOC = ROOT / "OPERATIONS.md"
VERIFIED_TARGETS = ROOT / "VERIFIED_SNAPSHOT_TARGETS.md"
MANUAL_CURATED_EXAMPLE = ROOT / "manual_curated_urls.example.json"
WORKFLOW = REPO_ROOT / ".github/workflows/scheduler.yml"
DATA_BRANCH_SCRIPT = REPO_ROOT / "scripts/push_crawler_to_data_branch.py"
PLAN = ROOT / "CLEANUP_PLAN.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(CONFIG.is_file(), "sources.zh.json exists")
    expect(TEST_RUNNER.is_file(), "run_tests.py exists")
    expect(REPORTER.is_file(), "report_snapshots.py exists")
    expect(STATUS_REPORTER.is_file(), "build_source_status_report.py exists")
    expect(MANUAL_VALIDATOR.is_file(), "validate_manual_curated_urls.py exists")
    expect(MANUAL_BACKLOG.is_file(), "build_manual_curated_backlog.py exists")
    expect(MANUAL_MANAGER.is_file(), "manage_manual_curated_urls.py exists")
    expect(RELATION_EXPORTER.is_file(), "export_snapshot_relations.py exists")
    expect(PUBLISH_AUDITOR.is_file(), "audit_publish_bundle.py exists")
    expect(DATA_BRANCH_MANIFEST.is_file(), "build_data_branch_manifest.py exists")
    expect(READINESS_CHECKER.is_file(), "check_data_branch_readiness.py exists")
    expect(MANUAL_PROBER.is_file(), "probe_manual_curated_urls.py exists")
    expect(MANUAL_CURATED_FILE.is_file(), "manual_curated_urls.json exists")
    expect(DATA_BRANCH_CHECKLIST.is_file(), "DATA_BRANCH_PUSH_CHECKLIST.md exists")
    expect(PRUNE_SCRIPT.is_file(), "prune_snapshots.py exists")
    expect(OPTIONS_DOC.is_file(), "SOURCE_OPTIONS.md exists")
    expect(README.is_file(), "README.md exists")
    expect(POLICY_DOC.is_file(), "CRAWL_POLICY.md exists")
    expect(OPS_DOC.is_file(), "OPERATIONS.md exists")
    expect(VERIFIED_TARGETS.is_file(), "VERIFIED_SNAPSHOT_TARGETS.md exists")
    expect(MANUAL_CURATED_EXAMPLE.is_file(), "manual_curated_urls.example.json exists")
    expect(WORKFLOW.is_file(), "GitHub workflow exists")
    expect(DATA_BRANCH_SCRIPT.is_file(), "data-branch publish script exists")
    expect(PLAN.is_file(), "cleanup plan exists")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    sources = config.get("sources", [])
    expect(len(sources) >= 10, "at least ten configured sources")
    expect(any(source.get("enabled", False) for source in sources), "has enabled sources")
    expect(any(not source.get("enabled", True) for source in sources), "has disabled fallback sources")
    expect(all("selection" in source for source in sources), "all sources define selection rules")
    expect(all("authority_tier" in source for source in sources), "all sources define authority tier")
    expect(all("lane" in source for source in sources), "all sources define lane")
    expect(all("snapshot" in source for source in sources), "all sources define snapshot rules")
    expect(all("relevance" in source for source in sources), "all sources define relevance rules")

    expect(STATE.is_file(), "latest-run.json exists")
    expect(HEALTH.is_file(), "source-health.json exists")
    expect(PAGE_CATALOG.is_file(), "page_catalog.json exists")
    expect(SNAPSHOT_ROOT.is_dir(), "snapshot root exists")
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    expect("schedule:" in workflow_text, "workflow has schedule trigger")
    expect("concurrency:" in workflow_text, "workflow has concurrency control")
    expect("python3 crawler/run_snapshot.py" in workflow_text, "workflow runs snapshot command")
    expect("python3 crawler/report_snapshots.py" in workflow_text, "workflow writes catalog report")
    expect("python3 crawler/build_source_status_report.py" in workflow_text, "workflow writes source status report")
    expect("python3 crawler/build_manual_curated_backlog.py" in workflow_text, "workflow writes manual curated backlog report")
    expect("python3 crawler/export_snapshot_relations.py" in workflow_text, "workflow exports snapshot relations")
    expect("python3 crawler/audit_publish_bundle.py" in workflow_text, "workflow audits publish bundle")
    expect("python3 crawler/build_data_branch_manifest.py" in workflow_text, "workflow writes data branch manifest")
    expect("python3 crawler/prune_snapshots.py" in workflow_text, "workflow prunes old runs/snapshots")
    expect("prune_catalog_without_snapshots" in workflow_text, "workflow exposes catalog pruning input")
    expect("python3 scripts/push_crawler_to_data_branch.py" in workflow_text, "workflow publishes to data branch")
    expect("--latest-only" in workflow_text, "workflow publishes latest run only to data branch")
    expect("crawler/build_source_status_report.py" in workflow_text, "workflow writes source status report")
    expect("retention-days:" in workflow_text, "workflow sets artifact retention")

    latest = json.loads(STATE.read_text(encoding="utf-8"))
    health = json.loads(HEALTH.read_text(encoding="utf-8"))
    catalog = json.loads(PAGE_CATALOG.read_text(encoding="utf-8"))
    expect("run_id" in latest, "latest run has run_id")
    expect(bool(latest.get("sources")), "latest run includes sources")
    expect(bool(health.get("sources")), "health file includes sources")
    expect(isinstance(catalog, dict), "page catalog is a dict")
    print("PASS: crawler framework verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
