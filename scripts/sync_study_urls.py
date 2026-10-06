#!/usr/bin/env python3
"""Rewrite question study_url values to current Microsoft Learn locations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from learn_links import resolve_study_url  # noqa: E402

QUESTIONS_PATH = ROOT / "app" / "data" / "questions.json"


def main() -> None:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    changed = 0
    for question in questions:
        old = question["study_url"]
        new = resolve_study_url(old)
        if new != old:
            question["study_url"] = new
            changed += 1
    QUESTIONS_PATH.write_text(json.dumps(questions, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {changed} study URLs in {QUESTIONS_PATH} ({len(questions)} questions).")


if __name__ == "__main__":
    main()
