import pygame


class Door:
    """Level-exit door. Animates open when the player approaches."""

    SHEET_PATH = "src/assets/elements/doors.png"
    GRID_COLS = 3
    GRID_ROWS = 2
    FRAME_SCALE = 3
    OPEN_FPS = 8.0
    APPROACH_PADDING = 40  # pixels around the door rect that count as "near"

    def __init__(self, x: int, ground_y: int) -> None:
        sheet = pygame.image.load(self.SHEET_PATH).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        frame_w = sheet_w // self.GRID_COLS
        frame_h = sheet_h // self.GRID_ROWS

        self.frames: list[pygame.Surface] = []
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                src = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), src)
                scaled = pygame.transform.scale(
                    frame,
                    (frame_w * self.FRAME_SCALE, frame_h * self.FRAME_SCALE),
                )
                self.frames.append(scaled)

        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x, ground_y))
        self.frame_index = 0.0
        self.state = "closed"  # closed → opening → open
        self.opened = False

    def reset(self) -> None:
        self.frame_index = 0.0
        self.state = "closed"
        self.opened = False
        self.image = self.frames[0]

    def update(self, dt: float, player_rect: pygame.Rect) -> None:
        if self.state == "closed":
            approach = self.rect.inflate(
                self.APPROACH_PADDING * 2, self.APPROACH_PADDING * 2
            )
            if approach.colliderect(player_rect):
                self.state = "opening"
                self.frame_index = 0.0
        elif self.state == "opening":
            self.frame_index += self.OPEN_FPS * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = float(len(self.frames) - 1)
                self.state = "open"
                self.opened = True
            self.image = self.frames[int(self.frame_index)]
        else:  # open
            self.image = self.frames[-1]

    def player_passed_through(self, player_rect: pygame.Rect) -> bool:
        if not self.opened:
            return False
        return self.rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
