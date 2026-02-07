import pygame
import random
import sys
import time
import os
import hashlib
from datetime import datetime, date

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

# --- Combo System ---
combo_count = 0
last_move_time = 0
combo_timeout = 3.0  # seconds
max_combo_reached = 0

# --- Achievements ---
achievements = {
    "first_win": {"name": "First Victory", "desc": "Complete your first level", "unlocked": False, "icon": "🏆"},
    "speed_demon": {"name": "Speed Demon", "desc": "Complete a level in under 30 seconds", "unlocked": False, "icon": "⚡"},
    "perfectionist": {"name": "Perfectionist", "desc": "Get ⭐⭐⭐ on any level", "unlocked": False, "icon": "✨"},
    "combo_master": {"name": "Combo Master", "desc": "Reach a 10x combo", "unlocked": False, "icon": "🔥"},
    "no_undo": {"name": "No Regrets", "desc": "Complete a level without undo", "unlocked": False, "icon": "💪"},
    "all_levels": {"name": "Champion", "desc": "Complete all 5 levels", "unlocked": False, "icon": "👑"},
    "fast_fingers": {"name": "Fast Fingers", "desc": "Make 5 moves in 10 seconds", "unlocked": False, "icon": "👆"},
    "patient": {"name": "Patient Player", "desc": "Complete a level with time remaining", "unlocked": False, "icon": "🧘"},
}
used_undo_this_level = False
moves_in_last_10_sec = []

# --- Plate Themes ---
current_theme = "classic"
unlocked_themes = ["classic"]
themes = {
    "classic": {"name": "Classic", "colors": [(70,130,255), (100,150,255), (130,170,255)], "icon": "🔵"},
    "fire": {"name": "Fire", "colors": [(255,69,0), (255,140,0), (255,215,0)], "icon": "🔥"},
    "nature": {"name": "Nature", "colors": [(34,139,34), (50,205,50), (144,238,144)], "icon": "🌿"},
    "ocean": {"name": "Ocean", "colors": [(0,105,148), (0,191,255), (135,206,250)], "icon": "🌊"},
    "sunset": {"name": "Sunset", "colors": [(255,99,71), (255,165,0), (255,192,203)], "icon": "🌅"},
    "neon": {"name": "Neon", "colors": [(255,0,255), (0,255,255), (255,255,0)], "icon": "💫"},
}

# --- Daily Challenge ---
daily_challenge_active = False
daily_challenge_seed = 0
daily_challenge_completed_today = False
daily_challenge_best_score = None
daily_challenge_leaderboard = []

# --- Name Prompt Input State ---
name_input_box = pygame.Rect(CONTENT_RECT.centerx - 150, CONTENT_RECT.centery - 30, 300, 50)
input_active = True
input_text = ""
input_error = ""

# --- Player and Leaderboard ---
player_name = ""
leaderboard_data = []

# --- Audio ---
music_enabled = True
sound_enabled = True
try:
    pygame.mixer.music.load('background.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    sound_move = pygame.mixer.Sound('move.wav'); sound_move.set_volume(0.5)
    sound_win = pygame.mixer.Sound('win.wav'); sound_win.set_volume(0.7)
except pygame.error:
    sound_move = sound_win = None

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled

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
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+60, 200, 50), "Play"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+120, 200, 50), "Daily Challenge"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+180, 200, 50), "Levels"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+240, 200, 50), "Achievements"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+300, 200, 50), "Themes"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+360, 200, 50), "Settings"),
    Button((CONTENT_RECT.centerx-100, CONTENT_RECT.top+420, 200, 50), "Quit")
]

