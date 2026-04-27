import random

import pygame

from src.door import Door
from src.platform import Platform
from src.traps import FallingBox
from src.utils.textures import TEXTURES


class Level:
    def __init__(
        self,
        platforms: list[Platform],
        trap_layouts: list[list[FallingBox]],
        door: Door,
    ) -> None:
        self.platforms = platforms
        self.trap_layouts = trap_layouts
        self.door = door
        self.traps = random.choice(self.trap_layouts)

    def update(
        self, dt: float, player_rect: pygame.Rect, screen_h: int
    ) -> None:
        for platform in self.platforms:
            platform.update(dt)
        for trap in self.traps:
            trap.update(dt, player_rect, screen_h)
        self.door.update(dt, player_rect)

    def player_lethal_hit(self, player_rect: pygame.Rect) -> bool:
        return any(trap.is_lethal(player_rect) for trap in self.traps)

    def is_complete(self, player_rect: pygame.Rect) -> bool:
        return self.door.player_passed_through(player_rect)

    def reset(self) -> None:
        for platform in self.platforms:
            platform.reset()
        self.traps = random.choice(self.trap_layouts)
        for trap in self.traps:
            trap.reset()
        self.door.reset()

    def draw(self, screen: pygame.Surface) -> None:
        for platform in self.platforms:
            platform.draw(screen)
        for trap in self.traps:
            trap.draw(screen)
        self.door.draw(screen)


def create_level_1(
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:
    """Phase 1 — horizontal traversal with sneaky traps and a door at the end.

    Vertical jump cap is ~178 px (JUMP_FORCE=800, GRAVITY=1800), so any
    vertical step is comfortably under that. Layout fans out horizontally
    instead of stacking tiers.
    """
    H = screen_height

    rock_a = TEXTURES["rock_1a"]
    rock_b = TEXTURES["rock_1b"]
    rock_c = TEXTURES["rock_1c"]
    rock_d = TEXTURES["rock_1d"]

    platforms = [
        # ─── Floor — four segments separated by lethal gaps ──────────
        Platform(0,    H - 80,  300, 20, rock_b),
        Platform(380,  H - 80,  240, 20, rock_b),
        Platform(700,  H - 80,  220, 20, rock_b),
        Platform(1000, H - 80,  280, 20, rock_b),

        # ─── Mid tier (~140 above floor) — alt route, two fakes ──────
        Platform(180,  H - 220, 128, 20, rock_c),
        Platform(440,  H - 220, 128, 20, rock_a, is_fake=True),
        Platform(620,  H - 220, 144, 20, rock_c),
        Platform(820,  H - 220, 128, 20, rock_a, is_fake=True),
        Platform(1040, H - 220, 144, 20, rock_c),

        # ─── A couple of high lookouts — purely optional ─────────────
        Platform(320,  H - 360, 128, 20, rock_d),
        Platform(760,  H - 360, 128, 20, rock_d),
    ]

    # Three distinct trap arrangements — one is picked randomly each run so
    # players can't memorize the timing. Each layout has six boxes spread
    # across the level and remains playable on its own.
    trap_layouts_x = [
        [340, 520, 660, 860, 950, 1140],
        [250, 460, 740, 870, 1080, 1200],
        [380, 580, 690, 820, 970, 1100],
    ]
    trap_layouts = [
        [FallingBox(x=x) for x in layout] for layout in trap_layouts_x
    ]

    door = Door(x=1220, ground_y=H - 80)

    spawn = (60, 200)
    return Level(platforms, trap_layouts, door), spawn
