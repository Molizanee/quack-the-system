# AGENTS.md - Developer Guidelines for Quack the System

## Project Overview

This is a Python 3.13 pygame project. The project uses `uv` for dependency management and currently has no tests or linting configuration set up.

---

## Build / Run Commands

### Running the Game
```bash
python main.py
```

Or with uv:
```bash
uv run python main.py
```

### Dependency Management
```bash
uv add <package>          # Add a new dependency
uv sync                   # Sync dependencies from pyproject.toml
```

---

## Testing

**No tests currently exist.** To add testing:

1. Install pytest: `uv add --dev pytest`
2. Run all tests: `pytest`
3. Run a single test file: `pytest tests/test_main.py`
4. Run a single test function: `pytest tests/test_main.py::test_function_name`
5. Run tests with verbose output: `pytest -v`

---

## Linting & Code Quality

### Recommended Setup

Add these tools to `pyproject.toml` for consistent code quality:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = []

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

Install tools:
```bash
uv add --dev ruff mypy pytest
```

### Running Linters
```bash
ruff check .              # Lint all files
ruff check --fix .       # Auto-fix issues
ruff format .            # Format code
mypy .                   # Type checking
```

---

## Code Style Guidelines

### General
- **Language**: Python 3.13+
- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Separate groups with blank lines
- Sort alphabetically within groups
- Use absolute imports for local modules

**Good:**
```python
import os
import sys
from pathlib import Path

import pygame

from src.game import Game
from src.player import Player
```

**Avoid:**
```python
from game import Game
import pygame, os, sys
```

### Naming Conventions
- **Variables/functions**: `snake_case` (e.g., `player_speed`, `handle_event`)
- **Classes**: `PascalCase` (e.g., `GameEngine`, `Sprite`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SCREEN_WIDTH`, `MAX_SPEED`)
- **Private members**: `_leading_underscore` (e.g., `_internal_state`)
- **File names**: `snake_case` (e.g., `game_engine.py`)

### Types
- Use type hints for all function signatures and variables when beneficial
- Use `Union` or `|` syntax for multiple types: `int | float` (Python 3.10+)
- Use `Optional` or `| None` for nullable types: `str | None`

**Good:**
```python
def move_player(dx: float, dy: float) -> None:
    position: tuple[int, int] = (0, 0)
```

### Error Handling
- Use specific exception types
- Avoid bare `except:` clauses
- Log errors before re-raising when appropriate
- Use context managers for resource cleanup

**Good:**
```python
try:
    image = pygame.image.load(path)
except FileNotFoundError:
    logger.error(f"Image not found: {path}")
    raise
```

### Functions
- Keep functions small and focused (single responsibility)
- Use descriptive names that explain what the function does
- Maximum ~50 lines per function
- Use docstrings for public APIs following Google/NumPy style

**Good:**
```python
def calculate_velocity(direction: str, speed: float) -> tuple[float, float]:
    """Calculate velocity vector from direction and speed.
    
    Args:
        direction: One of 'left', 'right', 'up', 'down'
        speed: Movement speed in pixels per frame
    
    Returns:
        Tuple of (x_velocity, y_velocity)
    """
    velocities = {
        'left': (-speed, 0),
        'right': (speed, 0),
        'up': (0, -speed),
        'down': (0, speed),
    }
    return velocities.get(direction, (0, 0))
```

### Classes
- Use dataclasses for simple data containers: `@dataclass`
- Use `__slots__` for classes with many instances to save memory
- Keep related functionality together (cohesion)

### Pygame-Specific Guidelines
- Use constants for magic numbers (screen size, colors, etc.)
- Group related constants into classes or modules
- Use `pygame.Rect` for collision detection
- Handle events in the main loop explicitly
- Use `clock.tick(fps)` to cap framerate

---

## Project Structure

```
quack-the-system/
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── src/                 # Source code (create this)
│   ├── __init__.py
│   ├── game.py
│   ├── player.py
│   └── constants.py
└── tests/               # Test files (create this)
    └── test_player.py
```

---

## Common Patterns

### Main Game Loop
```python
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game state
        # Draw frame
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
```

### Color Constants
```python
from pygame import Color

class Colors:
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
```

---

## Git Conventions

- Branch naming: `feature/description` or `fix/description`
- Commit messages: Imperative mood ("Add feature" not "Added feature")
- Use meaningful commit messages that explain the "why"

---

## Pre-commit Checklist

Before committing:
- [ ] Code runs without errors
- [ ] New code has type hints where beneficial
- [ ] No TODO/FIXME comments (or document why needed)
- [ ] Files formatted with ruff (if configured)
