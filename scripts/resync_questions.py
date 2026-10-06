#!/usr/bin/env python3
"""Reload SQLite question bank from app/data/questions.json."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database import DB_PATH, QUESTIONS_PATH  # noqa: E402


def main() -> None:
    raw = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM questions")
        for q in raw:
            conn.execute(
                """
                INSERT INTO questions (
                    id, domain, question_text, options_json, correct_indices_json,
                    explanation, study_url, is_multi_select
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    q["id"],
                    q["domain"],
                    q["question"],
                    json.dumps(q["options"]),
                    json.dumps(q["correct"]),
                    q["explanation"],
                    q["study_url"],
                    1 if q.get("multi_select") else 0,
                ),
            )
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        print(f"Reloaded {count} questions into {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
