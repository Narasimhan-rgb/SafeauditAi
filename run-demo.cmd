@echo off
setlocal EnableExtensions

REM SafeAudit AI local dashboard demo launcher for Windows CMD.
REM Double-click this file or run it from Command Prompt in the repository root.
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "VENV_PYTHON=%BACKEND%\.venv\Scripts\python.exe"

where py >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python launcher ^(py^) was not found.
    echo Install Python 3.11 or later and select "Add Python to PATH" during installation.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: npm was not found.
    echo Install Node.js LTS, close Command Prompt, then run this file again.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo   SafeAudit AI - local dashboard demo setup
echo ==================================================
echo.

cd /d "%BACKEND%"

REM Rebuild a broken or incomplete environment automatically.
if not exist "%VENV_PYTHON%" (
    echo Creating Python virtual environment...
    if exist ".venv" rmdir /s /q ".venv"
    py -m venv .venv
    if errorlevel 1 goto :python_error
)

REM Do not rely on activate.bat. Use the venv interpreter directly.
echo Installing backend packages...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :python_error
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto :python_error

if not exist ".env" (
    copy .env.example .env >nul
)

REM Keep demo mode enabled without adding duplicate settings.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='.env'; $c=Get-Content $p; if ($c -match '^\s*DEMO_MODE\s*=') { $c = $c -replace '^\s*DEMO_MODE\s*=.*$', 'DEMO_MODE=true'; Set-Content -Path $p -Value $c } else { Add-Content -Path $p -Value 'DEMO_MODE=true' }"

"%VENV_PYTHON%" -m app.seed_demo
if errorlevel 1 goto :python_error

cd /d "%FRONTEND%"
if not exist "node_modules" (
    echo Installing frontend packages. This can take a few minutes on the first run...
    call npm install
    if errorlevel 1 goto :node_error
)

echo.
echo Starting backend and frontend in two new windows...
start "SafeAudit Backend" cmd.exe /k call "%ROOT%start-backend.cmd"
start "SafeAudit Frontend" cmd.exe /k call "%ROOT%start-frontend.cmd"

echo.
echo The dashboard will open at http://localhost:5173
start "SafeAudit Dashboard" http://localhost:5173

echo.
echo Done. Keep the two SafeAudit command windows open while using the dashboard.
pause
exit /b 0

:python_error
echo.
echo Backend setup failed. Read the error above, then run this file again.
pause
exit /b 1

:node_error
echo.
echo Frontend setup failed. Read the error above, then run this file again.
pause
exit /b 1
