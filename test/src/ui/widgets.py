import pygame

from src import config


class Button:

    def __init__(self, x, y, w, h, text, accent=config.ACCENT_CYAN, text_color=config.TEXT_WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self._text = text
        self._accent = accent
        self._text_color = text_color
        self._font = pygame.font.Font(config.FONT_NAME, 26)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        base = self._accent
        if hovered:
            dim_factor = 0.42
        else:
            dim_factor = 0.28

        panel_color = []
        for channel in base:
            dimmed = int(channel * dim_factor)
            if dimmed > 255:
                dimmed = 255
            panel_color.append(dimmed)

        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        panel_fill = (panel_color[0], panel_color[1], panel_color[2], 235)
        pygame.draw.rect(panel, panel_fill, panel.get_rect(), border_radius=12)

        if hovered:
            border_alpha = 255
        else:
            border_alpha = 180
        border_color = (base[0], base[1], base[2], border_alpha)
        pygame.draw.rect(panel, border_color, panel.get_rect(), 2, border_radius=12)
        surface.blit(panel, self.rect.topleft)

        if hovered:
            label_color = base
        else:
            label_color = self._text_color
        label = self._font.render(self._text, True, label_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


class InputBox:

    def __init__(self, x, y, w, h, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self._placeholder = placeholder
        self._is_password = is_password
        self.active = False
        self._font = pygame.font.Font(config.FONT_NAME, 26)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.active = True

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_TAB, pygame.K_RETURN):
                pass
            elif len(self.text) < 20 and event.unicode.isprintable():
                self.text = self.text + event.unicode

    def draw(self, surface):
        if self.active:
            border = config.ACCENT_CYAN
        else:
            border = config.PANEL_BORDER

        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        fill_color = (config.PANEL_BG[0], config.PANEL_BG[1], config.PANEL_BG[2], 220)
        pygame.draw.rect(panel, fill_color, panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, border, panel.get_rect(), 2, border_radius=10)
        surface.blit(panel, self.rect.topleft)

        if self.text:
            if self._is_password:
                shown = "•" * len(self.text)
            else:
                shown = self.text
            color = config.TEXT_WHITE
        else:
            shown = self._placeholder
            color = config.TEXT_MUTED

        rendered = self._font.render(shown, True, color)
        surface.blit(rendered, (self.rect.x + 14, self.rect.y + self.rect.height // 2 - 15))


def sync_field_focus(event, box_a, box_b):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if box_a.rect.collidepoint(event.pos):
            box_b.active = False
        elif box_b.rect.collidepoint(event.pos):
            box_a.active = False
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
        was_a_active = box_a.active
        box_a.active = not was_a_active
        box_b.active = not box_b.active
