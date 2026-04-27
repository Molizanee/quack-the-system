#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# build_macos.sh — Build Quack The System for macOS
#
# Usage:
#   chmod +x scripts/build_macos.sh
#   ./scripts/build_macos.sh
#
# Output:
#   dist/QuackTheSystem      (standalone executable)
#   dist/QuackTheSystem.app  (macOS app bundle)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "══════════════════════════════════════════════════════════"
echo "  Building Quack The System — macOS"
echo "══════════════════════════════════════════════════════════"

cd "$PROJECT_ROOT"

# Ensure pyinstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "⚠  PyInstaller not found. Installing via uv..."
    uv add --dev pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Run PyInstaller
echo "🔨 Running PyInstaller..."
pyinstaller quack_the_system.spec --noconfirm

echo ""
echo "✅ Build complete!"
echo "   Executable: dist/QuackTheSystem"
echo "   App bundle: dist/QuackTheSystem.app"
echo ""
echo "To run the app:"
echo "   open dist/QuackTheSystem.app"
echo "   # or"
echo "   ./dist/QuackTheSystem"
