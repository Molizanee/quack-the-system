import pygame

TEXTURE_ROCK_1A_PATH = "src/assets/textures/1a.png"
TEXTURE_ROCK_1B_PATH = "src/assets/textures/1b.png"
TEXTURE_ROCK_1C_PATH = "src/assets/textures/1c.png"
TEXTURE_ROCK_1D_PATH = "src/assets/textures/1d.png"
TEXTURE_ROCK_1E_PATH = "src/assets/textures/1e.png"


def load_texture(path: str) -> pygame.Surface:
    pygame.display.set_mode()
    texture = pygame.image.load(path).convert_alpha()
    return texture


ROCK_TEXTURES = [
    load_texture(TEXTURE_ROCK_1A_PATH),
    load_texture(TEXTURE_ROCK_1B_PATH),
    load_texture(TEXTURE_ROCK_1C_PATH),
    load_texture(TEXTURE_ROCK_1D_PATH),
    load_texture(TEXTURE_ROCK_1E_PATH),
]
