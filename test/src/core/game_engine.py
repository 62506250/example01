import pygame

from src import config, theme
from src.entities.player import Player
from src.entities.targets import Target, SabotageItem, PowerUpItem
from src.core.spawner import Spawner
from src.core.scoring import ScoreCalculator
from src.core.audio import SoundManager
from src.ui.hud import Hud


class GameEngine:
    """Runs one full match between two players."""

    def __init__(self, player1_name, player2_name):
        self.player1 = Player(player1_name, 1, config.PLAYER1_CONTROLS)
        self.player2 = Player(player2_name, 2, config.PLAYER2_CONTROLS)

        self._spawner = Spawner()
        self._targets = []
        self._spawner.top_up_targets(self._targets)

        self._hud = Hud()
        self._sound = SoundManager()
        self._starfield = theme.StarField(count=50)
        self._game_over = False

    @property
    def game_over(self):
        return self._game_over

    def update(self, dt, keys):
        self._starfield.update(dt)
        if self._game_over:
            return

        self.player1.handle_movement(keys, dt)
        self.player2.handle_movement(keys, dt)

        if self.player1.can_shoot:
            self.player1.tick_time(dt)
        if self.player2.can_shoot:
            self.player2.tick_time(dt)

        for target in self._targets:
            target.update(dt)
        self._remove_dead_targets()

        new_powerup = self._spawner.maybe_spawn_powerup(dt, self._targets)
        if new_powerup is not None:
            self._targets.append(new_powerup)
        self._spawner.top_up_targets(self._targets)

        both_players_done = not self.player1.can_shoot and not self.player2.can_shoot
        if both_players_done and not self._game_over:
            self._game_over = True
            self._sound.play_game_over()

    def _remove_dead_targets(self):
        still_alive = []
        for target in self._targets:
            if target.alive:
                still_alive.append(target)
        self._targets = still_alive

    def handle_event(self, event):
        if self._game_over:
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.player1.is_shoot_key(event.key):
            self._fire(self.player1, self.player2)
        elif self.player2.is_shoot_key(event.key):
            self._fire(self.player2, self.player1)

    def _fire(self, shooter, opponent):
        if not shooter.can_shoot:
            return

        shot_pos = shooter.crosshair.position
        hit_target = self._find_target_at(shot_pos)
        hit = hit_target is not None

        distance = shooter.register_shot(hit=hit, shot_pos=shot_pos)
        self._sound.play_shoot()

        if hit_target is not None:
            bonus = hit_target.on_hit(shooter, opponent)
            points = ScoreCalculator.total_for_hit(distance, shooter.streak) + bonus
            shooter.add_score(points)

            if isinstance(hit_target, SabotageItem):
                self._sound.play_sabotage()
            elif isinstance(hit_target, PowerUpItem):
                self._sound.play_powerup()
            else:
                self._sound.play_hit()

            self._remove_dead_targets()
            self._spawner.top_up_targets(self._targets)

    def _find_target_at(self, point):
        for target in self._targets:
            if target.alive and target.collides_with_point(point):
                return target
        return None

    def draw(self, surface):
        theme.draw_background(surface, self._starfield)

        for target in self._targets:
            target.draw(surface)

        self.player1.crosshair.draw(surface)
        self.player2.crosshair.draw(surface)

        self._hud.draw(surface, self.player1, self.player2)
