#!/usr/bin/env python3
"""
Build practice questions from Microsoft Learn AZ-900 module and unit titles.

Uses the public Learn catalog API (same source as crawl_learn_az900.py).
Output: app/data/crawled_questions.json — merge with merge_extra_questions.py or --merge.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from learn_links import resolve_study_url  # noqa: E402

CATALOG_URL = "https://learn.microsoft.com/api/learn/catalog?locale=en-us"
CACHE = Path(__file__).resolve().parent / ".learn-catalog.json"
OUT = ROOT / "app" / "data" / "crawled_questions.json"
PATHS_FILE = ROOT / "app" / "data" / "learn_az900_paths.json"

DOMAIN_BY_PATH_KEYWORD = [
    ("cloud concept", "cloud_concepts"),
    ("architecture and service", "azure_architecture"),
    ("management and governance", "azure_management"),
]


def load_catalog() -> dict:
    if not CACHE.exists():
        CACHE.write_bytes(urllib.request.urlopen(CATALOG_URL, timeout=120).read())
    return json.loads(CACHE.read_text(encoding="utf-8-sig"))


def domain_for_path(title: str) -> str:
    lower = title.lower()
    for needle, domain in DOMAIN_BY_PATH_KEYWORD:
        if needle in lower:
            return domain
    return "azure_architecture"


def module_slug_from_url(url: str) -> str:
    match = re.search(r"/training/modules/([^/]+)/", url)
    return match.group(1) if match else ""


def pick_distractors(pool: list[str], correct: str, count: int = 3) -> list[str]:
    choices = [t for t in pool if t != correct]
    random.shuffle(choices)
    return choices[:count]


def build_questions(catalog: dict, paths_payload: dict) -> list[dict]:
    modules_by_url = {}
    for module in catalog.get("modules", []):
        url = (module.get("url") or "").split("?")[0].rstrip("/") + "/"
        modules_by_url[url] = module

    units_by_uid = {u["uid"]: u for u in catalog.get("units", [])}

    all_unit_titles: list[str] = []
    questions: list[dict] = []

    for path in paths_payload.get("learning_paths", []):
        domain = domain_for_path(path.get("title", ""))
        path_units: list[str] = []

        for mod_ref in path.get("modules", []):
            mod_url = mod_ref.get("url", "").split("?")[0].rstrip("/") + "/"
            module = modules_by_url.get(mod_url)
            if not module:
                continue

            module_title = module.get("title", mod_ref.get("title", "Azure module"))
            summary = (module.get("summary") or "").strip()
            unit_uids = module.get("units") or []
            unit_titles = []
            for uid in unit_uids:
                unit = units_by_uid.get(uid)
                if not unit:
                    continue
                title = unit.get("title", "").strip()
                if title and title.lower() not in {"introduction", "summary", "knowledge check", "module assessment"}:
                    unit_titles.append(title)
                    path_units.append(title)
                    all_unit_titles.append(title)

            if not unit_titles:
                continue

            for unit_title in unit_titles:
                distractors = pick_distractors(path_units, unit_title)
                while len(distractors) < 3:
                    distractors.append("Unrelated on-premises tape backup")
                options = distractors + [unit_title]
                random.shuffle(options)
                correct_index = options.index(unit_title)
                explanation = (
                    f"'{unit_title}' is a unit in the Learn module '{module_title}'. "
                    + (summary if summary else "Review this module on Microsoft Learn.")
                )
                slug = module_slug_from_url(mod_url)
                study_url = resolve_study_url(f"https://learn.microsoft.com/en-us/training/modules/{slug}/")
                questions.append(
                    {
                        "domain": domain,
                        "question": f"Which of the following is a unit in the Microsoft Learn module '{module_title}'?",
                        "options": options,
                        "correct": [correct_index],
                        "explanation": explanation,
                        "study_url": study_url,
                        "multi_select": False,
                        "source": f"learn:{slug}:{unit_title}",
                    }
                )

            if summary:
                true_statement = summary.split(".")[0].strip() + "."
                false_pool = [
                    "Azure eliminates all customer responsibility for data classification.",
                    "Hybrid cloud means using only a single public region.",
                    "IaaS requires the provider to manage all application source code.",
                ]
                options = false_pool + [true_statement]
                random.shuffle(options)
                questions.append(
                    {
                        "domain": domain,
                        "question": f"Which statement best describes the Learn module '{module_title}'?",
                        "options": options,
                        "correct": [options.index(true_statement)],
                        "explanation": summary,
                        "study_url": resolve_study_url(
                            f"https://learn.microsoft.com/en-us/training/modules/{module_slug_from_url(mod_url)}/"
                        ),
                        "multi_select": False,
                        "source": f"learn-summary:{module_slug_from_url(mod_url)}",
                    }
                )

    # De-dupe by question text
    seen: set[str] = set()
    unique: list[dict] = []
    for q in questions:
        key = q["question"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
    return unique


def merge_into_bank(crawled: list[dict]) -> None:
    bank_path = ROOT / "app" / "data" / "questions.json"
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    existing = {q["question"].strip().lower() for q in bank}
    next_id = max((q["id"] for q in bank), default=0) + 1
    added = 0
    for item in crawled:
        key = item["question"].strip().lower()
        if key in existing:
            continue
        bank.append(
            {
                "id": next_id,
                "domain": item["domain"],
                "question": item["question"],
                "options": item["options"],
                "correct": item["correct"],
                "explanation": item["explanation"],
                "study_url": item["study_url"],
                "multi_select": bool(item.get("multi_select")),
            }
        )
        existing.add(key)
        next_id += 1
        added += 1
    bank_path.write_text(json.dumps(bank, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {added} crawled questions ({len(bank)} total).")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "resync_questions.py")], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl AZ-900 practice questions from Microsoft Learn catalog.")
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Append new questions to app/data/questions.json and resync az900.db",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for option shuffle")
    args = parser.parse_args()
    random.seed(args.seed)

    if not PATHS_FILE.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "crawl_learn_az900.py")], check=True)

    catalog = load_catalog()
    paths_payload = json.loads(PATHS_FILE.read_text(encoding="utf-8"))
    crawled = build_questions(catalog, paths_payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(crawled, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(crawled)} questions to {OUT}")

    if args.merge:
        merge_into_bank(crawled)


if __name__ == "__main__":
    main()
