import pygame
import random
import sys
import time
import os

pygame.init()
pygame.mixer.init()

# --- Constants ---
WIDTH, HEIGHT = 1000, 600
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (180,180,180)
BLUE = (70,130,255)
YELLOW = (255,215,0)
GREEN = (0,200,0)
RED = (255,0,0)

FONT = pygame.font.SysFont("Segoe UI Emoji",25)
BIG_FONT = pygame.font.SysFont("Segoe UI Emoji",50)
SMALL_FONT = pygame.font.SysFont("Segoe UI Emoji", 20)

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Stacking Plates Game")
clock = pygame.time.Clock()

# --- Game States ---
current_screen = "name_prompt"
selected_level = 0
start_time = elapsed_time = score = 0
max_time_per_level = 300
CONTENT_RECT = pygame.Rect(80,60,WIDTH-160,HEIGHT-120)
STACK_COUNT = 3
PLATE_HEIGHT, STACK_WIDTH = 23, 133
move_history = []

# --- Name Prompt Input State ---
name_input_box = pygame.Rect(CONTENT_RECT.centerx - 150, CONTENT_RECT.centery - 30, 300, 50)
input_active = True
input_text = ""
input_error = ""

# --- Player and Leaderboard ---
player_name = ""
leaderboard_data = []

# --- Audio ---
try:
    pygame.mixer.music.load('background.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    sound_move = pygame.mixer.Sound('move.wav'); sound_move.set_volume(0.5)
    sound_win = pygame.mixer.Sound('win.wav'); sound_win.set_volume(0.7)
except pygame.error:
    sound_move = sound_win = None

# --- Level Config ---
base_total_plates = 4
plates_increment = 2
base_stacks = 3
MAX_LEVELS = 5
completed_levels = [True] + [False]*(MAX_LEVELS-1)

# --- Button Class ---
class Button:
    def __init__(self, rect, text, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.enabled = enabled

    def draw(self, s):
        clr = BLUE if self.enabled else GRAY
        pygame.draw.rect(s, clr, self.rect, border_radius=8)
        pygame.draw.rect(s, BLACK, self.rect, 2, border_radius=8)
        t = FONT.render(self.text, True, BLACK)
        s.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.centery - t.get_height()//2))

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

# --- Buttons ---
home_buttons = [
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+95, 200, 50), "Play"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+165, 200, 50), "Levels"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+235, 200, 50), "Help"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+305, 200, 50), "Quit"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+375, 200, 50), "Leaderboard")
]

level_buttons = [Button((CONTENT_RECT.left+50+(i%3)*220, CONTENT_RECT.top+70+(i//3)*100, 180, 60),
                        f"Level {i+1}", enabled=completed_levels[i]) for i in range(MAX_LEVELS)]

back_button = Button((10,10,140,40), "← Back")
win_back_button = Button((CONTENT_RECT.centerx-220, CONTENT_RECT.bottom-90, 180, 50), "Back to Home")
win_next_button = Button((CONTENT_RECT.centerx+40, CONTENT_RECT.bottom-90, 180, 50), "Next Level")
timeout_retry_button = Button((CONTENT_RECT.centerx-220, CONTENT_RECT.bottom-90, 180, 50), "Retry")
timeout_exit_button = Button((CONTENT_RECT.centerx+40, CONTENT_RECT.bottom-90, 180, 50), "Exit")
clear_lb_button = Button((CONTENT_RECT.centerx - 120, CONTENT_RECT.bottom - 100, 240, 60), "Clear Leaderboard")

# --- Utility Functions ---
def draw_text_center(txt, font, color, y):
    t = font.render(txt, True, color)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))

def draw_box():
    pygame.draw.rect(screen, (230,230,250), CONTENT_RECT, border_radius=12)
    pygame.draw.rect(screen, BLACK, CONTENT_RECT, 3, border_radius=12)

def draw_gradient(s, top, bottom):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0]*(1-t)+bottom[0]*t)
        g = int(top[1]*(1-t)+bottom[1]*t)
        b = int(top[2]*(1-t)+bottom[2]*t)
        pygame.draw.line(s, (r,g,b), (0,y), (WIDTH,y))

