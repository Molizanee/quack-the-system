import pygame

from src.constants import PlayerSettings


class Player(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        sheet = pygame.image.load(
            "src/assets/duck/ducky_3_spritesheet.png"
        ).convert_alpha()
        frame_w, frame_h = 32, 32

        def get_frame(col: int, row: int) -> pygame.Surface:
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), rect)
            return pygame.transform.scale(frame, (64, 64))

        idle_right = [get_frame(0, 0), get_frame(1, 0)]
        walk_right = [
            get_frame(0, 1),
            get_frame(1, 1),
            get_frame(2, 1),
            get_frame(3, 1),
            get_frame(4, 1),
            get_frame(5, 1),
        ]
        quack_right = [
            get_frame(0, 2),
            get_frame(1, 2),
            get_frame(2, 2),
            get_frame(3, 2),
            get_frame(4, 2),
        ]
        jump_right = [
            get_frame(0, 3),
            get_frame(1, 3),
            get_frame(2, 3),
            get_frame(3, 3),
        ]

        idle_left = [pygame.transform.flip(frame, True, False) for frame in idle_right]
        walk_left = [pygame.transform.flip(frame, True, False) for frame in walk_right]
        quack_left = [pygame.transform.flip(frame, True, False) for frame in quack_right]
        jump_left = [pygame.transform.flip(frame, True, False) for frame in jump_right]

        self.animations: dict[str, list[pygame.Surface]] = {
            "idle_right": idle_right,
            "walk_right": walk_right,
            "quack_right": quack_right,
            "jump_right": jump_right,
            "idle_left": idle_left,
            "walk_left": walk_left,
            "quack_left": quack_left,
            "jump_left": jump_left,
        }

        self.facing = "right"
        self.state = "idle_right"
        self.frame_index = 0.0
        self.animation_fps = 10.0
        self.idle_fps = 0.2
        self.quack_fps = 8.0

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0
        self.is_grounded: bool = False
        self.is_quacking: bool = False

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.velocity_x = 0.0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -PlayerSettings.SPEED
            self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = PlayerSettings.SPEED
            self.facing = "right"

    def jump(self) -> None:
        if self.is_grounded:
            self.velocity_y = -PlayerSettings.JUMP_FORCE
            self.is_grounded = False

    def quack(self) -> None:
        """Start the quack animation (one-shot, plays once then returns to idle)."""
        if not self.is_quacking:
            self.is_quacking = True
            self.frame_index = 0.0

    def update(
        self, dt: float, keys: pygame.key.ScancodeWrapper, platforms: list[pygame.Rect]
    ) -> None:
        self.handle_input(keys)

        # Apply gravity
        self.velocity_y += PlayerSettings.GRAVITY * dt

        # Horizontal movement
        self.rect.x += int(self.velocity_x * dt)

        # Vertical movement
        self.rect.y += int(self.velocity_y * dt)

        # Check platform collisions (landing on top)
        self.is_grounded = False
        for platform_rect in platforms:
            if self.rect.colliderect(platform_rect):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = platform_rect.top
                    self.velocity_y = 0
                    self.is_grounded = True

        # Ground probe: check if standing on a platform (edge-touching case)
        # pygame.Rect.colliderect returns False when rects share an edge,
        # so we probe 1 pixel below the player's feet to stay grounded.
        if not self.is_grounded and self.velocity_y >= 0:
            ground_probe = pygame.Rect(
                self.rect.x, self.rect.bottom, self.rect.width, 2
            )
            for platform_rect in platforms:
                if ground_probe.colliderect(platform_rect):
                    self.rect.bottom = platform_rect.top
                    self.velocity_y = 0
                    self.is_grounded = True
                    break

        # Choose animation state
        if not self.is_grounded:
            self.state = f"jump_{self.facing}"
            self.is_quacking = False
        elif self.is_quacking:
            self.state = f"quack_{self.facing}"
        elif self.velocity_x != 0:
            self.state = f"walk_{self.facing}"
        else:
            self.state = f"idle_{self.facing}"

        # Animate (time-based)
        frames = self.animations[self.state]
        if self.state.startswith("idle"):
            fps = self.idle_fps
        elif self.state.startswith("quack"):
            fps = self.quack_fps
        else:
            fps = self.animation_fps

        self.frame_index += fps * dt
        if self.frame_index >= len(frames):
            if self.is_quacking:
                # Quack is a one-shot animation
                self.is_quacking = False
                self.frame_index = 0.0
                self.state = f"idle_{self.facing}"
                frames = self.animations[self.state]
            else:
                self.frame_index = 0.0

        self.image = frames[int(self.frame_index)]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
