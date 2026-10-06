$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Get-PythonLauncher {
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py -and $py.Source -notlike "*\WindowsApps\*") {
    return @{ Exe = $py.Source; Prefix = @("-3") }
  }

  foreach ($name in @("python", "python3")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike "*\WindowsApps\*") {
      return @{ Exe = $cmd.Source; Prefix = @() }
    }
  }

  $local = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1
  if ($local) {
    return @{ Exe = $local.FullName; Prefix = @() }
  }

  throw @"
Python 3.10+ is not installed. WindowsApps\python.exe is a Store alias, not an interpreter.
Install it with: winget install -e --id Python.Python.3.12
"@
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  $python = Get-PythonLauncher
  & $python.Exe @($python.Prefix + @("-m", "venv", ".venv"))
  if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "venv creation failed. Install Python 3.10+ and run this script again."
  }
  & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
