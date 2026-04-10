import pygame


class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, start, end):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.start = pygame.Vector2(start)
        self.end = pygame.Vector2(end)

    def set_points(self, start, end):
        self.start.update(start)
        self.end.update(end)

    def update(self, dt):
        pass  # lifetime managed by Player

    def draw(self, screen):
        # Outer glow
        pygame.draw.line(screen, (0, 80, 255), self.start, self.end, 4)
        # Bright core
        pygame.draw.line(screen, (180, 220, 255), self.start, self.end, 1)
