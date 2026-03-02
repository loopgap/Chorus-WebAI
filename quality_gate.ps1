param()

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "Running static checks" -ForegroundColor Cyan
& $PythonExe -m ruff check .
if ($LASTEXITCODE -ne 0) { throw "Static checks failed with exit code $LASTEXITCODE" }

Write-Host "Running unit tests" -ForegroundColor Cyan
& $PythonExe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Unit tests failed with exit code $LASTEXITCODE" }

Write-Host "Running performance checks" -ForegroundColor Cyan
& $PythonExe perf_check.py
if ($LASTEXITCODE -ne 0) { throw "Performance checks failed with exit code $LASTEXITCODE" }

Write-Host "All quality gates passed" -ForegroundColor Green
