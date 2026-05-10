if (-not (Test-Path ".venv\\Scripts\\Activate.ps1")) {
    Write-Error "Virtual environment not found. Run 'uv sync' first."
    exit 1
}

. ".\.venv\Scripts\Activate.ps1"
