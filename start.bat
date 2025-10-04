@echo off
echo ============================================
echo      CarePath - Starting Application
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server...
start "CarePath Backend" cmd /k "echo Starting backend... && python backend.py"
timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend...
start "CarePath Frontend" cmd /k "echo Starting frontend... && cd carepath-ui && npm run dev"

echo.
echo ============================================
echo CarePath is starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Two windows will open:
echo - CarePath Backend (Python server)
echo - CarePath Frontend (React app)
echo.
echo Wait 10-15 seconds, then open:
echo http://localhost:5173
echo.
echo Close this window or press Ctrl+C in the
echo backend/frontend windows to stop.
echo ============================================
echo.
pause
