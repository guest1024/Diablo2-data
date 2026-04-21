#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/tier0/raw/blizzhackers-d2data/json-contents.json"
OUT_DIR = ROOT / "docs/tier0/raw/blizzhackers-d2data/json-files"
OUT_MANIFEST = ROOT / "docs/tier0/raw/blizzhackers-d2data/structured-subset-manifest.json"

KEY_FILES = {
    "armor.json",
    "misc.json",
    "levels.json",
    "itemtypes.json",
    "itemstatcost.json",
    "cubemain.json",
    "hireling.json",
    "charstats.json",
    "monstats.json",
    "monstats2.json",
    "monlvl.json",
    "monprop.json",
    "monplace.json",
    "difficultylevels.json",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    contents = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selected = [row for row in contents if row["name"] in KEY_FILES]

    downloaded = []
    failed = []
    for row in selected:
        url = row["download_url"]
        if not url:
            continue
        target = OUT_DIR / row["name"]
        last_error = None
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(url, timeout=180) as resp:
                    data = resp.read()
                target.write_bytes(data)
                downloaded.append(
                    {
                        "name": row["name"],
                        "download_url": url,
                        "path": str(target.relative_to(ROOT)),
                        "size": len(data),
                    }
                )
                last_error = None
                break
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                time.sleep(1.5 * attempt)
        if last_error is not None:
            failed.append({"name": row["name"], "download_url": url, "error": last_error})

    OUT_MANIFEST.write_text(
        json.dumps(
            {
                "downloaded_files": len(downloaded),
                "failed_files": len(failed),
                "files": downloaded,
                "failed": failed,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"downloaded_files": len(downloaded), "failed_files": len(failed)}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
