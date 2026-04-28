"""Menu screens and UI components for Quack the System.

Provides the main menu, credits screen, and in-game pause overlay.
All menus support keyboard (arrow keys + ENTER/SPACE) and mouse navigation.
"""

import math

import pygame

from src.utils.paths import resource_path

FONT_PATH = resource_path("src/assets/fonts/PixelPurl.ttf")

# ── Colour palette ────────────────────────────────────────────────────────
PANEL_NORMAL = (30, 30, 55, 180)
PANEL_HOVER = (70, 55, 120, 220)
TEXT_COLOR = (245, 245, 245)
TEXT_SHADOW = (10, 10, 20)
CREDITS_TITLE_COLOR = (255, 220, 100)
CREDITS_TEXT_COLOR = (220, 220, 235)
OVERLAY_COLOR = (0, 0, 0, 160)


class Button:
    """A styled menu button with hover/selection highlight.

    Supports both mouse hover detection and keyboard-driven selection.
    """

    def __init__(
        self,
        text: str,
        center_x: int,
        center_y: int,
        width: int = 340,
        height: int = 64,
        font_size: int = 34,
    ) -> None:
        self.text = text
        self.center_x = center_x
        self.center_y = center_y
        self.base_width = width
        self.base_height = height

        self.font = pygame.font.Font(FONT_PATH, font_size)
        self._rebuild_rect()

        # Animation state
        self._hover_t: float = 0.0  # 0→1 interpolation for smooth highlight

    # ── helpers ────────────────────────────────────────────────────────

    def _rebuild_rect(self) -> None:
        self.rect = pygame.Rect(0, 0, self.base_width, self.base_height)
        self.rect.center = (self.center_x, self.center_y)

    # ── public API ────────────────────────────────────────────────────

    def update(self, dt: float, selected: bool) -> None:
        """Smoothly interpolate hover intensity."""
        target = 1.0 if selected else 0.0
        speed = 8.0  # transition speed
        if self._hover_t < target:
            self._hover_t = min(target, self._hover_t + speed * dt)
        else:
            self._hover_t = max(target, self._hover_t - speed * dt)

    def draw(self, screen: pygame.Surface) -> None:
        t = self._hover_t

        # Slight scale-up when hovered
        scale = 1.0 + 0.06 * t
        w = int(self.base_width * scale)
        h = int(self.base_height * scale)
        panel = pygame.Surface((w, h), pygame.SRCALPHA)

        # Interpolate panel colour
        r = int(PANEL_NORMAL[0] + (PANEL_HOVER[0] - PANEL_NORMAL[0]) * t)
        g = int(PANEL_NORMAL[1] + (PANEL_HOVER[1] - PANEL_NORMAL[1]) * t)
        b = int(PANEL_NORMAL[2] + (PANEL_HOVER[2] - PANEL_NORMAL[2]) * t)
        a = int(PANEL_NORMAL[3] + (PANEL_HOVER[3] - PANEL_NORMAL[3]) * t)
        panel.fill((r, g, b, a))

        # Optional border glow
        if t > 0.01:
            border_alpha = int(180 * t)
            border_color = (160, 130, 255, border_alpha)
            border_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(border_surf, border_color, (0, 0, w, h), 3, border_radius=6)
            panel.blit(border_surf, (0, 0))

        # Text (centered)
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        shadow_surf = self.font.render(self.text, True, TEXT_SHADOW)
        tx = (w - text_surf.get_width()) // 2
        ty = (h - text_surf.get_height()) // 2
        panel.blit(shadow_surf, (tx + 2, ty + 2))
        panel.blit(text_surf, (tx, ty))

        # Blit panel centered
        dest = panel.get_rect(center=(self.center_x, self.center_y))
        screen.blit(panel, dest)

    def contains_point(self, pos: tuple[int, int]) -> bool:
        """Check if a screen position is inside the button rect."""
        return self.rect.collidepoint(pos)


# ══════════════════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════════════════


class MainMenu:
    """Landing screen with Começar, Créditos, and Sair buttons."""

    def __init__(
        self,
        bg_blurred: pygame.Surface,
        title_image: pygame.Surface,
        screen_w: int,
        screen_h: int,
    ) -> None:
        self.bg = bg_blurred
        self.title_image = title_image
        self.screen_w = screen_w
        self.screen_h = screen_h

        cx = screen_w // 2
        title_bottom = screen_h // 2 - 30 + title_image.get_height() // 2

        btn_start_y = title_bottom + 80
        btn_gap = 80

        self.buttons = [
            Button("Começar o Jogo", cx, btn_start_y),
            Button("Créditos", cx, btn_start_y + btn_gap),
            Button("Sair", cx, btn_start_y + btn_gap * 2),
        ]
        self.selected = 0
        self._time: float = 0.0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Process a single event. Returns action or None.

        Possible actions: ``"start"``, ``"credits"``, ``"quit"``.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._action_for(self.selected)

        if event.type == pygame.MOUSEMOTION:
            for i, btn in enumerate(self.buttons):
                if btn.contains_point(event.pos):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.buttons):
                if btn.contains_point(event.pos):
                    return self._action_for(i)

        return None

    def update(self, dt: float) -> None:
        self._time += dt
        for i, btn in enumerate(self.buttons):
            btn.update(dt, selected=(i == self.selected))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg, (0, 0))

        # Title image
        title_rect = self.title_image.get_rect(
            center=(self.screen_w // 2, self.screen_h // 2 - 30)
        )
        screen.blit(self.title_image, title_rect)

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)

    # ── private ────────────────────────────────────────────────────────

    @staticmethod
    def _action_for(index: int) -> str:
        return ("start", "credits", "quit")[index]


