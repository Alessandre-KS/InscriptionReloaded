import random
from constants import TITLE_SCREEN

# Active game state
current_game_state = TITLE_SCREEN

# Game systems
wave_system = None
enemy_spawner = None
score_system = None

# Active entities
player = None
gun = None
knife = None
ally = None

# Sprite groups
all_sprites = None
bullet_group = None
enemy_projectile_group = None
ground_enemy_group = None
flying_enemy_group = None
platform_group = None

# Screen shake variables
screen_shake_intensity = 0
screen_shake_duration = 0
screen_offset_x = 0
screen_offset_y = 0

def trigger_screen_shake(intensity=10, duration=20):
    global screen_shake_intensity, screen_shake_duration
    screen_shake_intensity = intensity
    screen_shake_duration = duration

def update_screen_shake():
    global screen_shake_intensity, screen_shake_duration, screen_offset_x, screen_offset_y
    if screen_shake_duration > 0:
        screen_shake_duration -= 1
        screen_offset_x = random.randint(-screen_shake_intensity, screen_shake_intensity)
        screen_offset_y = random.randint(-screen_shake_intensity, screen_shake_intensity)
        if screen_shake_duration % 5 == 0:
            screen_shake_intensity = max(0, screen_shake_intensity - 1)
    else:
        screen_offset_x = 0
        screen_offset_y = 0
        screen_shake_intensity = 0
    return screen_offset_x, screen_offset_y

# Boss flags
dragon_roar_played = False
boss_music_playing = False

# Game over & name entry
player_name = ""
name_entry_active = True
final_wave = 0
final_score = 0

