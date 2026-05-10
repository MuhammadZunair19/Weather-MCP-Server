@echo off
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Run "uv sync" first.
    exit /b 1
)

call ".\.venv\Scripts\activate.bat"
