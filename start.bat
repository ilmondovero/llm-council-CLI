@echo off
title LLM Council - Startup
echo ============================================================
echo  LLM Council - CLI-Based Multi-Model Deliberation System
echo ============================================================
echo.

:: Check if Python is available
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

:: Check if Node.js is available
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js/npm not found. Please install Node.js
    pause
    exit /b 1
)

:: Change to script directory
cd /d "%~dp0"

:: Kill any existing instances on our ports
echo [1/5] Cleaning up previous instances...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1
echo       Done.

echo.
echo [2/5] Checking Python dependencies...
py -c "import fastapi, uvicorn, httpx, pydantic" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo       Installing Python dependencies...
    py -m pip install fastapi uvicorn httpx pydantic --quiet
)
echo       Done.

echo.
echo [3/5] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo       Installing npm packages...
    cd frontend
    npm install --silent
    cd ..
)
echo       Done.

echo.
echo [4/5] Starting Backend Server (port 8001)...
start "LLM Council Backend" cmd /c "py -m backend.main"

:: Wait for backend to start
echo       Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

:: Check if backend is running
curl -s http://localhost:8001/ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       [WARNING] Backend may not have started correctly
) else (
    echo       Backend is running at http://localhost:8001
)

echo.
echo [5/5] Starting Frontend Server (port 5173)...
start "LLM Council Frontend" cmd /c "cd frontend && npm run dev"

:: Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo  LLM Council is now running!
echo ============================================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8001
echo.
echo  Council Members:
echo    - Gemini CLI  (Google)
echo    - Codex CLI   (OpenAI)
echo    - Claude CLI  (Anthropic)
echo.
echo  Press any key to open the browser...
pause >nul

:: Open browser
start http://localhost:5173

echo.
echo  To stop the servers, run stop.bat or close the terminal windows.
echo.
