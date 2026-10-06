#!/usr/bin/env python3
"""
Fetch AZ-900-related modules from the public Microsoft Learn catalog API.

Used to keep learning-path references and study guide metadata aligned with Learn.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "data" / "learn_az900_paths.json"
CATALOG_URL = "https://learn.microsoft.com/api/learn/catalog?locale=en-us"
CACHE = Path(__file__).resolve().parent / ".learn-catalog.json"

PATH_UIDS = [
    "learn.wwl.microsoft-azure-fundamentals-describe-cloud-concepts",
    "learn.wwl.azure-fundamentals-describe-azure-architecture-services",
    "learn.wwl.describe-azure-management-governance",
]


def load_catalog() -> dict:
    if not CACHE.exists():
        CACHE.write_bytes(urllib.request.urlopen(CATALOG_URL, timeout=120).read())
    return json.loads(CACHE.read_text(encoding="utf-8"))


def main() -> None:
    catalog = load_catalog()
    modules_by_uid = {m["uid"]: m for m in catalog.get("modules", [])}
    paths_by_uid = {p["uid"]: p for p in catalog.get("learningPaths", [])}

    payload = {
        "source": CATALOG_URL,
        "exam_page": "https://learn.microsoft.com/en-us/credentials/certifications/exams/az-900/",
        "learning_paths": [],
    }

    for path_uid in PATH_UIDS:
        path = paths_by_uid.get(path_uid)
        if not path:
            continue
        modules = []
        for module_uid in path.get("modules") or []:
            module = modules_by_uid.get(module_uid)
            if not module:
                continue
            modules.append(
                {
                    "title": module.get("title"),
                    "url": (module.get("url") or "").split("?")[0],
                    "duration_minutes": module.get("duration_in_minutes"),
                }
            )
        payload["learning_paths"].append(
            {
                "title": path.get("title"),
                "url": (path.get("url") or "").split("?")[0],
                "modules": modules,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(payload['learning_paths'])} paths)")


if __name__ == "__main__":
    main()
