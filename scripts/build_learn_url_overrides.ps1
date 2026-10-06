$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root ".venv\Scripts\python.exe"
Set-Location $root
$pairs = & $python -c @"
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(r'$root') / 'scripts'))
from learn_links import MODULE_ALIASES, UNIT_ALIASES, UNIT_RELOCATIONS, _modules_by_slug

qs = json.loads((Path(r'$root') / 'app/data/questions.json').read_text(encoding='utf-8'))
pairs = set()
for q in qs:
    m = re.match(r'https://learn\.microsoft\.com/en-us/training/modules/([^/]+)(?:/\d+-(.+))?', q['study_url'].split('?')[0].rstrip('/'))
    if not m:
        continue
    mod, unit = m.group(1), m.group(2)
    if not unit:
        continue
    if unit in UNIT_RELOCATIONS:
        mod, unit = UNIT_RELOCATIONS[unit]
    else:
        mod = MODULE_ALIASES.get(mod, mod)
        unit = UNIT_ALIASES.get(unit, unit)
    pairs.add((mod, unit))

mods = _modules_by_slug()
for mod, unit in sorted(pairs):
    print(f'{mod}|{unit}')
"@

$overrides = @{}
foreach ($line in $pairs) {
    if (-not $line) { continue }
    $parts = $line -split '\|', 2
    $mod = $parts[0]
    $unit = $parts[1]
    $found = $null
    foreach ($i in 1..15) {
        $url = "https://learn.microsoft.com/en-us/training/modules/$mod/$i-$unit"
        try {
            $null = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 20
            $found = $url
            break
        } catch {
            Start-Sleep -Milliseconds 200
        }
    }
    if ($found) {
        $overrides["$mod/$unit"] = $found
        Write-Host "OK $mod/$unit"
    } else {
        $root = "https://learn.microsoft.com/en-us/training/modules/$mod/"
        try {
            $null = Invoke-WebRequest -Uri $root -Method Head -UseBasicParsing -TimeoutSec 20
            $overrides["$mod/$unit"] = $root
            Write-Host "ROOT $mod/$unit"
        } catch {
            Write-Warning "MISSING $mod/$unit"
        }
    }
    Start-Sleep -Milliseconds 300
}

$out = Join-Path $PSScriptRoot "learn_url_overrides.json"
$overrides | ConvertTo-Json -Depth 3 | Set-Content -Path $out -Encoding utf8
Write-Host "Wrote $($overrides.Count) overrides to $out"
