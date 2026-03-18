from src.levels.level_ods_1 import Level, create_level_1

__all__ = ["Level", "levels", "init_levels"]


def init_levels(screen_width: int, screen_height: int) -> list[Level]:
    return [create_level_1(screen_width, screen_height)]


levels: list[Level] = []
