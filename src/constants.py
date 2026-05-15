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

    # Mario-style water physics. Underwater the duck falls slowly, has a low
    # terminal velocity, and each jump press is a swim stroke that adds
    # upward velocity instead of requiring contact with the ground. Strokes
    # are gated by a short cooldown so spamming Space doesn't shoot Duck
    # straight up.
    WATER_GRAVITY = 380
    WATER_TERMINAL_VELOCITY = 220
    WATER_STROKE_FORCE = 320
    WATER_STROKE_COOLDOWN = 0.22
