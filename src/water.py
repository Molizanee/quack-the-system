"""Underwater atmosphere — full-screen blue tint plus drifting bubble particles.

Two layers:

* ``draw_tint`` paints a semi-transparent blue over the whole screen so
  every entity reads as "underwater". Called between background and
  level entities.
* ``draw_bubbles`` blits bubble particles, called *after* the player so
  bubbles read as foreground.

Bubbles split into two streams: a slow ambient stream that drifts up
from the seabed and a burst stream that pours from Duck's tail when
they are stroking upward (``player_velocity_y < UP_THRESHOLD``).
"""

import random

import pygame

TINT_COLOR = (40, 110, 180)
TINT_ALPHA = 70  # 0..255 — keep subtle so the background still reads

AMBIENT_RATE = 1.2  # bubbles spawned per second across the level
UPWARD_BURST_RATE = 14.0  # bubbles per second while stroking up
UP_THRESHOLD = -40.0  # velocity_y below this counts as "going up"

BUBBLE_RADII = (2, 2, 3, 3, 4, 5)


class _Bubble:
    __slots__ = ("x", "y", "vx", "vy", "radius", "alpha", "alpha_decay")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        radius: int,
        alpha: int,
        alpha_decay: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alpha = alpha
        self.alpha_decay = alpha_decay

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.alpha = max(0.0, self.alpha - self.alpha_decay * dt)


class WaterAtmosphere:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.tint = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self.tint.fill((*TINT_COLOR, TINT_ALPHA))
        self._bubbles: list[_Bubble] = []
        self._ambient_carry = 0.0
        self._burst_carry = 0.0

    def reset(self) -> None:
        self._bubbles.clear()
        self._ambient_carry = 0.0
        self._burst_carry = 0.0

    def update(
        self,
        dt: float,
        player_rect: pygame.Rect,
        player_velocity_y: float = 0.0,
    ) -> None:
        # Ambient bubbles — random seeds from the seabed.
        self._ambient_carry += dt * AMBIENT_RATE
        while self._ambient_carry >= 1.0:
            self._ambient_carry -= 1.0
            self._spawn_ambient()

        # Burst stream while Duck is stroking upward.
        if player_velocity_y < UP_THRESHOLD:
            self._burst_carry += dt * UPWARD_BURST_RATE
            while self._burst_carry >= 1.0:
                self._burst_carry -= 1.0
                self._spawn_burst(player_rect)
        else:
            self._burst_carry = 0.0

        # Advance and cull.
        for b in self._bubbles:
            b.update(dt)
        self._bubbles = [
            b for b in self._bubbles
            if b.y > -20 and b.alpha > 4 and b.x > -20 and b.x < self.screen_w + 20
        ]

    def _spawn_ambient(self) -> None:
        x = random.uniform(0, self.screen_w)
        y = self.screen_h - random.uniform(0, 40)
        vy = -random.uniform(35, 70)
        vx = random.uniform(-12, 12)
        radius = random.choice(BUBBLE_RADII)
        alpha = random.randint(110, 180)
        self._bubbles.append(_Bubble(x, y, vx, vy, radius, alpha, alpha_decay=6.0))

    def _spawn_burst(self, player_rect: pygame.Rect) -> None:
        # Bubbles trail from just above Duck's back — natural for a swimmer.
        x = player_rect.centerx + random.uniform(-14, 14)
        y = player_rect.top + random.uniform(-6, 10)
        vy = -random.uniform(80, 150)
        vx = random.uniform(-25, 25)
        radius = random.choice(BUBBLE_RADII)
        alpha = random.randint(170, 230)
        self._bubbles.append(_Bubble(x, y, vx, vy, radius, alpha, alpha_decay=40.0))

    def draw_tint(self, screen: pygame.Surface) -> None:
        screen.blit(self.tint, (0, 0))

    def draw_bubbles(self, screen: pygame.Surface) -> None:
        for b in self._bubbles:
            d = b.radius * 2
            surf = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
            color = (220, 240, 255, int(b.alpha))
            pygame.draw.circle(surf, color, (b.radius + 1, b.radius + 1), b.radius)
            if b.radius >= 3:
                hi = (255, 255, 255, min(255, int(b.alpha) + 30))
                pygame.draw.circle(
                    surf, hi,
                    (b.radius, b.radius - 1),
                    max(1, b.radius // 3),
                )
            screen.blit(
                surf,
                (int(b.x - b.radius - 1), int(b.y - b.radius - 1)),
            )
