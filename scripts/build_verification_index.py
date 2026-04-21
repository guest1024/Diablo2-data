#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFY_DIR = ROOT / "docs/tier0/verification"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    suite = load_json(VERIFY_DIR / "verification-suite.json")
    routing = load_json(VERIFY_DIR / "routing-matrix.json")
    coverage = load_json(VERIFY_DIR / "surface-coverage-report.json")
    alignment = load_json(VERIFY_DIR / "curated-surface-alignment.json")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verification_suite": {
            "passed": suite["passed"],
            "total": suite["total"],
        },
        "routing_matrix": {
            "queries": routing["routing_matrix_total_queries"] if "routing_matrix_total_queries" in routing else len(routing["cases"]),
            "curated": sum(1 for row in routing["cases"] if row["lane"] == "curated"),
            "primary": sum(1 for row in routing["cases"] if row["lane"] == "primary"),
        },
        "surface_coverage": coverage,
        "curated_surface_alignment": alignment,
    }

    (VERIFY_DIR / "verification-index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Verification Index",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Verification suite: `{suite['passed']}/{suite['total']}` PASS",
        f"- Routing matrix: `{report['routing_matrix']['queries']}` queries",
        f"- Curated lane: `{report['routing_matrix']['curated']}`",
        f"- Primary lane: `{report['routing_matrix']['primary']}`",
        f"- bilingual term map entries: `{coverage['term_map_entries']}`",
        f"- curated anchor docs/chunks: `{coverage['curated_anchor_documents']}/{coverage['curated_anchor_chunks']}`",
        f"- runtime docs/chunks: `{coverage['runtime_documents']}/{coverage['runtime_chunks']}`",
        "",
        "## Verification artifacts",
        "",
        "- `docs/tier0/verification/verification-suite.md`",
        "- `docs/tier0/verification/routing-matrix.md`",
        "- `docs/tier0/verification/surface-coverage-report.md`",
        "- `docs/tier0/verification/curated-surface-alignment.md`",
        "",
    ]
    (VERIFY_DIR / "verification-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
