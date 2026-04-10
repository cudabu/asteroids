import random

import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from explosion import Explosion
from logger import log_event


class Asteroid(CircleShape):
    VERTEX_COUNT = 12
    RADIUS_VARIANCE = 0.35  # vertices vary ±35% from nominal radius
    ANGLE_VARIANCE = 0.4    # vertices nudged ±40% of their slice angle

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self._vertices = self._generate_vertices()

    def _generate_vertices(self):
        slice_angle = 360 / self.VERTEX_COUNT
        vertices = []
        for i in range(self.VERTEX_COUNT):
            angle = i * slice_angle + random.uniform(
                -slice_angle * self.ANGLE_VARIANCE,
                slice_angle * self.ANGLE_VARIANCE,
            )
            r = self.radius * random.uniform(
                1 - self.RADIUS_VARIANCE, 1 + self.RADIUS_VARIANCE
            )
            vertices.append(pygame.Vector2(0, r).rotate(angle))
        return vertices

    def draw(self, screen):
        points = [self.position + v for v in self._vertices]
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap()

    def split(self):
        Explosion(self.position.x, self.position.y, self.radius)
        self.kill()
        # Small asteroids worth the most — reward finishing them off
        kind = round(self.radius / ASTEROID_MIN_RADIUS)
        points = {1: 100, 2: 50, 3: 20}.get(kind, 100)
        if self.radius <= ASTEROID_MIN_RADIUS:
            return points
        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = self.velocity.rotate(angle) * 1.2
        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a2.velocity = self.velocity.rotate(-angle) * 1.2
        return points
