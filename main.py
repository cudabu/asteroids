import sys

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_LIVES, BOMB_SCORE_INTERVAL
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import Explosion
from bomb import Bomb
from laser import LaserBeam


def setup_groups():
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    Explosion.containers = (updatable, drawable)
    Bomb.containers = (updatable, drawable)
    LaserBeam.containers = (updatable, drawable)

    Bomb.asteroids = asteroids
    Player.asteroids = asteroids

    return updatable, drawable, asteroids, shots


def new_game():
    updatable, drawable, asteroids, shots = setup_groups()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    AsteroidField()
    return updatable, drawable, asteroids, shots, player


def draw_centered(screen, font, text, y, color="white"):
    surf = font.render(text, True, color)
    screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))


def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    background = pygame.transform.scale(
        pygame.image.load("background.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    font_large = pygame.font.SysFont(None, 96)
    font_med = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 36)

    # --- menu state (asteroids drift in background) ---
    menu_updatable, menu_drawable, _, _ = setup_groups()
    AsteroidField()

    state = "menu"
    updatable = drawable = asteroids = shots = player = None
    score = lives = next_bomb_threshold = 0
    game_over_timer = 0
    final_score = 0
    dt = 0

    while True:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_RETURN:
                        updatable, drawable, asteroids, shots, player = new_game()
                        score = 0
                        lives = PLAYER_LIVES
                        next_bomb_threshold = BOMB_SCORE_INTERVAL
                        state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()

                elif state == "playing":
                    if event.key == pygame.K_q:
                        player._cycle_weapon(-1)
                    elif event.key == pygame.K_e:
                        player._cycle_weapon(1)
                    elif event.key == pygame.K_b:
                        player.drop_bomb()

                elif state == "game_over":
                    if game_over_timer <= 0 and event.key == pygame.K_RETURN:
                        # Kill all game sprites and return to menu
                        updatable.empty()
                        drawable.empty()
                        asteroids.empty()
                        shots.empty()
                        # Rebuild menu background field
                        menu_updatable, menu_drawable, _, _ = setup_groups()
                        AsteroidField()
                        state = "menu"

        # --- update ---
        if state == "menu":
            menu_updatable.update(dt)
        elif state == "playing":
            log_state()
            updatable.update(dt)
            score += Player.pop_score()

            for asteroid in list(asteroids):
                if not player.is_invincible and asteroid.collides_with(player):
                    log_event("player_hit")
                    lives -= 1
                    if lives == 0:
                        final_score = score
                        game_over_timer = 1.0
                        player._kill_laser()
                        player.kill()
                        state = "game_over"
                        break
                    player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                for shot in list(shots):
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        score += asteroid.split()
                        shot.kill()

            if state == "playing":
                if score >= next_bomb_threshold:
                    player.bombs += 1
                    next_bomb_threshold += BOMB_SCORE_INTERVAL

        elif state == "game_over":
            game_over_timer -= dt
            updatable.update(dt)

        # --- draw ---
        screen.blit(background, (0, 0))

        if state == "menu":
            for obj in menu_drawable:
                obj.draw(screen)
            draw_centered(screen, font_large, "ASTEROIDS", SCREEN_HEIGHT // 2 - 120, "white")
            draw_centered(screen, font_med, "Press ENTER to Start", SCREEN_HEIGHT // 2, "cyan")
            draw_centered(screen, font_med, "Press ESC to Exit", SCREEN_HEIGHT // 2 + 60, "white")

        elif state == "playing":
            for obj in drawable:
                obj.draw(screen)
            screen.blit(font_small.render(f"Score: {score}", True, "white"), (10, 10))
            screen.blit(font_small.render(f"Lives: {lives}", True, "white"), (10, 40))
            screen.blit(font_small.render(f"Bombs: {player.bombs}", True, "orange"), (10, 70))
            screen.blit(font_small.render(f"Weapon: {player.weapon}", True, "cyan"), (10, 100))

        elif state == "game_over":
            for obj in drawable:
                obj.draw(screen)
            draw_centered(screen, font_large, "GAME OVER", SCREEN_HEIGHT // 2 - 120, "white")
            draw_centered(screen, font_med, f"Score: {final_score}", SCREEN_HEIGHT // 2, "white")
            if game_over_timer <= 0:
                draw_centered(screen, font_med, "Press ENTER to return to menu", SCREEN_HEIGHT // 2 + 70, "cyan")

        pygame.display.flip()


if __name__ == "__main__":
    main()
