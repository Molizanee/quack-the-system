import math

import pygame

from src.constants import WorldSettings
from src.levels import init_levels
from src.player import Player
from src.trap import EFFECT_REGISTRY
from src.utils.camera import Camera

# Game states
STATE_TITLE = "TITLE"
STATE_TRANSITION = "TRANSITION"
STATE_PLAYING = "PLAYING"

DEBUG = True  # Set to False when releasing; True shows trap zones during level design

# Custom font path
FONT_PATH = "src/assets/fonts/PixelPurl.ttf"
LETTER_PATH = "src/assets/letters/quack_the_sytem_main_letter.png"

# Title screen colors (tuples to avoid pygame.Color before init)
SHADOW_COLOR = (20, 20, 40)
OUTLINE_COLOR = (50, 50, 80)
SUBTITLE_COLOR = (255, 255, 255)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Quack The System")
    icon = pygame.image.load("src/assets/quack_the_system.png")
    pygame.display.set_icon(icon)

    info = pygame.display.Info()
    base_w, base_h = info.current_w, info.current_h

    # pygame.SCALED lets SDL handle resolution scaling at the GPU/renderer level.
    # The screen surface stays at a fixed logical size (base_w × base_h) and SDL
    # automatically scales it to fill the window — no manual scaling, no black flashes.
    screen = pygame.display.set_mode(
        (base_w, base_h), pygame.RESIZABLE | pygame.SCALED
    )

    clock = pygame.time.Clock()

    # Load and prepare background (once, at base resolution)
    bg_surface = pygame.image.load(
        "src/assets/backgrounds/inital_screen_background.png"
    ).convert()
    bg_surface = pygame.transform.scale(bg_surface, (base_w, base_h))
    bg_blurred = pygame.transform.gaussian_blur(
        bg_surface, radius=15, repeat_edge_pixels=True
    )

    title_image = pygame.image.load(LETTER_PATH).convert_alpha()
    max_width = int(base_w * 0.6)
    scale_factor = max_width / title_image.get_width()
    title_image = pygame.transform.scale(
        title_image, (max_width, int(title_image.get_height() * scale_factor))
    )
    subtitle_font = pygame.font.Font(FONT_PATH, 36)

    levels = init_levels(base_h)
    current_level, current_spawn = levels[0]

    player = Player(current_spawn[0], current_spawn[1])

    camera = Camera(WorldSettings.WIDTH, WorldSettings.HEIGHT)

    state = STATE_TITLE
    running = True
    title_time = 0.0  # Timer for subtitle pulse animation
    transition_timer = 0.0

    while running:
        dt = clock.tick(60) / 1000.0
        # Cap dt to avoid physics explosion after OS-blocked frames (e.g. during resize)
        dt = min(dt, 0.05)
        title_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if state == STATE_TITLE:
                    if event.key == pygame.K_SPACE:
                        state = STATE_TRANSITION
                        transition_timer = 0.0
                elif state == STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    elif event.key == pygame.K_q:
                        player.quack()

            # --- Update ---
        if state == STATE_TRANSITION:
            transition_timer += dt
            if transition_timer >= 1.0:
                state = STATE_PLAYING

        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            player.update(dt, keys, current_level.get_platform_rects())
            camera.update(player.rect, base_w, base_h)

            fired_effect = current_level.update_traps(player.rect)
            if fired_effect:
                EFFECT_REGISTRY[fired_effect](current_level, player)
                current_level.reset_traps()

        # --- Draw (screen is always base_w × base_h; SDL scales to window) ---
        if state == STATE_TITLE:
            screen.blit(bg_blurred, (0, 0))

            # Draw title image directly (pre-rendered "Quack The System")
            title_center = (base_w // 2, base_h // 2 - 30)
            title_rect = title_image.get_rect(center=title_center)
            screen.blit(title_image, title_rect)

            # Draw subtitle with pulsing opacity animation
            pulse = (math.sin(title_time * 3.0) + 1.0) / 2.0  # 0.0 → 1.0
            alpha = int(100 + 155 * pulse)  # Range: 100–255
            subtitle_surface = subtitle_font.render(
                "Pressione espaço para começar", True, SUBTITLE_COLOR
            )
            subtitle_surface.set_alpha(alpha)
            subtitle_rect = subtitle_surface.get_rect(
                center=(base_w // 2, title_rect.bottom + 60)
            )
            screen.blit(subtitle_surface, subtitle_rect)

        elif state == STATE_TRANSITION:
            fade_surface = pygame.Surface((base_w, base_h))
            fade_surface.fill((0, 0, 0))

            if transition_timer < 0.5:
                # First half: fade title screen to black
                screen.blit(bg_blurred, (0, 0))

                title_center = (base_w // 2, base_h // 2 - 30)
                title_rect = title_image.get_rect(center=title_center)
                screen.blit(title_image, title_rect)

                subtitle_surface = subtitle_font.render(
                    "Pressione espaço para começar", True, SUBTITLE_COLOR
                )
                subtitle_rect = subtitle_surface.get_rect(
                    center=(base_w // 2, title_rect.bottom + 60)
                )
                screen.blit(subtitle_surface, subtitle_rect)

                alpha = int((transition_timer / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
            else:
                # Second half: fade from black to playing screen
                cam = (int(camera.offset_x), int(camera.offset_y))
                screen.blit(bg_surface, (0, 0))
                current_level.draw(screen, cam, DEBUG)
                player.draw(screen, cam)

                alpha = int((1.0 - (transition_timer - 0.5) / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

        elif state == STATE_PLAYING:
            cam = (int(camera.offset_x), int(camera.offset_y))
            screen.blit(bg_surface, (0, 0))
            current_level.draw(screen, cam, DEBUG)
            player.draw(screen, cam)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
