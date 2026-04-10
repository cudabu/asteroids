import pygame

from bomb import Bomb
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS, PLAYER_TURN_SPEED,
    PLAYER_ACCELERATION, PLAYER_DRAG, PLAYER_MAX_SPEED,
    PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_INVINCIBILITY_SECONDS, PLAYER_BOMB_COUNT,
    SPREAD_ANGLE, SPREAD_COOLDOWN,
    RAPID_COOLDOWN, RAPID_SHOT_SPEED, RAPID_SHOT_RADIUS,
    LASER_KILL_RATE, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from laser import LaserBeam
import sounds
from shot import Shot


WEAPONS = ["Single", "Spread", "Rapid", "Laser"]


class Player(CircleShape):
    # Set in main.py so the laser raycast can check asteroids
    asteroids = None
    _pending_score = 0

    @classmethod
    def pop_score(cls):
        score = cls._pending_score
        cls._pending_score = 0
        return score

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.invincibility_timer = 0
        self.bombs = PLAYER_BOMB_COUNT
        self._weapon_index = 0
        self._laser_beam = None
        self.laser_kill_timer = 0

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

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        a, b, c = self.triangle()

        # Hull fill + outline
        pygame.draw.polygon(screen, (15, 30, 65), [a, b, c])
        pygame.draw.polygon(screen, (150, 200, 255), [a, b, c], 2)

        # Cockpit — small circle just behind the nose
        cockpit = self.position + forward * (self.radius * 0.35)
        pygame.draw.circle(screen, (80, 140, 255), cockpit, 4)

        # Engine glow when thrusting forward
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            exhaust = self.position - forward * self.radius
            pygame.draw.circle(screen, (255, 140, 0), exhaust, 5)
            pygame.draw.circle(screen, (255, 220, 80), exhaust, 2)

    def respawn(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS
        self._kill_laser()

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt):
        self.velocity += pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_ACCELERATION * dt
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

    def update(self, dt):
        self.shoot_timer -= dt
        self.laser_kill_timer -= dt
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

        if keys[pygame.K_SPACE] and self.weapon == "Laser":
            self._update_laser()
        else:
            self._kill_laser()
            if keys[pygame.K_SPACE]:
                self.shoot()

        self.wrap()

    def _kill_laser(self):
        if self._laser_beam:
            self._laser_beam.kill()
            self._laser_beam = None
            sounds.stop("laser_beam")

    def _cycle_weapon(self, direction):
        self._kill_laser()
        self._weapon_index = (self._weapon_index + direction) % len(WEAPONS)
        self.shoot_timer = 0

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

    def _shoot_single(self):
        sounds.play("shoot")
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

    def _shoot_spread(self):
        sounds.play("shoot_spread")
        for angle_offset in (-SPREAD_ANGLE, 0, SPREAD_ANGLE):
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset) * PLAYER_SHOOT_SPEED

    def _shoot_rapid(self):
        sounds.play("shoot")
        shot = Shot(self.position.x, self.position.y, RAPID_SHOT_RADIUS)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * RAPID_SHOT_SPEED

    def _raycast(self):
        """Returns (hit_asteroid, end_point) for the current firing direction."""
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        tip = self.position + direction * self.radius
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
        end = tip + direction * (hit_t if hit_asteroid else max(SCREEN_WIDTH, SCREEN_HEIGHT))
        return tip, hit_asteroid, end

    def _update_laser(self):
        tip, hit_asteroid, end = self._raycast()

        if self._laser_beam is None:
            self._laser_beam = LaserBeam(tip, end)
            sounds.loop("laser_beam")
        else:
            self._laser_beam.set_points(tip, end)

        if hit_asteroid and self.laser_kill_timer <= 0:
            Player._pending_score += hit_asteroid.split()
            self.laser_kill_timer = LASER_KILL_RATE
