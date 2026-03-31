from random import randint

import pygame

from src.constants import Colors


class Platform:
    def __init__(
        self, x: int, y: int, width: int, height: int, textures: list[pygame.Surface]
    ) -> None:

        platform_blocks = int(x / textures[0].width)
        platform_block_width = textures[0].width

        self.platform_blocks = platform_blocks
        self.platform_block_width = platform_block_width

        self.rect = pygame.Rect(
            x, y, self.platform_blocks * self.platform_block_width, height
        )
        self.textures = textures

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, Colors.GROUND, self.rect)
        for index in range(int(self.platform_blocks)):
            random = randint(0, len(self.textures) - 1)

            screen.blit(
                self.textures[random],
                (self.rect.x + index * self.platform_block_width, self.rect.y),
            )
