import json
import math
import random
import sys
from pathlib import Path

import pygame

from config import (
    PLAYER_SPEED,
    APPLE_POINTS,
    METEOR_PENALTY,
    GAME_TIME,
    START_METEORS,
    PLAYER_SIZE,
)

WIDTH = 1000
HEIGHT = 680
FPS = 60
FIELD_LEFT = 34
FIELD_TOP = 108
FIELD_RIGHT = WIDTH - 34
FIELD_BOTTOM = HEIGHT - 38

BG = (7, 13, 24)
PANEL = (14, 25, 43)
PANEL_2 = (20, 35, 58)
WHITE = (235, 244, 255)
MUTED = (145, 168, 196)
CYAN = (74, 219, 255)
GREEN = (72, 232, 139)
RED = (255, 88, 107)
ORANGE = (255, 167, 70)
YELLOW = (255, 220, 90)
GRID = (20, 45, 70)

BASE_DIR = Path(__file__).resolve().parent
SCORES_FILE = BASE_DIR / "scores.json"


def load_scores():
    try:
        data = json.loads(SCORES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data[:5]
    except Exception:
        pass
    return []


def save_score(name, score):
    scores = load_scores()
    scores.append({"name": name[:18], "score": int(score)})
    scores.sort(key=lambda item: item["score"], reverse=True)
    scores = scores[:5]
    try:
        SCORES_FILE.write_text(
            json.dumps(scores, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass
    return scores


def clamp(value, low, high):
    return max(low, min(high, value))


class Player:
    def __init__(self):
        self.size = PLAYER_SIZE
        self.x = WIDTH / 2
        self.y = HEIGHT - 110
        self.hit_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def update(self, keys, dt):
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx and dy:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        # A játék legfontosabb oktatási pontja:
        # ezt a PLAYER_SPEED értéket a config.py-ból olvassuk.
        self.x += dx * PLAYER_SPEED * 60 * dt
        self.y += dy * PLAYER_SPEED * 60 * dt

        half = self.size / 2
        self.x = clamp(self.x, FIELD_LEFT + half, FIELD_RIGHT - half)
        self.y = clamp(self.y, FIELD_TOP + half, FIELD_BOTTOM - half)

        if self.hit_timer > 0:
            self.hit_timer -= dt

    def draw(self, screen):
        rect = self.rect
        if self.hit_timer > 0 and int(self.hit_timer * 12) % 2 == 0:
            return

        shadow = pygame.Rect(rect.x + 5, rect.y + 7, rect.w, rect.h)
        pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)
        pygame.draw.rect(screen, CYAN, rect, border_radius=12)
        pygame.draw.rect(screen, (9, 35, 52), rect, width=3, border_radius=12)

        eye_y = rect.y + 13
        pygame.draw.circle(screen, BG, (rect.x + 13, eye_y), 4)
        pygame.draw.circle(screen, BG, (rect.right - 13, eye_y), 4)
        pygame.draw.arc(screen, BG, (rect.x + 10, rect.y + 18, rect.w - 20, 16), 0, math.pi, 2)


class Apple:
    def __init__(self):
        self.radius = 16
        self.respawn()

    def respawn(self):
        margin = 55
        self.x = random.randint(FIELD_LEFT + margin, FIELD_RIGHT - margin)
        self.y = random.randint(FIELD_TOP + margin, FIELD_BOTTOM - margin)

    @property
    def rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 120, 130), (self.x - 5, self.y - 5), 5)
        pygame.draw.line(screen, (110, 70, 35), (self.x, self.y - 13), (self.x + 3, self.y - 24), 4)
        pygame.draw.ellipse(screen, GREEN, (self.x + 2, self.y - 25, 15, 8))


