"""Shared ODS cutscene screens — intro narrative + end-of-phase lesson.

Every phase boots through ``OdsIntro`` (2-4 narrative panels in pt-BR) and
ends through ``OdsOutro`` (one short educational message). Both screens sit on
top of a blurred copy of the phase background and accept keyboard input
(Space/Enter to advance, ESC to skip the intro).
"""

import math

import pygame

from src.menu import OVERLAY_COLOR, TEXT_COLOR, TEXT_SHADOW
from src.utils.fonts import FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD

# Layout
PANEL_MARGIN_X = 140
PANEL_MARGIN_Y = 180
PANEL_PADDING = 48
PANEL_BG = (15, 15, 25, 210)
PANEL_BORDER = (180, 150, 255, 80)

# Per-panel fade-in pacing
FADE_IN_TIME = 0.6

# Accent colour for the "ODS 11 — Nome" header
ACCENT_COLOR = (255, 220, 100)


def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Greedy word-wrap that respects max_width using actual rendered width."""
    words = text.split(" ")
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_panel(
    screen: pygame.Surface,
    rect: pygame.Rect,
    alpha: float,
) -> None:
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    bg = (PANEL_BG[0], PANEL_BG[1], PANEL_BG[2], int(PANEL_BG[3] * alpha))
    panel.fill(bg)
    border_alpha = int(PANEL_BORDER[3] * alpha)
    pygame.draw.rect(
        panel,
        (PANEL_BORDER[0], PANEL_BORDER[1], PANEL_BORDER[2], border_alpha),
        panel.get_rect(),
        width=2,
        border_radius=10,
    )
    screen.blit(panel, rect.topleft)


def _draw_shadowed_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    pos: tuple[int, int],
    alpha: float,
) -> None:
    surf = font.render(text, True, color)
    surf.set_alpha(int(255 * alpha))
    shadow = font.render(text, True, TEXT_SHADOW)
    shadow.set_alpha(int(255 * alpha))
    screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
    screen.blit(surf, pos)


class OdsIntro:
    """Pre-gameplay narrative — 2 to 4 panels in pt-BR, advances on Space."""

    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        ods_number: int,
        ods_name: str,
        panels: list[str],
        bg_image: pygame.Surface,
    ) -> None:
        if not panels:
            raise ValueError("OdsIntro needs at least one narrative panel.")
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.ods_number = ods_number
        self.ods_name = ods_name
        self.panels = panels

        # Pre-render the blurred background once; subsequent frames just blit.
        self.bg = pygame.transform.gaussian_blur(
            bg_image, radius=10, repeat_edge_pixels=True
        )

        self.header_font = pygame.font.Font(FONT_SEMIBOLD, 28)
        self.body_font = pygame.font.Font(FONT_REGULAR, 32)
        self.footer_font = pygame.font.Font(FONT_REGULAR, 24)

        self.current_panel = 0
        self.fade_t = 0.0
        self._time = 0.0

        self.panel_rect = pygame.Rect(
            PANEL_MARGIN_X,
            PANEL_MARGIN_Y,
            screen_w - PANEL_MARGIN_X * 2,
            screen_h - PANEL_MARGIN_Y * 2,
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns ``"done"`` after the last panel is dismissed, ``"skip"`` on
        ESC, or ``None`` for any other event.
        """
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_ESCAPE:
            return "skip"
        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.fade_t < 1.0:
                # Snap to fully visible so impatient players don't get stuck
                # waiting for the fade; the same press still advances.
                self.fade_t = 1.0
            if self.current_panel >= len(self.panels) - 1:
                return "done"
            self.current_panel += 1
            self.fade_t = 0.0
        return None

    def update(self, dt: float) -> None:
        self._time += dt
        if self.fade_t < 1.0:
            self.fade_t = min(1.0, self.fade_t + dt / FADE_IN_TIME)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg, (0, 0))

        # Dim full-screen overlay reusing the menu palette
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        alpha = self.fade_t
        _draw_panel(screen, self.panel_rect, alpha)

        inner_x = self.panel_rect.left + PANEL_PADDING
        inner_y = self.panel_rect.top + PANEL_PADDING
        inner_w = self.panel_rect.width - PANEL_PADDING * 2

        header = f"ODS {self.ods_number} — {self.ods_name}"
        _draw_shadowed_text(
            screen, self.header_font, header, ACCENT_COLOR,
            (inner_x, inner_y), alpha,
        )
        inner_y += self.header_font.get_height() + 18

        # Panel body — wrap the current narrative paragraph
        body_text = self.panels[self.current_panel]
        for line in _wrap_text(body_text, self.body_font, inner_w):
            _draw_shadowed_text(
                screen, self.body_font, line, TEXT_COLOR,
                (inner_x, inner_y), alpha,
            )
            inner_y += self.body_font.get_height() + 6

        # Footer prompt — pulses gently to read as "interactive"
        is_last = self.current_panel >= len(self.panels) - 1
        prompt = (
            "Pressione Espaço para começar"
            if is_last
            else "Espaço para continuar — ESC para pular"
        )
        pulse = (math.sin(self._time * 3.0) + 1.0) * 0.5
        footer_alpha = (0.55 + 0.45 * pulse) * alpha
        footer_surf = self.footer_font.render(prompt, True, TEXT_COLOR)
        footer_surf.set_alpha(int(255 * footer_alpha))
        footer_pos = (
            self.panel_rect.centerx - footer_surf.get_width() // 2,
            self.panel_rect.bottom - PANEL_PADDING - footer_surf.get_height(),
        )
        screen.blit(footer_surf, footer_pos)

        # Panel index dots, bottom-left of the panel
        dot_y = self.panel_rect.bottom - PANEL_PADDING + 4
        dot_x = self.panel_rect.left + PANEL_PADDING
        for i in range(len(self.panels)):
            color = ACCENT_COLOR if i == self.current_panel else (110, 110, 130)
            pygame.draw.circle(screen, color, (dot_x + i * 18, dot_y), 5)


