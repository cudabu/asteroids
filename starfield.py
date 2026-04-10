import random

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class StarLayer:
    def __init__(self, count, speed_factor, size_range, brightness_range):
        self.speed_factor = speed_factor
        self.size_range = size_range
        self.brightness_range = brightness_range
        self.stars = [self._random_star() for _ in range(count)]

    def _random_star(self):
        x = random.uniform(0, SCREEN_WIDTH)
        y = random.uniform(0, SCREEN_HEIGHT)
        size = random.randint(*self.size_range)
        brightness = random.randint(*self.brightness_range)
        return [pygame.Vector2(x, y), size, brightness]

    def update(self, player_velocity, dt):
        shift = player_velocity * self.speed_factor * dt
        for star in self.stars:
            star[0] -= shift
            # wrap
            star[0].x %= SCREEN_WIDTH
            star[0].y %= SCREEN_HEIGHT

    def draw(self, screen):
        for pos, size, brightness in self.stars:
            color = (brightness, brightness, brightness)
            if size == 1:
                screen.set_at((int(pos.x), int(pos.y)), color)
            else:
                pygame.draw.circle(screen, color, pos, size)


class Starfield:
    def __init__(self):
        self.layers = [
            StarLayer(120, 0.04, (1, 1), (50,  110)),   # distant — faint, barely move
            StarLayer(50,  0.12, (1, 2), (110, 180)),   # mid — medium
            StarLayer(20,  0.25, (2, 3), (180, 255)),   # close — bright, drift noticeably
        ]

    def update(self, player_velocity, dt):
        for layer in self.layers:
            layer.update(player_velocity, dt)

    def draw(self, screen):
        for layer in self.layers:
            layer.draw(screen)