class Meteor:
    def __init__(self, difficulty=1.0):
        self.radius = random.randint(18, 28)
        self.reset(difficulty)

    def reset(self, difficulty=1.0):
        self.x = random.randint(FIELD_LEFT + 25, FIELD_RIGHT - 25)
        self.y = random.randint(FIELD_TOP - 250, FIELD_TOP - 40)
        self.speed = random.uniform(145, 225) * difficulty
        self.drift = random.uniform(-55, 55)
        self.spin = random.random() * math.tau

    @property
    def rect(self):
        r = self.radius - 3
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def update(self, dt, difficulty):
        self.y += self.speed * dt
        self.x += self.drift * dt
        self.spin += dt * 3

        if self.y - self.radius > FIELD_BOTTOM:
            self.reset(difficulty)
        if self.x < FIELD_LEFT + self.radius or self.x > FIELD_RIGHT - self.radius:
            self.drift *= -1

    def draw(self, screen):
        tail_len = 32
        tail_x = self.x - math.cos(self.spin) * 4
        pygame.draw.line(
            screen,
            ORANGE,
            (int(tail_x), int(self.y - self.radius)),
            (int(tail_x), int(self.y - self.radius - tail_len)),
            7,
        )
        pygame.draw.line(
            screen,
            YELLOW,
            (int(tail_x), int(self.y - self.radius)),
            (int(tail_x), int(self.y - self.radius - tail_len * 0.65)),
            3,
        )
        pygame.draw.circle(screen, (121, 88, 78), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (87, 62, 58), (int(self.x - 7), int(self.y - 3)), 6)
        pygame.draw.circle(screen, (162, 121, 92), (int(self.x + 7), int(self.y + 6)), 5)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pálfy Python Challenge – Te irányítod a játékot!")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_h1 = pygame.font.SysFont("consolas", 31, bold=True)
        self.font = pygame.font.SysFont("consolas", 22)
        self.font_small = pygame.font.SysFont("consolas", 17)
        self.font_tiny = pygame.font.SysFont("consolas", 14)

        self.state = "name"
        self.player_name = ""
        self.input_text = ""
        self.scores = load_scores()
        self.reset_game_objects()

    def reset_game_objects(self):
        self.player = Player()
        self.apple = Apple()
        self.meteors = [Meteor() for _ in range(START_METEORS)]
        self.score = 0
        self.apples = 0
        self.time_left = float(GAME_TIME)
        self.game_over_saved = False
        self.message = "Gyűjts almát, kerüld a meteorokat!"
        self.message_timer = 2.5

    def start_game(self):
        if not self.player_name.strip():
            self.player_name = "Névtelen"
        self.reset_game_objects()
        self.state = "play"

    def difficulty(self):
        elapsed = GAME_TIME - self.time_left
        return 1.0 + elapsed / 90.0

    def update(self, dt):
        if self.state != "play":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)
        diff = self.difficulty()

        for meteor in self.meteors:
            meteor.update(dt, diff)

        target_count = START_METEORS
        if self.time_left < GAME_TIME * 0.66:
            target_count += 1
        if self.time_left < GAME_TIME * 0.33:
            target_count += 1

        while len(self.meteors) < target_count:
            self.meteors.append(Meteor(diff))

        if self.player.rect.colliderect(self.apple.rect):
            self.score += APPLE_POINTS
            self.apples += 1
            self.apple.respawn()
            self.message = f"+{APPLE_POINTS} pont! Alma begyűjtve."
            self.message_timer = 1.0

        if self.player.hit_timer <= 0:
            for meteor in self.meteors:
                if self.player.rect.colliderect(meteor.rect):
                    self.score = max(0, self.score - METEOR_PENALTY)
                    self.player.hit_timer = 1.35
                    meteor.reset(diff)
                    self.message = f"-{METEOR_PENALTY} pont! Meteor találat."
                    self.message_timer = 1.4
                    break

        if self.message_timer > 0:
            self.message_timer -= dt

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.finish_game()

    def finish_game(self):
        if not self.game_over_saved:
            self.scores = save_score(self.player_name, self.score)
            self.game_over_saved = True
        self.state = "over"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if self.state == "name":
            if event.key == pygame.K_RETURN:
                self.player_name = self.input_text.strip() or "Névtelen"
                self.start_game()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode.isprintable() and len(self.input_text) < 18:
                self.input_text += event.unicode

        elif self.state == "play":
            if event.key == pygame.K_r:
                self.start_game()
            elif event.key == pygame.K_F2:
                self.state = "code"

        elif self.state == "code":
            if event.key in (pygame.K_F2, pygame.K_RETURN, pygame.K_SPACE):
                self.state = "play"

        elif self.state == "over":
            if event.key == pygame.K_r:
                self.start_game()
            elif event.key == pygame.K_n:
                self.state = "name"
                self.input_text = ""

    def text(self, text, font, color, x, y, align="left"):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if align == "center":
            rect.center = (x, y)
        elif align == "right":
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)
        return rect

    def draw_background(self):
        self.screen.fill(BG)
        pygame.draw.rect(
            self.screen,
            PANEL,
            (FIELD_LEFT, FIELD_TOP, FIELD_RIGHT - FIELD_LEFT, FIELD_BOTTOM - FIELD_TOP),
            border_radius=16,
        )
        for x in range(FIELD_LEFT, FIELD_RIGHT, 40):
            pygame.draw.line(self.screen, GRID, (x, FIELD_TOP), (x, FIELD_BOTTOM), 1)
        for y in range(FIELD_TOP, FIELD_BOTTOM, 40):
            pygame.draw.line(self.screen, GRID, (FIELD_LEFT, y), (FIELD_RIGHT, y), 1)
        pygame.draw.rect(
            self.screen,
            (40, 76, 105),
            (FIELD_LEFT, FIELD_TOP, FIELD_RIGHT - FIELD_LEFT, FIELD_BOTTOM - FIELD_TOP),
            width=2,
            border_radius=16,
        )

    def draw_header(self):
        self.text("PÁLFY PYTHON CHALLENGE", self.font_h1, CYAN, 35, 22)
        self.text("TE IRÁNYÍTOD A JÁTÉKOT!", self.font_small, MUTED, 38, 63)
        self.text(f"Játékos: {self.player_name}", self.font_small, WHITE, 470, 28)
        self.text(f"Sebesség: {PLAYER_SPEED}", self.font_small, YELLOW, 470, 55)
        remaining = max(0, int(math.ceil(self.time_left)))
        self.text(f"IDŐ  {remaining:02d}", self.font_h1, WHITE, WIDTH - 38, 25, align="right")

    def draw_hud(self):
        self.text(f"PONT: {self.score}", self.font, GREEN, 55, 125)
        self.text(f"ALMA: {self.apples}", self.font, RED, 220, 125)
        if self.message_timer > 0:
            color = GREEN if self.message.startswith("+") else RED if self.message.startswith("-") else MUTED
            self.text(self.message, self.font_small, color, WIDTH // 2, 139, align="center")
        self.text(
            "Mozgás: NYILAK / WASD     F2: kód     R: újrakezdés     ESC: kilépés",
            self.font_tiny,
            MUTED,
            WIDTH // 2,
            HEIGHT - 22,
            align="center",
        )

    def draw_game(self):
        self.draw_background()
        self.draw_header()
        self.draw_hud()
        self.apple.draw(self.screen)
        for meteor in self.meteors:
            meteor.draw(self.screen)
        self.player.draw(self.screen)

    def draw_name_screen(self):
        self.screen.fill(BG)
        self.text("PÁLFY PYTHON CHALLENGE", self.font_big, CYAN, WIDTH // 2, 115, align="center")
        self.text("„TE IRÁNYÍTOD A JÁTÉKOT!”", self.font_h1, WHITE, WIDTH // 2, 170, align="center")
        self.text("1. Mozgasd a robotot.", self.font, MUTED, WIDTH // 2, 240, align="center")
        self.text("2. Gyűjts almákat.", self.font, MUTED, WIDTH // 2, 276, align="center")
        self.text("3. Kerüld a meteorokat.", self.font, MUTED, WIDTH // 2, 312, align="center")
        self.text("Add meg a neved:", self.font, WHITE, WIDTH // 2, 385, align="center")

        box = pygame.Rect(WIDTH // 2 - 230, 425, 460, 58)
        pygame.draw.rect(self.screen, PANEL_2, box, border_radius=10)
        pygame.draw.rect(self.screen, CYAN, box, width=2, border_radius=10)
        shown = self.input_text + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else "")
        self.text(shown, self.font, GREEN, WIDTH // 2, 454, align="center")

        self.text("ENTER = JÁTÉK INDÍTÁSA", self.font_small, YELLOW, WIDTH // 2, 520, align="center")

        speed_box = pygame.Rect(WIDTH // 2 - 300, 565, 600, 70)
        pygame.draw.rect(self.screen, PANEL, speed_box, border_radius=12)
        pygame.draw.rect(self.screen, (42, 72, 100), speed_box, width=1, border_radius=12)
        self.text(
            f"A jelenlegi érték: PLAYER_SPEED = {PLAYER_SPEED}",
            self.font_small,
            CYAN,
            WIDTH // 2,
            584,
            align="center",
        )
        self.text(
            "A játék után írd át a config.py-ban 15-re!",
            self.font_tiny,
            MUTED,
            WIDTH // 2,
            613,
            align="center",
        )

    def draw_code_overlay(self):
        self.draw_game()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        self.screen.blit(overlay, (0, 0))

        card = pygame.Rect(135, 100, WIDTH - 270, HEIGHT - 180)
        pygame.draw.rect(self.screen, (5, 14, 24), card, border_radius=18)
        pygame.draw.rect(self.screen, CYAN, card, width=2, border_radius=18)

        self.text("MOST TE VAGY A PROGRAMOZÓ!", self.font_h1, CYAN, WIDTH // 2, 145, align="center")
        self.text("Nyisd meg a config.py fájlt, és keresd meg ezt a sort:", self.font_small, WHITE, WIDTH // 2, 205, align="center")

        code_box = pygame.Rect(215, 245, WIDTH - 430, 100)
        pygame.draw.rect(self.screen, (0, 0, 0), code_box, border_radius=10)
        pygame.draw.rect(self.screen, (48, 82, 108), code_box, width=1, border_radius=10)
        self.text(f"PLAYER_SPEED = {PLAYER_SPEED}", self.font_h1, GREEN, WIDTH // 2, 280, align="center")

        self.text("Írd át például erre:", self.font_small, WHITE, WIDTH // 2, 385, align="center")
        self.text("PLAYER_SPEED = 15", self.font_h1, YELLOW, WIDTH // 2, 430, align="center")
        self.text("Mentsd el → indítsd újra → érezd a különbséget!", self.font_small, MUTED, WIDTH // 2, 495, align="center")
        self.text("F2 / ENTER / SPACE = vissza a játékhoz", self.font_tiny, CYAN, WIDTH // 2, 555, align="center")

    def draw_game_over(self):
        self.screen.fill(BG)
        self.text("MENET VÉGE", self.font_big, CYAN, WIDTH // 2, 88, align="center")
        self.text(self.player_name, self.font_h1, WHITE, WIDTH // 2, 150, align="center")
        self.text(f"{self.score}", self.font_big, GREEN, WIDTH // 2, 225, align="center")
        self.text("PONT", self.font_small, MUTED, WIDTH // 2, 272, align="center")
        self.text(f"Begyűjtött almák: {self.apples}", self.font, WHITE, WIDTH // 2, 320, align="center")

        self.text("TOP 5", self.font_h1, YELLOW, WIDTH // 2, 382, align="center")
        y = 425
        if not self.scores:
            self.text("Még nincs eredmény.", self.font_small, MUTED, WIDTH // 2, y, align="center")
        else:
            for i, item in enumerate(self.scores, start=1):
                color = YELLOW if i == 1 else WHITE
                self.text(
                    f"{i}.  {item['name']:<18}  {item['score']:>4} pont",
                    self.font_small,
                    color,
                    WIDTH // 2,
                    y,
                    align="center",
                )
                y += 31

        self.text("R = új menet    N = új játékos    ESC = kilépés", self.font_small, CYAN, WIDTH // 2, 615, align="center")

    def draw(self):
        if self.state == "name":
            self.draw_name_screen()
        elif self.state == "play":
            self.draw_game()
        elif self.state == "code":
            self.draw_code_overlay()
        elif self.state == "over":
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
