import pygame

from src.constants import WorldSettings
from src.levels.trap_loader import generate_traps
from src.platform import Platform
from src.trap import TrapZone
from src.utils.textures import TEXTURES


class Level:
    def __init__(
        self, platforms: list[Platform], traps: list[TrapZone] | None = None
    ) -> None:
        self.platforms = platforms
        self.traps = traps or []

    def get_platform_rects(self) -> list[pygame.Rect]:
        return [platform.rect for platform in self.platforms]

    def update_traps(self, player_rect: pygame.Rect) -> str | None:
        """Returns an effect key if any trap fires this frame, else None."""
        for trap in self.traps:
            if trap.check_proximity(player_rect):
                return trap.trigger()
        return None

    def reset_traps(self) -> None:
        """Called on player death — each trap rolls its own World Memory chance."""
        for trap in self.traps:
            trap.try_reset()

    def draw(
        self,
        screen: pygame.Surface,
        camera: tuple[int, int] = (0, 0),
        debug: bool = False,
    ) -> None:
        for platform in self.platforms:
            platform.draw(screen, camera)
        if debug:
            for trap in self.traps:
                trap.draw_debug(screen, camera)


def create_level_1(
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:
    g = WorldSettings.HEIGHT - 40  # ground_y = 1360

    platforms = [
        # ── Ground ────────────────────────────────────────────────────────────────
        Platform(0, g, WorldSettings.WIDTH, 40, TEXTURES["rock_1b"]),

        # ── Zone A — Dark Stone, Intro (x 0–1100) ─────────────────────────────────
        # Wide platforms, comfortable gaps — teaches the jump mechanics
        Platform(200, g - 120, 192, 20, TEXTURES["rock_1a"]),  # P1: easy first step
        Platform(480, g - 240, 160, 20, TEXTURES["rock_1b"]),  # P2: gap 88px, +120
        Platform(700, g - 360, 144, 20, TEXTURES["rock_1c"]),  # P3: gap 60px, +120
        Platform(940, g - 240, 192, 20, TEXTURES["rock_1d"]),  # P4: breather drop

        # ── Zone B — Mossy Ruins, First Real Challenge (x 1100–2100) ─────────────
        # Narrower platforms, tighter gaps, one hard jump
        Platform(1200, g - 360, 128, 20, TEXTURES["rock_3a"]),  # P5: gap 68px, +120
        Platform(1440, g - 480, 112, 20, TEXTURES["rock_3b"]),  # P6: gap 112px, +120
        Platform(1700, g - 360, 128, 20, TEXTURES["rock_3c"]),  # P7: gap 148px, -120
        Platform(2000, g - 500,  96, 20, TEXTURES["rock_3d"]),  # P8: gap 172px, +140 (hard)

        # ── Zone C — Crystal Sky, Expert (x 2100–3000) ────────────────────────────
        # 80px platforms, big gaps, near-max heights — clear final ascent
        Platform(2200, g - 380, 80, 20, TEXTURES["rock_5a"]),   # P9:  gap 104px, -120
        Platform(2420, g - 540, 80, 20, TEXTURES["rock_5b"]),   # P10: gap 140px, +160 (very hard)
        Platform(2620, g - 420, 96, 20, TEXTURES["rock_5c"]),   # P11: gap 120px, -120
        Platform(2760, g - 560, 80, 20, TEXTURES["rock_5d"]),   # P12: gap 44px, +140 (hard)
        Platform(2880, g - 700, 128, 20, TEXTURES["rock_5a"]),  # P13: summit, +140
    ]

    # Randomise traps across floating platforms (skip ground at index 0)
    floating_rects = [p.rect for p in platforms[1:]]
    traps = generate_traps(floating_rects, count=4)

    spawn = (80, g - 60)  # on the ground near left edge
    return Level(platforms, traps), spawn
