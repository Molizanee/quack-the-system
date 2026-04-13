import pygame

from src.constants import WorldSettings
from src.platform import Platform
from src.utils.textures import TEXTURES


class Level:
    def __init__(self, platforms: list[Platform]) -> None:
        self.platforms = platforms

    def get_platform_rects(self) -> list[pygame.Rect]:
        return [platform.rect for platform in self.platforms]

    def draw(self, screen: pygame.Surface, camera: tuple[int, int] = (0, 0)) -> None:
        for platform in self.platforms:
            platform.draw(screen, camera)


def create_level_1(
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:
    ground_y = WorldSettings.HEIGHT - 40

    platforms = [
        # Ground spanning the full world width
        Platform(0, ground_y, WorldSettings.WIDTH, 40, TEXTURES["rock_1b"]),

        # --- Near spawn (left area) ---
        Platform(200, ground_y - 140, 150, 20, TEXTURES["rock_1b"]),
        Platform(450, ground_y - 240, 150, 20, TEXTURES["rock_1c"]),
        Platform(100, ground_y - 340, 120, 20, TEXTURES["rock_1d"]),
        Platform(350, ground_y - 420, 180, 20, TEXTURES["rock_1e"]),

        # --- Middle area ---
        Platform(700, ground_y - 160, 200, 20, TEXTURES["rock_1a"]),
        Platform(950, ground_y - 280, 160, 20, TEXTURES["rock_1c"]),
        Platform(800, ground_y - 400, 140, 20, TEXTURES["rock_1d"]),
        Platform(1100, ground_y - 180, 180, 20, TEXTURES["rock_1e"]),
        Platform(1200, ground_y - 320, 200, 20, TEXTURES["rock_1b"]),

        # --- Right area ---
        Platform(1500, ground_y - 150, 220, 20, TEXTURES["rock_1a"]),
        Platform(1700, ground_y - 280, 160, 20, TEXTURES["rock_1c"]),
        Platform(1900, ground_y - 200, 180, 20, TEXTURES["rock_1d"]),
        Platform(1600, ground_y - 420, 200, 20, TEXTURES["rock_1e"]),

        # --- Far right area ---
        Platform(2100, ground_y - 160, 200, 20, TEXTURES["rock_1b"]),
        Platform(2350, ground_y - 300, 180, 20, TEXTURES["rock_1a"]),
        Platform(2500, ground_y - 180, 200, 20, TEXTURES["rock_1c"]),
        Platform(2700, ground_y - 350, 160, 20, TEXTURES["rock_1d"]),

        # --- High platforms (staircase-like) ---
        Platform(500, ground_y - 550, 150, 20, TEXTURES["rock_1a"]),
        Platform(750, ground_y - 650, 150, 20, TEXTURES["rock_1e"]),
        Platform(1000, ground_y - 750, 180, 20, TEXTURES["rock_1b"]),
        Platform(1300, ground_y - 800, 200, 20, TEXTURES["rock_1c"]),
    ]

    spawn = (100, ground_y - 80)
    return Level(platforms), spawn

