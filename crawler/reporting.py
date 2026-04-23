from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def filter_catalog_rows(
    catalog: dict[str, dict[str, Any]],
    *,
    source_id: str | None = None,
    capture_status: str | None = None,
    lifecycle_status: str | None = None,
    snapshot_only: bool = False,
) -> list[dict[str, Any]]:
    rows = list(catalog.values())
    if source_id:
        rows = [row for row in rows if row.get("source_id") == source_id]
    if capture_status:
        rows = [row for row in rows if row.get("capture_status") == capture_status]
    if lifecycle_status:
        rows = [row for row in rows if row.get("lifecycle_status") == lifecycle_status]
    if snapshot_only:
        rows = [row for row in rows if row.get("snapshot_path")]
    rows.sort(key=lambda row: (row.get("source_id", ""), row.get("url", "")))
    return rows


def build_catalog_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "capture": Counter(), "lifecycle": Counter()})
    total_capture = Counter()
    total_lifecycle = Counter()

    for row in rows:
        source_id = row.get("source_id", "unknown")
        capture = row.get("capture_status", "unknown")
        lifecycle = row.get("lifecycle_status", "unknown")
        by_source[source_id]["count"] += 1
        by_source[source_id]["capture"][capture] += 1
        by_source[source_id]["lifecycle"][lifecycle] += 1
        total_capture[capture] += 1
        total_lifecycle[lifecycle] += 1

    normalized = {
        source_id: {
            "count": stats["count"],
            "capture": dict(stats["capture"]),
            "lifecycle": dict(stats["lifecycle"]),
        }
        for source_id, stats in sorted(by_source.items())
    }
    return {
        "total": len(rows),
        "capture": dict(total_capture),
        "lifecycle": dict(total_lifecycle),
        "by_source": normalized,
    }


def render_catalog_markdown(summary: dict[str, Any], rows: list[dict[str, Any]], limit: int = 20) -> str:
    lines = [
        "# Snapshot Catalog Report",
        "",
        f"- Total rows: `{summary['total']}`",
        f"- Capture statuses: `{summary['capture']}`",
        f"- Lifecycle statuses: `{summary['lifecycle']}`",
        "",
        "## By Source",
        "",
        "| Source | Count | Capture | Lifecycle |",
        "| --- | ---: | --- | --- |",
    ]
    for source_id, stats in summary["by_source"].items():
        lines.append(f"| {source_id} | {stats['count']} | `{stats['capture']}` | `{stats['lifecycle']}` |")

    lines.extend([
        "",
        f"## Sample Rows (first {min(limit, len(rows))})",
        "",
        "| Source | Title | Capture | Lifecycle | Snapshot | URL |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in rows[:limit]:
        lines.append(
            f"| {row.get('source_id','')} | {str(row.get('title','')).replace('|','/')} | {row.get('capture_status','')} | {row.get('lifecycle_status','')} | {row.get('snapshot_path','')} | {row.get('url','')} |"
        )
    return "\n".join(lines) + "\n"
