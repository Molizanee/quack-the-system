"""Patrolling rat enemy used in polluted-city style phases.

The sprite asset is still pending; until art lands we render a dark body with
two red eye dots so the hitbox is unmistakable on screen. Replace
``_draw_placeholder`` with a sprite blit once the asset exists.
"""

import pygame

WIDTH = 48
HEIGHT = 28
SPEED = 90.0  # pixels/second along the patrol axis
EYE_GAP = 16


class Rat:
    BODY_COLOR = (38, 32, 36)
    BELLY_COLOR = (66, 56, 60)
    EYE_COLOR = (210, 50, 50)

    def __init__(
        self,
        patrol_min_x: int,
        patrol_max_x: int,
        ground_y: int,
    ) -> None:
        if patrol_max_x <= patrol_min_x + WIDTH:
            raise ValueError("Rat patrol range must be wider than the rat.")
        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.ground_y = ground_y

        self.rect = pygame.Rect(patrol_min_x, ground_y - HEIGHT, WIDTH, HEIGHT)
        self._spawn = (self.rect.x, self.rect.y)
        self.direction = 1  # 1 = right, -1 = left

    def reset(self) -> None:
        self.rect.x, self.rect.y = self._spawn
        self.direction = 1

    def update(
        self, dt: float, target_rect: pygame.Rect | None = None
    ) -> None:
        # ``target_rect`` is accepted to match the homing-enemy interface
        # used in later phases; rats ignore it and just patrol.
        del target_rect
        self.rect.x += int(self.direction * SPEED * dt)
        if self.rect.left <= self.patrol_min_x:
            self.rect.left = self.patrol_min_x
            self.direction = 1
        elif self.rect.right >= self.patrol_max_x:
            self.rect.right = self.patrol_max_x
            self.direction = -1

    def is_lethal(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        # Body
        pygame.draw.rect(screen, self.BODY_COLOR, self.rect, border_radius=8)
        # Belly highlight so the rat reads as 3D, not a flat block
        belly = self.rect.inflate(-10, -HEIGHT // 2)
        belly.bottom = self.rect.bottom - 4
        pygame.draw.rect(screen, self.BELLY_COLOR, belly, border_radius=6)
        # Eyes — leading eye in the patrol direction sits closer to the muzzle
        eye_y = self.rect.top + 8
        if self.direction >= 0:
            front_x = self.rect.right - 10
            back_x = self.rect.right - 10 - EYE_GAP
        else:
            front_x = self.rect.left + 10
            back_x = self.rect.left + 10 + EYE_GAP
        pygame.draw.circle(screen, self.EYE_COLOR, (front_x, eye_y), 3)
        pygame.draw.circle(screen, self.EYE_COLOR, (back_x, eye_y), 3)
