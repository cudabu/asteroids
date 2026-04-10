import pygame

from constants import POPUP_LIFETIME, POPUP_RISE_SPEED


class ScorePopup(pygame.sprite.Sprite):
    _font = None

    def __init__(self, x, y, points):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        if ScorePopup._font is None:
            ScorePopup._font = pygame.font.SysFont(None, 28)
        self.text = f"+{points}"
        self.lifetime = POPUP_LIFETIME
        self.position = pygame.Vector2(x, y)

    def update(self, dt):
        self.position.y -= POPUP_RISE_SPEED * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        alpha = self.lifetime / POPUP_LIFETIME
        color = (255, round(220 * alpha + 35), round(50 * alpha))
        surf = self._font.render(self.text, True, color)
        screen.blit(surf, self.position)