# ══════════════════════════════════════════════════════════════════════════
# Credits Screen
# ══════════════════════════════════════════════════════════════════════════


class CreditsScreen:
    """Shows game credits over the blurred background."""

    CREDITS_LINES: list[tuple[str, bool]] = [
        ("Quack the System", True),   # True = title/heading style
        ("", False),
        ("Desenvolvido por", True),
        ("Marcos Olizane", False),
        ("", False),
        ("Engine", True),
        ("Python 3.13 + Pygame", False),
        ("", False),
        ("Assets", True),
        ("Sprites — Pixel Frog", False),
        ("Fonte — PixelPurl", False),
        ("UI — Kenney.nl", False),
        ("", False),
        ("Agradecimentos", True),
        ("Obrigado por jogar!", False),
    ]

    def __init__(
        self,
        bg_blurred: pygame.Surface,
        screen_w: int,
        screen_h: int,
    ) -> None:
        self.bg = bg_blurred
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.title_font = pygame.font.Font(FONT_PATH, 38)
        self.body_font = pygame.font.Font(FONT_PATH, 28)

        cx = screen_w // 2
        self.back_button = Button("Voltar", cx, screen_h - 90, width=220, height=56)
        self.selected = 0  # only one button
        self._time: float = 0.0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns ``"back"`` when the user wants to leave credits."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                return "back"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.contains_point(event.pos):
                return "back"

        return None

    def update(self, dt: float) -> None:
        self._time += dt
        # Back button is always "selected" since it's the only one
        mouse_over = self.back_button.contains_point(pygame.mouse.get_pos())
        self.back_button.update(dt, selected=True or mouse_over)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg, (0, 0))

        # Dark overlay for readability
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Render credits lines centered
        y = 100
        for text, is_heading in self.CREDITS_LINES:
            if not text:
                y += 18
                continue
            font = self.title_font if is_heading else self.body_font
            color = CREDITS_TITLE_COLOR if is_heading else CREDITS_TEXT_COLOR
            surf = font.render(text, True, color)
            shadow = font.render(text, True, TEXT_SHADOW)
            x = (self.screen_w - surf.get_width()) // 2
            screen.blit(shadow, (x + 2, y + 2))
            screen.blit(surf, (x, y))
            y += surf.get_height() + (20 if is_heading else 12)

        self.back_button.draw(screen)


# ══════════════════════════════════════════════════════════════════════════
# Pause Overlay
# ══════════════════════════════════════════════════════════════════════════


class PauseOverlay:
    """In-game pause screen with a blurred snapshot of the game.

    Call :meth:`capture` once when entering the paused state, then
    :meth:`update` / :meth:`draw` every frame.
    """

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.title_font = pygame.font.Font(FONT_PATH, 52)

        cx = screen_w // 2
        cy = screen_h // 2

        self.buttons = [
            Button("Recomeçar", cx, cy + 30, width=300, height=60),
            Button("Sair", cx, cy + 110, width=300, height=60),
        ]
        self.selected = 0
        self._snapshot: pygame.Surface | None = None
        self._time: float = 0.0

    def capture(self, screen: pygame.Surface) -> None:
        """Take a blurred snapshot of the current game frame."""
        self._snapshot = pygame.transform.gaussian_blur(
            screen.copy(), radius=12, repeat_edge_pixels=True
        )
        self._time = 0.0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns ``"resume"``, ``"restart"``, or ``"quit"``."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return ("restart", "quit")[self.selected]

        if event.type == pygame.MOUSEMOTION:
            for i, btn in enumerate(self.buttons):
                if btn.contains_point(event.pos):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.buttons):
                if btn.contains_point(event.pos):
                    return ("restart", "quit")[i]

        return None

    def update(self, dt: float) -> None:
        self._time += dt
        for i, btn in enumerate(self.buttons):
            btn.update(dt, selected=(i == self.selected))

    def draw(self, screen: pygame.Surface) -> None:
        # Blurred game snapshot
        if self._snapshot:
            screen.blit(self._snapshot, (0, 0))

        # Dark overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # "Pausado" title with fade-in
        fade = min(1.0, self._time * 3.0)
        title_surf = self.title_font.render("Pausado", True, TEXT_COLOR)
        title_surf.set_alpha(int(255 * fade))
        shadow_surf = self.title_font.render("Pausado", True, TEXT_SHADOW)
        shadow_surf.set_alpha(int(255 * fade))
        tx = (self.screen_w - title_surf.get_width()) // 2
        ty = self.screen_h // 2 - 80
        screen.blit(shadow_surf, (tx + 3, ty + 3))
        screen.blit(title_surf, (tx, ty))

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)