def init_game(level):
    global stacks, total_plates, STACK_COUNT, plates, selected_stack
    global start_time, elapsed_time, score, move_history, max_time_per_level

    total_plates = base_total_plates + plates_increment * level
    STACK_COUNT = base_stacks + (level // 2)
    plates = list(range(1, total_plates + 1))
    random.shuffle(plates)
    stacks = [[] for _ in range(STACK_COUNT)]
    sel = 0
    for plate in plates:
        stacks[sel].append(plate)
        sel = (sel + 1) % (STACK_COUNT - 1)

    selected_stack = None
    start_time = time.time()
    elapsed_time = score = 0
    move_history = []

    # Set time based on level (level 0 = 60s, level 1 = 120s, etc.)
    max_time_per_level = 60 * (level + 1)

def is_valid_move(f, t):
    if not stacks[f]: return False
    return not stacks[t] or stacks[f][-1] > stacks[t][-1]

def move_plate(f, t):
    global score
    if is_valid_move(f, t):
        plate = stacks[f].pop()
        stacks[t].append(plate)
        move_history.append((f, t, plate))
        score += 1
        if sound_move: sound_move.play()
        return True
    return False

def undo_move():
    global score
    if move_history:
        f, t, plate = move_history.pop()
        if stacks[t] and stacks[t][-1] == plate:
            stacks[t].pop()
            stacks[f].append(plate)
            score = max(0, score - 1)

def is_win():
    return any(len(s)==total_plates and all(s[i]<s[i+1] for i in range(len(s)-1)) for s in stacks)

def get_clicked_stack(pos):
    x, y = pos
    if not CONTENT_RECT.collidepoint(pos): return None
    idx = (x - CONTENT_RECT.left) // (CONTENT_RECT.width // STACK_COUNT)
    return idx if 0 <= idx < STACK_COUNT else None

def save_leaderboard():
    with open("leaderboard.txt", "w") as f:
        for name, level, moves, t in leaderboard_data:
            f.write(f"{name},{level},{moves},{t}\n")

def load_leaderboard():
    global leaderboard_data
    if os.path.exists("leaderboard.txt"):
        with open("leaderboard.txt", "r") as f:
            leaderboard_data = [line.strip().split(",") for line in f.readlines()]
            leaderboard_data = [(n, int(lv), int(mv), int(t)) for n, lv, mv, t in leaderboard_data]

def add_to_leaderboard(name, level, moves, t):
    leaderboard_data.append((name, level, moves, t))
    leaderboard_data.sort(key=lambda x: (x[1], x[2], x[3]))
    save_leaderboard()

def draw_stacks():
    y_base = CONTENT_RECT.bottom - 40
    width_each = CONTENT_RECT.width // STACK_COUNT
    for i in range(STACK_COUNT):
        x = CONTENT_RECT.left + i * width_each + width_each // 2
        rc = GREEN if is_win() and len(stacks[i]) == total_plates else GRAY
        pygame.draw.rect(screen, rc, (x - STACK_WIDTH // 2, y_base - 300, STACK_WIDTH, 300), 5 if rc == GREEN else 3)
        y = y_base
        for p in reversed(stacks[i]):
            w = 40 + p * 8
            rect = pygame.Rect(x - w // 2, y - PLATE_HEIGHT, w, PLATE_HEIGHT)
            clr = YELLOW if i == selected_stack else BLUE
            pygame.draw.rect(screen, clr, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            t = FONT.render(str(p), True, BLACK)
            screen.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))
            y -= PLATE_HEIGHT + 2

def draw_screens():
    global elapsed_time
    bg_colors = {
        "home": ((10, 100, 150), (60, 180, 200)),
        "levels": ((40, 20, 60), (130, 50, 150)),
        "help": ((60, 60, 60), (180, 180, 180)),
        "game": ((30, 30, 60), (80, 120, 180)),
        "win": ((0, 70, 0), (80, 180, 80)),
        "timeout": ((100, 0, 0), (180, 50, 50)),
        "name_prompt": ((40, 40, 80), (100, 100, 180)),
        "leaderboard": ((30, 30, 30), (90, 90, 90))
    }
    draw_gradient(screen, *bg_colors[current_screen])
    draw_box()

    if current_screen == "name_prompt":
        draw_text_center("Enter Your Name", BIG_FONT, BLACK, CONTENT_RECT.top + 40)
        pygame.draw.rect(screen, WHITE, name_input_box, 0, border_radius=10)
        pygame.draw.rect(screen, BLACK, name_input_box, 2, border_radius=10)
        name_surface = FONT.render(input_text, True, BLACK)
        screen.blit(name_surface, (name_input_box.x + 10, name_input_box.y + 10))
        if input_error:
            err_surface = SMALL_FONT.render(input_error, True, RED)
            screen.blit(err_surface, (CONTENT_RECT.centerx - err_surface.get_width()//2, name_input_box.bottom + 10))
        draw_text_center("Press Enter to Continue", SMALL_FONT, BLACK, CONTENT_RECT.bottom - 60)

    elif current_screen == "home":
        draw_text_center("Stacking Plates Game", BIG_FONT, BLACK, CONTENT_RECT.top + 20)
        for b in home_buttons: b.draw(screen)

    elif current_screen == "levels":
        draw_text_center("Select Level", BIG_FONT, WHITE, CONTENT_RECT.top + 20)
        for i, b in enumerate(level_buttons):
            b.enabled = completed_levels[i]
            b.draw(screen)
            if not b.enabled:
                l = FONT.render("\U0001F512", True, RED)
                screen.blit(l, (b.rect.right - 30, b.rect.top + 10))
        back_button.draw(screen)

    elif current_screen == "help":
        draw_text_center("Help", BIG_FONT, BLACK, CONTENT_RECT.top + 20)
        lines = [
            "Objective: Move ALL plates (in increasing order) onto any stack.",
            "- Move only one top plate at a time.",
            "- Can't place larger over smaller.",
            "- Each level adds 2 new plates.",
            "- Every 2 levels add another stack.",
            "- Click stacks to move.",
            "- Use ← Back to go back.",
            "- Press Z to undo last move.",
            "- You have 5 minutes per level."
        ]
        for i, ln in enumerate(lines):
            screen.blit(FONT.render(ln, True, BLACK), (CONTENT_RECT.left + 20, CONTENT_RECT.top + 80 + i * 30))
        back_button.draw(screen)

    elif current_screen == "game":
        draw_stacks()
        elapsed_time = int(time.time() - start_time)
        tleft = max(0, max_time_per_level - elapsed_time)
        screen.blit(FONT.render(f"Time Left: {tleft}s", True, BLACK), (CONTENT_RECT.left + 10, CONTENT_RECT.top + 10))
        sb = pygame.Rect(CONTENT_RECT.right - 160, CONTENT_RECT.top + 5, 140, 40)
        pygame.draw.rect(screen, (255, 255, 200), sb, border_radius=6)
        pygame.draw.rect(screen, BLACK, sb, 2, border_radius=6)
        screen.blit(FONT.render(f"Moves: {score}", True, BLACK), (sb.left + 10, sb.centery - 10))
        back_button.draw(screen)

    elif current_screen == "win":
        draw_text_center("\U0001F389 CONGRATULATIONS!", BIG_FONT, YELLOW, CONTENT_RECT.top + 50)
        draw_text_center(f"Level {selected_level+1} Completed", FONT, RED, CONTENT_RECT.top + 140)
        draw_text_center(f"Moves: {score} | Time: {elapsed_time}s", FONT, RED, CONTENT_RECT.top + 200)
        win_back_button.draw(screen)
        win_next_button.enabled = (selected_level+1 < MAX_LEVELS and completed_levels[selected_level+1])
        win_next_button.draw(screen)

    elif current_screen == "timeout":
        draw_text_center("⏰ TIME'S UP!", BIG_FONT, BLACK, CONTENT_RECT.top + 80)
        draw_text_center(f"Level {selected_level+1} failed", FONT, BLACK, CONTENT_RECT.top + 160)
        draw_text_center(f"Moves: {score} | Time: {elapsed_time}s", FONT, BLACK, CONTENT_RECT.top + 220)
        timeout_retry_button.draw(screen)
        timeout_exit_button.draw(screen)

    elif current_screen == "leaderboard":
        draw_text_center("Leaderboard", BIG_FONT, YELLOW, CONTENT_RECT.top + 30)
        headers = ["Name", "Level", "Moves", "Time"]
        for i, h in enumerate(headers):
            screen.blit(FONT.render(h, True, BLACK), (CONTENT_RECT.left + 80 + i * 180, CONTENT_RECT.top + 80))
        for i, (n, lv, mv, t) in enumerate(leaderboard_data[:10]):
            for j, val in enumerate([n, str(lv), str(mv), str(t)]):
                screen.blit(SMALL_FONT.render(val, True, RED), (CONTENT_RECT.left + 80 + j*180, CONTENT_RECT.top + 120 + i*30))
        back_button.draw(screen)
        clear_lb_button.draw(screen)

# --- Main loop ---
running = True
selected_stack = None

while running:
    clock.tick(30)
    pos = pygame.mouse.get_pos()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if current_screen == "name_prompt":
            if e.type == pygame.KEYDOWN:
                if input_active:
                    if e.key == pygame.K_RETURN:
                        if len(input_text.strip()) >= 2:
                            player_name = input_text.strip()
                            load_leaderboard()
                            current_screen = "home"
                        else:
                            input_error = "Name must be at least 2 characters"
                    elif e.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 20:
                            input_text += e.unicode

        elif e.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == "home":
                for b in home_buttons:
                    if b.is_clicked(pos):
                        if b.text == "Play":
                            selected_level = 0
                            init_game(0)
                            current_screen = "game"
                        elif b.text == "Levels":
                            current_screen = "levels"
                        elif b.text == "Help":
                            current_screen = "help"
                        elif b.text == "Quit":
                            running = False
                        elif b.text == "Leaderboard":
                            current_screen = "leaderboard"

            elif current_screen == "levels":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                else:
                    for i, b in enumerate(level_buttons):
                        if b.is_clicked(pos) and b.enabled:
                            selected_level = i
                            init_game(i)
                            current_screen = "game"

            elif current_screen == "help" and back_button.is_clicked(pos):
                current_screen = "home"

            elif current_screen == "game":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                else:
                    cs = get_clicked_stack(pos)
                    if cs is not None:
                        if selected_stack is None and stacks[cs]:
                            selected_stack = cs
                        elif selected_stack is not None:
                            move_plate(selected_stack, cs)
                            selected_stack = None
                if is_win():
                    completed_levels[selected_level] = True
                    if selected_level + 1 < MAX_LEVELS:
                        completed_levels[selected_level + 1] = True
                    if sound_win: sound_win.play()
                    if not any(n == player_name and lv == selected_level+1 and mv == score for n, lv, mv, t in leaderboard_data):
                        add_to_leaderboard(player_name, selected_level + 1, score, elapsed_time)
                    current_screen = "win"

            elif current_screen == "win":
                if win_back_button.is_clicked(pos):
                    current_screen = "home"
                elif win_next_button.is_clicked(pos) and win_next_button.enabled:
                    selected_level += 1
                    init_game(selected_level)
                    current_screen = "game"

            elif current_screen == "timeout":
                if timeout_retry_button.is_clicked(pos):
                    init_game(selected_level)
                    current_screen = "game"
                elif timeout_exit_button.is_clicked(pos):
                    current_screen = "home"

            elif current_screen == "leaderboard":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                elif clear_lb_button.is_clicked(pos):
                    leaderboard_data.clear()
                    save_leaderboard()

        elif e.type == pygame.KEYDOWN and current_screen == "game" and e.key == pygame.K_z:
            undo_move()

    if current_screen == "game":
        elapsed_time = int(time.time() - start_time)
        if elapsed_time >= max_time_per_level:
            current_screen = "timeout"

    draw_screens()
    pygame.display.flip()

pygame.quit()
sys.exit()