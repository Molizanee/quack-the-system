import pygame

from src.constants import Colors


class Platform:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, Colors.GROUND, self.rect)
