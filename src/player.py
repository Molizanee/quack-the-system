import pygame

from src.constants import Colors, PlayerSettings


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.rect = pygame.Rect(x, y, PlayerSettings.SIZE, PlayerSettings.SIZE)
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0
        self.is_grounded: bool = False

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.velocity_x = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -PlayerSettings.SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = PlayerSettings.SPEED

    def jump(self) -> None:
        if self.is_grounded:
            self.velocity_y = -PlayerSettings.JUMP_FORCE
            self.is_grounded = False

    def update(self, dt: float, platforms: list[pygame.Rect]) -> None:
        self.velocity_y += PlayerSettings.GRAVITY * dt
        self.rect.x = int(self.rect.x + self.velocity_x * dt)
        self.rect.y = int(self.rect.y + self.velocity_y * dt)
        self.is_grounded = False
        for platform_rect in platforms:
            if self.rect.colliderect(platform_rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform_rect.top
                    self.velocity_y = 0
                    self.is_grounded = True

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, Colors.PLAYER, self.rect)
