import json
import random
import sqlite3
import time
import uuid
from typing import Any

from app.database import DOMAINS, get_connection

MOCK_EXAM_COUNT = 45
MOCK_EXAM_MINUTES = 65
PASS_SCORE_PERCENT = 70


def row_to_question(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "domain": row["domain"],
        "domain_label": DOMAINS.get(row["domain"], row["domain"]),
        "question_text": row["question_text"],
        "options": json.loads(row["options_json"]),
        "is_multi_select": bool(row["is_multi_select"]),
    }


def get_question_public(row: sqlite3.Row) -> dict[str, Any]:
    q = row_to_question(row)
    return q


def get_question_with_answer(row: sqlite3.Row) -> dict[str, Any]:
    q = row_to_question(row)
    q["correct_indices"] = json.loads(row["correct_indices_json"])
    q["explanation"] = row["explanation"]
    q["study_url"] = row["study_url"]
    return q


def _normalize_indices(indices: list[int]) -> list[int]:
    return sorted(set(int(i) for i in indices))


def grade_answer(correct: list[int], submitted: list[int]) -> bool:
    return _normalize_indices(correct) == _normalize_indices(submitted)


def build_wrong_feedback(row: sqlite3.Row, submitted: list[int]) -> dict[str, Any]:
    full = get_question_with_answer(row)
    correct = full["correct_indices"]
    options = full["options"]
    correct_labels = [options[i] for i in correct]
    submitted_labels = [options[i] for i in submitted if 0 <= i < len(options)]

    why_parts = []
    if not submitted:
        why_parts.append("You did not select an answer.")
    elif grade_answer(correct, submitted):
        why_parts.append("Your selection matches the documented Azure guidance for this scenario.")
    else:
        why_parts.append(
            "Your choice does not match the best answer for this AZ-900 objective. "
            "Compare your reasoning with the explanation below and the linked Microsoft Learn topic."
        )
        if submitted_labels:
            why_parts.append(f"You selected: {'; '.join(submitted_labels)}.")
        why_parts.append(f"The correct answer is: {'; '.join(correct_labels)}.")

    return {
        "correct": False,
        "correct_indices": correct,
        "correct_options": correct_labels,
        "submitted_indices": submitted,
        "submitted_options": submitted_labels,
        "why_wrong": " ".join(why_parts),
        "explanation": full["explanation"],
        "study_url": full["study_url"],
    }


def build_correct_feedback(row: sqlite3.Row) -> dict[str, Any]:
    full = get_question_with_answer(row)
    return {
        "correct": True,
        "correct_indices": full["correct_indices"],
        "explanation": full["explanation"],
        "study_url": full["study_url"],
    }


def create_session(mode: str, domain: str | None = None) -> dict[str, Any]:
    conn = get_connection()
    try:
        if mode == "mock":
            rows = conn.execute("SELECT id, domain FROM questions").fetchall()
            by_domain: dict[str, list[int]] = {}
            for r in rows:
                by_domain.setdefault(r["domain"], []).append(r["id"])
            picked: list[int] = []
            targets = {
                "cloud_concepts": 12,
                "azure_architecture": 18,
                "azure_management": 15,
            }
            for d, n in targets.items():
                pool = by_domain.get(d, [])
                picked.extend(random.sample(pool, min(n, len(pool))))
            remaining = MOCK_EXAM_COUNT - len(picked)
            all_ids = [r["id"] for r in rows if r["id"] not in picked]
            if remaining > 0 and all_ids:
                picked.extend(random.sample(all_ids, min(remaining, len(all_ids))))
            random.shuffle(picked)
            question_ids = picked[:MOCK_EXAM_COUNT]
            duration = MOCK_EXAM_MINUTES
            domain_filter = None
        elif mode == "practice":
            if domain and domain in DOMAINS:
                rows = conn.execute(
                    "SELECT id FROM questions WHERE domain = ? ORDER BY id",
                    (domain,),
                ).fetchall()
                domain_filter = domain
            else:
                rows = conn.execute("SELECT id FROM questions ORDER BY id").fetchall()
                domain_filter = None
            question_ids = [r["id"] for r in rows]
            random.shuffle(question_ids)
            duration = None
        else:
            raise ValueError("Invalid mode")

        session_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO sessions (
                id, mode, domain_filter, question_ids_json, started_at, duration_minutes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                mode,
                domain_filter,
                json.dumps(question_ids),
                time.time(),
                duration,
            ),
        )
        conn.commit()
        return {
            "session_id": session_id,
            "mode": mode,
            "domain": domain_filter,
            "total_questions": len(question_ids),
            "duration_minutes": duration,
            "pass_score_percent": PASS_SCORE_PERCENT,
        }
    finally:
        conn.close()


def get_session(session_id: str) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    finally:
        conn.close()


def get_session_question(session_id: str, index: int) -> dict[str, Any] | None:
    session = get_session(session_id)
    if not session:
        return None
    ids = json.loads(session["question_ids_json"])
    if index < 0 or index >= len(ids):
        return None
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (ids[index],)).fetchone()
        if not row:
            return None
        answers = json.loads(session["answers_json"])
        prior = answers.get(str(index))
        payload = {
            "index": index,
            "total": len(ids),
            "question": get_question_public(row),
            "answered": prior is not None,
            "prior_submission": prior,
        }
        if prior is not None:
            selected = prior.get("selected", [])
            if prior.get("correct"):
                payload["feedback"] = build_correct_feedback(row)
                payload["is_correct"] = True
            else:
                payload["feedback"] = build_wrong_feedback(row, selected)
                payload["is_correct"] = False
        return payload
    finally:
        conn.close()


def submit_answer(session_id: str, index: int, selected: list[int]) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    ids = json.loads(session["question_ids_json"])
    if index < 0 or index >= len(ids):
        return {"error": "Invalid question index"}

    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (ids[index],)).fetchone()
        if not row:
            return {"error": "Question not found"}

        correct = json.loads(row["correct_indices_json"])
        is_correct = grade_answer(correct, selected)
        feedback = build_correct_feedback(row) if is_correct else build_wrong_feedback(row, selected)

        answers = json.loads(session["answers_json"])
        answers[str(index)] = {
            "selected": _normalize_indices(selected),
            "correct": is_correct,
        }
        conn.execute(
            "UPDATE sessions SET answers_json = ? WHERE id = ?",
            (json.dumps(answers), session_id),
        )
        conn.commit()

        return {
            "index": index,
            "is_correct": is_correct,
            "feedback": feedback,
        }
    finally:
        conn.close()


def complete_session(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    ids = json.loads(session["question_ids_json"])
    answers = json.loads(session["answers_json"])

    correct_count = sum(1 for a in answers.values() if a.get("correct"))
    answered = len(answers)
    total = len(ids)
    score = round((correct_count / total) * 100) if total else 0
    passed = score >= PASS_SCORE_PERCENT

    conn = get_connection()
    try:
        conn.execute("UPDATE sessions SET completed = 1 WHERE id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()

    wrong_details = []
    conn = get_connection()
    try:
        for i, qid in enumerate(ids):
            ans = answers.get(str(i))
            if ans and not ans.get("correct"):
                row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
                if row:
                    wrong_details.append(
                        {
                            "index": i,
                            "question_text": row["question_text"],
                            **build_wrong_feedback(row, ans.get("selected", [])),
                        }
                    )
    finally:
        conn.close()

    return {
        "mode": session["mode"],
        "total": total,
        "answered": answered,
        "correct_count": correct_count,
        "score_percent": score,
        "passed": passed,
        "pass_threshold": PASS_SCORE_PERCENT,
        "wrong_questions": wrong_details,
    }
