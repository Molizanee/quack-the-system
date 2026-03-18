import pygame

from src.platform import Platform


class Level:
    def __init__(self, platforms: list[Platform]) -> None:
        self.platforms = platforms

    def get_platform_rects(self) -> list[pygame.Rect]:
        return [platform.rect for platform in self.platforms]

    def draw(self, screen: pygame.Surface) -> None:
        for platform in self.platforms:
            platform.draw(screen)


def create_level_1(screen_width: int, screen_height: int) -> Level:
    ground = Platform(0, screen_height - 50, screen_width, 50)

    platforms = [
        ground,
        Platform(200, screen_height - 180, 150, 20),
        Platform(450, screen_height - 280, 150, 20),
        Platform(100, screen_height - 380, 120, 20),
    ]

    return Level(platforms)
