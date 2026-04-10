import pygame

from bomb import Bomb
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED,
    PLAYER_ACCELERATION, PLAYER_DRAG, PLAYER_MAX_SPEED,
    PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_INVINCIBILITY_SECONDS, PLAYER_BOMB_COUNT,
    SPREAD_ANGLE, SPREAD_COOLDOWN,
    RAPID_COOLDOWN, RAPID_SHOT_SPEED, RAPID_SHOT_RADIUS,
    LASER_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from laser import LaserBeam
from shot import Shot


WEAPONS = ["Single", "Spread", "Rapid", "Laser"]


class Player(CircleShape):
    # Set in main.py so the laser raycast can check asteroids
    asteroids = None

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.invincibility_timer = 0
        self.bombs = PLAYER_BOMB_COUNT
        self._weapon_index = 0

    @property
    def weapon(self):
        return WEAPONS[self._weapon_index]

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    @property
    def is_invincible(self):
        return self.invincibility_timer > 0

    def draw(self, screen):
        if self.is_invincible and int(self.invincibility_timer * 10) % 2 == 0:
            return
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def respawn(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt):
        self.velocity += pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_ACCELERATION * dt
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

    def update(self, dt):
        self.shoot_timer -= dt
        self.invincibility_timer = max(0, self.invincibility_timer - dt)
        self.velocity *= PLAYER_DRAG ** dt
        self.position += self.velocity * dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_b]:
            self.drop_bomb()
        self.wrap()

    def _cycle_weapon(self, direction):
        self._weapon_index = (self._weapon_index + direction) % len(WEAPONS)
        self.shoot_timer = 0  # no penalty when switching

    def drop_bomb(self):
        if self.bombs <= 0:
            return
        self.bombs -= 1
        Bomb(self.position.x, self.position.y)

    def shoot(self):
        if self.shoot_timer > 0:
            return
        if self.weapon == "Single":
            self._shoot_single()
            self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        elif self.weapon == "Spread":
            self._shoot_spread()
            self.shoot_timer = SPREAD_COOLDOWN
        elif self.weapon == "Rapid":
            self._shoot_rapid()
            self.shoot_timer = RAPID_COOLDOWN
        elif self.weapon == "Laser":
            self._shoot_laser()
            self.shoot_timer = LASER_COOLDOWN

    def _shoot_single(self):
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

    def _shoot_spread(self):
        for angle_offset in (-SPREAD_ANGLE, 0, SPREAD_ANGLE):
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset) * PLAYER_SHOOT_SPEED

    def _shoot_rapid(self):
        shot = Shot(self.position.x, self.position.y, RAPID_SHOT_RADIUS)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * RAPID_SHOT_SPEED

    def _shoot_laser(self):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        tip = self.position + direction * self.radius

        # Find the closest asteroid in the firing direction via ray-circle intersection
        hit_asteroid = None
        hit_t = float("inf")
        if self.asteroids:
            for asteroid in self.asteroids:
                oc = asteroid.position - tip
                tca = oc.dot(direction)
                if tca < 0:
                    continue
                d_sq = oc.length_squared() - tca * tca
                r_sq = asteroid.radius ** 2
                if d_sq > r_sq:
                    continue
                t = tca - (r_sq - d_sq) ** 0.5
                if 0 <= t < hit_t:
                    hit_t = t
                    hit_asteroid = asteroid

        # Beam ends at the hit point or the screen edge
        if hit_asteroid:
            end = tip + direction * hit_t
            hit_asteroid.split()
        else:
            # Extend to whichever screen boundary is hit first
            end = tip + direction * max(SCREEN_WIDTH, SCREEN_HEIGHT)

        LaserBeam(tip, end)
