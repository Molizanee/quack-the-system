import pygame

from src.constants import PlayerSettings
from src.platform import Platform
from src.utils.paths import resource_path


class Player(pygame.sprite.Sprite):
    # The duck sprite frame is 64x64 but the visible duck only fills the
    # middle ~40x48. A tight hitbox makes wall slides land on the body
    # rather than the transparent margin, and keeps trap collisions fair.
    HITBOX_W = 40
    HITBOX_H = 48
    HITBOX_INSET_X = 12  # symmetric left/right padding inside the frame
    HITBOX_INSET_Y = 12  # padding above the duck's head; feet sit ~4px above frame bottom

    # Per-substep cap on movement. Splitting motion into <= MAX_STEP px
    # chunks prevents tunneling: at gravity 1800 + jump_force 800, a
    # falling player can travel ~30px/frame, more than the 20px-thin
    # platforms. 8 < 20/2 leaves margin for the AABB sweep.
    MAX_STEP = 8

    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        sheet = pygame.image.load(
            resource_path("src/assets/duck/ducky_3_spritesheet.png")
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

        # `rect` IS the collision hitbox (every other system queries it).
        # `(x, y)` from callers is treated as the image-frame topleft so
        # existing spawn coordinates keep working visually.
        self.rect = pygame.Rect(
            int(x) + self.HITBOX_INSET_X,
            int(y) + self.HITBOX_INSET_Y,
            self.HITBOX_W,
            self.HITBOX_H,
        )

        # Float-precision position. pygame.Rect is integer-only, so we
        # accumulate movement here and round into the rect each step;
        # otherwise sub-pixel velocities (gravity tick, slow walk) would
        # silently truncate to zero each frame.
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

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
        self, dt: float, keys: pygame.key.ScancodeWrapper, platforms: list[Platform]
    ) -> None:
        self.handle_input(keys)
        self.velocity_y += PlayerSettings.GRAVITY * dt

        dx = self.velocity_x * dt
        dy = self.velocity_y * dt

        # Swept AABB via substepping. We resolve X then Y separately so
        # that walking into a wall while airborne still allows vertical
        # motion (and vice versa) — the standard pygame platformer trick.
        steps = max(1, int(max(abs(dx), abs(dy)) // self.MAX_STEP) + 1)
        step_dx = dx / steps
        step_dy = dy / steps

        self.is_grounded = False
        for _ in range(steps):
            # ── X-axis ────────────────────────────────────────────────
            self.pos_x += step_dx
            self.rect.x = int(self.pos_x)
            for platform in platforms:
                if not platform.is_solid:
                    continue
                if self.rect.colliderect(platform.rect):
                    if step_dx > 0:
                        self.rect.right = platform.rect.left
                    elif step_dx < 0:
                        self.rect.left = platform.rect.right
                    self.pos_x = float(self.rect.x)
                    self.velocity_x = 0.0
                    step_dx = 0.0  # cancel any remaining horizontal travel
                    break

            # ── Y-axis ────────────────────────────────────────────────
            self.pos_y += step_dy
            self.rect.y = int(self.pos_y)
            for platform in platforms:
                if not platform.is_solid:
                    continue
                if self.rect.colliderect(platform.rect):
                    if step_dy > 0:  # falling: land on top
                        self.rect.bottom = platform.rect.top
                        self.is_grounded = True
                        platform.on_land()
                    elif step_dy < 0:  # rising: bonk head, drop velocity
                        self.rect.top = platform.rect.bottom
                    self.pos_y = float(self.rect.y)
                    self.velocity_y = 0.0
                    step_dy = 0.0
                    break

        # Ground probe: pygame.Rect.colliderect treats shared edges as
        # non-overlapping, so a player resting exactly on a platform
        # would lose `is_grounded` between landings. Probe 1px below the
        # feet to keep the flag sticky while standing or walking.
        if not self.is_grounded and self.velocity_y >= 0:
            probe = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)
            for platform in platforms:
                if not platform.is_solid:
                    continue
                if probe.colliderect(platform.rect):
                    self.rect.bottom = platform.rect.top
                    self.pos_y = float(self.rect.y)
                    self.velocity_y = 0.0
                    self.is_grounded = True
                    platform.on_land()
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
        screen.blit(
            self.image,
            (self.rect.x - self.HITBOX_INSET_X, self.rect.y - self.HITBOX_INSET_Y),
        )

    def respawn(self, x: float, y: float) -> None:
        self.rect.topleft = (
            int(x) + self.HITBOX_INSET_X,
            int(y) + self.HITBOX_INSET_Y,
        )
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_grounded = False
        self.is_quacking = False
        self.frame_index = 0.0
        self.facing = "right"
        self.state = "idle_right"
        self.image = self.animations[self.state][0]
