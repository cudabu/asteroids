import pygame

from constants import LASER_BEAM_LIFETIME


class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, start, end):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.start = pygame.Vector2(start)
        self.end = pygame.Vector2(end)
        self.lifetime = LASER_BEAM_LIFETIME

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        alpha = self.lifetime / LASER_BEAM_LIFETIME  # 1.0 → 0.0
        brightness = round(255 * alpha)
        pygame.draw.line(screen, (brightness, brightness, 255), self.start, self.end, 2)
