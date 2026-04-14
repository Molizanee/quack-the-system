# GEMINI.md - Instructional Context for Quack the System

## Project Overview

**Quack The System** is a 2D platformer game built with Python 3.13 and `pygame-ce` (pygame Community Edition). It features physics-based movement, a camera system, and a state-based game flow (Title, Transition, Playing). The project uses `uv` for dependency management.

### Main Technologies
- **Python 3.13**: The primary programming language.
- **pygame-ce**: A modern fork of pygame used for game development.
- **uv**: Fast Python package manager and resolver.

### Architecture
- `main.py`: Entry point, contains the main game loop and state management.
- `src/`: Core source code directory.
    - `player.py`: Player class handling input, physics, and rendering.
    - `platform.py`: Platform class for level elements.
    - `levels/`: Level definitions and initialization.
    - `utils/`: Utility modules like `camera.py` and `textures.py`.
    - `constants.py`: Centralized game settings (colors, physics, dimensions).
    - `assets/`: Game assets (images, fonts, textures).

---

## Building and Running

### Prerequisites
- [uv](https://github.com/astral-sh/uv) must be installed.

### Setup
```bash
uv sync
```

### Running the Game
```bash
uv run main.py
```
Alternatively, if your environment is already set up:
```bash
python main.py
```

### Testing
Currently, no tests are implemented. To add tests, follow the guidelines in `AGENTS.md`.

---

## Development Conventions

### Coding Style
- **Python Version**: 3.13+
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- **Type Hints**: Mandatory for all function signatures and beneficial for variables.
- **Imports**: Standard library > Third-party > Local (sorted alphabetically).
- **Line Length**: Maximum 100 characters.

### Game Development Patterns
- **Delta Time (dt)**: Use `dt` for all movement and physics updates to ensure frame-rate independence.
- **Resolution Handling**: Uses `pygame.SCALED` for automatic GPU-level scaling of the logical screen size.
- **Constants**: All magic numbers and settings should reside in `src/constants.py`.
- **Collision**: Use `pygame.Rect` and the player's collision logic in `src/player.py`.

### Code Quality (Recommended)
Refer to `AGENTS.md` for `ruff` and `mypy` configurations. Use the following commands if configured:
```bash
ruff check .      # Linting
ruff format .     # Formatting
mypy .            # Type checking
```

### Asset Management
Assets are stored in `src/assets/`. Use relative paths from the project root (e.g., `src/assets/fonts/PixelPurl.ttf`).

---

## Key Files
- `main.py`: Game loop, state transitions (TITLE, TRANSITION, PLAYING).
- `src/player.py`: Physics, input handling (`handle_input`), and collision.
- `src/constants.py`: `WorldSettings` and `PlayerSettings`.
- `AGENTS.md`: Detailed developer guidelines and recommended tool setups.
- `ARCHITECTURE.md`: High-level overview of module connections and data flow.
