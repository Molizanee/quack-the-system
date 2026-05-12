import pygame

from src.hud import HUD
from src.levels import init_levels
from src.menu import CreditsScreen, MainMenu, PauseOverlay
from src.player import Player
from src.screens import OdsIntro, OdsOutro
from src.utils.paths import resource_path

# Game states
STATE_MENU = "MENU"
STATE_CREDITS = "CREDITS"
STATE_TRANSITION = "TRANSITION"
STATE_ODS_INTRO = "ODS_INTRO"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_ODS_OUTRO = "ODS_OUTRO"

LETTER_PATH = resource_path("src/assets/letters/quack_the_sytem_main_letter.png")

# Title screen colors (tuples to avoid pygame.Color before init)
SHADOW_COLOR = (20, 20, 40)
OUTLINE_COLOR = (50, 50, 80)
SUBTITLE_COLOR = (255, 255, 255)


def load_phase_background(
    level, base_w: int, base_h: int
) -> tuple[pygame.Surface, pygame.Surface]:
    """Load a phase's background and produce both the sharp and blurred copies.

    The sharp copy is used during gameplay and the second half of the entry
    transition; the blurred copy is reused by every menu/cutscene overlay so
    text reads cleanly on top of a busy image.
    """
    sharp = pygame.image.load(resource_path(level.background_path)).convert()
    sharp = pygame.transform.scale(sharp, (base_w, base_h))
    blurred = pygame.transform.gaussian_blur(
        sharp, radius=15, repeat_edge_pixels=True
    )
    return sharp, blurred


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

    levels = init_levels(base_h)
    current_level, current_spawn = levels[0]

    # Background is sourced from the current phase. The menu shows the blurred
    # version of the first phase's background as its backdrop.
    bg_surface, bg_blurred = load_phase_background(current_level, base_w, base_h)

    title_image = pygame.image.load(LETTER_PATH).convert_alpha()
    max_width = int(base_w * 0.6)
    scale_factor = max_width / title_image.get_width()
    title_image = pygame.transform.scale(
        title_image, (max_width, int(title_image.get_height() * scale_factor))
    )

    player = Player(current_spawn[0], current_spawn[1])
    hud = HUD()
    deaths = 0

    # ── Menu screens ──────────────────────────────────────────────────
    main_menu = MainMenu(bg_blurred, title_image, base_w, base_h)
    credits_screen = CreditsScreen(bg_blurred, base_w, base_h)
    pause_overlay = PauseOverlay(base_w, base_h)

    intro_screen: OdsIntro | None = None
    outro_screen: OdsOutro | None = None

    state = STATE_MENU
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

            # ── Menu state event routing ──────────────────────────────
            if state == STATE_MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    action = main_menu.handle_event(event)
                    if action == "start":
                        state = STATE_TRANSITION
                        transition_timer = 0.0
                    elif action == "credits":
                        state = STATE_CREDITS
                    elif action == "quit":
                        running = False

            elif state == STATE_CREDITS:
                action = credits_screen.handle_event(event)
                if action == "back":
                    state = STATE_MENU

            elif state == STATE_ODS_INTRO:
                if intro_screen is None:
                    continue
                action = intro_screen.handle_event(event)
                if action in ("done", "skip"):
                    intro_screen = None
                    state = STATE_PLAYING

            elif state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Capture current frame for blur, then pause
                        pause_overlay.capture(screen)
                        state = STATE_PAUSED
                    elif event.key == pygame.K_SPACE:
                        player.jump()
                    elif event.key == pygame.K_q:
                        player.quack()

            elif state == STATE_PAUSED:
                action = pause_overlay.handle_event(event)
                if action == "resume":
                    state = STATE_PLAYING
                elif action == "restart":
                    deaths = 0
                    player.respawn(current_spawn[0], current_spawn[1])
                    current_level.reset()
                    state = STATE_PLAYING
                elif action == "quit":
                    running = False

            elif state == STATE_ODS_OUTRO:
                if outro_screen is None:
                    continue
                action = outro_screen.handle_event(event)
                if action == "continue":
                    outro_screen = None
                    deaths = 0
                    player.respawn(current_spawn[0], current_spawn[1])
                    current_level.reset()
                    state = STATE_MENU

        # --- Update ---
        if state == STATE_MENU:
            main_menu.update(dt)

        elif state == STATE_CREDITS:
            credits_screen.update(dt)

        elif state == STATE_TRANSITION:
            transition_timer += dt
            if transition_timer >= 1.0:
                intro_screen = OdsIntro(
                    screen_w=base_w,
                    screen_h=base_h,
                    ods_number=current_level.ods_number,
                    ods_name=current_level.ods_name,
                    panels=current_level.intro_panels,
                    bg_image=bg_surface,
                )
                state = STATE_ODS_INTRO

        elif state == STATE_ODS_INTRO:
            if intro_screen is not None:
                intro_screen.update(dt)

        elif state == STATE_PLAYING:
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
                outro_screen = OdsOutro(
                    screen_w=base_w,
                    screen_h=base_h,
                    ods_number=current_level.ods_number,
                    ods_name=current_level.ods_name,
                    lesson_text=current_level.outro_text,
                    bg_image=bg_surface,
                    deaths=deaths,
                )
                state = STATE_ODS_OUTRO

        elif state == STATE_PAUSED:
            pause_overlay.update(dt)

        elif state == STATE_ODS_OUTRO:
            if outro_screen is not None:
                outro_screen.update(dt)

        # --- Draw (screen is always base_w × base_h; SDL scales to window) ---
        if state == STATE_MENU:
            main_menu.draw(screen)

        elif state == STATE_CREDITS:
            credits_screen.draw(screen)

        elif state == STATE_TRANSITION:
            fade_surface = pygame.Surface((base_w, base_h))
            fade_surface.fill((0, 0, 0))

            if transition_timer < 0.5:
                # First half: fade menu to black
                main_menu.draw(screen)

                alpha = int((transition_timer / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
            else:
                # Second half: fade from black to the phase background — the
                # intro screen will appear on top of this once the timer ends.
                screen.blit(bg_surface, (0, 0))

                alpha = int((1.0 - (transition_timer - 0.5) / 0.5) * 255)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

        elif state == STATE_ODS_INTRO:
            if intro_screen is not None:
                intro_screen.draw(screen)

        elif state == STATE_PLAYING:
            screen.blit(bg_surface, (0, 0))
            current_level.draw(screen)
            player.draw(screen)
            hud.draw(screen, deaths)

        elif state == STATE_PAUSED:
            pause_overlay.draw(screen)

        elif state == STATE_ODS_OUTRO:
            if outro_screen is not None:
                outro_screen.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
