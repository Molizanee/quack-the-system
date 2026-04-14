import random

import pygame

from src.trap import TrapZone


def generate_traps(
    platforms: list[pygame.Rect],
    count: int = 3,
    radius_range: tuple[int, int] = (30, 45),
    reset_chance_range: tuple[float, float] = (0.4, 1.0),
    effect: str = "placeholder",
) -> list[TrapZone]:
    """Pick *count* random platforms and place a trap zone on each.

    Traps are centred horizontally on the platform and sit just above
    its surface so they trigger when the player lands.
    """
    if not platforms:
        return []

    chosen = random.sample(platforms, min(count, len(platforms)))
    traps: list[TrapZone] = []

    for i, plat in enumerate(chosen):
        radius = random.randint(radius_range[0], radius_range[1])
        reset = round(random.uniform(reset_chance_range[0], reset_chance_range[1]), 2)

        # Centre the zone on the platform, slightly above its top edge
        cx = plat.centerx
        cy = plat.top - radius // 2

        traps.append(
            TrapZone(
                trap_id=f"trap_{i + 1:02d}",
                x=cx,
                y=cy,
                radius=radius,
                effect=effect,
                reset_chance=reset,
            )
        )

    return traps
