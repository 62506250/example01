import random
import pygame

from src.entities.base import GameEntity
from src import config


class Crosshair(GameEntity):

    def __init__(self, x, y, color):
        super().__init__(x, y)
        self._color = color
        self._visible = False

    @property
    def visible(self):
        return self._visible

    def reveal(self):
        self._visible = True

    def move(self, dx, dy, dt):
        speed = config.CROSSHAIR_SPEED * dt
        new_x = self._x + dx * speed
        new_y = self._y + dy * speed

        margin = config.CROSSHAIR_SIZE
        min_x = margin
        max_x = config.SCREEN_WIDTH - margin
        min_y = config.PLAY_AREA_TOP + margin
        max_y = config.SCREEN_HEIGHT - margin

        if new_x < min_x:
            new_x = min_x
        if new_x > max_x:
            new_x = max_x
        if new_y < min_y:
            new_y = min_y
        if new_y > max_y:
            new_y = max_y

        self._x = new_x
        self._y = new_y

    def teleport_random(self):
        margin = config.CROSSHAIR_SIZE * 2
        self._x = random.uniform(margin, config.SCREEN_WIDTH - margin)
        self._y = random.uniform(config.PLAY_AREA_TOP + margin, config.SCREEN_HEIGHT - margin)

    def update(self, dt):
        pass

    def get_rect(self):
        size = config.CROSSHAIR_SIZE
        return pygame.Rect(self._x - size, self._y - size, size * 2, size * 2)

    def draw(self, surface):
        if not self._visible:
            return

        size = config.CROSSHAIR_SIZE
        cx = int(self._x)
        cy = int(self._y)

        pygame.draw.circle(surface, self._color, (cx, cy), size, 2)
        pygame.draw.line(surface, self._color, (cx - size - 6, cy), (cx - 4, cy), 2)
        pygame.draw.line(surface, self._color, (cx + 4, cy), (cx + size + 6, cy), 2)
        pygame.draw.line(surface, self._color, (cx, cy - size - 6), (cx, cy - 4), 2)
        pygame.draw.line(surface, self._color, (cx, cy + 4), (cx, cy + size + 6), 2)
        pygame.draw.circle(surface, self._color, (cx, cy), 2)


class Player:
    def __init__(self, name, player_number, controls):
        self._name = name
        self._player_number = player_number
        self._controls = controls
        self._color = config.PLAYER_COLORS[player_number]

        self._bullets = config.STARTING_BULLETS
        self._time_left = config.STARTING_TIME_SECONDS
        self._score = 0
        self._streak = 0

        self._last_shot_pos = None

        start_x = random.uniform(120, config.SCREEN_WIDTH - 120)
        start_y = random.uniform(config.PLAY_AREA_TOP + 60, config.SCREEN_HEIGHT - 60)
        self._crosshair = Crosshair(start_x, start_y, self._color)

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def bullets(self):
        return self._bullets

    @property
    def time_left(self):
        if self._time_left < 0.0:
            return 0.0
        return self._time_left

    @property
    def score(self):
        return self._score

    @property
    def crosshair(self):
        return self._crosshair

    @property
    def streak(self):
        return self._streak

    @property
    def controls(self):
        return self._controls

    @property
    def can_shoot(self):
        return self._bullets > 0 and self._time_left > 0

    def add_bullets(self, amount):
        new_amount = self._bullets + amount
        if new_amount < 0:
            new_amount = 0
        self._bullets = new_amount

    def add_time(self, seconds):
        new_time = self._time_left + seconds
        if new_time < 0.0:
            new_time = 0.0
        self._time_left = new_time

    def add_score(self, amount):
        self._score = self._score + amount

    def scramble_aim(self):
        self._crosshair.teleport_random()

    def tick_time(self, dt):
        if self._time_left > 0:
            self._time_left = self._time_left - dt
            if self._time_left < 0:
                self._time_left = 0.0

    def handle_movement(self, keys, dt):
        dx = 0.0
        dy = 0.0
        if keys[self._controls["left"]]:
            dx -= 1
        if keys[self._controls["right"]]:
            dx += 1
        if keys[self._controls["up"]]:
            dy -= 1
        if keys[self._controls["down"]]:
            dy += 1
        if dx != 0 or dy != 0:
            self._crosshair.move(dx, dy, dt)

    def is_shoot_key(self, key):
        return key == self._controls["shoot"]

    def register_shot(self, hit, shot_pos):
        self._bullets = self._bullets - 1
        if self._bullets < 0:
            self._bullets = 0
        self._crosshair.reveal()

        distance = 0.0
        if self._last_shot_pos is not None:
            old_x, old_y = self._last_shot_pos
            new_x, new_y = shot_pos
            distance = ((new_x - old_x) ** 2 + (new_y - old_y) ** 2) ** 0.5
        self._last_shot_pos = shot_pos

        if hit:
            self._streak = self._streak + 1
        else:
            self._streak = 0

        return distance
