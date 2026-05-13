"""Random water mines for Phase 2.

A ``MineField`` owns a rectangular bounds zone and pops ``WaterMine``
instances into it on a randomised cadence. Each mine cycles through a
short lifecycle:

    warning  -> armed   -> fading   -> expired
    (0.5 s)     (3.0 s)    (0.4 s)

* ``warning`` flashes a red/yellow halo so the player can see a mine
  about to materialise; it is NOT lethal yet.
* ``armed`` shows the spiky body and IS lethal on collision.
* ``fading`` is a brief cool-down where the mine dims out; not lethal.
* ``expired`` mines are pruned by the field on the next tick.

The field caps how many mines can be active at once so the screen
never fills with them.
"""

import math
import random

import pygame

# ── Mine lifecycle constants ───────────────────────────────────────
RADIUS = 16
WARNING_DURATION = 0.5
ARMED_DURATION = 3.0
FADE_DURATION = 0.4

# ── MineField cadence ──────────────────────────────────────────────
SPAWN_INTERVAL_MIN = 0.3
SPAWN_INTERVAL_MAX = 0.8
MAX_ACTIVE_MINES = 8
# Don't spawn closer than this to Duck — prevents instant-kill spawn-on-top.
MIN_SPAWN_DISTANCE = 80
# Default minimum separation between two simultaneous mines so the field
# is visually spread instead of clumping near one corner.
MIN_MINE_DISTANCE = 140
# Number of random samples to try before giving up on a spawn slot.
SPAWN_ATTEMPTS = 16


class WaterMine:
    BODY_COLOR = (28, 30, 32)
    SPIKE_COLOR = (40, 40, 44)
    RIM_COLOR = (110, 220, 110)
    LIGHT_COLOR = (240, 50, 40)
    WARNING_COLOR = (255, 60, 40)

    def __init__(self, cx: int, cy: int) -> None:
        self.cx = cx
        self.cy = cy
        self.rect = pygame.Rect(cx - RADIUS, cy - RADIUS, RADIUS * 2, RADIUS * 2)
        self.state = "warning"
        self.timer = WARNING_DURATION
        self.t_total = 0.0

    @property
    def expired(self) -> bool:
        return self.state == "expired"

    def update(self, dt: float) -> None:
        self.t_total += dt
        self.timer -= dt
        if self.timer > 0.0:
            return
        if self.state == "warning":
            self.state = "armed"
            self.timer = ARMED_DURATION
        elif self.state == "armed":
            self.state = "fading"
            self.timer = FADE_DURATION
        elif self.state == "fading":
            self.state = "expired"

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return self.state == "armed" and self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == "warning":
            self._draw_warning(screen)
        elif self.state == "armed":
            self._draw_armed(screen, alpha=255)
        elif self.state == "fading":
            ratio = max(0.0, self.timer / FADE_DURATION)
            self._draw_armed(screen, alpha=int(255 * ratio))

    def _draw_warning(self, screen: pygame.Surface) -> None:
        # Pulsing halo to telegraph the spawn location.
        pulse = 0.5 + 0.5 * math.sin(self.t_total * 22)
        halo_radius = int(RADIUS + 6 + pulse * 4)
        alpha = int(80 + 120 * pulse)
        surf = pygame.Surface(
            (halo_radius * 2 + 4, halo_radius * 2 + 4), pygame.SRCALPHA
        )
        pygame.draw.circle(
            surf,
            (*self.WARNING_COLOR, alpha),
            (halo_radius + 2, halo_radius + 2),
            halo_radius,
            width=3,
        )
        screen.blit(surf, (self.cx - halo_radius - 2, self.cy - halo_radius - 2))

    def _draw_armed(self, screen: pygame.Surface, alpha: int) -> None:
        side = RADIUS * 2 + 16
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        cx, cy = side // 2, side // 2
        # Spikes
        for angle_deg in range(0, 360, 30):
            rad = math.radians(angle_deg)
            ox = int(math.cos(rad) * (RADIUS + 6))
            oy = int(math.sin(rad) * (RADIUS + 6))
            pygame.draw.line(
                surf,
                (*self.SPIKE_COLOR, alpha),
                (cx, cy),
                (cx + ox, cy + oy),
                3,
            )
        # Body
        pygame.draw.circle(surf, (*self.BODY_COLOR, alpha), (cx, cy), RADIUS)
        pygame.draw.circle(surf, (*self.RIM_COLOR, alpha), (cx, cy), RADIUS, 2)
        # Blinking red light
        blink = 0.5 + 0.5 * math.sin(self.t_total * 7)
        light_radius = 3 + int(2 * blink)
        light_alpha = int((140 + 115 * blink) * (alpha / 255))
        pygame.draw.circle(
            surf,
            (*self.LIGHT_COLOR, light_alpha),
            (cx, cy),
            light_radius,
        )
        screen.blit(surf, (self.cx - cx, self.cy - cy))


class MineField:
    """Spawns ``WaterMine`` instances at random within a bounds zone."""

    def __init__(
        self,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
        max_active: int = MAX_ACTIVE_MINES,
        min_mine_distance: int = MIN_MINE_DISTANCE,
    ) -> None:
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.max_active = max_active
        self.min_mine_distance = min_mine_distance
        self.mines: list[WaterMine] = []
        self._spawn_timer = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def reset(self) -> None:
        self.mines.clear()
        self._spawn_timer = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def update(self, dt: float, player_rect: pygame.Rect | None = None) -> None:
        for mine in self.mines:
            mine.update(dt)
        self.mines = [m for m in self.mines if not m.expired]

        self._spawn_timer -= dt
        if self._spawn_timer > 0.0:
            return
        self._spawn_timer = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
        if len(self.mines) < self.max_active:
            self._try_spawn_one(player_rect)

    def _try_spawn_one(self, player_rect: pygame.Rect | None) -> None:
        # Sample several random points until we find one that's far enough
        # from Duck AND from every other live mine. This is what makes the
        # field look spread across the level instead of clumped together.
        d2_min_mine = self.min_mine_distance * self.min_mine_distance
        d2_min_duck = MIN_SPAWN_DISTANCE * MIN_SPAWN_DISTANCE
        for _ in range(SPAWN_ATTEMPTS):
            cx = random.randint(self.x_min + RADIUS, self.x_max - RADIUS)
            cy = random.randint(self.y_min + RADIUS, self.y_max - RADIUS)
            if player_rect is not None:
                dx = cx - player_rect.centerx
                dy = cy - player_rect.centery
                if dx * dx + dy * dy < d2_min_duck:
                    continue
            too_close = False
            for other in self.mines:
                dx = cx - other.cx
                dy = cy - other.cy
                if dx * dx + dy * dy < d2_min_mine:
                    too_close = True
                    break
            if too_close:
                continue
            self.mines.append(WaterMine(cx, cy))
            return
        # All attempts landed too close; skip this spawn.

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return any(m.is_lethal(player_rect) for m in self.mines)

    def draw(self, screen: pygame.Surface) -> None:
        for mine in self.mines:
            mine.draw(screen)
