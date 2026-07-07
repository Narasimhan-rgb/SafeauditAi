@echo off
setlocal EnableExtensions

REM SafeAudit AI local verification command for Windows CMD.
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "VENV_PYTHON=%BACKEND%\.venv\Scripts\python.exe"
cd /d "%BACKEND%"

if not exist "%VENV_PYTHON%" (
    echo ERROR: Backend virtual environment was not found.
    echo Run run-demo.cmd once from the repository root first.
    pause
    exit /b 1
)

REM Install the exact backend dependencies before tests so global Python is never used.
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Dependency installation failed.
    pause
    exit /b 1
)

set "PYTHONPATH=."
"%VENV_PYTHON%" -m unittest discover -s tests -v

if errorlevel 1 (
    echo.
    echo Tests failed. Read the output above.
    pause
    exit /b 1
)

echo.
echo All SafeAudit backend unit tests passed.
pause
