import random

import pygame


EXPLOSION_LIFETIME = 0.6
EXPLOSION_PARTICLE_COUNT = 10
EXPLOSION_SPEED_SCALE = 1.5
EXPLOSION_MAX_PARTICLE_RADIUS = 3


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.lifetime = EXPLOSION_LIFETIME
        count = int(EXPLOSION_PARTICLE_COUNT * (radius / 20))
        speed = radius * EXPLOSION_SPEED_SCALE
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, 360)
            vel = pygame.Vector2(0, 1).rotate(angle) * random.uniform(speed * 0.5, speed)
            self.particles.append([pygame.Vector2(x, y), vel])

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        for particle in self.particles:
            particle[0] += particle[1] * dt

    def draw(self, screen):
        progress = self.lifetime / EXPLOSION_LIFETIME  # 1.0 → 0.0 as it expires
        radius = max(1, round(EXPLOSION_MAX_PARTICLE_RADIUS * progress))
        for particle in self.particles:
            pygame.draw.circle(screen, "white", particle[0], radius)
