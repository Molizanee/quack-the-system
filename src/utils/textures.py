import pygame

TEXTURE_PATHS = {
    # Set 1 — dark stone (Zone A: dungeon entrance)
    "rock_1a": "src/assets/textures/1a.png",
    "rock_1b": "src/assets/textures/1b.png",
    "rock_1c": "src/assets/textures/1c.png",
    "rock_1d": "src/assets/textures/1d.png",
    "rock_1e": "src/assets/textures/1e.png",
    # Set 3 — mossy/overgrown (Zone B: ancient ruins)
    "rock_3a": "src/assets/textures/3a.png",
    "rock_3b": "src/assets/textures/3b.png",
    "rock_3c": "src/assets/textures/3c.png",
    "rock_3d": "src/assets/textures/3d.png",
    # Set 5 — crystal/luminous (Zone C: sky fortress)
    "rock_5a": "src/assets/textures/5a.png",
    "rock_5b": "src/assets/textures/5b.png",
    "rock_5c": "src/assets/textures/5c.png",
    "rock_5d": "src/assets/textures/5d.png",
}


def load_textures() -> dict[str, pygame.Surface]:
    pygame.display.set_mode()
    textures: dict[str, pygame.Surface] = {}
    for key, path in TEXTURE_PATHS.items():
        texture = pygame.image.load(path).convert_alpha()
        textures[key] = texture
    return textures


TEXTURES = load_textures()
