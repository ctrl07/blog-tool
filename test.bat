@echo off
setlocal EnableDelayedExpansion
title Blog Extractor — Setup ^& Run

set SCRIPT_DIR=%~dp0
set VENV=%SCRIPT_DIR%.venv
set VENV_PY="%VENV%\Scripts\python.exe"

:: ── Locate Python 3.13 (Microsoft Store) ──────────────────────────────────
set PY=%LOCALAPPDATA%\Microsoft\WindowsApps\python3.13.exe
if not exist "%PY%" (
    echo [ERROR] Python 3.13 not found at:
    echo   %PY%
    echo.
    echo Please install Python 3.13 from the Microsoft Store, then re-run this file.
    pause
    exit /b 1
)

:: ── Install uv if missing ──────────────────────────────────────────────────
where uv >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing uv package manager...
    "%PY%" -m pip install uv --quiet
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install uv. Check your internet connection.
        pause
        exit /b 1
    )
    echo uv installed.
)

:: ── Create venv if missing ─────────────────────────────────────────────────
if not exist "%VENV%\Scripts\python.exe" (
    echo Creating virtual environment...
    uv venv "%VENV%" --python "%PY%"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: ── Install / sync dependencies ────────────────────────────────────────────
echo Checking dependencies...
uv pip install --python %VENV_PY% -r "%SCRIPT_DIR%requirements.txt" --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency install failed. Check your internet connection.
    pause
    exit /b 1
)

:: ── Install Playwright Chromium browser (once) ────────────────────────────
set PW_MARKER=%VENV%\playwright_installed.txt
if not exist "%PW_MARKER%" (
    echo Installing Playwright Chromium browser ^(first run only^)...
    %VENV_PY% -m playwright install chromium
    if %ERRORLEVEL% EQU 0 (
        echo installed > "%PW_MARKER%"
    ) else (
        echo [WARNING] Playwright browser install failed — you can retry by deleting:
        echo           %PW_MARKER%
    )
)

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
%VENV_PY% "%SCRIPT_DIR%extract.py"

echo.
pause
