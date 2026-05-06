@echo off
setlocal EnableDelayedExpansion
title Blog Extractor

:: ── Install uv if missing ──────────────────────────────────────────────────
where uv >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install uv. Check your internet connection.
        pause
        exit /b 1
    )
)

:: ── Sync dependencies ──────────────────────────────────────────────────────
echo Installing dependencies...
uv sync --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency install failed. Check your internet connection.
    pause
    exit /b 1
)

:: ── Install Playwright Chromium browser (once) ────────────────────────────
echo Checking Playwright browser...
uv run playwright install chromium --quiet 2>nul

:: ── Find Chrome ────────────────────────────────────────────────────────────
set CHROME=
for %%P in (
    "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) do (
    if exist %%P set CHROME=%%P
)
if "!CHROME!"=="" (
    where chrome >NUL 2>&1 && set CHROME=chrome.exe
)
if "!CHROME!"=="" (
    echo [ERROR] Chrome not found. Install Google Chrome and re-run.
    pause
    exit /b 1
)

:: ── Launch Chrome with remote debugging ───────────────────────────────────
echo Starting Chrome in remote debug mode on port 9222...
start "" !CHROME! --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug
timeout /t 3 /nobreak >NUL

:: ── Run extractor ──────────────────────────────────────────────────────────
echo.
echo Running Blog Extractor...
uv run python extract.py

echo.
pause
