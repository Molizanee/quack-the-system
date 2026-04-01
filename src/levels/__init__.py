from src.levels.level_ods_1 import Level, create_level_1

__all__ = ["Level", "levels", "init_levels"]


def init_levels(screen_height: int) -> list[tuple[Level, tuple[int, int]]]:
    return [create_level_1(screen_height)]


levels: list[tuple[Level, tuple[int, int]]] = []
