import math

import pygame

from circleshape import CircleShape
from constants import BOMB_RADIUS, BOMB_FUSE_SECONDS, BOMB_BLAST_RADIUS
from explosion import Explosion
from logger import log_event
import sounds


class Bomb(CircleShape):
    # Set in main.py before any Bomb is created
    asteroids = None

    def __init__(self, x, y):
        super().__init__(x, y, BOMB_RADIUS)
        self.timer = BOMB_FUSE_SECONDS

    def draw(self, screen):
        pulse = 1 + 0.4 * math.sin(self.timer * 10)
        draw_radius = max(1, round(self.radius * pulse))
        frac = self.timer / BOMB_FUSE_SECONDS
        color = (255, round(165 * frac), 0)
        pygame.draw.circle(screen, color, self.position, draw_radius)
        pygame.draw.circle(screen, "white", self.position, draw_radius + 2, 1)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self._detonate()

    def _detonate(self):
        sounds.play("bomb")
        Explosion(self.position.x, self.position.y, BOMB_BLAST_RADIUS * 0.8)
        if self.asteroids:
            for asteroid in list(self.asteroids):
                log_event("asteroid_shot")
                asteroid.kill()
        self.kill()
