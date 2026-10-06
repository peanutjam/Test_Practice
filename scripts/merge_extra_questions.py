#!/usr/bin/env python3
"""Merge curated extra questions and refresh Microsoft Learn links."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from learn_links import resolve_study_url  # noqa: E402

QUESTIONS_PATH = ROOT / "app" / "data" / "questions.json"
EXTRA_PATH = ROOT / "scripts" / "az900_extra_questions.json"


def main() -> None:
    base = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    extra = json.loads(EXTRA_PATH.read_text(encoding="utf-8"))

    existing_text = {q["question"].strip().lower() for q in base}
    next_id = max(q["id"] for q in base) + 1 if base else 1
    added = 0

    for item in extra:
        key = item["question"].strip().lower()
        if key in existing_text:
            continue
        base.append(
            {
                "id": next_id,
                "domain": item["domain"],
                "question": item["question"],
                "options": item["options"],
                "correct": item["correct"],
                "explanation": item["explanation"],
                "study_url": resolve_study_url(item["study_url"]),
                "multi_select": bool(item.get("multi_select")),
            }
        )
        existing_text.add(key)
        next_id += 1
        added += 1

    for question in base:
        question["study_url"] = resolve_study_url(question["study_url"])

    QUESTIONS_PATH.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")
    print(f"Added {added} questions; total {len(base)} in {QUESTIONS_PATH}")

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "resync_questions.py")],
        check=True,
    )


if __name__ == "__main__":
    main()
