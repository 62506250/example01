# توی این کد من مجبور شدم که پای گیم و استفاده از فایل ها رو یاد بگیرم
# ساختار کلی کد ارث بری و این چیزا نیست و بیشتر استفاده یک کلاس توی کلاس دیگه ایه
import pygame
import sys
import json
import os
import random
WIDTH = 1000
HEIGHT = 700
FPS = 60
USERS_FILE = "users.json"
LEADERBOARD_FILE = "leaderboard.json"
#این کد رنگای RBG هستش
BG_COLOR = (25, 25, 35)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (70, 70, 70)
GREEN = (50, 220, 100)
RED = (220, 70, 70)
BLUE = (70, 130, 220)
YELLOW = (240, 220, 70)
LIGHT_BLUE = (70, 220, 220)
PINK = (220, 70, 220)
ORANGE = (255, 165, 0)
TARGET_COLORS = [RED, YELLOW, LIGHT_BLUE, PINK, GREEN]

#این کلاس برای مدیریت فایل ها و ورود و ثبت نام لیدر برده
class DataManager:
    def __init__(self, users_file, leaderboard_file):
        self.users_file = users_file
        self.leaderboard_file = leaderboard_file
        self.ensure_files()
    def ensure_files(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as f:
                json.dump({}, f)
        if not os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, "w") as f:
                json.dump([], f)
    def load_users(self):
        with open(self.users_file, "r") as f:
            return json.load(f)
    def save_users(self, users):
        with open(self.users_file, "w") as f:
            json.dump(users, f)
    def sign_up(self, username, password):
        users = self.load_users()
        if username in users:
            return False, "Username already exists!"
        users[username] = password
        self.save_users(users)
        return True, "Sign up successful!"
    def login(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "Username not found!"
        if users[username] != password:
            return False, "Wrong password!"
        return True, "Login successful!"
    def load_leaderboard(self):
        with open(self.leaderboard_file, "r") as f:
            return json.load(f)
    def save_leaderboard(self, leaderboard):
        with open(self.leaderboard_file, "w") as f:
            json.dump(leaderboard, f,)
    def add_score(self, username, score):
        leaderboard = self.load_leaderboard()
        leaderboard.append({"username":username,"score":score})
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.save_leaderboard(leaderboard)

# این یکی کلاس برای سرعت نشانه و حرکتش و شکلشه
class Player:
    def __init__(self, username, x, y, color, controls, shoot_key):
        self.username = username
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.shoot_key = shoot_key
        self.score = 0
        self.ammo = 10
# تعداد تیرا رو میتونین تغییر بدین
        self.speed = 4
# اگه خواستین میتونین این سرعت و مشخصات و ایناش رو عوض کنید حالا من امتحان کردم این سرعت حرکت اوکی بود (منظورم سرعت نشونه اتس) 
        self.last_shot_pos = None
        self.last_shot_timer = 0
    def move(self, keys):
        if keys[self.controls["left"]]:
            self.x -= self.speed
        if keys[self.controls["right"]]:
            self.x += self.speed
        if keys[self.controls["up"]]:
            self.y -= self.speed
        if keys[self.controls["down"]]:
            self.y += self.speed
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH:
            self.x = WIDTH
        if self.y < 80:
            self.y = 80
        if self.y > HEIGHT:
            self.y = HEIGHT
#تو این یکی نشانه رو میکشیم هر کی دوست داشت میتونه تغییرش بده
    def draw_shot_mark(self, screen):
        if self.last_shot_pos and self.last_shot_timer > 0:
            shot_x, shot_y = self.last_shot_pos
            pygame.draw.circle(screen, self.color, (shot_x, shot_y), 10, 2)
            pygame.draw.line(screen, self.color, (shot_x - 8, shot_y), (shot_x + 8, shot_y), 2)
            pygame.draw.line(screen, self.color, (shot_x, shot_y - 8), (shot_x, shot_y + 8), 2)
# تو این یکی هم اون یه لحظه ای که نشانه باید نشون داده بشه
    def update_shot_mark(self):
        if self.last_shot_timer > 0:
            self.last_shot_timer -= 1
        if self.last_shot_timer <= 0:
            self.last_shot_pos = None

# این یکی کلاس هم برای سیبل هاست
class Target:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
# سیبلا یه سری دایره های رنگین اگه خواستین میتونین بهش مشخصات اضافه کنین قشنگ تر شه
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    def is_hit(self, shot_x, shot_y):
        d = (shot_x - self.x) ** 2 + (shot_y - self.y) ** 2
        return d <= self.radius ** 2

# من یه آیتم گذاشتم که هر وقت بزنیدش بهتون پنج تاتیر اضافه میده
class AmmoItem:
    def __init__(self, x, y, radius=18):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = ORANGE
        self.ammo_bonus = 5
# اینجا هم کشیدمش
    def draw(self, screen, font):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        t = font.render("+5",True, WHITE)
        t2 = t.get_rect(center=(self.x, self.y))
        screen.blit(t, t2)
    def is_hit(self, shot_x, shot_y):
        d = (shot_x - self.x) ** 2 + (shot_y - self.y) ** 2
        return d <= self.radius ** 2

# همه ی دکمه ها
class Button:
    def __init__(self, x, y, w, h, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        t = font.render(self.text, True, self.text_color)
        t2 = t.get_rect(center=self.rect.center)
        screen.blit(t, t2)
    def is_clicked(self, p):
        return self.rect.collidepoint(p)

# منظورم اینجا اون قسمتاست که که باید بنویسی تا و از کربر یه چیزی میخواد مثل سن یا یوزرنیم پسورد
class InputBox:
    def __init__(self, x, y, w, h, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.is_password = is_password
        self.active = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                pass
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if len(self.text) < 20:
                    self.text += event.unicode
    def draw(self, screen, font):
        color = WHITE if self.active else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        if self.text == "":
            show_text = self.placeholder
            screen.blit(font.render(show_text, True, DARK_GRAY), (self.rect.x + 10, self.rect.y + 10))
        else:
            show_text = "*" * len(self.text) if self.is_password else self.text
            screen.blit(font.render(show_text, True, WHITE), (self.rect.x + 10, self.rect.y + 10))

# این کلاس تقریبا همه ی کار های بازی رو انجام میده و تقریبا مکان تلفیق همه ی کلاساست
class GameManager:
    def __init__(self):
        self.data = DataManager(USERS_FILE, LEADERBOARD_FILE)
        self.state = "MENU"
# راستش این فونت ها رو بلد نبودم از چت جی پی تی پرسیدم
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 60)
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.message = ""
        self.player1_user = None
        self.player2_user = None
        self.login_stage = 1
# اینجا قرار از همون کلاس INputBox استفاده کنم
        self.signup_username = InputBox(350, 180, 300, 45, "New username")
        self.signup_password = InputBox(350, 250, 300, 45, "New password", True)
        self.login_username = InputBox(350, 220, 300, 45, "Username")
        self.login_password = InputBox(350, 290, 300, 45, "Password", True)
# اینم دکمه ها
        self.menu_buttons = [Button(400, 200, 200, 50, "Sign Up", BLUE), Button(400, 270, 200, 50, "Login Players", GREEN), Button(400, 340, 200, 50, "Help", LIGHT_BLUE, (0, 0, 0)), Button(400, 410, 200, 50, "Leaderboard", YELLOW, (0, 0, 0)), Button(400, 480, 200, 50, "Exit", RED)]
        self.signup_buttons = [Button(370, 340, 120, 45, "Create", GREEN), Button(510, 340, 120, 45, "Back", RED)]
        self.login_buttons = [Button(370, 390, 120, 45, "Login", GREEN), Button(510, 390, 120, 45, "Back", RED)]
        self.leaderboard_buttons = [Button(420, 600, 160, 45, "Back", RED)]
        self.help_buttons = [Button(420, 600, 160, 45, "Back", RED)]
        self.game_over_buttons = [Button(330, 430, 160, 50, "Menu", BLUE), Button(510, 430, 160, 50, "Leaderboard", YELLOW, (0, 0, 0))]
        self.player1 = None
        self.player2 = None
        self.targets = []
        self.ammo_items = []
# این قسمت پایین هم تنظیمات بازیه شامل زمان و زمان اسپان و اینا
        self.game_timer = 60 * FPS
        self.max_targets = 5
        self.ammo_spawn = 15 * FPS
        self.ammo_spawn_timer = self.ammo_spawn
# ساخت سیبلا و استفاده از کلاس Target
    def create_random_target(self):
        radius = random.randint(20, 40)
        x = random.randint(radius + 20, WIDTH - radius - 20)
        y = random.randint(radius + 100, HEIGHT - radius - 20)
        color = random.choice(TARGET_COLORS)
        return Target(x, y, radius, color)
    def create_ammo_item(self):
        radius = 15
        x = random.randint(radius + 20, WIDTH - radius - 20)
        y = random.randint(radius + 100, HEIGHT - radius - 20)
        return AmmoItem(x, y, radius)
# نقطه های شروع (منظورم از همه نظره) 
    def start_game(self):
        self.player1 = Player(username=self.player1_user, x=200, y=350, color=GREEN, controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN}, shoot_key=pygame.K_SPACE)
        self.player2 = Player(username=self.player2_user, x=800, y=350, color=LIGHT_BLUE, controls={"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s}, shoot_key=pygame.K_q)
        self.targets = []
        for _ in range(self.max_targets):
            self.targets.append(self.create_random_target())
        self.ammo_items = []
        self.ammo_spawn_timer = self.ammo_spawn
        self.game_timer = 60 * FPS
        self.message = ""
        self.state = "PLAYING"
# این ریست رو پدرم در اومد تا بفهمم بزارم اصلا هی میگشتم دنبال مشکل
    def reset_forms(self):
        self.signup_username.text = ""
        self.signup_password.text = ""
        self.login_username.text = ""
        self.login_password.text = ""
        self.signup_username.active = False
        self.signup_password.active = False
        self.login_username.active = False
        self.login_password.active = False
    def reset_login_process(self):
        self.player1_user = None
        self.player2_user = None
        self.login_stage = 1
        self.login_username.text = ""
        self.login_password.text = ""
        self.login_username.active = False
        self.login_password.active = False
    def shoot(self, player):
# این یعنی اگه گلوله نداشت کاری نکن
        if player.ammo <= 0:
            return
# اگه گلوله داشت که خب این کارا رو بکن
        player.ammo -= 1
        player.last_shot_pos = (player.x, player.y)
        player.last_shot_timer = 20
        hit_target = None
        for target in self.targets:
            if target.is_hit(player.x, player.y):
                hit_target = target
                break
# اینم میگه اگه خورد به سیبل چی میشه
        if hit_target:
            player.score += 1
            self.targets.remove(hit_target)
            self.targets.append(self.create_random_target())
        hit_ammo = None
        for item in self.ammo_items:
            if item.is_hit(player.x, player.y):
                hit_ammo = item
                break
        if hit_ammo:
            player.ammo += hit_ammo.ammo_bonus
            self.ammo_items.remove(hit_ammo)
# پایان بازی
    def end_game(self):
        if self.player1:
            self.data.add_score(self.player1.username, self.player1.score)
        if self.player2:
            self.data.add_score(self.player2.username, self.player2.score)
        self.state = "GAME_OVER"
# تابع برای اینه که وضهیت معلوم بشه
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.state == "MENU":
                self.handle_menu_events(e)
            elif self.state == "SIGNUP":
                self.handle_signup_events(e)
            elif self.state == "LOGIN":
                self.handle_login_events(e)
            elif self.state == "LEADERBOARD":
                self.handle_leaderboard_events(e)
            elif self.state == "HELP":
                self.handle_help_events(e)
            elif self.state == "PLAYING":
                self.handle_playing_events(e)
            elif self.state == "GAME_OVER":
                self.handle_game_over_events(e)
# مدیریت توی وضعیت منو
    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.menu_buttons[0].is_clicked(pos):
                self.message = ""
                self.reset_forms()
                self.state = "SIGNUP"
            elif self.menu_buttons[1].is_clicked(pos):
                self.message = ""
                self.reset_login_process()
                self.state = "LOGIN"
            elif self.menu_buttons[2].is_clicked(pos):
                self.message = ""
                self.state = "HELP"
            elif self.menu_buttons[3].is_clicked(pos):
                self.message = ""
                self.state = "LEADERBOARD"
            elif self.menu_buttons[4].is_clicked(pos):
                pygame.quit()
                sys.exit()
# مدیریت توی وضغیت ثبت نام
    def handle_signup_events(self, event):
        self.signup_username.handle_event(event)
        self.signup_password.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self.signup_username.active:
                self.signup_username.active = False
                self.signup_password.active = True
            else:
                self.signup_password.active = False
                self.signup_username.active = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.do_signup()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.signup_buttons[0].is_clicked(pos):
                self.do_signup()
            elif self.signup_buttons[1].is_clicked(pos):
                self.message = ""
                self.state = "MENU"
# فکر کنم نیازی به توضیح نیست
    def do_signup(self):
        username = self.signup_username.text.strip()
        password = self.signup_password.text.strip()
        if username == "" or password == "":
            self.message = "Username and password cannot be empty!"
            return
        success, msg = self.data.sign_up(username, password)
        self.message = msg
        if success:
            self.state = "MENU"
# مدیریت وضعیت ورود
    def handle_login_events(self, event):
        self.login_username.handle_event(event)
        self.login_password.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self.login_username.active:
                self.login_username.active = False
                self.login_password.active = True
            else:
                self.login_password.active = False
                self.login_username.active = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.do_login()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.login_buttons[0].is_clicked(pos):
                self.do_login()
            elif self.login_buttons[1].is_clicked(pos):
                self.message = ""
                self.state = "MENU"
# این برای اینه که مطمثن بشیم هردو بازیکن لاگین کردن
    def do_login(self):
        username = self.login_username.text.strip()
        password = self.login_password.text.strip()
        if username == "" or password == "":
            self.message = "Username and password cannot be empty!"
            return
        success, msg = self.data.login(username, password)
        if not success:
            self.message = msg
            return
        if self.login_stage == 1:
            self.player1_user = username
            self.login_stage = 2
            self.login_username.text = ""
            self.login_password.text = ""
            self.message = "Player 1 logged in. Now Player 2 login."
        elif self.login_stage == 2:
            if username == self.player1_user:
                self.message = "Player 2 cannot use the same account as Player 1!"
                return
            self.player2_user = username
            self.message = "Both players logged in successfully!"
            self.start_game()
# مدیریت وضعیت جدول امتیازات
    def handle_leaderboard_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.leaderboard_buttons[0].is_clicked(pos):
                self.state = "MENU"
# قسمت help
    def handle_help_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.help_buttons[0].is_clicked(pos):
                self.state = "MENU"
# مدیریت وضعیت بازی
    def handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.player1.shoot_key:
                self.shoot(self.player1)
            elif event.key == self.player2.shoot_key:
                self.shoot(self.player2)
            elif event.key == pygame.K_ESCAPE:
                self.end_game()
# مدیریت پایانش
    def handle_game_over_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.game_over_buttons[0].is_clicked(pos):
                self.message = ""
                self.state = "MENU"
            elif self.game_over_buttons[1].is_clicked(pos):
                self.state = "LEADERBOARD"
    def update(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            self.player1.move(keys)
            self.player2.move(keys)
            self.player1.update_shot_mark()
            self.player2.update_shot_mark()
            self.game_timer -= 1
            self.ammo_spawn_timer -= 1
            if self.ammo_spawn_timer <= 0:
                self.ammo_items.append(self.create_ammo_item())
                self.ammo_spawn_timer = self.ammo_spawn
            if self.game_timer <= 0 or (self.player1.ammo <= 0 and self.player2.ammo <= 0):
                self.end_game()
# این برای نمایش همه شونه دیگه
    def draw(self, screen):
        screen.fill(BG_COLOR)
        if self.state == "MENU":
            self.draw_menu(screen)
        elif self.state == "SIGNUP":
            self.draw_signup(screen)
        elif self.state == "LOGIN":
            self.draw_login(screen)
        elif self.state == "LEADERBOARD":
            self.draw_leaderboard(screen)
        elif self.state == "HELP":
            self.draw_help(screen)
        elif self.state == "PLAYING":
            self.draw_playing(screen)
        elif self.state == "GAME_OVER":
            self.draw_game_over(screen)
        pygame.display.flip()
# اینام نمایش جزئی ترن من دیگه زیاد توضیح نمیدم
    def draw_title(self, screen, text, y=60):
        surface = self.title_font.render(text, True, WHITE)
        rect = surface.get_rect(center=(WIDTH // 2, y))
        screen.blit(surface, rect)
    def draw_message(self, screen, color=RED, y=470):
        if self.message:
            msg_surface = self.small_font.render(self.message, True, color)
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, y))
            screen.blit(msg_surface, msg_rect)
    def draw_menu(self, screen):
        self.draw_title(screen, "2-Player Shooting Game")
        info1 = self.small_font.render("Player 1: Arrow Keys + SPACE", True, GRAY)
        info2 = self.small_font.render("Player 2: W A S D + Q", True, GRAY)
        screen.blit(info1, (390, 145))
        screen.blit(info2, (430, 170))
        for button in self.menu_buttons:
            button.draw(screen, self.font)
        self.draw_message(screen)
    def draw_signup(self, screen):
        self.draw_title(screen, "Sign Up")
        self.signup_username.draw(screen, self.font)
        self.signup_password.draw(screen, self.font)
        for button in self.signup_buttons:
            button.draw(screen, self.font)
        hint = self.small_font.render("TAB to switch fields - ENTER to submit", True, GRAY)
        screen.blit(hint, (360, 520))
        self.draw_message(screen)
    def draw_login(self, screen):
        if self.login_stage == 1:
            title = "Login Player 1"
            subtitle = "Enter account for Player 1"
        else:
            title = "Login Player 2"
            subtitle = "Enter account for Player 2"
        self.draw_title(screen, title)
        subtitle_surface = self.small_font.render(subtitle, True, YELLOW)
        subtitle_rect = subtitle_surface.get_rect(center=(WIDTH // 2, 150))
        screen.blit(subtitle_surface, subtitle_rect)
        self.login_username.draw(screen, self.font)
        self.login_password.draw(screen, self.font)
        for button in self.login_buttons:
            button.draw(screen, self.font)
        hint = self.small_font.render("TAB to switch fields - ENTER to login", True, GRAY)
        screen.blit(hint, (370, 520))
        self.draw_message(screen)
    def draw_leaderboard(self, screen):
        self.draw_title(screen, "Leaderboard")
        leaderboard = self.data.load_leaderboard()
        header1 = self.font.render("Rank", True, YELLOW)
        header2 = self.font.render("Username", True, YELLOW)
        header3 = self.font.render("Score", True, YELLOW)
        screen.blit(header1, (250, 140))
        screen.blit(header2, (420, 140))
        screen.blit(header3, (650, 140))
        if len(leaderboard) == 0:
            empty_text = self.font.render("No scores yet.", True, GRAY)
            screen.blit(empty_text, (430, 250))
        else:
            max_show = min(10, len(leaderboard))
            for i in range(max_show):
                row = leaderboard[i]
                rank_surface = self.font.render(str(i + 1), True, WHITE)
                user_surface = self.font.render(row["username"], True, WHITE)
                score_surface = self.font.render(str(row["score"]), True, WHITE)
                y = 190 + i * 35
                screen.blit(rank_surface, (260, y))
                screen.blit(user_surface, (420, y))
                screen.blit(score_surface, (660, y))
        for button in self.leaderboard_buttons:
            button.draw(screen, self.font)
# کل قسمت help همینه تقریبا
    def draw_help(self, screen):
        self.draw_title(screen, "Game Help")
        lines = [
            "Goal:",
            "Hit targets for earn points. Each target gives 1 point.",
            "Players:",
            "Player 1 -> Move: Arrow Keys | Shoot: SPACE",
            "Player 2 -> Move: W: UP A: LEFT S: DOWN D: RIGHT | Shoot: Q",
            "Rules:",
            "1. You are invisible.",
            "2. The shot position is shown only for a second after your shooting.",
            "3. Each player starts with 10 bullets.",
            "4. Game ends when time finishes or both players run out of ammo.",
            "Item:",
            "Every 15 seconds an ammo item appears.",
            "Whoever shoots it gets +5 bullets.",
            "Other:",
            "Press ESC during the game to finish early."]
        y = 130
        for line in lines:
            color = WHITE
            if "Goal:" in line or "Players:" in line or "Rules:" in line or "Special Item:" in line or "Other:" in line:
                color = YELLOW
            text_surface = self.small_font.render(line, True, color)
            screen.blit(text_surface, (120, y))
            y += 28
        for button in self.help_buttons:
            button.draw(screen, self.font)
    def draw_playing(self, screen):
        for target in self.targets:
            target.draw(screen)
        for item in self.ammo_items:
            item.draw(screen, self.small_font)
        self.player1.draw_shot_mark(screen)
        self.player2.draw_shot_mark(screen)
        p1_info = self.font.render(f"{self.player1.username} | Score: {self.player1.score} | Ammo: {self.player1.ammo}", True,self.player1.color)
        p2_info = self.font.render(f"{self.player2.username} | Score: {self.player2.score} | Ammo: {self.player2.ammo}", True, self.player2.color)
        timer_seconds = self.game_timer // FPS
        next_item_seconds = self.ammo_spawn_timer // FPS
        timer_surface = self.font.render(f"Time: {timer_seconds}", True, WHITE)
        item_surface = self.small_font.render(f"Next ammo item in: {next_item_seconds}s", True, ORANGE)
        help_text = self.small_font.render(
            "Invisible aim | Shoot ammo item for +5 bullets | ESC to end game", True,GRAY)
        screen.blit(p1_info, (20, 20))
        screen.blit(p2_info, (20, 60))
        screen.blit(timer_surface, (850, 20))
        screen.blit(item_surface, (760, 55))
        screen.blit(help_text, (250, 665))
    def draw_game_over(self, screen):
        self.draw_title(screen, "Game Over")
        if self.player1.score > self.player2.score:
            result_text = f"Winner: {self.player1.username}"
            result_color = self.player1.color
        elif self.player2.score > self.player1.score:
            result_text = f"Winner: {self.player2.username}"
            result_color = self.player2.color
        else:
            result_text = "Draw!"
            result_color = WHITE
        result_surface = self.font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(WIDTH // 2, 180))
        screen.blit(result_surface, result_rect)
        p1_surface = self.font.render(f"{self.player1.username}: {self.player1.score} points", True,self.player1.color)
        p2_surface = self.font.render(
            f"{self.player2.username}: {self.player2.score} points", True, self.player2.color)
        p1_rect = p1_surface.get_rect(center=(WIDTH // 2, 250))
        p2_rect = p2_surface.get_rect(center=(WIDTH // 2, 300))
        screen.blit(p1_surface, p1_rect)
        screen.blit(p2_surface, p2_rect)
        for button in self.game_over_buttons:
            button.draw(screen, self.font)
#اینم اجرای برنامه
def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2-Player Shooting Game")
    clock = pygame.time.Clock()
    game = GameManager()
    while True:
        game.handle_events()
        game.update()
        game.draw(screen)
        clock.tick(FPS)
run()