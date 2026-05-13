"""Shared ``Level`` container used by every phase factory.

Each phase file (``level_ods_1.py``, ``level_ods_2.py``, ...) defines its
geometry, narrative text, and hazard layouts, then bundles everything into
this class. The class itself is phase-agnostic: it owns the update/draw
loop, the smog/rooftop/door-floor trap state machines, and the lethal-hit
check that ``main.py`` polls every frame.
"""

import random

import pygame

from src.door import Door
from src.platform import Platform
from src.rat import Rat
from src.smog import SmogCloud
from src.traps import FallingBox

# Cadência da chuva de entulho enquanto o smog está ativo.
FOG_DEBRIS_INTERVAL = 0.42  # segundos entre cada caixa extra


class Level:
    """Container for everything that lives inside a phase."""

    def __init__(
        self,
        platforms: list[Platform],
        trap_layouts: list[list[FallingBox]],
        door: Door,
        enemies: list[Rat],
        ods_number: int,
        ods_name: str,
        intro_panels: list[str],
        outro_text: str,
        background_path: str,
        rooftop_platforms: list[Platform],
        door_floor_platform: Platform,
        smog_candidates: list[tuple[int, int, int, int]],
        smog_count: int,
        fog_debris_texture_key: str = "debris_1",
        swim_mode: bool = False,
        atmosphere=None,
        music_path: str = "",
        mine_field=None,
    ) -> None:
        self.platforms = platforms
        self.trap_layouts = trap_layouts
        self.door = door
        self.enemies = enemies
        self.ods_number = ods_number
        self.ods_name = ods_name
        self.intro_panels = intro_panels
        self.outro_text = outro_text
        self.background_path = background_path

        self.rooftop_platforms = rooftop_platforms
        self.door_floor_platform = door_floor_platform
        self.smog_candidates = smog_candidates
        self.smog_count = smog_count
        self.fog_debris_texture_key = fog_debris_texture_key
        self.swim_mode = swim_mode
        self.atmosphere = atmosphere
        self.music_path = music_path
        self.mine_field = mine_field

        self.traps = random.choice(self.trap_layouts)
        self.smog_clouds = self._roll_smog_clouds()
        self.dynamic_traps: list[FallingBox] = []

        # When a level has no rooftop platforms (e.g. open-water Phase 2),
        # the door-floor trap would always fire — treat it as already
        # disarmed by initialising the visited flag.
        self._rooftop_visited = len(self.rooftop_platforms) == 0
        self._smog_active = False
        self._fog_debris_carry = 0.0

    # ── Helpers ─────────────────────────────────────────────────

    def _roll_smog_clouds(self) -> list[SmogCloud]:
        count = min(self.smog_count, len(self.smog_candidates))
        choices = random.sample(self.smog_candidates, count)
        return [SmogCloud(x=x, y=y, width=w, height=h) for x, y, w, h in choices]

    def _check_rooftop_visited(self, player_rect: pygame.Rect) -> None:
        if self._rooftop_visited:
            return
        for rooftop in self.rooftop_platforms:
            # Standing on a rooftop reads as feet aligned with the top edge.
            # Mid-jump overlap counts too, so the trap disarms even on a brush.
            standing_on = (
                rooftop.rect.left <= player_rect.centerx <= rooftop.rect.right
                and abs(player_rect.bottom - rooftop.rect.top) < 8
            )
            if standing_on or rooftop.rect.colliderect(player_rect):
                self._rooftop_visited = True
                return

    def _check_door_floor_trap(self, player_rect: pygame.Rect) -> None:
        if self._rooftop_visited:
            return
        floor = self.door_floor_platform
        if floor.state != "stable":
            return
        # Player must be standing on top of the floor segment for the trap to fire.
        on_top = (
            floor.rect.left <= player_rect.centerx <= floor.rect.right
            and abs(player_rect.bottom - floor.rect.top) < 6
        )
        if on_top:
            floor.state = "collapsing"
            floor.collapse_timer = 0.0

    def _spawn_fog_debris(self, player_rect: pygame.Rect) -> None:
        """Drop one extra debris box between Duck and the door."""
        spawn_left = max(player_rect.right + 20, 80)
        spawn_right = self.door.rect.left - 40
        if spawn_left >= spawn_right:
            return
        x = random.randint(spawn_left, spawn_right)
        box = FallingBox(x=x, texture_key=self.fog_debris_texture_key)
        # Start already falling from above the screen so it lands without the
        # usual proximity-arming step.
        box.rect.x = x
        box.rect.y = -box.BOX_SIZE
        box.state = "falling"
        box.velocity_y = 80.0
        self.dynamic_traps.append(box)

    # ── Level lifecycle ─────────────────────────────────────────

    def update(
        self,
        dt: float,
        player_rect: pygame.Rect,
        screen_h: int,
        player_velocity_y: float = 0.0,
    ) -> None:
        for platform in self.platforms:
            platform.update(dt)
        for trap in self.traps:
            trap.update(dt, player_rect, screen_h)
        for enemy in self.enemies:
            enemy.update(dt, player_rect)
        for cloud in self.smog_clouds:
            cloud.update(dt, player_rect)
        self.door.update(dt, player_rect)

        self._check_rooftop_visited(player_rect)
        self._check_door_floor_trap(player_rect)

        # Fog-time debris — while any smog is in its triggered state, drop
        # extra rocks at a steady cadence.
        self._smog_active = any(c.state == "triggered" for c in self.smog_clouds)
        if self._smog_active:
            self._fog_debris_carry += dt
            while self._fog_debris_carry >= FOG_DEBRIS_INTERVAL:
                self._fog_debris_carry -= FOG_DEBRIS_INTERVAL
                self._spawn_fog_debris(player_rect)
        else:
            self._fog_debris_carry = 0.0

        for trap in self.dynamic_traps:
            trap.update(dt, player_rect, screen_h)
        self.dynamic_traps = [
            t for t in self.dynamic_traps if t.state != "broken"
        ]

        if self.atmosphere is not None:
            self.atmosphere.update(dt, player_rect, player_velocity_y)

        if self.mine_field is not None:
            self.mine_field.update(dt, player_rect)

    def player_lethal_hit(self, player_rect: pygame.Rect) -> bool:
        if any(trap.is_lethal(player_rect) for trap in self.traps):
            return True
        if any(trap.is_lethal(player_rect) for trap in self.dynamic_traps):
            return True
        if any(enemy.is_lethal(player_rect) for enemy in self.enemies):
            return True
        if self.mine_field is not None and self.mine_field.is_lethal(player_rect):
            return True
        return False

    def is_complete(self, player_rect: pygame.Rect) -> bool:
        return self.door.player_passed_through(player_rect)

    def reset(self) -> None:
        for platform in self.platforms:
            platform.reset()
        self.traps = random.choice(self.trap_layouts)
        for trap in self.traps:
            trap.reset()
        for enemy in self.enemies:
            enemy.reset()
        self.smog_clouds = self._roll_smog_clouds()
        self.dynamic_traps.clear()
        self.door.reset()
        self._rooftop_visited = len(self.rooftop_platforms) == 0
        self._smog_active = False
        self._fog_debris_carry = 0.0
        if self.atmosphere is not None:
            self.atmosphere.reset()
        if self.mine_field is not None:
            self.mine_field.reset()

    def draw(self, screen: pygame.Surface) -> None:
        # Water tint sits between the background and every entity so the
        # whole scene reads as "underwater" without obscuring the duck.
        if self.atmosphere is not None:
            self.atmosphere.draw_tint(screen)
        for cloud in self.smog_clouds:
            cloud.draw_footprint(screen)
        for platform in self.platforms:
            platform.draw(screen)
        for trap in self.traps:
            trap.draw(screen)
        for trap in self.dynamic_traps:
            trap.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        if self.mine_field is not None:
            self.mine_field.draw(screen)
        self.door.draw(screen)
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        for cloud in self.smog_clouds:
            cloud.draw_screen_overlay(screen, screen_w, screen_h)

    def draw_foreground(self, screen: pygame.Surface) -> None:
        """Draw layers that should sit in front of the player (bubbles)."""
        if self.atmosphere is not None:
            self.atmosphere.draw_bubbles(screen)
