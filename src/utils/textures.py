import pygame

TEXTURE_PATHS = {
    "rock_1a": "src/assets/textures/1a.png",
    "rock_1b": "src/assets/textures/1b.png",
    "rock_1c": "src/assets/textures/1c.png",
    "rock_1d": "src/assets/textures/1d.png",
    "rock_1e": "src/assets/textures/1e.png",
}


def load_textures() -> dict[str, pygame.Surface]:
    pygame.display.set_mode()
    textures: dict[str, pygame.Surface] = {}
    for key, path in TEXTURE_PATHS.items():
        texture = pygame.image.load(path).convert_alpha()
        textures[key] = texture
    return textures


TEXTURES = load_textures()
