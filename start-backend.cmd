@echo off
setlocal EnableExtensions
set "BACKEND=%~dp0backend"
set "VENV_PYTHON=%BACKEND%\.venv\Scripts\python.exe"

cd /d "%BACKEND%"

if not exist "%VENV_PYTHON%" (
    echo ERROR: Backend environment was not found.
    echo Run run-demo.cmd once from the repository root first.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -m uvicorn app.main:app --reload --port 8000
