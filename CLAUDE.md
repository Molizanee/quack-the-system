# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Quack the System** is a 2D platformer game built with Python 3.13 and pygame-ce. A duck character navigates platforms across a 3000×1400-pixel world.

## Commands

```bash
# Run the game
python main.py
# or
uv run python main.py

# Dependency management
uv add <package>     # Add dependency
uv sync              # Sync from pyproject.toml

# Linting/formatting (install first with: uv add --dev ruff mypy pytest)
ruff check .         # Lint
ruff check --fix .   # Auto-fix
ruff format .        # Format
mypy .               # Type check

# Tests (none exist yet)
pytest               # Run all tests
pytest tests/test_file.py::test_function  # Run single test
```

## Architecture

**Game states:** TITLE → TRANSITION (1s fade) → PLAYING

**Entry point:** `main.py` — owns the game loop, state machine, asset loading, and rendering.

**Key modules:**
- `src/constants.py` — `Colors`, `PlayerSettings` (SIZE=50px, SPEED=400, JUMP_FORCE=800, GRAVITY=1800), `WorldSettings` (3000×1400)
- `src/player.py` — `Player` sprite: `handle_input()` sets velocity, `update(dt, platforms)` applies gravity and resolves collisions, `draw()` renders with animation
- `src/platform.py` — `Platform`: rect-based geometry with texture rendering
- `src/levels/__init__.py` — `init_levels(width, height)` returns `list[Level]` and spawn point
- `src/levels/level_ods_1.py` — `Level` class + `create_level_1()`: defines ground and floating platforms
- `src/utils/camera.py` — `Camera`: follows player, clamps to world bounds; apply offset when drawing
- `src/utils/textures.py` — `TEXTURES` dict loaded from `src/assets/textures/`

**Critical data path in the game loop (PLAYING state):**
1. `player.handle_input(keys)` → sets `velocity_x`
2. `player.update(dt, current_level.get_platform_rects())` → physics + collision
3. Camera offset applied when drawing level and player

## Code Style

- Python 3.13+, 100-char line length, 4-space indent
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- Type hints on all function signatures
- Import order: stdlib → third-party → local (separated by blank lines, sorted alphabetically within groups)
- Use absolute imports for local modules (`from src.player import Player`)
- Use `pygame.Rect` for all collision detection
- Group magic numbers into `constants.py` classes rather than inlining them

## Git Conventions

- Branch naming: `feature/description` or `fix/description`
- Commit messages: imperative mood ("Add feature", not "Added feature")
