from abc import abstractmethod
import random
import math
import pygame

from src.entities.base import GameEntity
from src import config


class Target(GameEntity):

    COLOR = (255, 90, 100)
    GLOW = (255, 150, 150)

    def __init__(self, x, y, radius=config.TARGET_RADIUS):
        super().__init__(x, y)
        self._radius = radius
        self._lifetime = None
        self._age = 0.0
        self._pulse = random.uniform(0, math.tau)

    @property
    def radius(self):
        return self._radius

    @property
    def expired(self):
        if self._lifetime is None:
            return False
        return self._age >= self._lifetime

    def update(self, dt):
        self._age += dt
        self._pulse += dt * 3
        if self.expired:
            self.kill()

    def get_rect(self):
        return pygame.Rect(
            self._x - self._radius,
            self._y - self._radius,
            self._radius * 2,
            self._radius * 2,
        )

    def _draw_glowing_body(self, surface, glow_alpha, glow_radius_scale):
        cx = int(self._x)
        cy = int(self._y)
        pulse = 2 * math.sin(self._pulse)

        glow_size = self._radius * 3
        glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_center = glow_size // 2
        glow_radius = int(self._radius * glow_radius_scale + pulse)
        glow_color = (self.GLOW[0], self.GLOW[1], self.GLOW[2], glow_alpha)
        pygame.draw.circle(glow, glow_color, (glow_center, glow_center), glow_radius)
        surface.blit(glow, (cx - glow_center, cy - glow_center))

        pygame.draw.circle(surface, self.COLOR, (cx, cy), self._radius)
        pygame.draw.circle(surface, (20, 10, 15), (cx, cy), self._radius, 2)
        return cx, cy

    def draw(self, surface):
        cx, cy = self._draw_glowing_body(surface, glow_alpha=60, glow_radius_scale=1.4)
        pygame.draw.line(surface, (90, 60, 30), (cx, cy - self._radius), (cx + 3, cy - self._radius - 8), 3)

    def on_hit(self, shooter, opponent):
        self.kill()
        return 0

    def label(self):
        return "Target"


class PowerUpItem(Target):

    COLOR = config.ACCENT_GOLD
    GLOW = config.ACCENT_GOLD

    def __init__(self, x, y):
        super().__init__(x, y, radius=config.TARGET_RADIUS - 4)
        self._lifetime = config.POWERUP_LIFETIME

    def draw(self, surface):
        cx, cy = self._draw_glowing_body(surface, glow_alpha=70, glow_radius_scale=1.5)
        self._draw_icon(surface)

        if self._lifetime:
            remaining_ratio = 1 - self._age / self._lifetime
            if remaining_ratio < 0.0:
                remaining_ratio = 0.0
            end_angle = -math.pi / 2 + remaining_ratio * math.tau
            ring_rect = pygame.Rect(
                cx - self._radius - 5, cy - self._radius - 5,
                (self._radius + 5) * 2, (self._radius + 5) * 2,
            )
            pygame.draw.arc(surface, (255, 255, 255), ring_rect, -math.pi / 2, end_angle, 2)

    @abstractmethod
    def _draw_icon(self, surface):
        raise NotImplementedError

    @abstractmethod
    def on_hit(self, shooter, opponent):
        raise NotImplementedError


class ExtraAmmoItem(PowerUpItem):
    """Gives the shooter extra bullets."""

    COLOR = config.ACCENT_GREEN
    GLOW = config.ACCENT_GREEN

    def _draw_icon(self, surface):
        cx = int(self._x)
        cy = int(self._y)
        for i in range(3):
            pygame.draw.rect(surface, (20, 40, 25), (cx - 7 + i * 5, cy - 7, 3, 14))

    def on_hit(self, shooter, opponent):
        self.kill()
        shooter.add_bullets(config.EXTRA_AMMO_AMOUNT)
        return 0

    def label(self):
        return "+Ammo"


class ExtraTimeItem(PowerUpItem):
    """Gives the shooter extra time."""

    COLOR = config.ACCENT_PURPLE
    GLOW = config.ACCENT_PURPLE

    def _draw_icon(self, surface):
        cx = int(self._x)
        cy = int(self._y)
        pygame.draw.circle(surface, (30, 20, 45), (cx, cy), 8, 2)
        pygame.draw.line(surface, (30, 20, 45), (cx, cy), (cx, cy - 5), 2)
        pygame.draw.line(surface, (30, 20, 45), (cx, cy), (cx + 4, cy), 2)

    def on_hit(self, shooter, opponent):
        self.kill()
        shooter.add_time(config.EXTRA_TIME_AMOUNT)
        return 0

    def label(self):
        return "+Time"


class SabotageItem(PowerUpItem):

    COLOR = (90, 90, 100)
    GLOW = (200, 60, 60)
    EFFECT_CHOICES = ("time", "ammo", "aim")

    def __init__(self, x, y):
        super().__init__(x, y)
        self._effect = random.choice(self.EFFECT_CHOICES)

    def _draw_icon(self, surface):
        cx = int(self._x)
        cy = int(self._y)
        pygame.draw.line(surface, (255, 255, 255), (cx - 6, cy - 6), (cx + 6, cy + 6), 3)
        pygame.draw.line(surface, (255, 255, 255), (cx - 6, cy + 6), (cx + 6, cy - 6), 3)

    def on_hit(self, shooter, opponent):
        self.kill()
        if self._effect == "time":
            opponent.add_time(-config.SABOTAGE_TIME_PENALTY)
        elif self._effect == "ammo":
            opponent.add_bullets(-config.SABOTAGE_AMMO_PENALTY)
        else:
            opponent.scramble_aim()
        return 0

    def label(self):
        return "Sabotage (" + self._effect + ")"
