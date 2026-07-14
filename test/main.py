import sys
import pygame

from src import config
from src.data_manager import DataManager
from src.ui.screens import MenuScreen


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.CAPTION)
        self._surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()
        self._running = True

        self._data = DataManager(config.DATABASE_FILE)
        self._screen = MenuScreen(self._data)

    def run(self):
        while self._running:
            dt = self._clock.tick(config.FPS) / 1000.0
            self._handle_events()
            self._screen.update(dt)
            self._go_to_next_screen_if_needed()
            self._screen.draw(self._surface)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return
            self._screen.handle_event(event)

    def _go_to_next_screen_if_needed(self):
        next_screen = self._screen.next_screen()
        if next_screen is not None:
            self._screen = next_screen


if __name__ == "__main__":
    app = App()
    app.run()
