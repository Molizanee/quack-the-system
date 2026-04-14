import math
import random

import pygame


# Effect registry: maps string keys to callables(level, player) -> None.
# Future trap effects register here without touching trigger logic.
EFFECT_REGISTRY: dict[str, callable] = {
    "placeholder": lambda level, player: player.die(),
}


class TrapZone:
    def __init__(
        self,
        trap_id: str,
        x: int,
        y: int,
        radius: int,
        effect: str,
        reset_chance: float,
    ) -> None:
        self.trap_id = trap_id
        self.center = pygame.Vector2(x, y)
        self.radius = radius
        self.effect = effect          # key into EFFECT_REGISTRY
        self.reset_chance = reset_chance
        self.triggered = False        # True after the trap fires

    def check_proximity(self, player_rect: pygame.Rect) -> bool:
        """Returns True if player centre is within radius and trap is still active."""
        if self.triggered:
            return False
        player_center = pygame.Vector2(player_rect.centerx, player_rect.centery)
        return player_center.distance_to(self.center) <= self.radius

    def trigger(self) -> str:
        """Marks the trap as fired and returns the effect key to execute."""
        self.triggered = True
        return self.effect

    def try_reset(self) -> None:
        """Called on player respawn — resets state based on World Memory probability."""
        if self.triggered and random.random() < self.reset_chance:
            self.triggered = False

    def draw_debug(
        self, screen: pygame.Surface, camera: tuple[int, int] = (0, 0)
    ) -> None:
        """Red semi-transparent square centred on the trigger zone (dev mode only)."""
        size = self.radius * 2
        surf = pygame.Surface((size, size))
        surf.fill((255, 0, 0))
        surf.set_alpha(153)           # ~60% opacity (153/255 ≈ 0.6)
        screen.blit(
            surf,
            (
                int(self.center.x - self.radius) - camera[0],
                int(self.center.y - self.radius) - camera[1],
            ),
        )
