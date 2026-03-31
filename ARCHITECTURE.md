# Quack The System - Architecture

## Project Overview

**Quack The System** is a pygame platformer game with:
- 3 game states: TITLE → TRANSITION → PLAYING
- Player movement with gravity and platform collision
- Level system with platform-based gameplay

## Module Structure & Connections

```
main.py
├── init_levels(width, height)          → returns list[Level]
├── Player(x, y)                        → positioned on ground
├── Game loop states:
│   ├── TITLE: Press SPACE → TRANSITION
│   ├── TRANSITION: 1s fade → PLAYING  
│   └── PLAYING:
│       ├── player.handle_input(keys)  → WASD/Arrow keys
│       ├── player.update(dt, platforms) → physics + collision
│       └── player.draw(screen)

src/
├── constants.py
│   ├── Colors (BLACK, WHITE, PLAYER, GROUND)
│   └── PlayerSettings (SIZE, SPEED, JUMP_FORCE, GRAVITY)
├── player.py
│   └── Player class:
│       ├── handle_input() → sets velocity_x
│       ├── jump() → applies velocity_y if grounded
│       ├── update() → applies gravity, collision detection
│       └── draw() → renders player rect
├── platform.py
│   └── Platform class: rect + draw()
└── levels/
    ├── __init__.py
    │   └── init_levels() → calls create_level_1()
    └── level_ods_1.py
        ├── Level class: platforms list, get_platform_rects(), draw()
        └── create_level_1(): generates ground + floating platforms
```

## Key Connections

1. **main.py:53** calls `init_levels()` → returns `[Level]`
2. **main.py:56** creates `Player` positioned on `ground.rect.top`
3. **main.py:109** passes `current_level.get_platform_rects()` to `player.update()` for collision
4. **Level.draw()** iterates platforms → calls `Platform.draw()`
5. **Player.update()** checks collision against all platform rects

## Function Flow

```
main() → pygame.init()
       → Load assets (background, title image)
       → init_levels() → [Level(platforms)]
       → Game loop:
           │─→ Process events (QUIT, VIDEORESIZE, KEYDOWN)
           │─→ Update state based on current state:
           │   │─→ TITLE: wait for SPACE
           │   │─→ TRANSITION: fade animation (1s)
           │   │─→ PLAYING: 
           │   │       ├─→ player.handle_input(keys)
           │   │       ├─→ player.update(dt, platforms)
           │   │       └─→ (collision resolved inside update)
           │─→ Draw based on state:
           │   │─→ TITLE: background + title + pulsing subtitle
           │   │─→ TRANSITION: fade effect
           │   │─→ PLAYING: background + level + player
           └─→ pygame.display.flip() → render frame
```

## Data Flow

| Component | Input | Output |
|-----------|-------|--------|
| `init_levels(w, h)` | screen dimensions | `list[Level]` |
| `Level.get_platform_rects()` | - | `list[pygame.Rect]` |
| `Player.handle_input(keys)` | keyboard state | `self.velocity_x` |
| `Player.update(dt, platforms)` | delta time, platform rects | updated position + velocity |
| `Player.draw(screen)` | screen surface | rendered rectangle |
| `Platform.draw(screen)` | screen surface | rendered rectangle |

## Constants

Defined in `src/constants.py`:

- **Colors**: BLACK, WHITE, PLAYER (blue), GROUND (gray)
- **PlayerSettings**: SIZE (50px), SPEED (400 px/s), JUMP_FORCE (600), GRAVITY (1800)
