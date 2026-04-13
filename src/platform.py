from random import randint

import pygame

from src.constants import Colors


class Platform:
    def __init__(
        self, x: int, y: int, width: int, height: int, textures: pygame.Surface
    ) -> None:

        platform_blocks = max(1, int(width / textures.width))
        platform_block_width = textures.width

        self.platform_blocks = platform_blocks
        self.platform_block_width = platform_block_width

        self.rect = pygame.Rect(
            x, y, self.platform_blocks * self.platform_block_width, height
        )
        self.textures = textures

    def draw(self, screen: pygame.Surface, camera: tuple[int, int] = (0, 0)) -> None:
        offset_rect = self.rect.move(-camera[0], -camera[1])
        pygame.draw.rect(screen, Colors.GROUND, offset_rect)
        for index in range(int(self.platform_blocks)):
            # random = randint(0, 1)

            screen.blit(
                self.textures,
                (
                    self.rect.x + index * self.platform_block_width - camera[0],
                    self.rect.y - camera[1],
                ),
            )
