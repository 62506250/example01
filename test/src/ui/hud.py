import pygame

from src import config, theme
from src.entities.player import Player

class Hud:
    def __init__(self):
        self._name_font = pygame.font.Font(config.FONT_NAME, 24)
        self._stat_font = pygame.font.Font(config.FONT_NAME, 18)

    def draw(self, surface, player1, player2):
        self._draw_player_panel(surface, player1, anchor_left=True)
        self._draw_player_panel(surface, player2, anchor_left=False)

        pygame.draw.line(
            surface, config.PANEL_BORDER,
            (0, config.PLAY_AREA_TOP - 6),
            (config.SCREEN_WIDTH, config.PLAY_AREA_TOP - 6), 1,
        )

    def _draw_player_panel(self, surface, player, anchor_left):
        pad = 16
        width = 300
        height = 98
        if anchor_left:
            x = pad
        else:
            x = config.SCREEN_WIDTH - width - pad
        y = pad

        rect = pygame.Rect(x, y, width, height)
        theme.draw_panel(surface, rect, border_color=player.color, alpha=200)

        name_render = self._name_font.render(player.name, True, player.color)
        surface.blit(name_render, (x + 14, y + 8))

        bar_width = width - 28
        self._draw_stat_bar(
            surface, x + 14, y + 38, bar_width, "Bullets", player.bullets,
            config.STARTING_BULLETS, config.ACCENT_GREEN,
        )
        self._draw_stat_bar(
            surface, x + 14, y + 63, bar_width, "Time", round(player.time_left, 1),
            config.STARTING_TIME_SECONDS, config.ACCENT_PURPLE, suffix="s",
        )

        score_text = self._stat_font.render("Score: " + str(player.score), True, config.ACCENT_GOLD)
        score_x = x + width - score_text.get_width() - 14
        surface.blit(score_text, (score_x, y + 8))

        if not player.can_shoot:
            warning_text = self._stat_font.render("OUT!", True, config.ACCENT_RED)
            surface.blit(warning_text, (score_x, y + 30))

    def _draw_stat_bar(self, surface, x, y, width, label, value, max_value, color, suffix=""):
        if max_value:
            ratio = value / max_value
        else:
            ratio = 0
        if ratio < 0.0:
            ratio = 0.0
        if ratio > 1.0:
            ratio = 1.0

        label_text = self._stat_font.render(label + ": " + str(value) + suffix, True, config.TEXT_WHITE)
        surface.blit(label_text, (x, y - 16))

        pygame.draw.rect(surface, (40, 38, 55), (x, y, width, 8), border_radius=4)
        filled_width = int(width * ratio)
        pygame.draw.rect(surface, color, (x, y, filled_width, 8), border_radius=4)
