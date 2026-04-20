#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "docs/tier0/status-snapshot.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(SNAPSHOT.is_file(), "status snapshot exists")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    readiness = snapshot["readiness"]
    counts = snapshot["counts"]
    entrypoints = snapshot["entrypoints"]

    expect(all(readiness.values()), "all readiness flags are true")
    expect(counts["sources"] >= 5, "snapshot reports at least 5 sources")
    expect(counts["captures"] >= 15, "snapshot reports at least 15 captures")
    expect(counts["documents"] >= 20, "snapshot reports at least 20 documents")
    expect(counts["chunks"] >= counts["documents"], "snapshot chunks >= documents")
    expect(counts["artifact_checksums"] >= 10, "snapshot reports checksum coverage")
    for key in ("readme", "handoff", "consumer_guide", "neo4j_playbook"):
        expect((ROOT / entrypoints[key]).is_file(), f"entrypoint file exists for {key}")
    expect("run_tier0_pipeline.py" in entrypoints["pipeline"], "pipeline entrypoint command present")
    expect("verify_tier0_stack.py" in entrypoints["verify_stack"], "stack verify entrypoint command present")
    expect("verify_artifact_checksums.py" in entrypoints["verify_checksums"], "checksum verify entrypoint command present")
    print("PASS: tier0 status snapshot verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
