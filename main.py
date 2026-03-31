import math

import pygame

from src.constants import PlayerSettings
from src.levels import init_levels
from src.player import Player

# Game states
STATE_TITLE = "TITLE"
STATE_TRANSITION = "TRANSITION"
STATE_PLAYING = "PLAYING"

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
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    clock = pygame.time.Clock()

    # Load and prepare background
    bg_surface = pygame.image.load(
        "src/assets/backgrounds/inital_screen_background.png"
    ).convert()
    bg_surface = pygame.transform.scale(bg_surface, (width, height))
    bg_blurred = pygame.transform.gaussian_blur(
        bg_surface, radius=15, repeat_edge_pixels=True
    )

    title_image = pygame.image.load(LETTER_PATH).convert_alpha()
    max_width = int(width * 0.6)
    scale_factor = max_width / title_image.get_width()
    title_image = pygame.transform.scale(
        title_image, (max_width, int(title_image.get_height() * scale_factor))
    )
    subtitle_font = pygame.font.Font(FONT_PATH, 36)

    levels = init_levels(width, height)
    current_level, current_spawn = levels[0]

    player = Player(current_spawn[0], current_spawn[1])

    state = STATE_TITLE
    running = True
    title_time = 0.0  # Timer for subtitle pulse animation
    transition_timer = 0.0

    while running:
        dt = clock.tick(60) / 1000.0
        title_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                bg_surface = pygame.image.load(
                    "src/assets/backgrounds/inital_screen_background.png"
                ).convert()
                bg_surface = pygame.transform.scale(bg_surface, (width, height))
                bg_blurred = pygame.transform.gaussian_blur(
                    bg_surface, radius=15, repeat_edge_pixels=True
                )
                # title_font = pygame.font.Font(FONT_PATH, 96)
                subtitle_font = pygame.font.Font(FONT_PATH, 36)

                levels = init_levels(width, height)
                current_level, current_spawn = levels[0]

                player.rect.x = current_spawn[0]
                player.rect.y = current_spawn[1]

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

        # --- Update ---
        if state == STATE_TRANSITION:
            transition_timer += dt
            if transition_timer >= 1.0:
                state = STATE_PLAYING

        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(dt, current_level.get_platform_rects())

        # --- Draw ---
        if state == STATE_TITLE:
            screen.blit(bg_blurred, (0, 0))

            # Draw title image directly (pre-rendered "Quack The System")
            title_center = (width // 2, height // 2 - 30)
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
                center=(width // 2, title_rect.bottom + 60)
            )
            screen.blit(subtitle_surface, subtitle_rect)

        elif state == STATE_TRANSITION:
            fade_surface = pygame.Surface((width, height))
            fade_surface.fill((0, 0, 0))

            if transition_timer < 0.5:
                # First half: fade title screen to black
                screen.blit(bg_blurred, (0, 0))

                title_center = (width // 2, height // 2 - 30)
                title_rect = title_image.get_rect(center=title_center)
                screen.blit(title_image, title_rect)

                subtitle_surface = subtitle_font.render(
                    "Pressione espaço para começar", True, SUBTITLE_COLOR
                )
                subtitle_rect = subtitle_surface.get_rect(
                    center=(width // 2, title_rect.bottom + 60)
                )
                screen.blit(subtitle_surface, subtitle_rect)

                alpha = int((transition_timer / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
            else:
                # Second half: fade from black to playing screen
                screen.blit(bg_surface, (0, 0))
                current_level.draw(screen)
                player.draw(screen)

                alpha = int((1.0 - (transition_timer - 0.5) / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

        elif state == STATE_PLAYING:
            screen.blit(bg_surface, (0, 0))
            current_level.draw(screen)
            player.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
