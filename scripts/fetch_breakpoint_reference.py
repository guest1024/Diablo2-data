#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL = "https://diablo2.io/forums/character-info-t850955.html"
OUT_PATH = ROOT / "docs/tier0/raw/diablo2-io/character-info.html"
MANIFEST_PATH = ROOT / "docs/tier0/raw/diablo2-io/character-info-manifest.json"


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://diablo2.io/",
        },
    )
    with urllib.request.urlopen(request, timeout=180) as resp:
        content = resp.read()
        content_type = resp.headers.get("Content-Type", "")
    OUT_PATH.write_bytes(content)
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "url": URL,
                "path": str(OUT_PATH.relative_to(ROOT)),
                "size": len(content),
                "content_type": content_type,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"path": str(OUT_PATH.relative_to(ROOT)), "size": len(content)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
