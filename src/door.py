"""Procedural portal door used to advance from one phase to the next.

Renders entirely with pygame primitives — no sprite asset. The door reads as
a stone arch with a glowing amber energy field inside. When Duck enters the
approach zone the field's brightness ramps up over ``OPEN_DURATION`` seconds
and, once fully open, the door spawns amber particles drifting upward.

Public API:
- ``__init__(x, ground_y)`` — places the door's bottom-center at (x, ground_y).
- ``update(dt, player_rect)`` — drives the closed → opening → open state machine.
- ``player_passed_through(player_rect)`` — True once open and touching Duck.
- ``reset()`` — back to closed.
- ``draw(screen)`` — renders the frame, the glow gradient, and any particles.
- ``rect`` — the door's footprint, used by the level for collision and HUD.
"""

import math
import random

import pygame

WIDTH = 56
HEIGHT = 91
APPROACH_PADDING = 40
OPEN_DURATION = 0.6  # seconds for closed → fully open

FRAME_COLOR = (54, 58, 70)
FRAME_HIGHLIGHT = (118, 124, 142)
FRAME_SHADOW = (28, 30, 40)
GLOW_COLOR = (255, 200, 80)
GLOW_CORE = (255, 240, 200)

PARTICLE_RATE_PER_SEC = 18.0
PARTICLE_LIFE = 1.1


class Door:
    def __init__(self, x: int, ground_y: int) -> None:
        self.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.rect.midbottom = (x, ground_y)
        self._origin = self.rect.topleft

        self.state = "closed"
        self.open_t = 0.0  # 0..1 — progress toward fully open
        self.opened = False

        self._anim_t = 0.0
        self._particle_carry = 0.0
        self._particles: list[dict] = []

    def reset(self) -> None:
        self.rect.topleft = self._origin
        self.state = "closed"
        self.open_t = 0.0
        self.opened = False
        self._anim_t = 0.0
        self._particle_carry = 0.0
        self._particles.clear()

    # ── State machine ───────────────────────────────────────────

    def update(self, dt: float, player_rect: pygame.Rect) -> None:
        self._anim_t += dt
        if self.state == "closed":
            approach = self.rect.inflate(
                APPROACH_PADDING * 2, APPROACH_PADDING * 2
            )
            if approach.colliderect(player_rect):
                self.state = "opening"
                self.open_t = 0.0
        elif self.state == "opening":
            self.open_t = min(1.0, self.open_t + dt / OPEN_DURATION)
            if self.open_t >= 1.0:
                self.state = "open"
                self.opened = True
        elif self.state == "open":
            self._particle_carry += dt * PARTICLE_RATE_PER_SEC
            while self._particle_carry >= 1.0:
                self._particles.append(self._spawn_particle())
                self._particle_carry -= 1.0

        for particle in self._particles:
            particle["y"] -= particle["speed"] * dt
            particle["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

    def _spawn_particle(self) -> dict:
        return {
            "x": self.rect.left + 14 + random.random() * (WIDTH - 28),
            "y": self.rect.bottom - 17,
            "speed": 28.0 + random.random() * 38.0,
            "life": PARTICLE_LIFE * (0.7 + 0.6 * random.random()),
            "radius": 2 + int(random.random() * 2),
        }

    def player_passed_through(self, player_rect: pygame.Rect) -> bool:
        if not self.opened:
            return False
        return self.rect.colliderect(player_rect)

    # ── Drawing ─────────────────────────────────────────────────

    def _glow_intensity(self) -> float:
        if self.state == "closed":
            pulse = (math.sin(self._anim_t * 2.0) + 1.0) * 0.5
            return 0.18 + 0.12 * pulse
        if self.state == "opening":
            return 0.18 + 0.72 * self.open_t
        pulse = (math.sin(self._anim_t * 4.0) + 1.0) * 0.5
        return 0.85 + 0.15 * pulse

    def draw(self, screen: pygame.Surface) -> None:
        # Soft drop shadow grounding the door on the floor.
        shadow_rect = self.rect.copy()
        shadow_rect.height += 4
        pygame.draw.rect(
            screen,
            FRAME_SHADOW,
            shadow_rect,
            border_top_left_radius=17,
            border_top_right_radius=17,
        )

        # Outer arch frame — rounded top, square bottom so it sits flush.
        pygame.draw.rect(
            screen,
            FRAME_COLOR,
            self.rect,
            border_top_left_radius=15,
            border_top_right_radius=15,
        )

        # Inner cutout — the "doorway" hole where the energy lives.
        cutout_pad_x = 8
        cutout_top_pad = 10
        cutout_bottom_pad = 7
        cutout = pygame.Rect(
            self.rect.left + cutout_pad_x,
            self.rect.top + cutout_top_pad,
            self.rect.width - cutout_pad_x * 2,
            self.rect.height - cutout_top_pad - cutout_bottom_pad,
        )

        intensity = self._glow_intensity()
        glow_surface = pygame.Surface(cutout.size, pygame.SRCALPHA)
        layers = 6
        for i in range(layers):
            t = i / (layers - 1)
            shrink_x = int(t * cutout.width * 0.55)
            shrink_y = int(t * cutout.height * 0.55)
            inner = pygame.Rect(
                0, 0,
                max(2, cutout.width - shrink_x),
                max(2, cutout.height - shrink_y),
            )
            inner.center = (cutout.width // 2, cutout.height // 2)
            color = GLOW_CORE if i == layers - 1 else GLOW_COLOR
            alpha = int(255 * intensity * (1.0 - t * 0.55))
            pygame.draw.ellipse(
                glow_surface, (color[0], color[1], color[2], alpha), inner
            )
        screen.blit(glow_surface, cutout.topleft)

        # Inner ring — arched top to match outer frame, gives the cutout depth.
        pygame.draw.rect(
            screen,
            FRAME_HIGHLIGHT,
            cutout,
            width=2,
            border_top_left_radius=11,
            border_top_right_radius=11,
        )

        # Keystone block at the top of the arch.
        keystone = pygame.Rect(0, 0, 13, 8)
        keystone.midtop = (self.rect.centerx, self.rect.top + 4)
        pygame.draw.rect(screen, FRAME_HIGHLIGHT, keystone, border_radius=2)

        # Side-pillar highlights for a hint of dimensionality.
        highlight_strip_w = 2
        left_strip = pygame.Rect(
            self.rect.left + 4,
            self.rect.top + 15,
            highlight_strip_w,
            self.rect.height - 21,
        )
        right_strip = pygame.Rect(
            self.rect.right - 4 - highlight_strip_w,
            self.rect.top + 15,
            highlight_strip_w,
            self.rect.height - 21,
        )
        pygame.draw.rect(screen, FRAME_HIGHLIGHT, left_strip)
        pygame.draw.rect(screen, FRAME_HIGHLIGHT, right_strip)

        # Particles — drawn last so they layer over the frame on exit edges.
        for particle in self._particles:
            life_ratio = max(0.0, min(1.0, particle["life"] / PARTICLE_LIFE))
            alpha = int(255 * life_ratio)
            radius = particle["radius"]
            particle_surf = pygame.Surface(
                (radius * 2, radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surf, (*GLOW_CORE, alpha), (radius, radius), radius
            )
            screen.blit(
                particle_surf,
                (int(particle["x"] - radius), int(particle["y"] - radius)),
            )
