"""Radioactive crab — homing seabed/low-water enemy.

Sprite asset pending. Drawn procedurally: red shell with green
radioactive rim, two pincers and small legs. Crabs can lift off the
seabed within their y bounds and home toward Duck with random jitter,
slower and more erratic than the sharks.

Interface: ``update(dt, target_rect)`` / ``is_lethal(player_rect)`` /
``draw(screen)`` / ``reset()`` — matches Shark/Rat.
"""

import math
import random

import pygame

WIDTH = 52
HEIGHT = 34
SPEED = 199.5  # max homing speed (px/s) (+50% over 133)
VERTICAL_SCALE = 0.8  # crabs can rise but feel heavier than sharks
JITTER_WEIGHT = 0.7  # crabs are jitterier than sharks
JITTER_REFRESH_MIN = 0.25
JITTER_REFRESH_MAX = 0.7


class Crab:
    SHELL_COLOR = (190, 80, 60)
    SHELL_OUTLINE = (90, 30, 20)
    RIM_COLOR = (110, 220, 110)
    EYE_STALK_COLOR = (110, 220, 110)
    EYE_COLOR = (255, 240, 60)
    PUPIL_COLOR = (0, 0, 0)
    PINCER_COLOR = (190, 80, 60)
    LEG_COLOR = (90, 30, 20)

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
            raise ValueError("Crab x range must be wider than the crab.")
        if y_max <= y_min + HEIGHT:
            raise ValueError("Crab y range must be taller than the crab.")
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        sx = start_x if start_x is not None else (x_min + x_max) // 2 - WIDTH // 2
        sy = start_y if start_y is not None else y_max - HEIGHT  # rest on the floor
        self.rect = pygame.Rect(sx, sy, WIDTH, HEIGHT)
        self._spawn = (sx, sy)
        self.direction = 1  # facing
        self._jitter_timer = 0.0
        self._jitter_dx = 0.0
        self._jitter_dy = 0.0
        self._leg_t = 0.0

    def reset(self) -> None:
        self.rect.x, self.rect.y = self._spawn
        self.direction = 1
        self._jitter_timer = 0.0
        self._jitter_dx = 0.0
        self._jitter_dy = 0.0
        self._leg_t = 0.0

    def update(self, dt: float, target_rect: pygame.Rect | None = None) -> None:
        self._leg_t += dt
        self._jitter_timer -= dt
        if self._jitter_timer <= 0.0:
            self._jitter_timer = random.uniform(
                JITTER_REFRESH_MIN, JITTER_REFRESH_MAX
            )
            self._jitter_dx = random.uniform(-1.0, 1.0)
            self._jitter_dy = random.uniform(-1.0, 1.0)

        if target_rect is None:
            nx, ny = self._jitter_dx, self._jitter_dy
        else:
            dx = target_rect.centerx - self.rect.centerx
            dy = target_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy) or 1.0
            home_x, home_y = dx / dist, dy / dist
            nx = (1.0 - JITTER_WEIGHT) * home_x + JITTER_WEIGHT * self._jitter_dx
            ny = (1.0 - JITTER_WEIGHT) * home_y + JITTER_WEIGHT * self._jitter_dy

        if nx > 0.05:
            self.direction = 1
        elif nx < -0.05:
            self.direction = -1

        vx = nx * SPEED
        vy = ny * SPEED * VERTICAL_SCALE

        self.rect.x += int(vx * dt)
        self.rect.y += int(vy * dt)

        # Clamp to bounds.
        if self.rect.left < self.x_min:
            self.rect.left = self.x_min
        if self.rect.right > self.x_max:
            self.rect.right = self.x_max
        if self.rect.top < self.y_min:
            self.rect.top = self.y_min
        if self.rect.bottom > self.y_max:
            self.rect.bottom = self.y_max

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        body = pygame.Rect(self.rect.x + 6, self.rect.y + 10, WIDTH - 12, HEIGHT - 14)
        # Legs (3 per side, scuttling)
        wiggle = math.sin(self._leg_t * 10.0) * 2
        for i in range(3):
            offset_x = (i - 1) * 6
            leg_top_y = self.rect.bottom - 12
            leg_bot_y = self.rect.bottom + int(wiggle if i % 2 == 0 else -wiggle)
            pygame.draw.line(
                screen, self.LEG_COLOR,
                (body.left + offset_x, leg_top_y),
                (body.left + offset_x - 4, leg_bot_y), 3,
            )
            pygame.draw.line(
                screen, self.LEG_COLOR,
                (body.right + offset_x, leg_top_y),
                (body.right + offset_x + 4, leg_bot_y), 3,
            )
        # Pincers
        pygame.draw.polygon(
            screen, self.PINCER_COLOR,
            [
                (body.left - 8, body.centery - 2),
                (body.left + 2, body.centery - 8),
                (body.left + 2, body.centery + 6),
            ],
        )
        pygame.draw.polygon(
            screen, self.PINCER_COLOR,
            [
                (body.right + 8, body.centery - 2),
                (body.right - 2, body.centery - 8),
                (body.right - 2, body.centery + 6),
            ],
        )
        # Shell
        pygame.draw.ellipse(screen, self.SHELL_COLOR, body)
        pygame.draw.ellipse(screen, self.RIM_COLOR, body, 3)
        pygame.draw.ellipse(screen, self.SHELL_OUTLINE, body, 1)
        # Eye stalks
        stalk_top = body.top - 6
        left_eye = (body.centerx - 6, stalk_top)
        right_eye = (body.centerx + 6, stalk_top)
        pygame.draw.line(screen, self.EYE_STALK_COLOR,
                         (body.centerx - 6, body.top + 2), left_eye, 2)
        pygame.draw.line(screen, self.EYE_STALK_COLOR,
                         (body.centerx + 6, body.top + 2), right_eye, 2)
        pygame.draw.circle(screen, self.EYE_COLOR, left_eye, 3)
        pygame.draw.circle(screen, self.EYE_COLOR, right_eye, 3)
        pygame.draw.circle(screen, self.PUPIL_COLOR, left_eye, 1)
        pygame.draw.circle(screen, self.PUPIL_COLOR, right_eye, 1)
