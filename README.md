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
.\run.ps1
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

## Question bank

Questions live in `app/data/questions.json`. Refresh the bank and Microsoft Learn links:

```powershell
node scripts/generate-questions.mjs
python scripts/merge_extra_questions.py
python scripts/sync_study_urls.py
python scripts/resync_questions.py
```

`merge_extra_questions.py` adds curated items from `scripts/az900_extra_questions.json`.  
`sync_study_urls.py` rewrites broken Learn unit URLs (Microsoft renumbered many AZ-900 modules).

## Crawl questions from Microsoft Learn

Command (from the project root, with `.venv` active or `python` on PATH):

```powershell
python scripts/crawl_learn_az900.py
python scripts/crawl_questions_from_learn.py --merge
```

One-liner:

```powershell
python scripts/crawl_learn_az900.py; python scripts/crawl_questions_from_learn.py --merge
```

Preview crawled output without changing the app:

```powershell
python scripts/crawl_questions_from_learn.py
# review app/data/crawled_questions.json, then merge when ready:
python scripts/crawl_questions_from_learn.py --merge
```

### How the crawler works

1. **`crawl_learn_az900.py`** downloads the public [Microsoft Learn catalog API](https://learn.microsoft.com/api/learn/catalog?locale=en-us) (cached locally as `scripts/.learn-catalog.json`, gitignored). It selects the three official **Introduction to Cloud Infrastructure** learning paths used for AZ-900 and writes `app/data/learn_az900_paths.json` (path titles, module list, and module URLs).

2. **`crawl_questions_from_learn.py`** reads that file plus the catalog and, for each module in those paths:
   - Loads each module’s **summary** and **unit titles** (skips intro/summary/knowledge-check units).
   - Builds multiple-choice items:
     - **Unit recognition** — “Which of the following is a unit in module *X*?” with the real unit title as the correct answer and other unit titles from the same path as distractors.
     - **Module summary** — “Which statement best describes module *X*?” using the first sentence of the official module summary as the correct option.
   - Assigns an exam **domain** (`cloud_concepts`, `azure_architecture`, or `azure_management`) from the learning path title.
   - Sets each question’s **study_url** via `scripts/learn_links.py` so links point at current Learn module pages (not retired unit URLs).
   - Deduplicates by question text and writes **`app/data/crawled_questions.json`**.

3. With **`--merge`**, new questions (by unique question text) are appended to **`app/data/questions.json`**, then **`scripts/resync_questions.py`** reloads **`az900.db`** so the running app sees them without deleting the database.

Crawled questions are **metadata-based study checks** tied to Learn’s AZ-900 path structure. They are not copied from real exam items. For higher-quality additions, edit `scripts/az900_extra_questions.json` and run `python scripts/merge_extra_questions.py`.

## PDF study guide

```powershell
pip install -r requirements.txt
python scripts/crawl_learn_az900.py
python scripts/generate_study_guide_pdf.py
```

Output: [docs/AZ-900-Study-Guide.pdf](docs/AZ-900-Study-Guide.pdf) (concept reference by skill area plus official Learn paths — no practice questions).

To rebuild verified link overrides after large question changes:

```powershell
.\scripts\build_learn_url_overrides.ps1
python scripts/sync_study_urls.py
python scripts/resync_questions.py
```

## Exam alignment

Content follows the three AZ-900 skill areas:

1. Describe cloud concepts (25–30%)
2. Describe Azure architecture and services (35–40%)
3. Describe Azure management and governance (30–35%)

This app is an unofficial study aid; always use [Microsoft Learn AZ-900 training](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-900/) for authoritative objectives.
