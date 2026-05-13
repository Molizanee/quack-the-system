"""Onboarding overlay for the first phase.

Shows a keyboard-shortcut cheat sheet in pt-BR for the first 10 seconds of
Phase 1, or until the player presses any gameplay key — whichever comes
first. Once dismissed/timed-out, the overlay stays hidden for the rest of
the run (it does not re-appear on death/restart).
"""

import pygame

from src.menu import TEXT_COLOR, TEXT_SHADOW
from src.utils.fonts import FONT_MEDIUM, FONT_SEMIBOLD

DISPLAY_TIME = 10.0
FADE_TIME = 0.5

PANEL_BG = (15, 15, 25, 210)
PANEL_BORDER = (180, 150, 255, 110)
ACCENT_COLOR = (255, 220, 100)

TIPS: list[tuple[str, str]] = [
    ("A  /  ←", "Andar para a esquerda"),
    ("D  /  →", "Andar para a direita"),
    ("ESPACO", "Pular"),
    ("Q", "Quack"),
    ("ESC", "Pausar"),
]

TITLE_TEXT = "Controles"


class ControllerTips:
    """Fading cheat-sheet shown at the start of Phase 1 only."""

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.title_font = pygame.font.Font(FONT_SEMIBOLD, 28)
        self.key_font = pygame.font.Font(FONT_SEMIBOLD, 22)
        self.label_font = pygame.font.Font(FONT_MEDIUM, 22)

        self.elapsed = 0.0
        self.dismissing = False
        self.dismiss_elapsed = 0.0
        self.done = False

        self.panel_surface = self._build_panel()

    def _build_panel(self) -> pygame.Surface:
        pad_x = 28
        pad_y = 20
        line_gap = 8
        col_gap = 24

        title_surf = self.title_font.render(TITLE_TEXT, True, ACCENT_COLOR)
        title_shadow = self.title_font.render(TITLE_TEXT, True, TEXT_SHADOW)

        key_surfs = [self.key_font.render(k, True, TEXT_COLOR) for k, _ in TIPS]
        label_surfs = [self.label_font.render(l, True, TEXT_COLOR) for _, l in TIPS]
        key_shadows = [self.key_font.render(k, True, TEXT_SHADOW) for k, _ in TIPS]
        label_shadows = [self.label_font.render(l, True, TEXT_SHADOW) for _, l in TIPS]

        max_key_w = max(s.get_width() for s in key_surfs)
        max_label_w = max(s.get_width() for s in label_surfs)
        row_h = max(
            key_surfs[0].get_height(),
            label_surfs[0].get_height(),
        )

        content_w = max(title_surf.get_width(), max_key_w + col_gap + max_label_w)
        content_h = (
            title_surf.get_height()
            + line_gap
            + len(TIPS) * row_h
            + (len(TIPS) - 1) * line_gap
        )

        panel_w = content_w + pad_x * 2
        panel_h = content_h + pad_y * 2
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        pygame.draw.rect(
            panel,
            PANEL_BORDER,
            panel.get_rect(),
            width=2,
            border_radius=10,
        )

        title_x = (panel_w - title_surf.get_width()) // 2
        title_y = pad_y
        panel.blit(title_shadow, (title_x + 2, title_y + 2))
        panel.blit(title_surf, (title_x, title_y))

        row_y = title_y + title_surf.get_height() + line_gap
        key_col_x = pad_x
        label_col_x = pad_x + max_key_w + col_gap
        for i, _ in enumerate(TIPS):
            y = row_y + i * (row_h + line_gap)
            panel.blit(key_shadows[i], (key_col_x + 2, y + 2))
            panel.blit(key_surfs[i], (key_col_x, y))
            panel.blit(label_shadows[i], (label_col_x + 2, y + 2))
            panel.blit(label_surfs[i], (label_col_x, y))

        return panel

    def player_acted(self) -> None:
        """Mark the overlay for fade-out after the first gameplay input."""
        if self.done or self.dismissing:
            return
        self.dismissing = True
        self.dismiss_elapsed = 0.0

    def update(self, dt: float) -> None:
        if self.done:
            return
        self.elapsed += dt
        if not self.dismissing and self.elapsed >= DISPLAY_TIME:
            self.dismissing = True
            self.dismiss_elapsed = 0.0
        if self.dismissing:
            self.dismiss_elapsed += dt
            if self.dismiss_elapsed >= FADE_TIME:
                self.done = True

    def _alpha(self) -> float:
        if self.elapsed < FADE_TIME:
            return self.elapsed / FADE_TIME
        if self.dismissing:
            return max(0.0, 1.0 - self.dismiss_elapsed / FADE_TIME)
        return 1.0

    def draw(self, screen: pygame.Surface) -> None:
        if self.done:
            return
        alpha = self._alpha()
        if alpha <= 0.0:
            return
        surface = self.panel_surface.copy()
        surface.set_alpha(int(255 * alpha))
        x = (self.screen_w - surface.get_width()) // 2
        y = self.screen_h - surface.get_height() - 32
        screen.blit(surface, (x, y))
