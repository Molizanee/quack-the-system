from src.levels.level import Level
from src.levels.level_ods_1 import create_level_1
from src.levels.level_ods_2 import create_level_2

__all__ = ["Level", "levels", "init_levels"]


def init_levels(
    screen_width: int, screen_height: int
) -> list[tuple[Level, tuple[int, int]]]:
    return [
        create_level_1(screen_height),
        create_level_2(screen_width, screen_height),
    ]


levels: list[tuple[Level, tuple[int, int]]] = []