level_buttons = [Button((CONTENT_RECT.left+50+(i%3)*220, CONTENT_RECT.top+70+(i//3)*100, 180, 60),
                        f"Level {i+1}", enabled=completed_levels[i]) for i in range(MAX_LEVELS)]

back_button = Button((10,10,140,40), "← Back")
win_back_button = Button((CONTENT_RECT.centerx-220, CONTENT_RECT.bottom-90, 180, 50), "Back to Home")
win_next_button = Button((CONTENT_RECT.centerx+40, CONTENT_RECT.bottom-90, 180, 50), "Next Level")
timeout_retry_button = Button((CONTENT_RECT.centerx-220, CONTENT_RECT.bottom-90, 180, 50), "Retry")
timeout_exit_button = Button((CONTENT_RECT.centerx+40, CONTENT_RECT.bottom-90, 180, 50), "Exit")
clear_lb_button = Button((CONTENT_RECT.centerx - 120, CONTENT_RECT.bottom - 100, 240, 60), "Clear Leaderboard")

# Settings buttons
music_toggle_button = Button((CONTENT_RECT.centerx - 150, CONTENT_RECT.centery - 80, 300, 50), "Music: ON")
sound_toggle_button = Button((CONTENT_RECT.centerx - 150, CONTENT_RECT.centery - 10, 300, 50), "Sound: ON")
hint_button = Button((CONTENT_RECT.right - 160, CONTENT_RECT.bottom - 60, 140, 40), "Hint")

# Theme buttons (3x2 grid)
theme_buttons = []
for i, (theme_id, theme_data) in enumerate(themes.items()):
    x = CONTENT_RECT.left + 60 + (i % 3) * 240
    y = CONTENT_RECT.top + 120 + (i // 3) * 100
    theme_buttons.append((Button((x, y, 200, 70), f"{theme_data['icon']} {theme_data['name']}"), theme_id))

# Daily challenge buttons
daily_play_button = Button((CONTENT_RECT.centerx - 100, CONTENT_RECT.centery + 40, 200, 50), "Play Today's Challenge")
daily_leaderboard_button = Button((CONTENT_RECT.centerx - 100, CONTENT_RECT.centery + 100, 200, 50), "View Leaderboard")

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
    global combo_count, last_move_time, max_combo_reached, used_undo_this_level, moves_in_last_10_sec
    global daily_challenge_active, daily_challenge_seed

    if daily_challenge_active:
        # Daily challenge: fixed configuration based on today's date
        total_plates = 6
        STACK_COUNT = 3
        random.seed(daily_challenge_seed)
        plates = list(range(1, total_plates + 1))
        random.shuffle(plates)
        max_time_per_level = 180  # 3 minutes for daily challenge
    else:
        # Normal game
        total_plates = base_total_plates + plates_increment * level
        STACK_COUNT = base_stacks + (level // 2)
        plates = list(range(1, total_plates + 1))
        random.shuffle(plates)
        max_time_per_level = 60 * (level + 1)
    
    stacks = [[] for _ in range(STACK_COUNT)]
    sel = 0
    for plate in plates:
        stacks[sel].append(plate)
        sel = (sel + 1) % (STACK_COUNT - 1)

    selected_stack = None
    start_time = time.time()
    elapsed_time = score = 0
    move_history = []
    combo_count = 0
    last_move_time = time.time()
    max_combo_reached = 0
    used_undo_this_level = False
    moves_in_last_10_sec = []

def is_valid_move(f, t):
    if not stacks[f]: return False
    return not stacks[t] or stacks[f][-1] > stacks[t][-1]

def move_plate(f, t):
    global score, combo_count, last_move_time, max_combo_reached, moves_in_last_10_sec
    if is_valid_move(f, t):
        plate = stacks[f].pop()
        stacks[t].append(plate)
        move_history.append((f, t, plate))
        score += 1
        
        # Combo system
        current_time = time.time()
        if current_time - last_move_time <= combo_timeout:
            combo_count += 1
        else:
            combo_count = 1
        last_move_time = current_time
        max_combo_reached = max(max_combo_reached, combo_count)
        
        # Track moves for fast_fingers achievement
        moves_in_last_10_sec.append(current_time)
        moves_in_last_10_sec = [t for t in moves_in_last_10_sec if current_time - t <= 10]
        
        if sound_move and sound_enabled: sound_move.play()
        return True
    else:
        # Invalid move breaks combo
        combo_count = 0
    return False

def undo_move():
    global score, combo_count, used_undo_this_level
    if move_history:
        f, t, plate = move_history.pop()
        if stacks[t] and stacks[t][-1] == plate:
            stacks[t].pop()
            stacks[f].append(plate)
            score = max(0, score - 1)
            combo_count = 0  # Undo breaks combo
            used_undo_this_level = True

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

def get_hint():
    """Suggest a valid move to help the player"""
    # Find the smallest plate that can be moved
    for i in range(STACK_COUNT):
        if not stacks[i]:
            continue
        plate = stacks[i][-1]
        # Try to find a valid destination
        for j in range(STACK_COUNT):
            if i != j and is_valid_move(i, j):
                return (i, j)
    return None

def check_achievements():
    """Check and unlock achievements"""
    global achievements, unlocked_themes
    newly_unlocked = []
    
    # First win
    if not achievements["first_win"]["unlocked"] and is_win():
        achievements["first_win"]["unlocked"] = True
        newly_unlocked.append("first_win")
    
    # Speed demon (< 30 seconds)
    if not achievements["speed_demon"]["unlocked"] and is_win() and elapsed_time < 30:
        achievements["speed_demon"]["unlocked"] = True
        newly_unlocked.append("speed_demon")
        if "fire" not in unlocked_themes:
            unlocked_themes.append("fire")
    
    # Perfectionist (⭐⭐⭐)
    optimal_moves = total_plates - 1
    if not achievements["perfectionist"]["unlocked"] and is_win() and score <= optimal_moves + 5:
        achievements["perfectionist"]["unlocked"] = True
        newly_unlocked.append("perfectionist")
        if "neon" not in unlocked_themes:
            unlocked_themes.append("neon")
    
    # Combo master (10x combo)
    if not achievements["combo_master"]["unlocked"] and max_combo_reached >= 10:
        achievements["combo_master"]["unlocked"] = True
        newly_unlocked.append("combo_master")
        if "sunset" not in unlocked_themes:
            unlocked_themes.append("sunset")
    
    # No undo
    if not achievements["no_undo"]["unlocked"] and is_win() and not used_undo_this_level:
        achievements["no_undo"]["unlocked"] = True
        newly_unlocked.append("no_undo")
        if "nature" not in unlocked_themes:
            unlocked_themes.append("nature")
    
    # All levels
    if not achievements["all_levels"]["unlocked"] and all(completed_levels):
        achievements["all_levels"]["unlocked"] = True
        newly_unlocked.append("all_levels")
        if "ocean" not in unlocked_themes:
            unlocked_themes.append("ocean")
    
    # Fast fingers (5 moves in 10 seconds)
    if not achievements["fast_fingers"]["unlocked"] and len(moves_in_last_10_sec) >= 5:
        achievements["fast_fingers"]["unlocked"] = True
        newly_unlocked.append("fast_fingers")
    
    # Patient (complete with time remaining)
    if not achievements["patient"]["unlocked"] and is_win() and elapsed_time < max_time_per_level - 30:
        achievements["patient"]["unlocked"] = True
        newly_unlocked.append("patient")
    
    return newly_unlocked

def get_combo_color():
    """Get color based on combo level"""
    if combo_count >= 15:
        return (255, 0, 0)  # Red - ON FIRE!
    elif combo_count >= 10:
        return (255, 140, 0)  # Orange
    elif combo_count >= 5:
        return (255, 215, 0)  # Yellow
    else:
        return WHITE

def get_combo_multiplier():
    """Get score multiplier based on combo"""
    if combo_count >= 15:
        return 5.0
    elif combo_count >= 10:
        return 3.0
    elif combo_count >= 5:
        return 2.0
    else:
        return 1.0

def get_daily_seed():
    """Generate seed based on today's date"""
    today = date.today()
    date_string = today.strftime("%Y-%m-%d")
    # Create consistent seed from date
    return int(hashlib.md5(date_string.encode()).hexdigest()[:8], 16)

def load_daily_challenge_data():
    """Load daily challenge completion status and leaderboard"""
    global daily_challenge_completed_today, daily_challenge_best_score, daily_challenge_leaderboard
    
    today = date.today().strftime("%Y-%m-%d")
    
    if os.path.exists("daily_challenge.txt"):
        with open("daily_challenge.txt", "r") as f:
            lines = f.readlines()
            if lines:
                saved_date = lines[0].strip()
                if saved_date == today:
                    # Today's challenge data exists
                    if len(lines) > 1:
                        daily_challenge_completed_today = lines[1].strip() == "completed"
                    if len(lines) > 2 and lines[2].strip():
                        parts = lines[2].strip().split(",")
                        daily_challenge_best_score = {
                            "moves": int(parts[0]),
                            "time": int(parts[1]),
                            "combo": int(parts[2])
                        }
                    # Load leaderboard
                    if len(lines) > 3:
                        daily_challenge_leaderboard = []
                        for line in lines[3:]:
                            if line.strip():
                                parts = line.strip().split(",")
                                daily_challenge_leaderboard.append({
                                    "name": parts[0],
                                    "moves": int(parts[1]),
                                    "time": int(parts[2]),
                                    "combo": int(parts[3])
                                })
                else:
                    # New day, reset
                    daily_challenge_completed_today = False
                    daily_challenge_best_score = None
                    daily_challenge_leaderboard = []

def save_daily_challenge_data():
    """Save daily challenge completion and leaderboard"""
    today = date.today().strftime("%Y-%m-%d")
    
    with open("daily_challenge.txt", "w") as f:
        f.write(f"{today}\n")
        f.write(f"{'completed' if daily_challenge_completed_today else 'not_completed'}\n")
        
        if daily_challenge_best_score:
            f.write(f"{daily_challenge_best_score['moves']},{daily_challenge_best_score['time']},{daily_challenge_best_score['combo']}\n")
        else:
            f.write("\n")
        
        # Save leaderboard
        for entry in daily_challenge_leaderboard:
            f.write(f"{entry['name']},{entry['moves']},{entry['time']},{entry['combo']}\n")

def submit_daily_challenge_score(name, moves, time_taken, combo):
    """Submit score to daily challenge leaderboard"""
    global daily_challenge_completed_today, daily_challenge_best_score, daily_challenge_leaderboard
    
    daily_challenge_completed_today = True
    daily_challenge_best_score = {
        "moves": moves,
        "time": time_taken,
        "combo": combo
    }
    
    # Add to leaderboard
    daily_challenge_leaderboard.append({
        "name": name,
        "moves": moves,
        "time": time_taken,
        "combo": combo
    })
    
    # Sort by moves, then time, then combo (descending)
    daily_challenge_leaderboard.sort(key=lambda x: (x["moves"], x["time"], -x["combo"]))
    
    # Keep top 10
    daily_challenge_leaderboard = daily_challenge_leaderboard[:10]
    
    save_daily_challenge_data()

def draw_stacks():
    y_base = CONTENT_RECT.bottom - 40
    width_each = CONTENT_RECT.width // STACK_COUNT
    theme_colors = themes[current_theme]["colors"]
    
    for i in range(STACK_COUNT):
        x = CONTENT_RECT.left + i * width_each + width_each // 2
        rc = GREEN if is_win() and len(stacks[i]) == total_plates else GRAY
        pygame.draw.rect(screen, rc, (x - STACK_WIDTH // 2, y_base - 300, STACK_WIDTH, 300), 5 if rc == GREEN else 3)
        
        # Draw stack number
        stack_label = SMALL_FONT.render(f"Stack {i+1}", True, BLACK)
        screen.blit(stack_label, (x - stack_label.get_width()//2, y_base + 10))
        
        y = y_base
        for p in reversed(stacks[i]):
            w = 40 + p * 8
            rect = pygame.Rect(x - w // 2, y - PLATE_HEIGHT, w, PLATE_HEIGHT)
            
            # Use theme colors
            if i == selected_stack:
                clr = YELLOW
            else:
                color_index = (p - 1) % len(theme_colors)
                clr = theme_colors[color_index]
            
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
        "leaderboard": ((30, 30, 30), (90, 90, 90)),
        "settings": ((50, 50, 100), (120, 120, 180)),
        "achievements": ((80, 40, 120), (140, 80, 180)),
        "themes": ((20, 80, 100), (60, 140, 160)),
        "daily_challenge": ((100, 50, 0), (180, 120, 40)),
        "daily_leaderboard": ((40, 40, 40), (100, 100, 100))
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
        draw_text_center(f"Welcome, {player_name}!", FONT, BLACK, CONTENT_RECT.top + 70)
        for b in home_buttons: b.draw(screen)

    elif current_screen == "daily_challenge":
        draw_text_center("📅 Daily Challenge", BIG_FONT, YELLOW, CONTENT_RECT.top + 30)
        
        today = date.today().strftime("%B %d, %Y")
        draw_text_center(today, FONT, WHITE, CONTENT_RECT.top + 90)
        
        # Challenge info
        draw_text_center("Today's Puzzle: 6 plates, 3 stacks, 3 minutes", SMALL_FONT, WHITE, CONTENT_RECT.top + 130)
        draw_text_center("Everyone gets the same puzzle!", SMALL_FONT, GREEN, CONTENT_RECT.top + 160)
        
        # Status
        if daily_challenge_completed_today:
            draw_text_center("✅ Completed Today!", FONT, GREEN, CONTENT_RECT.centery - 40)
            if daily_challenge_best_score:
                score_text = f"Your Score: {daily_challenge_best_score['moves']} moves, {daily_challenge_best_score['time']}s, {daily_challenge_best_score['combo']}x combo"
                draw_text_center(score_text, SMALL_FONT, YELLOW, CONTENT_RECT.centery - 10)
            draw_text_center("You can play again to improve!", SMALL_FONT, WHITE, CONTENT_RECT.centery + 20)
        else:
            draw_text_center("⏳ Not completed yet", FONT, RED, CONTENT_RECT.centery - 20)
            draw_text_center("Be the first to complete today's challenge!", SMALL_FONT, WHITE, CONTENT_RECT.centery + 10)
        
        daily_play_button.draw(screen)
        daily_leaderboard_button.draw(screen)
        back_button.draw(screen)

    elif current_screen == "daily_leaderboard":
        draw_text_center("📊 Today's Leaderboard", BIG_FONT, YELLOW, CONTENT_RECT.top + 30)
        
        today = date.today().strftime("%B %d, %Y")
        draw_text_center(today, SMALL_FONT, WHITE, CONTENT_RECT.top + 80)
        
        if daily_challenge_leaderboard:
            headers = ["Rank", "Name", "Moves", "Time", "Combo"]
            for i, h in enumerate(headers):
                screen.blit(FONT.render(h, True, BLACK), (CONTENT_RECT.left + 40 + i * 150, CONTENT_RECT.top + 120))
            
            for i, entry in enumerate(daily_challenge_leaderboard[:10]):
                rank = f"#{i+1}"
                color = YELLOW if i < 3 else WHITE
                vals = [rank, entry["name"], str(entry["moves"]), f"{entry['time']}s", f"{entry['combo']}x"]
                for j, val in enumerate(vals):
                    screen.blit(SMALL_FONT.render(val, True, color), (CONTENT_RECT.left + 40 + j*150, CONTENT_RECT.top + 160 + i*30))
        else:
            draw_text_center("No scores yet today!", FONT, GRAY, CONTENT_RECT.centery)
            draw_text_center("Be the first to complete the challenge!", SMALL_FONT, WHITE, CONTENT_RECT.centery + 40)
        
        back_button.draw(screen)

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
            "- Press H for a hint.",
            "- Time limit increases per level."
        ]
        for i, ln in enumerate(lines):
            screen.blit(FONT.render(ln, True, BLACK), (CONTENT_RECT.left + 20, CONTENT_RECT.top + 80 + i * 30))
        back_button.draw(screen)

    elif current_screen == "settings":
        draw_text_center("Settings", BIG_FONT, BLACK, CONTENT_RECT.top + 40)
        music_toggle_button.text = f"Music: {'ON' if music_enabled else 'OFF'}"
        sound_toggle_button.text = f"Sound Effects: {'ON' if sound_enabled else 'OFF'}"
        music_toggle_button.draw(screen)
        sound_toggle_button.draw(screen)
        back_button.draw(screen)

    elif current_screen == "game":
        draw_stacks()
        elapsed_time = int(time.time() - start_time)
        tleft = max(0, max_time_per_level - elapsed_time)
        
        # Time display with color warning
        time_color = RED if tleft < 30 else BLACK
        time_text = f"{'Daily Challenge' if daily_challenge_active else f'Level {selected_level+1}'} | Time: {tleft}s"
        screen.blit(FONT.render(time_text, True, time_color), (CONTENT_RECT.left + 10, CONTENT_RECT.top + 10))
        
        # Combo display
        if combo_count > 0:
            current_time = time.time()
            if current_time - last_move_time <= combo_timeout:
                combo_color = get_combo_color()
                combo_text = f"COMBO x{combo_count}"
                if combo_count >= 15:
                    combo_text += " 🔥 ON FIRE!"
                elif combo_count >= 10:
                    combo_text += " 🔥"
                combo_surf = FONT.render(combo_text, True, combo_color)
                combo_rect = combo_surf.get_rect(center=(CONTENT_RECT.centerx, CONTENT_RECT.top + 20))
                # Draw glow effect
                for offset in [(2,2), (-2,2), (2,-2), (-2,-2)]:
                    glow_surf = FONT.render(combo_text, True, (50,50,50))
                    screen.blit(glow_surf, (combo_rect.x + offset[0], combo_rect.y + offset[1]))
                screen.blit(combo_surf, combo_rect)
        
        sb = pygame.Rect(CONTENT_RECT.right - 160, CONTENT_RECT.top + 5, 140, 40)
        pygame.draw.rect(screen, (255, 255, 200), sb, border_radius=6)
        pygame.draw.rect(screen, BLACK, sb, 2, border_radius=6)
        screen.blit(FONT.render(f"Moves: {score}", True, BLACK), (sb.left + 10, sb.centery - 10))
        
        back_button.draw(screen)
        hint_button.draw(screen)

    elif current_screen == "win":
        draw_text_center("\U0001F389 CONGRATULATIONS!", BIG_FONT, YELLOW, CONTENT_RECT.top + 50)
        
        if daily_challenge_active:
            draw_text_center("Daily Challenge Completed!", FONT, GREEN, CONTENT_RECT.top + 120)
        else:
            draw_text_center(f"Level {selected_level+1} Completed", FONT, RED, CONTENT_RECT.top + 120)
        
        draw_text_center(f"Moves: {score} | Time: {elapsed_time}s | Max Combo: {max_combo_reached}x", FONT, RED, CONTENT_RECT.top + 180)
        
        # Show performance rating
        optimal_moves = total_plates - 1
        if score <= optimal_moves + 5:
            rating = "⭐⭐⭐ Perfect!"
        elif score <= optimal_moves + 15:
            rating = "⭐⭐ Great!"
        else:
            rating = "⭐ Good!"
        draw_text_center(rating, FONT, YELLOW, CONTENT_RECT.top + 240)
        
        if daily_challenge_active:
            draw_text_center("Score submitted to leaderboard!", SMALL_FONT, GREEN, CONTENT_RECT.top + 300)
        
        win_back_button.draw(screen)
        if not daily_challenge_active:
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

    elif current_screen == "achievements":
        draw_text_center("Achievements", BIG_FONT, YELLOW, CONTENT_RECT.top + 30)
        unlocked_count = sum(1 for a in achievements.values() if a["unlocked"])
        draw_text_center(f"{unlocked_count}/{len(achievements)} Unlocked", SMALL_FONT, WHITE, CONTENT_RECT.top + 80)
        
        y = CONTENT_RECT.top + 120
        for ach_id, ach in achievements.items():
            color = GREEN if ach["unlocked"] else GRAY
            icon = ach["icon"] if ach["unlocked"] else "🔒"
            text = f"{icon} {ach['name']}: {ach['desc']}"
            surf = SMALL_FONT.render(text, True, color)
            screen.blit(surf, (CONTENT_RECT.left + 40, y))
            y += 35
        
        back_button.draw(screen)

    elif current_screen == "themes":
        draw_text_center("Plate Themes", BIG_FONT, YELLOW, CONTENT_RECT.top + 30)
        draw_text_center(f"Current: {themes[current_theme]['icon']} {themes[current_theme]['name']}", FONT, WHITE, CONTENT_RECT.top + 80)
        
        for btn, theme_id in theme_buttons:
            is_unlocked = theme_id in unlocked_themes
            btn.enabled = is_unlocked
            btn.draw(screen)
            if not is_unlocked:
                lock = FONT.render("🔒", True, RED)
                screen.blit(lock, (btn.rect.right - 30, btn.rect.top + 10))
            elif theme_id == current_theme:
                check = FONT.render("✓", True, GREEN)
                screen.blit(check, (btn.rect.left + 10, btn.rect.top + 10))
        
        draw_text_center("Unlock themes by completing achievements!", SMALL_FONT, WHITE, CONTENT_RECT.bottom - 80)
        back_button.draw(screen)

# --- Main loop ---
running = True
selected_stack = None

# Load daily challenge data
daily_challenge_seed = get_daily_seed()
load_daily_challenge_data()

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
                            daily_challenge_active = False
                            init_game(0)
                            current_screen = "game"
                        elif b.text == "Daily Challenge":
                            current_screen = "daily_challenge"
                        elif b.text == "Levels":
                            current_screen = "levels"
                        elif b.text == "Achievements":
                            current_screen = "achievements"
                        elif b.text == "Themes":
                            current_screen = "themes"
                        elif b.text == "Quit":
                            running = False
                        elif b.text == "Settings":
                            current_screen = "settings"

            elif current_screen == "levels":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                else:
                    for i, b in enumerate(level_buttons):
                        if b.is_clicked(pos) and b.enabled:
                            selected_level = i
                            daily_challenge_active = False
                            init_game(i)
                            current_screen = "game"

            elif current_screen == "daily_challenge":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                elif daily_play_button.is_clicked(pos):
                    daily_challenge_active = True
                    daily_challenge_seed = get_daily_seed()
                    init_game(0)  # Level doesn't matter for daily challenge
                    current_screen = "game"
                elif daily_leaderboard_button.is_clicked(pos):
                    current_screen = "daily_leaderboard"

            elif current_screen == "daily_leaderboard":
                if back_button.is_clicked(pos):
                    current_screen = "daily_challenge"

            elif current_screen == "help" and back_button.is_clicked(pos):
                current_screen = "home"

            elif current_screen == "game":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                elif hint_button.is_clicked(pos):
                    hint = get_hint()
                    if hint:
                        from_stack, to_stack = hint
                        # Highlight the hint briefly
                        selected_stack = from_stack
                else:
                    cs = get_clicked_stack(pos)
                    if cs is not None:
                        if selected_stack is None and stacks[cs]:
                            selected_stack = cs
                        elif selected_stack is not None:
                            move_plate(selected_stack, cs)
                            selected_stack = None
                if is_win():
                    if daily_challenge_active:
                        # Submit to daily challenge leaderboard
                        submit_daily_challenge_score(player_name, score, elapsed_time, max_combo_reached)
                    else:
                        # Normal level completion
                        completed_levels[selected_level] = True
                        if selected_level + 1 < MAX_LEVELS:
                            completed_levels[selected_level + 1] = True
                        check_achievements()  # Check for unlocked achievements
                        if not any(n == player_name and lv == selected_level+1 and mv == score for n, lv, mv, t in leaderboard_data):
                            add_to_leaderboard(player_name, selected_level + 1, score, elapsed_time)
                    
                    if sound_win and sound_enabled: sound_win.play()
                    current_screen = "win"

            elif current_screen == "win":
                if win_back_button.is_clicked(pos):
                    daily_challenge_active = False
                    current_screen = "home"
                elif not daily_challenge_active and win_next_button.is_clicked(pos) and win_next_button.enabled:
                    selected_level += 1
                    daily_challenge_active = False
                    init_game(selected_level)
                    current_screen = "game"

            elif current_screen == "timeout":
                if timeout_retry_button.is_clicked(pos):
                    if daily_challenge_active:
                        daily_challenge_seed = get_daily_seed()
                    init_game(selected_level)
                    current_screen = "game"
                elif timeout_exit_button.is_clicked(pos):
                    daily_challenge_active = False
                    current_screen = "home"

            elif current_screen == "leaderboard":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                elif clear_lb_button.is_clicked(pos):
                    leaderboard_data.clear()
                    save_leaderboard()

            elif current_screen == "settings":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                elif music_toggle_button.is_clicked(pos):
                    toggle_music()
                elif sound_toggle_button.is_clicked(pos):
                    toggle_sound()

            elif current_screen == "achievements":
                if back_button.is_clicked(pos):
                    current_screen = "home"

            elif current_screen == "themes":
                if back_button.is_clicked(pos):
                    current_screen = "home"
                else:
                    for btn, theme_id in theme_buttons:
                        if btn.is_clicked(pos) and theme_id in unlocked_themes:
                            current_theme = theme_id

        elif e.type == pygame.KEYDOWN and current_screen == "game":
            if e.key == pygame.K_z:
                undo_move()
            elif e.key == pygame.K_h:
                hint = get_hint()
                if hint:
                    from_stack, to_stack = hint
                    selected_stack = from_stack

    if current_screen == "game":
        elapsed_time = int(time.time() - start_time)
        if elapsed_time >= max_time_per_level:
            current_screen = "timeout"

    draw_screens()
    pygame.display.flip()

pygame.quit()
sys.exit()