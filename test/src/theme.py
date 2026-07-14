import random
import math
import pygame

from src import config


def draw_vertical_gradient(surface, top_color, bottom_color):
    height = surface.get_height()
    width = surface.get_width()

    for y in range(height):
        t = y / max(1, height - 1)
        red = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        green = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        blue = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (red, green, blue), (0, y), (width, y))


def draw_glow_text(surface, font, text, center, color=config.TEXT_WHITE, glow_color=config.ACCENT_CYAN):
    glow_offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)]
    for dx, dy in glow_offsets:
        glow_surface = font.render(text, True, glow_color)
        glow_surface.set_alpha(60)
        glow_rect = glow_surface.get_rect(center=(center[0] + dx, center[1] + dy))
        surface.blit(glow_surface, glow_rect)

    main_surface = font.render(text, True, color)
    surface.blit(main_surface, main_surface.get_rect(center=center))


def draw_panel(surface, rect, border_color=config.PANEL_BORDER, alpha=210, radius=16):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    fill_color = (config.PANEL_BG[0], config.PANEL_BG[1], config.PANEL_BG[2], alpha)
    pygame.draw.rect(panel, fill_color, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_color, panel.get_rect(), 2, border_radius=radius)
    surface.blit(panel, rect.topleft)


class StarField:

    def __init__(self, count=70):
        self._stars = []
        for _ in range(count):
            star = {
                "x": random.uniform(0, config.SCREEN_WIDTH),
                "y": random.uniform(0, config.SCREEN_HEIGHT),
                "speed": random.uniform(6, 24),
                "size": random.uniform(1, 2.6),
                "twinkle": random.uniform(0, math.tau),
            }
            self._stars.append(star)

    def update(self, dt):
        for star in self._stars:
            star["y"] += star["speed"] * dt
            star["twinkle"] += dt * 2
            if star["y"] > config.SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.uniform(0, config.SCREEN_WIDTH)

    def draw(self, surface):
        for star in self._stars:
            brightness = 120 + int(80 * (0.5 + 0.5 * math.sin(star["twinkle"])))
            blue = brightness + 40
            if blue > 255:
                blue = 255
            color = (brightness, brightness, blue)
            position = (int(star["x"]), int(star["y"]))
            radius = max(1, int(star["size"]))
            pygame.draw.circle(surface, color, position, radius)


def draw_background(surface, starfield):
    draw_vertical_gradient(surface, config.BG_TOP, config.BG_BOTTOM)
    starfield.draw(surface)
