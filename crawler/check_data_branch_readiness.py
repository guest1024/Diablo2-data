#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
PUBLISH_AUDIT = CURRENT_DIR / 'state/publish-audit.json'
MANUAL_BACKLOG = CURRENT_DIR / 'state/manual-curated-backlog.md'
WORKFLOW = PROJECT_ROOT / '.github/workflows/scheduler.yml'
REMOTE_PROBE = CURRENT_DIR / 'state/data-branch-remote-probe.json'
OUT_PATH = CURRENT_DIR / 'state/data-branch-readiness.json'


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', *args], cwd=PROJECT_ROOT, text=True, capture_output=True)


def build_readiness() -> dict:
    checks: dict[str, bool] = {}
    warnings: list[str] = []
    details: dict[str, object] = {}

    remote = run_git('remote', '-v')
    remote_text = remote.stdout.strip()
    checks['origin_configured'] = 'origin' in remote_text
    details['git_remote'] = remote_text
    if not checks['origin_configured']:
        warnings.append('git remote origin is not configured')

    checks['publish_audit_exists'] = PUBLISH_AUDIT.is_file()
    if PUBLISH_AUDIT.is_file():
        audit = json.loads(PUBLISH_AUDIT.read_text(encoding='utf-8'))
        details['publish_audit'] = audit
        checks['latest_only'] = bool(audit.get('latest_only'))
        checks['preview_nonempty'] = int(audit.get('preview_count', 0)) > 0
        checks['required_files_present'] = all(audit.get('required_files_present', {}).values())
        if not checks['latest_only']:
            warnings.append('publish audit is not running in latest-only mode')
    else:
        checks['latest_only'] = False
        checks['preview_nonempty'] = False
        checks['required_files_present'] = False
        warnings.append('publish audit missing; run crawler/audit_publish_bundle.py first')

    checks['manual_backlog_exists'] = MANUAL_BACKLOG.is_file()
    if MANUAL_BACKLOG.is_file():
        backlog_text = MANUAL_BACKLOG.read_text(encoding='utf-8')
        details['manual_backlog_excerpt'] = '\n'.join(backlog_text.splitlines()[:20])
        if 'rogue_camp_163' in backlog_text:
            warnings.append('rogue_camp_163 still needs manual curated URLs')
    else:
        warnings.append('manual curated backlog report is missing')

    checks['workflow_exists'] = WORKFLOW.is_file()
    if WORKFLOW.is_file():
        workflow_text = WORKFLOW.read_text(encoding='utf-8')
        checks['workflow_latest_only'] = '--latest-only' in workflow_text
        checks['workflow_publish_step'] = 'push_crawler_to_data_branch.py' in workflow_text
    else:
        checks['workflow_latest_only'] = False
        checks['workflow_publish_step'] = False
        warnings.append('crawler workflow file is missing')

    checks['remote_probe_exists'] = REMOTE_PROBE.is_file()
    first_push_will_create_branch = None
    if REMOTE_PROBE.is_file():
        remote_probe = json.loads(REMOTE_PROBE.read_text(encoding='utf-8'))
        details['remote_probe'] = remote_probe
        checks['remote_accessible'] = bool(remote_probe.get('remote_accessible'))
        checks['remote_exists'] = bool(remote_probe.get('remote_exists'))
        branch_exists = bool(remote_probe.get('branch_exists'))
        first_push_will_create_branch = not branch_exists and checks['remote_accessible'] and checks['remote_exists']
        if first_push_will_create_branch:
            warnings.append('remote data branch does not exist yet; first real push will create it')
    else:
        checks['remote_accessible'] = False
        checks['remote_exists'] = False
        warnings.append('remote probe missing; run crawler/probe_data_branch_remote.py first')

    ready = all(checks.values())
    details['warnings'] = warnings
    details['first_push_will_create_branch'] = first_push_will_create_branch
    return {
        'checks': checks,
        'warnings': warnings,
        'details': details,
        'ready': ready,
    }


def main() -> int:
    readiness = build_readiness()
    OUT_PATH.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(readiness, ensure_ascii=False, indent=2))
    return 0 if readiness['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