class OdsOutro:
    """Post-gameplay educational message — single short lesson, Space to continue."""

    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        ods_number: int,
        ods_name: str,
        lesson_text: str,
        bg_image: pygame.Surface,
        deaths: int,
    ) -> None:
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.ods_number = ods_number
        self.ods_name = ods_name
        self.lesson_text = lesson_text
        self.deaths = deaths

        self.bg = pygame.transform.gaussian_blur(
            bg_image, radius=10, repeat_edge_pixels=True
        )

        self.title_font = pygame.font.Font(FONT_BOLD, 56)
        self.header_font = pygame.font.Font(FONT_SEMIBOLD, 30)
        self.body_font = pygame.font.Font(FONT_REGULAR, 30)
        self.footer_font = pygame.font.Font(FONT_REGULAR, 24)

        self.fade_t = 0.0
        self._time = 0.0

        self.panel_rect = pygame.Rect(
            PANEL_MARGIN_X,
            PANEL_MARGIN_Y,
            screen_w - PANEL_MARGIN_X * 2,
            screen_h - PANEL_MARGIN_Y * 2,
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns ``"continue"`` on Space/Enter once the fade is complete."""
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.fade_t < 1.0:
                self.fade_t = 1.0
                return None
            return "continue"
        return None

    def update(self, dt: float) -> None:
        self._time += dt
        if self.fade_t < 1.0:
            self.fade_t = min(1.0, self.fade_t + dt / FADE_IN_TIME)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg, (0, 0))

        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        alpha = self.fade_t
        _draw_panel(screen, self.panel_rect, alpha)

        inner_x = self.panel_rect.left + PANEL_PADDING
        inner_y = self.panel_rect.top + PANEL_PADDING
        inner_w = self.panel_rect.width - PANEL_PADDING * 2

        title = "Fase completa"
        _draw_shadowed_text(
            screen, self.title_font, title, TEXT_COLOR,
            (inner_x, inner_y), alpha,
        )
        inner_y += self.title_font.get_height() + 12

        header = f"ODS {self.ods_number} — {self.ods_name}"
        _draw_shadowed_text(
            screen, self.header_font, header, ACCENT_COLOR,
            (inner_x, inner_y), alpha,
        )
        inner_y += self.header_font.get_height() + 18

        for line in _wrap_text(self.lesson_text, self.body_font, inner_w):
            _draw_shadowed_text(
                screen, self.body_font, line, TEXT_COLOR,
                (inner_x, inner_y), alpha,
            )
            inner_y += self.body_font.get_height() + 6

        # Death tally — small, bottom-left
        death_text = f"Mortes nesta tentativa: {self.deaths}"
        death_surf = self.footer_font.render(death_text, True, TEXT_COLOR)
        death_surf.set_alpha(int(220 * alpha))
        screen.blit(
            death_surf,
            (
                inner_x,
                self.panel_rect.bottom - PANEL_PADDING - death_surf.get_height(),
            ),
        )

        # Continue prompt, bottom-right
        pulse = (math.sin(self._time * 3.0) + 1.0) * 0.5
        prompt_alpha = (0.55 + 0.45 * pulse) * alpha
        prompt_surf = self.footer_font.render(
            "Pressione Espaço para continuar", True, TEXT_COLOR
        )
        prompt_surf.set_alpha(int(255 * prompt_alpha))
        screen.blit(
            prompt_surf,
            (
                self.panel_rect.right - PANEL_PADDING - prompt_surf.get_width(),
                self.panel_rect.bottom - PANEL_PADDING - prompt_surf.get_height(),
            ),
        )
