# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Quack the System.

Build commands:
    macOS:   pyinstaller quack_the_system.spec
    Windows: pyinstaller quack_the_system.spec

The resulting output depends on the platform:
    macOS:   dist/QuackTheSystem.app (app bundle)
    Windows: dist/QuackTheSystem.exe (standalone executable)
"""

import platform
import sys
from pathlib import Path

block_cipher = None

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(SPECPATH)
ASSETS_DIR = ROOT / "src" / "assets"

# ── Data files (assets bundled into the executable) ────────────────────
# Format: (source, destination_in_bundle)
datas = [
    (str(ASSETS_DIR), "src/assets"),
]

# ── Analysis ───────────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=["pygame"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Build configuration per platform ──────────────────────────────────
if platform.system() == "Darwin":
    # macOS: use one-folder mode + .app BUNDLE (recommended by PyInstaller)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="QuackTheSystem",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="QuackTheSystem",
    )

    app = BUNDLE(
        coll,
        name="QuackTheSystem.app",
        icon=str(ASSETS_DIR / "quack_the_system.png"),
        bundle_identifier="com.quackthesystem.game",
        info_plist={
            "CFBundleName": "Quack The System",
            "CFBundleDisplayName": "Quack The System",
            "CFBundleVersion": "0.1.0",
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
else:
    # Windows / Linux: single-file executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="QuackTheSystem",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon=str(ASSETS_DIR / "quack_the_system.png"),
    )
