#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs/tier0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    fetch_manifest = json.loads((TIER0 / "fetch-manifest.json").read_text(encoding="utf-8"))
    results = fetch_manifest.get("results", [])

    snapshot_rows = []
    by_source: dict[str, int] = {}
    for row in results:
        output_path = Path(row["output_path"])
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        if not output_path.exists():
            continue
        rel = str(output_path.relative_to(ROOT))
        digest = sha256_file(output_path)
        item = {
            "source_id": row["source_id"],
            "label": row["label"],
            "url": row["url"],
            "local_path": rel,
            "bytes": output_path.stat().st_size,
            "sha256": digest,
            "status": row["status"],
            "content_type": row.get("content_type"),
            "captured_at": fetch_manifest.get("generated_at"),
        }
        snapshot_rows.append(item)
        by_source[row["source_id"]] = by_source.get(row["source_id"], 0) + 1

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_snapshots": len(snapshot_rows),
        "by_source": by_source,
        "snapshots": snapshot_rows,
    }

    out_json = TIER0 / "snapshot-manifest.json"
    out_md = TIER0 / "snapshot-manifest.md"
    out_json.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Tier0 Snapshot Manifest",
        "",
        f"- Generated at: `{snapshot['generated_at']}`",
        f"- Total snapshots: `{snapshot['total_snapshots']}`",
        "",
        "## Per-source counts",
        "",
    ]
    for source_id, count in sorted(by_source.items()):
        lines.append(f"- `{source_id}`: `{count}`")
    lines.extend(["", "## Snapshot rows", "", "| Source | Label | URL | Local path | Bytes |", "|---|---|---|---|---:|"])
    for row in snapshot_rows:
        lines.append(f"| {row['source_id']} | {row['label']} | {row['url']} | `{row['local_path']}` | {row['bytes']} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"total_snapshots": len(snapshot_rows), "sources": len(by_source)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
