import math

import pygame


class Platform:
    COLLAPSE_DELAY = 0.18
    COLLAPSE_GRAVITY = 1800.0

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        textures: pygame.Surface,
        is_fake: bool = False,
    ) -> None:
        self.textures = textures
        self.platform_block_width = textures.width
        self.platform_blocks = max(1, width // self.platform_block_width)
        actual_width = self.platform_blocks * self.platform_block_width

        self.rect = pygame.Rect(x, y, actual_width, height)
        self._origin = (x, y)

        self.is_fake = is_fake
        self.state = "stable"  # stable → collapsing → fallen
        self.collapse_timer = 0.0
        self.fall_velocity = 0.0
        self.shake_offset = 0.0

    @property
    def is_solid(self) -> bool:
        return self.state != "fallen"

    def on_land(self) -> None:
        if self.is_fake and self.state == "stable":
            self.state = "collapsing"
            self.collapse_timer = 0.0

    def update(self, dt: float) -> None:
        if self.state == "collapsing":
            self.collapse_timer += dt
            self.shake_offset = math.sin(self.collapse_timer * 60.0) * 2.0
            if self.collapse_timer >= self.COLLAPSE_DELAY:
                self.state = "fallen"
                self.shake_offset = 0.0
        elif self.state == "fallen":
            self.fall_velocity += self.COLLAPSE_GRAVITY * dt
            self.rect.y += int(self.fall_velocity * dt)

    def reset(self) -> None:
        self.state = "stable"
        self.collapse_timer = 0.0
        self.fall_velocity = 0.0
        self.shake_offset = 0.0
        self.rect.x, self.rect.y = self._origin

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == "fallen" and self.rect.top > screen.get_height():
            return
        offset_x = int(self.shake_offset)
        for index in range(self.platform_blocks):
            screen.blit(
                self.textures,
                (
                    self.rect.x + index * self.platform_block_width + offset_x,
                    self.rect.y,
                ),
            )
