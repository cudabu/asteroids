import math

import pygame

from circleshape import CircleShape
from constants import BOMB_RADIUS, BOMB_FUSE_SECONDS, BOMB_BLAST_RADIUS, ASTEROID_MIN_RADIUS
from explosion import Explosion
from logger import log_event


class Bomb(CircleShape):
    # Set in main.py before any Bomb is created
    asteroids = None
    # Accumulates points from detonations; drained by main loop each frame
    _pending_score = 0

    @classmethod
    def pop_score(cls):
        score = cls._pending_score
        cls._pending_score = 0
        return score

    def __init__(self, x, y):
        super().__init__(x, y, BOMB_RADIUS)
        self.timer = BOMB_FUSE_SECONDS

    def draw(self, screen):
        # Pulse between half and full size using the fuse countdown
        pulse = 1 + 0.4 * math.sin(self.timer * 10)
        draw_radius = max(1, round(self.radius * pulse))
        # Shift from white → orange as fuse burns down
        frac = self.timer / BOMB_FUSE_SECONDS  # 1.0 → 0.0
        color = (255, round(165 * frac), 0)
        pygame.draw.circle(screen, color, self.position, draw_radius)
        pygame.draw.circle(screen, "white", self.position, draw_radius + 2, 1)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self._detonate()

    def _detonate(self):
        Explosion(self.position.x, self.position.y, BOMB_BLAST_RADIUS * 0.8)
        if self.asteroids:
            for asteroid in list(self.asteroids):
                if self.position.distance_to(asteroid.position) < BOMB_BLAST_RADIUS + asteroid.radius:
                    log_event("asteroid_shot")
                    kind = round(asteroid.radius / ASTEROID_MIN_RADIUS)
                    Bomb._pending_score += {1: 100, 2: 50, 3: 20}.get(kind, 100)
                    asteroid.kill()
        self.kill()
