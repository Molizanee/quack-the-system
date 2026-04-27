@echo off
REM ──────────────────────────────────────────────────────────────
REM build_windows.bat — Build Quack The System for Windows
REM
REM Usage:
REM   scripts\build_windows.bat
REM
REM Output:
REM   dist\QuackTheSystem.exe
REM ──────────────────────────────────────────────────────────────

echo ===========================================================
echo   Building Quack The System — Windows
echo ===========================================================

cd /d "%~dp0\.."

REM Ensure pyinstaller is available
where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] PyInstaller not found. Installing via uv...
    uv add --dev pyinstaller
)

REM Clean previous builds
echo [*] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
echo [*] Running PyInstaller...
pyinstaller quack_the_system.spec --noconfirm

echo.
echo [OK] Build complete!
echo     Executable: dist\QuackTheSystem.exe
echo.
echo To run the game:
echo     dist\QuackTheSystem.exe
