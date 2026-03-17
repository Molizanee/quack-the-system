import pygame

from src.constants import Colors, PlayerSettings
from src.platform import Platform
from src.player import Player


def main() -> None:
    pygame.init()
    screen_info = pygame.display.Info()

    # Simulate windowded screen
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    # screen = pygame.display.set_mode(
    #     (screen_info.current_w, screen_info.current_h),
    #     pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,
    # )
    clock = pygame.time.Clock()

    ground = Platform(0, screen_info.current_h - 50, screen_info.current_w, 50)
    player = Player(screen_info.current_w // 2, ground.rect.top - PlayerSettings.SIZE)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                ground = Platform(0, event.h - 50, event.w, 50)
                player.rect.bottom = ground.rect.top
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(dt, ground.rect)

        screen.fill(Colors.BLACK)
        ground.draw(screen)
        player.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
