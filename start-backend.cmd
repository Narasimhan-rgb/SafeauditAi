@echo off
setlocal EnableExtensions
cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Backend environment was not found.
    echo Run run-demo.cmd once from the repository root first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000
