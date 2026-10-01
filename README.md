# AZ-900 Exam Prep

Local web app for **Microsoft Azure Fundamentals (AZ-900)** practice and timed mock exams.

## Features

- **Mock exam** — 45 questions, 65-minute timer, domain-weighted selection (aligned to exam skill areas)
- **Practice mode** — study by domain or the full bank
- **Immediate feedback** — on incorrect answers: correct choice, explanation, why your answer missed, and a **Microsoft Learn** link
- **Results review** — score, pass/fail (70% threshold, similar to ~700/1000), and a review list of missed questions

## Requirements

- Python 3.10+ (recommended: install from [python.org](https://www.python.org/downloads/) and enable “Add to PATH”)

## Quick start

```powershell
cd "C:\Users\James Ma\Projects\az900-prep"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

## Question bank

Questions live in `app/data/questions.json` (generated from `scripts/generate-questions.mjs`):

```powershell
node scripts/generate-questions.mjs
```

Delete `az900.db` after editing questions so the app re-seeds on next startup.

## Exam alignment

Content follows the three AZ-900 skill areas:

1. Describe cloud concepts (25–30%)
2. Describe Azure architecture and services (35–40%)
3. Describe Azure management and governance (30–35%)

This app is an unofficial study aid; always use [Microsoft Learn AZ-900 training](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-900/) for authoritative objectives.
