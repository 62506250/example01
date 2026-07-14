from abc import ABC, abstractmethod
import pygame

from src import config, theme
from src.data_manager import DataManager
from src.ui.widgets import Button, InputBox, sync_field_focus

CAPTION_TITLE = "1v1 SHOOTER ARENA"


class Screen(ABC):
    def __init__(self):
        self._starfield = theme.StarField()
        self._next = None

    def _draw_backdrop(self, surface):
        self._starfield.update(1 / config.FPS)
        theme.draw_background(surface, self._starfield)

    @abstractmethod
    def handle_event(self, event):
        raise NotImplementedError

    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, surface):
        raise NotImplementedError

    def next_screen(self):
        upcoming = self._next
        self._next = None
        return upcoming


class MenuScreen(Screen):

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._title_font = pygame.font.Font(config.FONT_NAME, 56)
        self._subtitle_font = pygame.font.Font(config.FONT_NAME, 18)

        cx = config.SCREEN_WIDTH // 2
        w = 260
        h = 56
        gap = 18
        start_y = 300

        self._buttons = {
            "signup": Button(cx - w // 2, start_y, w, h, "Sign Up", config.ACCENT_CYAN),
            "login": Button(cx - w // 2, start_y + (h + gap), w, h, "Login & Play", config.ACCENT_GREEN),
            "help": Button(cx - w // 2, start_y + 2 * (h + gap), w, h, "How to Play", config.ACCENT_PURPLE),
            "leaderboard": Button(cx - w // 2, start_y + 3 * (h + gap), w, h, "Leaderboard", config.ACCENT_GOLD),
            "exit": Button(cx - w // 2, start_y + 4 * (h + gap), w, h, "Exit", config.ACCENT_RED),
        }

    def next_screen(self):
        upcoming = self._next
        self._next = None
        return upcoming

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        pos = event.pos
        if self._buttons["signup"].is_clicked(pos):
            self._next = SignUpScreen(self._data)
        elif self._buttons["login"].is_clicked(pos):
            self._next = LoginScreen(self._data)
        elif self._buttons["help"].is_clicked(pos):
            self._next = HelpScreen(self._data)
        elif self._buttons["leaderboard"].is_clicked(pos):
            self._next = LeaderboardScreen(self._data)
        elif self._buttons["exit"].is_clicked(pos):
            pygame.quit()
            raise SystemExit

    def draw(self, surface):
        self._draw_backdrop(surface)
        theme.draw_glow_text(
            surface, self._title_font, CAPTION_TITLE, (config.SCREEN_WIDTH // 2, 140),
            glow_color=config.ACCENT_CYAN,
        )
        subtitle = self._subtitle_font.render(
            "Two players. One arena. Best aim wins.", True, config.TEXT_MUTED
        )
        surface.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 190)))

        for button in self._buttons.values():
            button.draw(surface)


class SignUpScreen(Screen):

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._title_font = pygame.font.Font(config.FONT_NAME, 44)
        self._hint_font = pygame.font.Font(config.FONT_NAME, 18)

        cx = config.SCREEN_WIDTH // 2
        self._username_box = InputBox(cx - 160, 260, 320, 50, "Choose a username")
        self._password_box = InputBox(cx - 160, 330, 320, 50, "Choose a password", is_password=True)
        self._username_box.active = True

        self._create_btn = Button(cx - 150, 410, 140, 50, "Create", config.ACCENT_GREEN)
        self._back_btn = Button(cx + 10, 410, 140, 50, "Back", config.ACCENT_RED)

        self._message = ""
        self._message_color = config.ACCENT_RED

    def _submit(self):
        success, msg = self._data.sign_up(self._username_box.text, self._password_box.text)
        self._message = msg
        if success:
            self._message_color = config.ACCENT_GREEN
            self._username_box.text = ""
            self._password_box.text = ""
        else:
            self._message_color = config.ACCENT_RED

    def handle_event(self, event):
        self._username_box.handle_event(event)
        self._password_box.handle_event(event)
        sync_field_focus(event, self._username_box, self._password_box)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._submit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._create_btn.is_clicked(event.pos):
                self._submit()
            elif self._back_btn.is_clicked(event.pos):
                self._next = MenuScreen(self._data)

    def draw(self, surface):
        self._draw_backdrop(surface)
        theme.draw_glow_text(
            surface, self._title_font, "Create Account", (config.SCREEN_WIDTH // 2, 160),
            glow_color=config.ACCENT_CYAN,
        )
        self._username_box.draw(surface)
        self._password_box.draw(surface)
        self._create_btn.draw(surface)
        self._back_btn.draw(surface)

        hint = self._hint_font.render("TAB to switch fields · ENTER to submit", True, config.TEXT_MUTED)
        surface.blit(hint, hint.get_rect(center=(config.SCREEN_WIDTH // 2, 500)))

        if self._message:
            msg = self._hint_font.render(self._message, True, self._message_color)
            surface.blit(msg, msg.get_rect(center=(config.SCREEN_WIDTH // 2, 540)))


class LoginScreen(Screen):

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._title_font = pygame.font.Font(config.FONT_NAME, 44)
        self._hint_font = pygame.font.Font(config.FONT_NAME, 18)

        cx = config.SCREEN_WIDTH // 2
        self._username_box = InputBox(cx - 160, 300, 320, 50, "Username")
        self._password_box = InputBox(cx - 160, 370, 320, 50, "Password", is_password=True)
        self._username_box.active = True

        self._login_btn = Button(cx - 150, 450, 140, 50, "Login", config.ACCENT_GREEN)
        self._back_btn = Button(cx + 10, 450, 140, 50, "Back", config.ACCENT_RED)

        self._stage = 1  # 1 = Player 1 is logging in, 2 = Player 2 is logging in
        self._player1_name = None
        self._message = ""
        self._message_color = config.ACCENT_RED

    def _submit(self):
        username = self._username_box.text.strip()
        password = self._password_box.text

        if not username or not password:
            self._message = "Username and password cannot be empty."
            self._message_color = config.ACCENT_RED
            return

        success, msg = self._data.login(username, password)
        if not success:
            self._message = msg
            self._message_color = config.ACCENT_RED
            return

        if self._stage == 1:
            self._player1_name = username
            self._stage = 2
            self._username_box.text = ""
            self._password_box.text = ""
            self._username_box.active = True
            self._password_box.active = False
            self._message = "Player 1 ready. Now Player 2, log in."
            self._message_color = config.ACCENT_GREEN
            return

        if username == self._player1_name:
            self._message = "Player 2 needs a different account than Player 1."
            self._message_color = config.ACCENT_RED
            return

        self._next = PlayingScreen(self._player1_name, username, self._data)

    def handle_event(self, event):
        self._username_box.handle_event(event)
        self._password_box.handle_event(event)
        sync_field_focus(event, self._username_box, self._password_box)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._submit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._login_btn.is_clicked(event.pos):
                self._submit()
            elif self._back_btn.is_clicked(event.pos):
                self._next = MenuScreen(self._data)

    def draw(self, surface):
        self._draw_backdrop(surface)

        if self._stage == 1:
            title = "Player 1: Log In"
            accent = config.ACCENT_CYAN
        else:
            title = "Player 2: Log In"
            accent = config.ACCENT_MAGENTA

        theme.draw_glow_text(
            surface, self._title_font, title, (config.SCREEN_WIDTH // 2, 160), glow_color=accent
        )

        if self._player1_name:
            note = self._hint_font.render("Player 1: " + self._player1_name, True, config.ACCENT_CYAN)
            surface.blit(note, note.get_rect(center=(config.SCREEN_WIDTH // 2, 210)))

        self._username_box.draw(surface)
        self._password_box.draw(surface)
        self._login_btn.draw(surface)
        self._back_btn.draw(surface)

        hint = self._hint_font.render("TAB to switch fields · ENTER to log in", True, config.TEXT_MUTED)
        surface.blit(hint, hint.get_rect(center=(config.SCREEN_WIDTH // 2, 540)))

        if self._message:
            msg = self._hint_font.render(self._message, True, self._message_color)
            surface.blit(msg, msg.get_rect(center=(config.SCREEN_WIDTH // 2, 575)))


class HelpScreen(Screen):

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._title_font = pygame.font.Font(config.FONT_NAME, 44)
        self._font = pygame.font.Font(config.FONT_NAME, 20)

        cx = config.SCREEN_WIDTH // 2
        self._back_btn = Button(cx - 90, 660, 180, 46, "Back", config.ACCENT_RED)

        self._sections = [
            ("Goal", [
                "Shoot the apples for points. The farther your shot is from",
                "your previous one, the more points you earn (1-5).",
                "Land hits back-to-back without missing for a combo bonus.",
            ], config.ACCENT_GOLD),
            ("Controls", [
                "Player 1  -  Move: W A S D   |   Shoot: SPACE",
                "Player 2  -  Move: Arrow Keys |   Shoot: ENTER",
            ], config.ACCENT_CYAN),
            ("Aiming", [
                "Your crosshair starts hidden at a random spot.",
                "It's revealed the moment you take your first shot.",
            ], config.ACCENT_PURPLE),
            ("Bullets & Time", [
                "Each player starts with the same bullets and time.",
                "Run out of either and you can no longer shoot.",
                "The match ends once BOTH players can no longer shoot.",
            ], config.ACCENT_GREEN),
            ("Power-ups", [
                "Green  = bonus bullets for you.",
                "Purple = bonus time for you.",
                "Gray   = sabotage! Hurts your opponent's time, ammo, or aim.",
            ], config.ACCENT_MAGENTA),
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self._back_btn.is_clicked(event.pos):
            self._next = MenuScreen(self._data)

    def draw(self, surface):
        self._draw_backdrop(surface)
        theme.draw_glow_text(
            surface, self._title_font, "How to Play", (config.SCREEN_WIDTH // 2, 80),
            glow_color=config.ACCENT_CYAN,
        )
        panel_rect = pygame.Rect(80, 130, config.SCREEN_WIDTH - 160, 500)
        theme.draw_panel(surface, panel_rect)

        y = 150
        for heading, lines, color in self._sections:
            heading_surface = self._font.render(heading, True, color)
            surface.blit(heading_surface, (110, y))
            y += 30
            for line in lines:
                line_surface = self._font.render(line, True, config.TEXT_WHITE)
                surface.blit(line_surface, (130, y))
                y += 26
            y += 10

        self._back_btn.draw(surface)


class LeaderboardScreen(Screen):

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._title_font = pygame.font.Font(config.FONT_NAME, 44)
        self._header_font = pygame.font.Font(config.FONT_NAME, 22)
        self._row_font = pygame.font.Font(config.FONT_NAME, 20)

        cx = config.SCREEN_WIDTH // 2
        self._back_btn = Button(cx - 90, 660, 180, 46, "Back", config.ACCENT_RED)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self._back_btn.is_clicked(event.pos):
            self._next = MenuScreen(self._data)

    def draw(self, surface):
        self._draw_backdrop(surface)
        theme.draw_glow_text(
            surface, self._title_font, "Leaderboard", (config.SCREEN_WIDTH // 2, 80),
            glow_color=config.ACCENT_GOLD,
        )
        panel_rect = pygame.Rect(200, 130, config.SCREEN_WIDTH - 400, 500)
        theme.draw_panel(surface, panel_rect)

        all_rows = self._data.load_leaderboard()
        rows = all_rows[:10]
        rank_x = 230
        name_x = 340
        score_x = 620

        rank_header = self._header_font.render("Rank", True, config.ACCENT_GOLD)
        surface.blit(rank_header, (rank_x, 150))
        surface.blit(self._header_font.render("Player", True, config.ACCENT_GOLD), (name_x, 150))
        surface.blit(self._header_font.render("Score", True, config.ACCENT_GOLD), (score_x, 150))

        if not rows:
            empty = self._row_font.render("No scores yet -- go play a match!", True, config.TEXT_MUTED)
            surface.blit(empty, empty.get_rect(center=(config.SCREEN_WIDTH // 2, 320)))
        else:
            row_index = 0
            for row in rows:
                y = 195 + row_index * 34
                rank_text = self._row_font.render(str(row_index + 1), True, config.TEXT_WHITE)
                name_text = self._row_font.render(row["username"], True, config.TEXT_WHITE)
                score_text = self._row_font.render(str(row["score"]), True, config.TEXT_WHITE)
                surface.blit(rank_text, (rank_x, y))
                surface.blit(name_text, (name_x, y))
                surface.blit(score_text, (score_x, y))
                row_index += 1

        self._back_btn.draw(surface)


class GameOverScreen(Screen):
    """Shows the final scores and winner, and offers a rematch, the
    main menu, or the leaderboard."""

    def __init__(self, data, player1_name, player2_name, score1, score2):
        super().__init__()
        self._data = data
        self._player1_name = player1_name
        self._player2_name = player2_name
        self._score1 = score1
        self._score2 = score2

        self._title_font = pygame.font.Font(config.FONT_NAME, 50)
        self._font = pygame.font.Font(config.FONT_NAME, 28)
        self._hint_font = pygame.font.Font(config.FONT_NAME, 18)

        cx = config.SCREEN_WIDTH // 2
        self._rematch_btn = Button(cx - 300, 480, 190, 54, "Play Again", config.ACCENT_GREEN)
        self._menu_btn = Button(cx - 95, 480, 190, 54, "Main Menu", config.ACCENT_CYAN)
        self._leaderboard_btn = Button(cx + 110, 480, 190, 54, "Leaderboard", config.ACCENT_GOLD)

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if self._rematch_btn.is_clicked(event.pos):
            self._next = PlayingScreen(self._player1_name, self._player2_name, self._data)
        elif self._menu_btn.is_clicked(event.pos):
            self._next = MenuScreen(self._data)
        elif self._leaderboard_btn.is_clicked(event.pos):
            self._next = LeaderboardScreen(self._data)

    def draw(self, surface):
        self._draw_backdrop(surface)
        theme.draw_glow_text(
            surface, self._title_font, "Match Over", (config.SCREEN_WIDTH // 2, 140),
            glow_color=config.ACCENT_GOLD,
        )

        if self._score1 == self._score2:
            winner_text = "It's a tie!"
            winner_color = config.ACCENT_GOLD
        elif self._score1 > self._score2:
            winner_text = self._player1_name + " wins!"
            winner_color = config.ACCENT_CYAN
        else:
            winner_text = self._player2_name + " wins!"
            winner_color = config.ACCENT_MAGENTA

        winner_surface = self._font.render(winner_text, True, winner_color)
        surface.blit(winner_surface, winner_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 220)))

        panel_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 220, 270, 440, 150)
        theme.draw_panel(surface, panel_rect)

        p1_line = self._font.render(self._player1_name + ": " + str(self._score1) + " pts", True, config.ACCENT_CYAN)
        p2_line = self._font.render(self._player2_name + ": " + str(self._score2) + " pts", True, config.ACCENT_MAGENTA)
        surface.blit(p1_line, p1_line.get_rect(center=(config.SCREEN_WIDTH // 2, 315)))
        surface.blit(p2_line, p2_line.get_rect(center=(config.SCREEN_WIDTH // 2, 365)))

        self._rematch_btn.draw(surface)
        self._menu_btn.draw(surface)
        self._leaderboard_btn.draw(surface)


class PlayingScreen(Screen):

    def __init__(self, player1_name, player2_name, data):
        from src.core.game_engine import GameEngine  

        self._data = data
        self._engine = GameEngine(player1_name, player2_name)
        self._score_recorded = False
        self._next = None

    def handle_event(self, event):
        self._engine.handle_event(event)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._engine.update(dt, keys)

        if self._engine.game_over and not self._score_recorded:
            self._data.add_score(self._engine.player1.name, self._engine.player1.score)
            self._data.add_score(self._engine.player2.name, self._engine.player2.score)
            self._score_recorded = True
            self._next = GameOverScreen(
                self._data,
                self._engine.player1.name,
                self._engine.player2.name,
                self._engine.player1.score,
                self._engine.player2.score,
            )

    def draw(self, surface):
        self._engine.draw(surface)
