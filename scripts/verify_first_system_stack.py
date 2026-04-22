#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    {
        "name": "verify_chroma_package",
        "cmd": [sys.executable, "scripts/verify_chroma_package.py"],
    },
    {
        "name": "build_graph_support_assets",
        "cmd": [sys.executable, "scripts/build_graph_support_assets.py"],
    },
    {
        "name": "verify_graph_support_assets",
        "cmd": [sys.executable, "scripts/verify_graph_support_assets.py"],
    },
    {
        "name": "verify_bilingual_term_map",
        "cmd": [sys.executable, "scripts/verify_bilingual_term_map.py"],
    },
    {
        "name": "verify_curated_anchor_routing",
        "cmd": [sys.executable, "scripts/verify_curated_anchor_routing.py"],
    },
    {
        "name": "verify_routing_matrix",
        "cmd": [sys.executable, "scripts/verify_routing_matrix.py"],
    },
    {
        "name": "verify_curated_surface_alignment",
        "cmd": [sys.executable, "scripts/verify_curated_surface_alignment.py"],
    },
    {
        "name": "build_surface_coverage_report",
        "cmd": [sys.executable, "scripts/build_surface_coverage_report.py"],
    },
    {
        "name": "build_verification_index",
        "cmd": [sys.executable, "scripts/build_verification_index.py"],
    },
    {
        "name": "build_curated_catalog",
        "cmd": [sys.executable, "scripts/build_curated_catalog.py"],
    },
    {
        "name": "build_term_map_catalog",
        "cmd": [sys.executable, "scripts/build_term_map_catalog.py"],
    },
    {
        "name": "verify_strategy_docs",
        "cmd": [sys.executable, "scripts/verify_strategy_docs.py"],
    },
    {
        "name": "verify_doc_handbooks",
        "cmd": [sys.executable, "scripts/verify_doc_handbooks.py"],
    },
]


def run_check(check: dict[str, object]) -> dict[str, object]:
    proc = subprocess.run(
        check["cmd"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "name": check["name"],
        "returncode": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout_tail": "\n".join(proc.stdout.strip().splitlines()[-12:]),
        "stderr_tail": "\n".join(proc.stderr.strip().splitlines()[-12:]),
    }


def main() -> int:
    results = [run_check(check) for check in CHECKS]
    passed = sum(1 for row in results if row["passed"])

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": len(results),
        "results": results,
    }

    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verification-suite.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Verification Suite",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Passed: `{report['passed']}/{report['total']}`",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for row in results:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"| {row['name']} | {status} |")
    lines.extend(["", "## Check tails", ""])
    for row in results:
        lines.append(f"### {row['name']}")
        lines.append("")
        lines.append(f"- status: `{'PASS' if row['passed'] else 'FAIL'}`")
        if row["stdout_tail"]:
            lines.append("- stdout tail:")
            lines.append("```text")
            lines.append(str(row["stdout_tail"]))
            lines.append("```")
        if row["stderr_tail"]:
            lines.append("- stderr tail:")
            lines.append("```text")
            lines.append(str(row["stderr_tail"]))
            lines.append("```")
        lines.append("")
    (out_dir / "verification-suite.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"passed": passed, "total": len(results)}, ensure_ascii=False))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
