@echo off
title LLM Council - Shutdown
echo ============================================================
echo  Stopping LLM Council servers...
echo ============================================================
echo.

:: Kill processes on port 8001 (backend)
echo [1/2] Stopping Backend (port 8001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo       Killed process %%a
)
echo       Done.

:: Kill processes on port 5173 (frontend)
echo [2/2] Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo       Killed process %%a
)
echo       Done.

echo.
echo ============================================================
echo  All LLM Council servers have been stopped.
echo ============================================================
pause
