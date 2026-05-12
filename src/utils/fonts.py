"""Centralized font paths for the Pixelify Sans family.

Every UI surface in the game loads through these constants so swapping the
font family later is a single-file change. Pick the weight that matches the
role of the text:

- ``FONT_REGULAR`` — body copy, footer prompts.
- ``FONT_MEDIUM``  — button labels, HUD counter; needs to read at smaller sizes.
- ``FONT_SEMIBOLD`` — section headings ("ODS 11 — Nome", credits subheaders).
- ``FONT_BOLD``    — big titles ("Pausado", "Fase completa").
"""

from src.utils.paths import resource_path

FONT_REGULAR = resource_path("src/assets/fonts/PixelifySans-Regular.ttf")
FONT_MEDIUM = resource_path("src/assets/fonts/PixelifySans-Medium.ttf")
FONT_SEMIBOLD = resource_path("src/assets/fonts/PixelifySans-SemiBold.ttf")
FONT_BOLD = resource_path("src/assets/fonts/PixelifySans-Bold.ttf")
