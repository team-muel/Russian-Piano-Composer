<#
.SYNOPSIS
    Local CI verification script for Russian Piano Composer.

.DESCRIPTION
    Runs lint (ruff), type checking (mypy), and tests (pytest)
    against the project. Equivalent to the GitHub Actions CI pipeline.

    This script should be run from within the project's virtual environment.

.EXAMPLE
    .\.venv\Scripts\Activate.ps1
    powershell -File ci.ps1
#>

$ErrorActionPreference = "Stop"

# Activate virtual environment if not already active
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found at .venv/" -ForegroundColor Red
    Write-Host "Create it with: py -3.12 -m venv .venv" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Russian Piano Composer — Local CI"      -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Lint
Write-Host "[1/3] Running ruff lint..." -ForegroundColor Yellow
& $venvPython -m ruff check src/ tests/
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: ruff lint failed." -ForegroundColor Red
    exit 1
}
Write-Host "PASS: ruff lint" -ForegroundColor Green
Write-Host ""

# Step 2: Type check
Write-Host "[2/3] Running mypy type check..." -ForegroundColor Yellow
& $venvPython -m mypy src/
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: mypy type check failed." -ForegroundColor Red
    exit 1
}
Write-Host "PASS: mypy type check" -ForegroundColor Green
Write-Host ""

# Step 3: Tests
Write-Host "[3/3] Running pytest..." -ForegroundColor Yellow
& $venvPython -m pytest tests/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: pytest failed." -ForegroundColor Red
    exit 1
}
Write-Host "PASS: pytest" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host " All CI checks passed!"                   -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
