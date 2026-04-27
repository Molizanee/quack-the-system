@echo off
REM ──────────────────────────────────────────────────────────────
REM build_windows.bat — Build Quack The System for Windows
REM
REM Prerequisites:
REM   - uv must be installed (https://docs.astral.sh/uv/)
REM
REM Usage (from the project root):
REM   scripts\build_windows.bat
REM
REM Output:
REM   dist\QuackTheSystem.exe
REM ──────────────────────────────────────────────────────────────

echo ===========================================================
echo   Building Quack The System - Windows
echo ===========================================================

REM Navigate to project root (parent of scripts/)
cd /d "%~dp0\.."

REM Sync all dependencies (including dev group: pyinstaller + pillow)
echo [*] Syncing dependencies...
uv sync --group dev
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv sync failed. Is uv installed?
    echo         Install it from: https://docs.astral.sh/uv/
    exit /b 1
)

REM Clean previous builds
echo [*] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller through uv so it uses the project venv
REM (ensures pygame-ce is used, not a system-wide pygame)
echo [*] Running PyInstaller...
uv run pyinstaller quack_the_system.spec --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed! Check the error messages above.
    exit /b 1
)

echo.
echo [OK] Build complete!
echo     Executable: dist\QuackTheSystem.exe
echo.
echo To run the game:
echo     dist\QuackTheSystem.exe
