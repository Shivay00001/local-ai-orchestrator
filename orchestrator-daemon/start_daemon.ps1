$ErrorActionPreference = "Stop"

Write-Host "Starting Local AI Orchestrator Daemon..." -ForegroundColor Cyan

# Check for venv
if (Test-Path ".venv") {
    Write-Host "Activating virtual environment (.venv)..."
    & .venv\Scripts\Activate.ps1
} elseif (Test-Path "venv") {
    Write-Host "Activating virtual environment (venv)..."
    & venv\Scripts\Activate.ps1
}

# Add current directory to PYTHONPATH so imports work
$env:PYTHONPATH = $PWD

# Run the server
Write-Host "Starting Uvicorn server on port 8000..."
python src/main.py
