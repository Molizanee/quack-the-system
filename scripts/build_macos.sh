#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# build_macos.sh — Build Quack The System for macOS
#
# Prerequisites:
#   - uv must be installed (https://docs.astral.sh/uv/)
#
# Usage:
#   chmod +x scripts/build_macos.sh
#   ./scripts/build_macos.sh
#
# Output:
#   dist/QuackTheSystem      (standalone folder)
#   dist/QuackTheSystem.app  (macOS app bundle)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "══════════════════════════════════════════════════════════"
echo "  Building Quack The System — macOS"
echo "══════════════════════════════════════════════════════════"

cd "$PROJECT_ROOT"

# Sync all dependencies (including dev group: pyinstaller + pillow)
echo "📦 Syncing dependencies..."
uv sync --group dev

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Run PyInstaller through uv so it uses the project venv
echo "🔨 Running PyInstaller..."
uv run pyinstaller quack_the_system.spec --noconfirm

echo ""
echo "✅ Build complete!"
echo "   Executable: dist/QuackTheSystem"
echo "   App bundle: dist/QuackTheSystem.app"
echo ""
echo "To run the app:"
echo "   open dist/QuackTheSystem.app"
echo "   # or"
echo "   ./dist/QuackTheSystem/QuackTheSystem"
