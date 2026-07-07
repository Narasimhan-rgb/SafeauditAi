@echo off
setlocal EnableExtensions

REM Start SafeAudit AI for an authorised local PPE pilot.
REM Before running: set MODEL_PATH and DEMO_MODE=false in backend\.env.
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "VENV_PYTHON=%BACKEND%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo ERROR: Backend environment was not found.
    echo Run run-demo.cmd once first to create the local environment.
    pause
    exit /b 1
)

if not exist "%BACKEND%\.env" (
    echo ERROR: backend\.env was not found.
    pause
    exit /b 1
)

findstr /r /c:"^[ ]*MODEL_PATH[ ]*=[ ]*.[^ ]*" "%BACKEND%\.env" >nul
if errorlevel 1 (
    echo ERROR: MODEL_PATH is missing or empty in backend\.env.
    pause
    exit /b 1
)

findstr /r /i /c:"^[ ]*DEMO_MODE[ ]*=[ ]*false[ ]*$" "%BACKEND%\.env" >nul
if errorlevel 1 (
    echo ERROR: Set DEMO_MODE=false in backend\.env before starting a pilot.
    pause
    exit /b 1
)

if not exist "%FRONTEND%\node_modules" (
    echo ERROR: Frontend packages were not found.
    echo Run run-demo.cmd once first.
    pause
    exit /b 1
)

echo.
echo Starting SafeAudit AI in local pilot mode...
start "SafeAudit Backend" cmd.exe /k call "%ROOT%start-backend.cmd"
start "SafeAudit Frontend" cmd.exe /k call "%ROOT%start-frontend.cmd"
start "SafeAudit Dashboard" http://localhost:5173

echo.
echo Dashboard opened at http://localhost:5173
pause
