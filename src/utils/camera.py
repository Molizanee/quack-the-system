import pygame


class Camera:
    """Camera that follows the player and clamps to world boundaries.

    The camera stores an offset that should be subtracted from world
    coordinates when drawing, so objects scroll in the opposite direction
    of camera movement.
    """

    def __init__(self, world_width: int, world_height: int) -> None:
        self.world_width = world_width
        self.world_height = world_height
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    def update(self, target: pygame.Rect, screen_width: int, screen_height: int) -> None:
        """Center the camera on *target*, clamping to world edges.

        Args:
            target: The rect to follow (typically the player).
            screen_width: Width of the visible screen area.
            screen_height: Height of the visible screen area.
        """
        # Centre the target on screen
        self.offset_x = target.centerx - screen_width // 2
        self.offset_y = target.centery - screen_height // 2

        # Clamp so we never show area outside the world
        self.offset_x = max(0, min(self.offset_x, self.world_width - screen_width))
        self.offset_y = max(0, min(self.offset_y, self.world_height - screen_height))

    def apply(self, rect: pygame.Rect) -> tuple[int, int]:
        """Return the screen position for a world-space rect.

        Args:
            rect: A rect in world coordinates.

        Returns:
            Tuple of (screen_x, screen_y) after applying camera offset.
        """
        return (int(rect.x - self.offset_x), int(rect.y - self.offset_y))

    def apply_pos(self, x: float, y: float) -> tuple[int, int]:
        """Return the screen position for arbitrary world coordinates.

        Args:
            x: World x coordinate.
            y: World y coordinate.

        Returns:
            Tuple of (screen_x, screen_y) after applying camera offset.
        """
        return (int(x - self.offset_x), int(y - self.offset_y))
