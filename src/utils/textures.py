import pygame

from src.utils.paths import resource_path

TEXTURE_PATHS = {
    "rock_1a": resource_path("src/assets/textures/1a.png"),
    "rock_1b": resource_path("src/assets/textures/1b.png"),
    "rock_1c": resource_path("src/assets/textures/1c.png"),
    "rock_1d": resource_path("src/assets/textures/1d.png"),
    "rock_1e": resource_path("src/assets/textures/1e.png"),
}


def load_textures() -> dict[str, pygame.Surface]:
    pygame.display.set_mode()
    textures: dict[str, pygame.Surface] = {}
    for key, path in TEXTURE_PATHS.items():
        texture = pygame.image.load(path).convert_alpha()
        textures[key] = texture
    return textures


TEXTURES = load_textures()
