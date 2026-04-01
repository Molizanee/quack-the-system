import pygame

from src.platform import Platform
from src.utils.textures import TEXTURES


class Level:
    def __init__(self, platforms: list[Platform]) -> None:
        self.platforms = platforms

    def get_platform_rects(self) -> list[pygame.Rect]:
        return [platform.rect for platform in self.platforms]

    def draw(self, screen: pygame.Surface) -> None:
        for platform in self.platforms:
            platform.draw(screen)


def create_level_1(
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:

    platforms = [
        Platform(200, screen_height - 180, 150, 20, TEXTURES["rock_1b"]),
        Platform(450, screen_height - 280, 150, 20, TEXTURES["rock_1c"]),
        Platform(100, screen_height - 380, 120, 20, TEXTURES["rock_1d"]),
    ]

    return Level(platforms), (100, 200)
