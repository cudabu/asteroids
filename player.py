import pygame

from circleshape import CircleShape
from bomb import Bomb
from constants import PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_ACCELERATION, PLAYER_DRAG, PLAYER_MAX_SPEED, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS, PLAYER_INVINCIBILITY_SECONDS, PLAYER_BOMB_COUNT
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.invincibility_timer = 0
        self.bombs = PLAYER_BOMB_COUNT

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
        # Flash by skipping draw on alternating 0.1s intervals while invincible
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

    def drop_bomb(self):
        if self.bombs <= 0:
            return
        self.bombs -= 1
        Bomb(self.position.x, self.position.y)

    def shoot(self):
        if self.shoot_timer > 0:
            return
        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
