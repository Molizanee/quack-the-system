import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pygame
import pytest

from src.trap import TrapZone


def make_rect(cx: int, cy: int, size: int = 50) -> pygame.Rect:
    """Helper: return a pygame.Rect centred at (cx, cy)."""
    rect = pygame.Rect(0, 0, size, size)
    rect.center = (cx, cy)
    return rect


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def make_trap(x: int = 100, y: int = 100, radius: int = 80, reset_chance: float = 0.6) -> TrapZone:
    return TrapZone(
        trap_id="test_trap",
        x=x,
        y=y,
        radius=radius,
        effect="placeholder",
        reset_chance=reset_chance,
    )


# ── 1. Proximity inside radius ────────────────────────────────────────────────

def test_proximity_inside_radius():
    trap = make_trap(x=100, y=100, radius=80)
    player_rect = make_rect(100, 100)  # centred exactly on trap
    assert trap.check_proximity(player_rect) is True


# ── 2. Proximity outside radius ───────────────────────────────────────────────

def test_proximity_outside_radius():
    trap = make_trap(x=100, y=100, radius=80)
    player_rect = make_rect(300, 300)  # far away
    assert trap.check_proximity(player_rect) is False


# ── 3. Already triggered — never fires again ──────────────────────────────────

def test_already_triggered_never_fires():
    trap = make_trap(x=100, y=100, radius=80)
    trap.triggered = True
    player_rect = make_rect(100, 100)  # inside radius
    assert trap.check_proximity(player_rect) is False


# ── 4. try_reset with chance=1.0 always resets ───────────────────────────────

def test_try_reset_always_resets():
    trap = make_trap(reset_chance=1.0)
    trap.triggered = True
    trap.try_reset()
    assert trap.triggered is False


# ── 5. try_reset with chance=0.0 never resets ────────────────────────────────

def test_try_reset_never_resets():
    trap = make_trap(reset_chance=0.0)
    trap.triggered = True
    trap.try_reset()
    assert trap.triggered is True


# ── 6. load_traps with valid JSON ─────────────────────────────────────────────

def test_load_traps_valid_json(tmp_path, monkeypatch):
    data = {
        "traps": [
            {"id": "t1", "type": "proximity", "x": 320, "y": 540,
             "radius": 80, "effect": "placeholder", "reset_chance": 0.6},
            {"id": "t2", "type": "proximity", "x": 600, "y": 200,
             "radius": 50, "effect": "placeholder", "reset_chance": 1.0},
        ]
    }
    level_dir = tmp_path / "src" / "levels" / "data"
    level_dir.mkdir(parents=True)
    (level_dir / "level_1.json").write_text(json.dumps(data))

    # Redirect Path resolution inside load_traps to use tmp_path
    import src.levels.trap_loader as loader
    original_path_cls = loader.Path

    def patched_path(s: str) -> Path:
        return tmp_path / s

    monkeypatch.setattr(loader, "Path", patched_path)

    traps = loader.load_traps(1)
    assert len(traps) == 2
    assert traps[0].trap_id == "t1"
    assert traps[0].radius == 80
    assert traps[1].trap_id == "t2"
    assert traps[1].reset_chance == 1.0


# ── 7. load_traps with missing file returns [] ────────────────────────────────

def test_load_traps_missing_file(monkeypatch):
    import src.levels.trap_loader as loader

    def patched_path(s: str) -> Path:
        return Path("/nonexistent/path/level_99.json")

    monkeypatch.setattr(loader, "Path", patched_path)

    traps = loader.load_traps(99)
    assert traps == []
