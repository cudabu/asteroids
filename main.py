import sys

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_LIVES
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import Explosion
from bomb import Bomb
from laser import LaserBeam


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    clock = pygame.time.Clock()
    dt = 0
    score = 0
    lives = PLAYER_LIVES
    font = pygame.font.SysFont(None, 36)

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = pygame.transform.scale(
        pygame.image.load("background.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    AsteroidField()

    Shot.containers = (shots, updatable, drawable)
    Explosion.containers = (updatable, drawable)
    Bomb.containers = (updatable, drawable)
    Bomb.asteroids = asteroids
    LaserBeam.containers = (updatable, drawable)
    Player.asteroids = asteroids

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    player._cycle_weapon(-1)
                elif event.key == pygame.K_e:
                    player._cycle_weapon(1)

        dt = clock.tick(60) / 1000

        updatable.update(dt)
        score += Bomb.pop_score()

        for asteroid in asteroids:
            if not player.is_invincible and asteroid.collides_with(player):
                log_event("player_hit")
                lives -= 1
                if lives == 0:
                    print(f"Game over! Final score: {score}")
                    sys.exit()
                player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    score += asteroid.split()
                    shot.kill()

        screen.blit(background, (0, 0))

        for obj in drawable:
            obj.draw(screen)

        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surf, (10, 10))
        lives_surf = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_surf, (10, 40))
        bombs_surf = font.render(f"Bombs: {player.bombs}", True, "orange")
        screen.blit(bombs_surf, (10, 70))
        weapon_surf = font.render(f"Weapon: {player.weapon}", True, "cyan")
        screen.blit(weapon_surf, (10, 100))

        pygame.display.flip()


if __name__ == "__main__":
    main()
