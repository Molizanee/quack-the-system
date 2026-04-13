from pygame import Color


class Colors:
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    PLAYER = Color(0, 120, 255)
    GROUND = Color(100, 100, 100)


class PlayerSettings:
    SIZE = 50
    SPEED = 400
    JUMP_FORCE = 800
    GRAVITY = 1800
