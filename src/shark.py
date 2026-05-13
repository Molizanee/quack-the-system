"""Radioactive shark — homing mid-water enemy.

Sprite asset pending. Drawn procedurally: green torpedo body, yellow eye,
tooth row, dorsal fin, tail. Each shark owns a rectangular bounds zone
and chases Duck within it: velocity is a blend of "toward Duck" plus a
random jitter that resamples every ~0.5 s so the path stays unpredictable.

Interface: ``update(dt, target_rect)`` / ``is_lethal(player_rect)`` /
``draw(screen)`` / ``reset()`` — matches the Rat/Crab interface so the
``Level.enemies`` list can hold any mix.
"""

import math
import random

import pygame

WIDTH = 88
HEIGHT = 36
SPEED = 357.0  # max speed (px/s) when heading straight at Duck (+50% over 238)
VERTICAL_SCALE = 1.0  # vertical chase matches horizontal — sharks dive as fast as they swim
JITTER_WEIGHT = 0.30  # 0 = perfect homing, 1 = pure random; lower = harder to dodge
JITTER_REFRESH_MIN = 0.15  # seconds between jitter resamples (more responsive)
JITTER_REFRESH_MAX = 0.40
BOB_AMPLITUDE = 3
BOB_FREQ = 3.5


class Shark:
    BODY_COLOR = (90, 180, 110)
    BODY_OUTLINE = (40, 90, 50)
    BELLY_COLOR = (200, 230, 200)
    EYE_COLOR = (255, 240, 60)
    PUPIL_COLOR = (0, 0, 0)
    TOOTH_COLOR = (255, 255, 255)

    def __init__(
        self,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
        start_x: int | None = None,
        start_y: int | None = None,
    ) -> None:
        if x_max <= x_min + WIDTH:
            raise ValueError("Shark x range must be wider than the shark.")
        if y_max <= y_min + HEIGHT:
            raise ValueError("Shark y range must be taller than the shark.")
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        sx = start_x if start_x is not None else (x_min + x_max) // 2 - WIDTH // 2
        sy = start_y if start_y is not None else (y_min + y_max) // 2 - HEIGHT // 2
        self.rect = pygame.Rect(sx, sy, WIDTH, HEIGHT)
        self._spawn = (sx, sy)
        self.direction = 1  # facing: 1 right, -1 left
        self._jitter_timer = 0.0
        self._jitter_dx = 0.0
        self._jitter_dy = 0.0
        self._bob_t = 0.0

    def reset(self) -> None:
        self.rect.x, self.rect.y = self._spawn
        self.direction = 1
        self._jitter_timer = 0.0
        self._jitter_dx = 0.0
        self._jitter_dy = 0.0
        self._bob_t = 0.0

    def update(self, dt: float, target_rect: pygame.Rect | None = None) -> None:
        # Refresh the random jitter periodically so motion is unpredictable
        # but still mostly chasing Duck.
        self._jitter_timer -= dt
        if self._jitter_timer <= 0.0:
            self._jitter_timer = random.uniform(
                JITTER_REFRESH_MIN, JITTER_REFRESH_MAX
            )
            self._jitter_dx = random.uniform(-1.0, 1.0)
            self._jitter_dy = random.uniform(-1.0, 1.0)

        if target_rect is None:
            # No target — drift in the last jittered direction so we never
            # come to a dead stop.
            nx, ny = self._jitter_dx, self._jitter_dy
        else:
            dx = target_rect.centerx - self.rect.centerx
            dy = target_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy) or 1.0
            home_x, home_y = dx / dist, dy / dist
            nx = (1.0 - JITTER_WEIGHT) * home_x + JITTER_WEIGHT * self._jitter_dx
            ny = (1.0 - JITTER_WEIGHT) * home_y + JITTER_WEIGHT * self._jitter_dy

        # Face the direction of horizontal travel.
        if nx > 0.05:
            self.direction = 1
        elif nx < -0.05:
            self.direction = -1

        vx = nx * SPEED
        vy = ny * SPEED * VERTICAL_SCALE

        self.rect.x += int(vx * dt)
        self.rect.y += int(vy * dt)

        # Bob overlay (small visual sway) — done as an offset so it doesn't
        # accumulate into the bounded position.
        self._bob_t += dt
        bob = int(BOB_AMPLITUDE * math.sin(self._bob_t * BOB_FREQ))

        # Clamp to bounds.
        if self.rect.left < self.x_min:
            self.rect.left = self.x_min
        if self.rect.right > self.x_max:
            self.rect.right = self.x_max
        if self.rect.top < self.y_min - bob:
            self.rect.top = self.y_min - bob
        if self.rect.bottom > self.y_max - bob:
            self.rect.bottom = self.y_max - bob

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        body = pygame.Rect(self.rect)
        # Body
        pygame.draw.ellipse(screen, self.BODY_COLOR, body)
        pygame.draw.ellipse(screen, self.BODY_OUTLINE, body, 2)
        # Belly (lighter underside)
        belly = body.inflate(-20, -HEIGHT // 2)
        belly.centery = body.centery + 6
        pygame.draw.ellipse(screen, self.BELLY_COLOR, belly)
        # Tail (triangle on the trailing side)
        if self.direction > 0:
            tail = [
                (body.left + 4, body.centery),
                (body.left - 18, body.top - 2),
                (body.left - 18, body.bottom + 2),
            ]
        else:
            tail = [
                (body.right - 4, body.centery),
                (body.right + 18, body.top - 2),
                (body.right + 18, body.bottom + 2),
            ]
        pygame.draw.polygon(screen, self.BODY_COLOR, tail)
        pygame.draw.polygon(screen, self.BODY_OUTLINE, tail, 2)
        # Dorsal fin
        fin = [
            (body.centerx, body.top - 12),
            (body.centerx - 12 * self.direction, body.top + 2),
            (body.centerx + 12 * self.direction, body.top + 2),
        ]
        pygame.draw.polygon(screen, self.BODY_COLOR, fin)
        pygame.draw.polygon(screen, self.BODY_OUTLINE, fin, 2)
        # Eye on the leading side
        if self.direction > 0:
            eye_x = body.right - 18
            mouth_x = body.right - 6
        else:
            eye_x = body.left + 18
            mouth_x = body.left + 6
        eye_y = body.centery - 4
        pygame.draw.circle(screen, self.EYE_COLOR, (eye_x, eye_y), 4)
        pygame.draw.circle(screen, self.PUPIL_COLOR, (eye_x, eye_y), 2)
        # Teeth
        for i in range(3):
            cx = mouth_x + (i - 1) * 5 * self.direction
            top = body.centery + 4
            bot = top + 5
            pygame.draw.polygon(
                screen,
                self.TOOTH_COLOR,
                [(cx - 2, top), (cx + 2, top), (cx, bot)],
            )
