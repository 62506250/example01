import random

from src import config
from src.entities.targets import (
    Target,
    ExtraAmmoItem,
    ExtraTimeItem,
    SabotageItem,
)

POWERUP_CLASSES = [ExtraAmmoItem, ExtraTimeItem, SabotageItem]


class Spawner:

    def __init__(self):
        self._powerup_timer = self._roll_powerup_interval()

    @staticmethod
    def _roll_powerup_interval():
        return random.uniform(
            config.POWERUP_SPAWN_MIN_INTERVAL, config.POWERUP_SPAWN_MAX_INTERVAL
        )

    @staticmethod
    def _random_position(margin=60):
        x = random.uniform(margin, config.SCREEN_WIDTH - margin)
        y = random.uniform(config.PLAY_AREA_TOP + margin, config.SCREEN_HEIGHT - margin)
        return x, y

    def spawn_target(self):
        x, y = self._random_position()
        return Target(x, y)

    def maybe_spawn_powerup(self, dt, existing_powerups):
        self._powerup_timer -= dt
        if self._powerup_timer <= 0:
            self._powerup_timer = self._roll_powerup_interval()
            x, y = self._random_position()
            powerup_class = random.choice(POWERUP_CLASSES)
            return powerup_class(x, y)
        return None

    def top_up_targets(self, targets):
        while len(targets) < config.MAX_TARGETS_ON_SCREEN:
            new_target = self.spawn_target()
            targets.append(new_target)
