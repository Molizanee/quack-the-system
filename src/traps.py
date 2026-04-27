import pygame

from src.utils.textures import TEXTURES


class FallingBox:
    """A box that drops without warning when the player wanders below it."""

    BOX_SIZE = 48
    GRAVITY = 1500.0
    TRIGGER_RANGE_X = 90

    def __init__(self, x: int, texture_key: str = "rock_1a") -> None:
        self.spawn_x = x
        self.start_y = -self.BOX_SIZE - 20
        self.rect = pygame.Rect(x, self.start_y, self.BOX_SIZE, self.BOX_SIZE)
        base = TEXTURES[texture_key]
        self.image = pygame.transform.scale(base, (self.BOX_SIZE, self.BOX_SIZE))

        self.state = "armed"  # armed → falling → broken
        self.velocity_y = 0.0

    def reset(self) -> None:
        self.rect.x = self.spawn_x
        self.rect.y = self.start_y
        self.state = "armed"
        self.velocity_y = 0.0

    def update(self, dt: float, player_rect: pygame.Rect, screen_h: int) -> None:
        if self.state == "armed":
            if abs(player_rect.centerx - self.rect.centerx) < self.TRIGGER_RANGE_X:
                self.state = "falling"
        elif self.state == "falling":
            self.velocity_y += self.GRAVITY * dt
            self.rect.y += int(self.velocity_y * dt)
            if self.rect.top > screen_h:
                self.state = "broken"

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return self.state == "falling" and self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == "falling":
            screen.blit(self.image, self.rect.topleft)
