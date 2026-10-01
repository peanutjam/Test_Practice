$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
}

.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
