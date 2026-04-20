#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/tier0/artifact-checksums.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    expect(MANIFEST.is_file(), "artifact checksum manifest exists")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expect(payload["artifact_count"] == len(payload["entries"]), "artifact count matches entries length")

    for entry in payload["entries"]:
        path = ROOT / entry["path"]
        expect(path.is_file(), f"{entry['path']} exists")
        expect(path.stat().st_size == entry["size"], f"{entry['path']} size matches")
        expect(sha256_file(path) == entry["sha256"], f"{entry['path']} sha256 matches")

    print("PASS: artifact checksum verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
