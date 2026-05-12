import pygame

from src.utils.fonts import FONT_MEDIUM
from src.utils.paths import resource_path

SKULL_PATH = resource_path("src/assets/icons/Skull.png")


class HUD:
    TEXT_COLOR = (245, 245, 245)
    SHADOW_COLOR = (0, 0, 0)
    PANEL_COLOR = (15, 15, 25, 170)

    def __init__(self, font_size: int = 32, icon_size: int = 36) -> None:
        self.font = pygame.font.Font(FONT_MEDIUM, font_size)
        icon = pygame.image.load(SKULL_PATH).convert_alpha()
        self.icon = pygame.transform.scale(icon, (icon_size, icon_size))
        self.icon_size = icon_size

    def draw(self, screen: pygame.Surface, deaths: int) -> None:
        label = f"x {deaths}"
        text = self.font.render(label, True, self.TEXT_COLOR)
        shadow = self.font.render(label, True, self.SHADOW_COLOR)

        pad = 12
        panel_w = self.icon_size + pad * 2 + text.get_width() + 8
        panel_h = max(self.icon_size, text.get_height()) + pad
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(self.PANEL_COLOR)

        x, y = 20, 20
        screen.blit(panel, (x, y))

        icon_y = y + (panel_h - self.icon_size) // 2
        screen.blit(self.icon, (x + pad, icon_y))

        text_x = x + pad + self.icon_size + 8
        text_y = y + (panel_h - text.get_height()) // 2
        screen.blit(shadow, (text_x + 2, text_y + 2))
        screen.blit(text, (text_x, text_y))
