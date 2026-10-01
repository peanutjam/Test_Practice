import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "az900.db"
QUESTIONS_PATH = Path(__file__).resolve().parent / "data" / "questions.json"

DOMAINS = {
    "cloud_concepts": "Describe cloud concepts (25–30%)",
    "azure_architecture": "Describe Azure architecture and services (35–40%)",
    "azure_management": "Describe Azure management and governance (30–35%)",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                domain TEXT NOT NULL,
                question_text TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_indices_json TEXT NOT NULL,
                explanation TEXT NOT NULL,
                study_url TEXT NOT NULL,
                is_multi_select INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                domain_filter TEXT,
                question_ids_json TEXT NOT NULL,
                answers_json TEXT NOT NULL DEFAULT '{}',
                started_at REAL NOT NULL,
                duration_minutes INTEGER,
                completed INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            _seed_questions(conn)
        conn.commit()
    finally:
        conn.close()


def _seed_questions(conn: sqlite3.Connection) -> None:
    raw = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
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
