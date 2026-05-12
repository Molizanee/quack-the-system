"""Smog cloud vision hazard — used by Polluted City (ODS 11) and any future
phase that wants atmospheric obscuration without a hard-collision trap.

Behaviour:
- ``idle`` — a faint particle haze marks the cloud's footprint on the level.
- ``triggered`` — player rect overlapped the footprint; a full-screen dark
  overlay drops over the gameplay layer for ``TRIGGER_DURATION`` seconds.
- ``dissipating`` — overlay alpha fades to zero over ``DISSIPATE_DURATION``.
- ``spent`` — the cloud is exhausted for the rest of the run; ``reset`` brings
  it back.

The cloud is **not** lethal. Its job is to hide the level so the player has to
commit to a jump they pre-read, not to deal damage on contact.
"""

import math

import pygame

TRIGGER_DURATION = 1.6
DISSIPATE_DURATION = 0.4
OVERLAY_RGBA = (60, 60, 70, 235)
HAZE_COLOR = (110, 110, 120)
HAZE_PUFF_COUNT = 4


class SmogCloud:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        density: float = 0.85,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.density = max(0.0, min(1.0, density))
        self.state = "idle"  # idle → triggered → dissipating → spent
        self.timer = 0.0
        self._anim_t = 0.0
        self._puffs = self._build_puffs()

    def _build_puffs(self) -> list[tuple[int, int, int]]:
        cx = self.rect.centerx
        cy = self.rect.centery
        step = max(28, self.rect.width // HAZE_PUFF_COUNT)
        radius = max(36, self.rect.height // 2)
        puffs: list[tuple[int, int, int]] = []
        for i in range(HAZE_PUFF_COUNT):
            offset = (i - (HAZE_PUFF_COUNT - 1) / 2) * step
            puff_x = int(cx + offset)
            puff_y = cy
            puffs.append((puff_x, puff_y, radius))
        return puffs

    def reset(self) -> None:
        self.state = "idle"
        self.timer = 0.0
        self._anim_t = 0.0

    def update(self, dt: float, player_rect: pygame.Rect) -> None:
        self._anim_t += dt
        if self.state == "idle":
            if self.rect.colliderect(player_rect):
                self.state = "triggered"
                self.timer = 0.0
        elif self.state == "triggered":
            self.timer += dt
            if self.timer >= TRIGGER_DURATION:
                self.state = "dissipating"
                self.timer = 0.0
        elif self.state == "dissipating":
            self.timer += dt
            if self.timer >= DISSIPATE_DURATION:
                self.state = "spent"
                self.timer = 0.0

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return False

    def draw_footprint(self, screen: pygame.Surface) -> None:
        """Faint puff drawn on the level layer so players can see the zone."""
        if self.state == "spent":
            return
        pulse = (math.sin(self._anim_t * 1.8) + 1.0) * 0.5
        base_alpha = int(60 + 30 * pulse * self.density)
        for px, py, radius in self._puffs:
            haze_surface = pygame.Surface(
                (radius * 2, radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                haze_surface,
                (*HAZE_COLOR, base_alpha),
                (radius, radius),
                radius,
            )
            screen.blit(haze_surface, (px - radius, py - radius))

    def draw_screen_overlay(
        self, screen: pygame.Surface, screen_w: int, screen_h: int
    ) -> None:
        """Full-screen dark overlay drawn on top of the gameplay layer."""
        if self.state == "triggered":
            alpha = OVERLAY_RGBA[3]
        elif self.state == "dissipating":
            t = 1.0 - (self.timer / DISSIPATE_DURATION)
            alpha = int(OVERLAY_RGBA[3] * t)
        else:
            return
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((OVERLAY_RGBA[0], OVERLAY_RGBA[1], OVERLAY_RGBA[2], alpha))
        screen.blit(overlay, (0, 0))
