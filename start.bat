@echo off
REM Infini Think Application Launcher
REM This script starts both Flask Backend and React Frontend

echo.
echo ========================================
echo   INFINI THINK - Starting Application
echo ========================================
echo.

REM Check if Node is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    pause
    exit /b 1
)

REM Start Flask Backend
echo [1/2] Starting Flask Backend on port 5000...
start "Infini Think Backend" cmd /k "cd /d "%~dp0" && venv\Scripts\python.exe run_flask.py"
timeout /t 3 /nobreak

REM Start React Frontend
echo [2/2] Starting React Frontend on port 3000...
start "Infini Think Frontend" cmd /k "cd /d "%~dp0frontend" && npm start"
timeout /t 5 /nobreak

echo.
echo ========================================
echo   APPLICATION STARTED SUCCESSFULLY
echo ========================================
echo.
echo FRONTEND: http://localhost:3000
echo BACKEND:  http://localhost:5000
echo.
echo Both windows will stay open. Close them to stop the application.
echo.
pause
