# AGENTS.md

## Project Facts (verified)
- Python version is pinned to 3.13 (`.python-version`); project requires `>=3.13` (`pyproject.toml`).
- Dependency management uses `uv`; runtime dependency is `pygame-ce>=2.5.7`.
- `README.md` is empty; rely on code and config as source of truth.
- No tests, CI workflows, pre-commit config, lint config, or typecheck config are currently present.

## Commands
- Install and sync dependencies: `uv sync`
- Run game (preferred): `uv run python main.py`
- Alternate run (if dependencies are already installed): `python main.py`

## Fast Verification
- Launch game and verify flow manually: title -> transition -> gameplay (`SPACE`).
- In gameplay, verify movement (`A`/`D` or arrows), jump (`SPACE`), quack (`Q`), quit (`ESC`).

## Entrypoints
- `main.py`: game loop, state machine (`TITLE`, `TRANSITION`, `PLAYING`), rendering.
- `src/player.py`: movement, gravity, collision, animation, draw.
- `src/levels/__init__.py`: `init_levels(screen_height) -> list[(Level, spawn)]`.
- `src/levels/level_ods_1.py`: level layout via `create_level_1()`.
- `src/platform.py`: platform rect sizing and texture blitting.
- `src/utils/camera.py`: camera follow and clamp.
- `src/constants.py`: world and player tuning constants.

## Non-Obvious Gotchas
- Run commands from repo root; asset paths are relative (`src/assets/...`).
- `src/utils/textures.py` loads textures at import time (`TEXTURES = load_textures()`) and calls `pygame.display.set_mode()` inside `load_textures()`.
- `main.py` imports `src.levels` at module import time, so texture-loading side effects happen before `main()` executes.
- `Player.update(dt, keys, platforms)` already calls `handle_input`; avoid duplicate input handling elsewhere.
- Some prose docs are stale; prefer current code signatures and constants over documentation.
- Current asset filenames include misspellings that match code paths and should not be "fixed" without updating references:
  - `src/assets/backgrounds/inital_screen_background.png`
  - `src/assets/letters/quack_the_sytem_main_letter.png`
