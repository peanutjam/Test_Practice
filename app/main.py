from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.database import DOMAINS, init_db
from app import quiz

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR.parent / "static"
TEMPLATES_DIR = APP_DIR.parent / "templates"

app = FastAPI(title="AZ-900 Exam Prep", version="1.0.0)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StartSessionBody(BaseModel):
    mode: str = Field(description="mock or practice")
    domain: str | None = None


class SubmitBody(BaseModel):
    selected: list[int] = Field(default_factory=list)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse((TEMPLATES_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/api/meta")
def meta() -> dict:
    from app.database import get_connection

    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    finally:
        conn.close()
    return {
        "exam_name": "Microsoft Azure Fundamentals (AZ-900)",
        "mock_question_count": quiz.MOCK_EXAM_COUNT,
        "mock_duration_minutes": quiz.MOCK_EXAM_MINUTES,
        "pass_score_percent": quiz.PASS_SCORE_PERCENT,
        "question_bank_size": total,
        "domains": [{"id": k, "label": v} for k, v in DOMAINS.items()],
    }


@app.post("/api/sessions")
def start_session(body: StartSessionBody) -> dict:
    if body.mode not in ("mock", "practice"):
        raise HTTPException(400, "mode must be mock or practice")
    if body.domain and body.domain not in DOMAINS:
        raise HTTPException(400, "Invalid domain")
    return quiz.create_session(body.mode, body.domain)


@app.get("/api/sessions/{session_id}/questions/{index}")
def get_question(session_id: str, index: int) -> dict:
    data = quiz.get_session_question(session_id, index)
    if not data:
        raise HTTPException(404, "Question or session not found")
    session = quiz.get_session(session_id)
    return {
        **data,
        "mode": session["mode"],
        "duration_minutes": session["duration_minutes"],
        "started_at": session["started_at"],
    }


@app.post("/api/sessions/{session_id}/questions/{index}/submit")
def submit(session_id: str, index: int, body: SubmitBody) -> dict:
    result = quiz.submit_answer(session_id, index, body.selected)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.post("/api/sessions/{session_id}/complete")
def complete(session_id: str) -> dict:
    result = quiz.complete_session(session_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
