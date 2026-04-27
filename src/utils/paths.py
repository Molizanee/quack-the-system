"""Resolve asset paths for both development and PyInstaller-bundled builds.

When running from source, paths are resolved relative to the project root.
When bundled by PyInstaller, assets are extracted to a temp dir whose path
is stored in ``sys._MEIPASS``.
"""

import os
import sys


def resource_path(relative_path: str) -> str:
    """Get absolute path to a resource, works for dev and PyInstaller bundles.

    Args:
        relative_path: Path relative to the project root (e.g.
            ``"src/assets/fonts/PixelPurl.ttf"``).

    Returns:
        Absolute filesystem path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores its path in _MEIPASS
        base_path: str = sys._MEIPASS  # type: ignore[attr-defined]
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
