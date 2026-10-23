import os
import sys
import pygame

# Game window dimensions
WIDTH, HEIGHT = 960, 540
GROUND_LEVEL = HEIGHT - 50

# Base asset directory (supports both script and PyInstaller frozen executable)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSET_DIR = os.path.join(
    BASE_DIR,
    "ASSETS" if os.path.exists(os.path.join(BASE_DIR, "ASSETS")) else "assets"
)

# Audio volume settings
AUDIO_VOLUMES = {
    "title_music": 0.5,
    "gameplay_music": 0.4,
    "boss_music": 0.4,
    "sound_effects": 0.3
}

# Debug settings
DEBUG_START_WAVE = 1

# Game states
TITLE_SCREEN = 0
GAME_ACTIVE = 1
LEADERBOARD = 2
NAME_ENTRY = 3
PAUSED = 4
HOW_TO_PLAY = 5

# Background margins
BACKGROUND_MARGIN_BOTTOM = 50

# Platform positions
platform_positions = [
    (WIDTH // 4 - 60, 380),
    (3 * WIDTH // 4 - 60, 380),
    (WIDTH // 6 - 60, 280),
    (WIDTH // 2 - 60, 260),
    (5 * WIDTH // 6 - 60, 280),
    (WIDTH // 3 - 60, 160),
    (2 * WIDTH // 3 - 60, 160)
]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 220, 100)
CYAN = (0, 255, 255)
DARK_GRAY = (20, 20, 30)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)

# Static UI button rects
TITLE_START_BTN = pygame.Rect(WIDTH // 2 - 150, 315, 300, 45)
TITLE_LEADERBOARD_BTN = pygame.Rect(WIDTH // 2 - 150, 365, 300, 45)
TITLE_HOWTOPLAY_BTN = pygame.Rect(WIDTH // 2 - 150, 415, 300, 45)
LEADERBOARD_BACK_BTN = pygame.Rect(WIDTH // 2 - 160, 420, 320, 55)
HOWTOPLAY_BACK_BTN = pygame.Rect(WIDTH // 2 - 120, 440, 240, 50)
NAME_ENTRY_SUBMIT_BTN = pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
NAME_ENTRY_INPUT_BOX = pygame.Rect(WIDTH // 2 - 200, 320, 400, 60)
