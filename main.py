import math

import pygame

from src.hud import HUD
from src.levels import init_levels
from src.player import Player
from src.utils.paths import resource_path

# Game states
STATE_TITLE = "TITLE"
STATE_TRANSITION = "TRANSITION"
STATE_PLAYING = "PLAYING"
STATE_PHASE_COMPLETE = "PHASE_COMPLETE"

# Custom font path
FONT_PATH = resource_path("src/assets/fonts/PixelPurl.ttf")
LETTER_PATH = resource_path("src/assets/letters/quack_the_sytem_main_letter.png")

# Title screen colors (tuples to avoid pygame.Color before init)
SHADOW_COLOR = (20, 20, 40)
OUTLINE_COLOR = (50, 50, 80)
SUBTITLE_COLOR = (255, 255, 255)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Quack The System")
    icon = pygame.image.load(resource_path("src/assets/quack_the_system.png"))
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
        resource_path("src/assets/backgrounds/inital_screen_background.png")
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
    hud = HUD()
    deaths = 0

    state = STATE_TITLE
    running = True
    title_time = 0.0  # Timer for subtitle pulse animation
    transition_timer = 0.0
    complete_timer = 0.0
    complete_font = pygame.font.Font(FONT_PATH, 64)
    complete_sub_font = pygame.font.Font(FONT_PATH, 30)

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
                elif state == STATE_PHASE_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        deaths = 0
                        player.respawn(current_spawn[0], current_spawn[1])
                        current_level.reset()
                        state = STATE_PLAYING

            # --- Update ---
        if state == STATE_TRANSITION:
            transition_timer += dt
            if transition_timer >= 1.0:
                state = STATE_PLAYING

        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            player.update(dt, keys, current_level.platforms)
            current_level.update(dt, player.rect, base_h)

            died = (
                player.rect.top > base_h
                or current_level.player_lethal_hit(player.rect)
            )
            if died:
                deaths += 1
                player.respawn(current_spawn[0], current_spawn[1])
                current_level.reset()
            elif current_level.is_complete(player.rect):
                state = STATE_PHASE_COMPLETE
                complete_timer = 0.0

        if state == STATE_PHASE_COMPLETE:
            complete_timer += dt

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
            hud.draw(screen, deaths)

        elif state == STATE_PHASE_COMPLETE:
            screen.blit(bg_surface, (0, 0))
            current_level.draw(screen)
            player.draw(screen)
            hud.draw(screen, deaths)

            fade_alpha = min(180, int(complete_timer * 360))
            overlay = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, fade_alpha))
            screen.blit(overlay, (0, 0))

            if complete_timer > 0.4:
                title_surface = complete_font.render(
                    "Fase 1 completa!", True, SUBTITLE_COLOR
                )
                title_rect = title_surface.get_rect(
                    center=(base_w // 2, base_h // 2 - 30)
                )
                screen.blit(title_surface, title_rect)

                sub_pulse = (math.sin(complete_timer * 3.0) + 1.0) / 2.0
                sub_alpha = int(120 + 135 * sub_pulse)
                sub_surface = complete_sub_font.render(
                    "Fase 2 em breve — pressione espaço para tentar de novo",
                    True,
                    SUBTITLE_COLOR,
                )
                sub_surface.set_alpha(sub_alpha)
                sub_rect = sub_surface.get_rect(
                    center=(base_w // 2, title_rect.bottom + 50)
                )
                screen.blit(sub_surface, sub_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
    