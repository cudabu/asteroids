import random
import sys

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_LIVES, BOMB_SCORE_INTERVAL, ASTEROID_SPAWN_RATE_SECONDS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import Explosion
from bomb import Bomb
from laser import LaserBeam
from scorepopup import ScorePopup
import sounds
from starfield import Starfield


HIGHSCORE_FILE = "highscore.txt"


def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


def update_difficulty(score):
    AsteroidField.speed_multiplier = min(2.0, 1.0 + score / 15000)
    AsteroidField.spawn_rate = max(0.45, ASTEROID_SPAWN_RATE_SECONDS - score / 15000 * 0.35)
    AsteroidField.max_asteroids = min(20, 10 + score // 3000)


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
    ScorePopup.containers = (updatable, drawable)

    Bomb.asteroids = asteroids
    Player.asteroids = asteroids
    AsteroidField.asteroids_group = asteroids

    return updatable, drawable, asteroids, shots


def new_game():
    AsteroidField.speed_multiplier = 1.0
    AsteroidField.spawn_rate = ASTEROID_SPAWN_RATE_SECONDS
    AsteroidField.max_asteroids = 10
    updatable, drawable, asteroids, shots = setup_groups()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    AsteroidField()
    return updatable, drawable, asteroids, shots, player


def draw_centered(surface, font, text, y, color="white"):
    surf = font.render(text, True, color)
    surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))


def shield_hud_text(player):
    if player.shield_active:
        return f"Shield: {player.shield_timer:.1f}s", (0, 200, 255)
    elif player.shield_cooldown > 0:
        return f"Shield: {player.shield_cooldown:.1f}s cd", (120, 120, 120)
    else:
        return "Shield: READY  [F]", (0, 255, 180)


def main():
    pygame.init()
    sounds.load()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    starfield = Starfield()

    font_large = pygame.font.SysFont(None, 96)
    font_med = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 36)

    highscore = load_highscore()

    # --- menu state (asteroids drift in background) ---
    menu_updatable, menu_drawable, _, _ = setup_groups()
    AsteroidField()

    state = "menu"
    updatable = drawable = asteroids = shots = player = None
    score = lives = next_bomb_threshold = 0
    game_over_timer = 0
    final_score = 0
    shake_timer = 0.0
    shake_intensity = 8
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
                    elif event.key == pygame.K_f:
                        player.activate_shield()

                elif state == "game_over":
                    if game_over_timer <= 0 and event.key == pygame.K_RETURN:
                        updatable.empty()
                        drawable.empty()
                        asteroids.empty()
                        shots.empty()
                        menu_updatable, menu_drawable, _, _ = setup_groups()
                        AsteroidField()
                        state = "menu"

        # --- update ---
        starfield.update(player.velocity if player and state == "playing" else pygame.Vector2(0, 0), dt)

        if state == "menu":
            menu_updatable.update(dt)

        elif state == "playing":
            log_state()
            updatable.update(dt)
            score += Player.pop_score()
            update_difficulty(score)

            for asteroid in list(asteroids):
                if not player.is_invincible and not player.shield_active and asteroid.collides_with(player):
                    log_event("player_hit")
                    lives -= 1
                    shake_timer = 0.4
                    if lives == 0:
                        final_score = score
                        if final_score > highscore:
                            highscore = final_score
                            save_highscore(highscore)
                        game_over_timer = 1.0
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

        # --- draw to canvas ---
        canvas.fill((5, 5, 15))
        starfield.draw(canvas)

        if state == "menu":
            for obj in menu_drawable:
                obj.draw(canvas)
            draw_centered(canvas, font_large, "ASTEROIDS", SCREEN_HEIGHT // 2 - 140, "white")
            draw_centered(canvas, font_med, "Press ENTER to Start", SCREEN_HEIGHT // 2 - 20, "cyan")
            draw_centered(canvas, font_med, "Press ESC to Exit", SCREEN_HEIGHT // 2 + 50, "white")
            if highscore > 0:
                draw_centered(canvas, font_small, f"High Score: {highscore}", SCREEN_HEIGHT // 2 + 120, (255, 215, 0))

        elif state == "playing":
            for obj in drawable:
                obj.draw(canvas)
            canvas.blit(font_small.render(f"Score: {score}", True, "white"), (10, 10))
            canvas.blit(font_small.render(f"High Score: {highscore}", True, (255, 215, 0)), (10, 40))
            canvas.blit(font_small.render(f"Lives: {lives}", True, "white"), (10, 70))
            canvas.blit(font_small.render(f"Bombs: {player.bombs}", True, "orange"), (10, 100))
            canvas.blit(font_small.render(f"Weapon: {player.weapon}", True, "cyan"), (10, 130))
            shield_text, shield_color = shield_hud_text(player)
            canvas.blit(font_small.render(shield_text, True, shield_color), (10, 160))

        elif state == "game_over":
            for obj in drawable:
                obj.draw(canvas)
            draw_centered(canvas, font_large, "GAME OVER", SCREEN_HEIGHT // 2 - 140, "white")
            draw_centered(canvas, font_med, f"Score: {final_score}", SCREEN_HEIGHT // 2 - 20, "white")
            if final_score >= highscore and final_score > 0:
                draw_centered(canvas, font_med, "New High Score!", SCREEN_HEIGHT // 2 + 45, (255, 215, 0))
            else:
                draw_centered(canvas, font_small, f"High Score: {highscore}", SCREEN_HEIGHT // 2 + 50, (255, 215, 0))
            if game_over_timer <= 0:
                draw_centered(canvas, font_med, "Press ENTER to return to menu", SCREEN_HEIGHT // 2 + 110, "cyan")

        # --- screen shake: blit canvas to screen with random offset ---
        if shake_timer > 0:
            shake_timer -= dt
            ox = random.randint(-shake_intensity, shake_intensity)
            oy = random.randint(-shake_intensity, shake_intensity)
        else:
            ox, oy = 0, 0

        screen.blit(canvas, (ox, oy))
        pygame.display.flip()


if __name__ == "__main__":
    main()
