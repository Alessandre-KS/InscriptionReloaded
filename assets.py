import os
import pygame
from constants import (
    ASSET_DIR, WIDTH, HEIGHT, BACKGROUND_MARGIN_BOTTOM,
    AUDIO_VOLUMES, TITLE_SCREEN, GAME_ACTIVE, LEADERBOARD,
    NAME_ENTRY, HOW_TO_PLAY, LEADERBOARD_BACK_BTN, HOWTOPLAY_BACK_BTN
)
from database import get_leaderboard_data
import state

# --- FONTS ---
def load_font(font_path, size):
    try:
        full_path = os.path.join(ASSET_DIR, font_path)
        if os.path.exists(full_path):
            return pygame.font.Font(full_path, size)
        return pygame.font.Font(f"assets/{font_path}", size)
    except Exception as e:
        print(f"[FONT ERROR] Could not load {font_path}: {e}")
        return pygame.font.Font(None, size)

CUSTOM_FONT_REGULAR = None
CUSTOM_FONT_BOLD = None
CUSTOM_FONT_TITLE = None
CUSTOM_FONT_SMALL = None

def initialize_fonts():
    global CUSTOM_FONT_REGULAR, CUSTOM_FONT_BOLD, CUSTOM_FONT_TITLE, CUSTOM_FONT_SMALL
    try:
        CUSTOM_FONT_REGULAR = load_font("PressStart2P-Regular.ttf", 16)
        CUSTOM_FONT_BOLD = load_font("PressStart2P-Regular.ttf", 18)
        CUSTOM_FONT_TITLE = load_font("PressStart2P-Regular.ttf", 32)
        CUSTOM_FONT_SMALL = load_font("PressStart2P-Regular.ttf", 12)
        print("[FONT] PressStart2P font loaded successfully")
    except Exception as e:
        print(f"[FONT ERROR] Could not load custom fonts: {e}")
        CUSTOM_FONT_REGULAR = pygame.font.Font(None, 16)
        CUSTOM_FONT_BOLD = pygame.font.Font(None, 18)
        CUSTOM_FONT_TITLE = pygame.font.Font(None, 32)
        CUSTOM_FONT_SMALL = pygame.font.Font(None, 12)

# --- SOUND & MUSIC ---
def load_sound(name, volume=1.0, sound_type="effect"):
    try:
        path = os.path.join(ASSET_DIR, name)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            if sound_type == "effect":
                final_volume = volume * AUDIO_VOLUMES["sound_effects"]
            else:
                final_volume = volume
            sound.set_volume(final_volume)
            return sound
        else:
            print(f"[SOUND WARNING] Could not find {name}")
            return None
    except Exception as e:
        print(f"[SOUND ERROR] Could not load {name}: {e}")
        return None

dragon_roar_sound = None
gun_sound = None
gun_empty_sound = None
player_hit_sound = None
player_blast_sound = None

title_music = None
gameplay_music = None
boss_music = None

current_music = None
music_playing = False

def load_sounds():
    global dragon_roar_sound, gun_sound, player_hit_sound, player_blast_sound, gun_empty_sound
    global title_music, gameplay_music, boss_music
    print("[SOUND] Loading sound effects and music...")

    dragon_roar_sound = load_sound("dragonRoar.wav", volume=0.7)
    gun_sound = load_sound("gunSound.wav", volume=0.5)
    gun_empty_sound = load_sound("gunEmptySound.wav", volume=0.6)
    player_hit_sound = load_sound("playerGetHit.wav", volume=0.6)
    player_blast_sound = load_sound("playerBlast.wav", volume=0.8)

    title_music_path = os.path.join(ASSET_DIR, "titleScreenBG.wav")
    if os.path.exists(title_music_path):
        title_music = title_music_path
        print("[SOUND] Title screen music loaded successfully")

    gameplay_music_path = os.path.join(ASSET_DIR, "gameplayBackground.mp3")
    if os.path.exists(gameplay_music_path):
        gameplay_music = gameplay_music_path
        print("[SOUND] Gameplay background music loaded successfully")

    boss_music_path = os.path.join(ASSET_DIR, "bossMusic.wav")
    if os.path.exists(boss_music_path):
        boss_music = boss_music_path
        print("[SOUND] Boss music loaded successfully")

def play_music(music_type, loop=True):
    global current_music, music_playing
    if current_music != music_type:
        stop_music()
    try:
        music_file = None
        volume = 0.0
        if music_type == "title" and title_music:
            music_file = title_music
            volume = AUDIO_VOLUMES["title_music"]
        elif music_type == "gameplay" and gameplay_music:
            music_file = gameplay_music
            volume = AUDIO_VOLUMES["gameplay_music"]
        elif music_type == "boss" and boss_music:
            music_file = boss_music
            volume = AUDIO_VOLUMES["boss_music"]

        if music_file:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(volume)
            if loop:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.play()
            current_music = music_type
            music_playing = True
            print(f"[MUSIC] Now playing: {music_type} at volume {volume}")
    except Exception as e:
        print(f"[MUSIC ERROR] Could not play {music_type} music: {e}")

def stop_music():
    global current_music, music_playing
    pygame.mixer.music.stop()
    current_music = None
    music_playing = False
    print("[MUSIC] Music stopped")

def update_music_for_state(target_state=None, is_boss=None):
    if target_state is None:
        target_state = state.current_game_state
    if target_state in [TITLE_SCREEN, LEADERBOARD, HOW_TO_PLAY]:
        if current_music != "title":
            play_music("title")
    elif target_state == GAME_ACTIVE:
        if is_boss is None:
            is_boss = state.wave_system.is_boss_wave() if state.wave_system else False
        if not is_boss and current_music != "gameplay":
            play_music("gameplay")
    elif target_state == NAME_ENTRY:
        stop_music()

# --- BACKGROUND SYSTEM ---
BACKGROUND_ORIGINAL = None
background_surface = None
current_wave_temperature = 0.0
current_wave_darkness = 0.0

def load_background():
    global BACKGROUND_ORIGINAL, background_surface
    try:
        bg = load_image("mainGameBackGround.jpg")
        available_height = HEIGHT - BACKGROUND_MARGIN_BOTTOM
        bg_ratio = bg.get_width() / bg.get_height()
        target_ratio = WIDTH / available_height

        if bg_ratio > target_ratio:
            new_height = available_height
            new_width = int(bg.get_width() * (available_height / bg.get_height()))
        else:
            new_width = WIDTH
            new_height = int(bg.get_height() * (WIDTH / bg.get_width()))

        scaled_bg = pygame.transform.scale(bg, (new_width, new_height))
        dark_overlay = pygame.Surface((new_width, new_height))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(50)
        scaled_bg.blit(dark_overlay, (0, 0))

        BACKGROUND_ORIGINAL = pygame.Surface((WIDTH, available_height))
        BACKGROUND_ORIGINAL.blit(scaled_bg, (WIDTH//2 - new_width//2, available_height//2 - new_height//2))
        background_surface = BACKGROUND_ORIGINAL.copy()
        print("[BACKGROUND] Loaded with subtle dark overlay (20% reduction)")
    except Exception as e:
        print(f"[BACKGROUND ERROR] Could not load background: {e}")
        available_height = HEIGHT - BACKGROUND_MARGIN_BOTTOM
        BACKGROUND_ORIGINAL = pygame.Surface((WIDTH, available_height))
        BACKGROUND_ORIGINAL.fill((50, 50, 80))
        background_surface = BACKGROUND_ORIGINAL.copy()

def update_background_for_wave(wave_number):
    global background_surface, current_wave_temperature, current_wave_darkness
    if BACKGROUND_ORIGINAL is None:
        return
    cycle_wave = (wave_number - 1) % 10
    progress = cycle_wave / 9.0
    current_wave_temperature = progress
    current_wave_darkness = progress * 0.9

    background_surface = BACKGROUND_ORIGINAL.copy()

    if current_wave_temperature > 0:
        temp_surface = pygame.Surface((WIDTH, HEIGHT - BACKGROUND_MARGIN_BOTTOM))
        temp_color = (
            min(255, int(100 * current_wave_temperature)),
            min(255, int(30 * current_wave_temperature)),
            min(255, int(10 * current_wave_temperature))
        )
        temp_surface.fill(temp_color)
        temp_surface.set_alpha(int(80 * current_wave_temperature))
        background_surface.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_ADD)

    if current_wave_darkness > 0:
        dark_surface = pygame.Surface((WIDTH, HEIGHT - BACKGROUND_MARGIN_BOTTOM))
        dark_surface.fill((0, 0, 0))
        dark_surface.set_alpha(int(220 * current_wave_darkness))
        background_surface.blit(dark_surface, (0, 0))

def draw_background(screen=None):
    if screen is None:
        screen = pygame.display.get_surface()
    if screen and background_surface:
        screen.blit(background_surface, (0, 0))
        margin_rect = pygame.Rect(0, HEIGHT - BACKGROUND_MARGIN_BOTTOM, WIDTH, BACKGROUND_MARGIN_BOTTOM)
        pygame.draw.rect(screen, (20, 20, 30), margin_rect)
        pygame.draw.line(screen, (50, 50, 70), (0, HEIGHT - BACKGROUND_MARGIN_BOTTOM), 
                         (WIDTH, HEIGHT - BACKGROUND_MARGIN_BOTTOM), 2)

# --- IMAGE LOADING & FRAME LOADERS ---
_IMAGE_CACHE = {}

def load_image(name):
    if name in _IMAGE_CACHE:
        return _IMAGE_CACHE[name].copy()
    path = os.path.join(ASSET_DIR, name)
    try:
        raw = pygame.image.load(path)
        image = raw.convert_alpha() if pygame.display.get_surface() is not None else raw
        _IMAGE_CACHE[name] = image
        return image.copy()
    except Exception as e:
        print(f"[ERROR] Could not load {name}: {e}")
        placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255))
        _IMAGE_CACHE[name] = placeholder
        return placeholder.copy()

def load_player_frames():
    frames = []
    for fname in ["MAIN RUN - FRAME1.png", "MAIN RUN - FRAME2.png",
                  "MAIN RUN - FRAME3.png", "MAIN-IDLE.png"]:
        img = load_image(fname)
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        frames.append(cropped_img)
    return frames

def load_frog_frames():
    frames = []
    target_height = 50
    for i in range(1, 9):
        img = load_image(f"frogFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_rocket_frames():
    frames = []
    target_height = 70
    for i in range(1, 13):
        img = load_image(f"rocketEnemyFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_ghoul_frames():
    frames = []
    target_height = 70
    for i in range(1, 8):
        img = load_image(f"Ghoul{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_axolotl_frames():
    frames = []
    target_height = 50
    for i in range(1, 7):
        img = load_image(f"axoltlFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_bat_frames():
    frames = []
    target_height = 30
    for i in range(1, 3):
        img = load_image(f"bat{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_reaper_frames():
    frames = []
    target_height = 60
    for i in range(1, 7):
        img = load_image(f"reaperFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_ally_frames():
    frames = []
    target_height = 40
    for i in range(1, 20):
        img = load_image(f"partnerFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_witch_frames():
    frames = []
    target_height = 60
    for i in range(1, 7):
        img = load_image(f"witchFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_witch_projectile_image():
    img = load_image("witchFrameFire.png")
    img_rect = img.get_bounding_rect()
    cropped_img = img.subsurface(img_rect).copy()
    new_w = int(cropped_img.get_width() * 0.5)
    new_h = int(cropped_img.get_height() * 0.5)
    return pygame.transform.scale(cropped_img, (new_w, new_h))

def load_dragon_frames():
    frames = []
    target_height = 150
    for i in range(1, 14):
        img = load_image(f"dragon-{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_fire_boss_frames():
    frames = []
    target_height = 200
    for i in range(1, 6):
        img = load_image(f"FireBossFrame{i}.png")
        img_rect = img.get_bounding_rect()
        cropped_img = img.subsurface(img_rect).copy()
        scale_factor = target_height / cropped_img.get_height()
        new_w = int(cropped_img.get_width() * scale_factor)
        new_h = int(cropped_img.get_height() * scale_factor)
        frames.append(pygame.transform.scale(cropped_img, (new_w, new_h)))
    return frames

def load_ak_image():
    return load_image("akGun.png")

def load_pistol_image():
    return load_image("pistol.png")

def load_shotgun_image():
    return load_image("Shotgun.png")

def load_blast_radius_image():
    img = load_image("blastRadius.png")
    return pygame.transform.scale(img, (200, 200))

def load_platform_image():
    img = load_image("woodPlatform.png")
    return pygame.transform.scale(img, (120, 20))

# --- ASSET CACHES ---
PLAYER_FRAMES_RIGHT = []
PLAYER_FRAMES_LEFT = []
PLAYER_MASKS_RIGHT = []
PLAYER_MASKS_LEFT = []

FROG_FRAMES = []
FROG_FRAMES_FLIPPED = []
FROG_MASKS = []
FROG_MASKS_FLIPPED = []

GHOUL_FRAMES = []
GHOUL_FRAMES_FLIPPED = []
GHOUL_MASKS = []
GHOUL_MASKS_FLIPPED = []

AXOLOTL_FRAMES = []
AXOLOTL_FRAMES_FLIPPED = []
AXOLOTL_MASKS = []
AXOLOTL_MASKS_FLIPPED = []

WITCH_FRAMES = []
WITCH_FRAMES_FLIPPED = []
WITCH_MASKS = []
WITCH_MASKS_FLIPPED = []

BAT_FRAMES = []
BAT_FRAMES_FLIPPED = []
BAT_MASKS = []
BAT_MASKS_FLIPPED = []

REAPER_FRAMES = []
REAPER_FRAMES_FLIPPED = []
REAPER_MASKS = []
REAPER_MASKS_FLIPPED = []

ROCKET_FRAMES = []
ROCKET_FRAMES_FLIPPED = []
ROCKET_MASKS = []
ROCKET_MASKS_FLIPPED = []

ALLY_FRAMES = []
ALLY_FRAMES_FLIPPED = []
ALLY_MASKS = []
ALLY_MASKS_FLIPPED = []

DRAGON_FRAMES = []
DRAGON_FRAMES_FLIPPED = []
DRAGON_MASKS = []
DRAGON_MASKS_FLIPPED = []

FIRE_BOSS_FRAMES = []
FIRE_BOSS_FRAMES_FLIPPED = []
FIRE_BOSS_MASKS = []
FIRE_BOSS_MASKS_FLIPPED = []

WITCH_PROJECTILE_IMAGE = None
WITCH_PROJECTILE_MASK = None

PLATFORM_IMAGE = None
PLATFORM_MASK = None

BLAST_RADIUS_IMAGE = None
BLAST_RADIUS_MASK = None

TITLE_BG_IMAGE = None
CROWN_IMAGE = None

TITLE_MENU_SURFACE = None
TITLE_START_TEXT = None
TITLE_LEADERBOARD_TEXT = None
TITLE_HOWTOPLAY_TEXT = None

HOWTOPLAY_PANEL_SURFACE = None
HOWTOPLAY_TITLE_TEXT = None
HOWTOPLAY_INSTRUCTION_TEXTS = []
HOWTOPLAY_BACK_BTN_SURFACE = None
HOWTOPLAY_BACK_TEXT = None

LEADERBOARD_PANEL_SURFACE = None
BACK_BUTTON_SURFACE = None

COUNTDOWN_BG_SURF = None
STATS_BG_SURF = None

cached_leaderboard = None

def refresh_leaderboard_data():
    global cached_leaderboard
    cached_leaderboard = get_leaderboard_data(limit=5)

cached_ui_texts = {}

def get_cached_text(font, text, color):
    key = (id(font), text, color)
    surf = cached_ui_texts.get(key)
    if surf is None:
        surf = font.render(text, True, color)
        if len(cached_ui_texts) > 256:
            cached_ui_texts.clear()
        cached_ui_texts[key] = surf
    return surf

def _build_frame_cache(frames):
    flipped = [pygame.transform.flip(f, True, False) for f in frames]
    masks = [pygame.mask.from_surface(f) for f in frames]
    masks_flipped = [pygame.mask.from_surface(f) for f in flipped]
    return frames, flipped, masks, masks_flipped

def initialize_assets():
    global PLAYER_FRAMES_RIGHT, PLAYER_FRAMES_LEFT, PLAYER_MASKS_RIGHT, PLAYER_MASKS_LEFT
    global FROG_FRAMES, FROG_FRAMES_FLIPPED, FROG_MASKS, FROG_MASKS_FLIPPED
    global GHOUL_FRAMES, GHOUL_FRAMES_FLIPPED, GHOUL_MASKS, GHOUL_MASKS_FLIPPED
    global AXOLOTL_FRAMES, AXOLOTL_FRAMES_FLIPPED, AXOLOTL_MASKS, AXOLOTL_MASKS_FLIPPED
    global WITCH_FRAMES, WITCH_FRAMES_FLIPPED, WITCH_MASKS, WITCH_MASKS_FLIPPED
    global BAT_FRAMES, BAT_FRAMES_FLIPPED, BAT_MASKS, BAT_MASKS_FLIPPED
    global REAPER_FRAMES, REAPER_FRAMES_FLIPPED, REAPER_MASKS, REAPER_MASKS_FLIPPED
    global ROCKET_FRAMES, ROCKET_FRAMES_FLIPPED, ROCKET_MASKS, ROCKET_MASKS_FLIPPED
    global ALLY_FRAMES, ALLY_FRAMES_FLIPPED, ALLY_MASKS, ALLY_MASKS_FLIPPED
    global DRAGON_FRAMES, DRAGON_FRAMES_FLIPPED, DRAGON_MASKS, DRAGON_MASKS_FLIPPED
    global FIRE_BOSS_FRAMES, FIRE_BOSS_FRAMES_FLIPPED, FIRE_BOSS_MASKS, FIRE_BOSS_MASKS_FLIPPED
    global WITCH_PROJECTILE_IMAGE, WITCH_PROJECTILE_MASK
    global PLATFORM_IMAGE, PLATFORM_MASK
    global BLAST_RADIUS_IMAGE, BLAST_RADIUS_MASK
    global TITLE_BG_IMAGE, CROWN_IMAGE
    global TITLE_MENU_SURFACE, TITLE_START_TEXT, TITLE_LEADERBOARD_TEXT, TITLE_HOWTOPLAY_TEXT
    global HOWTOPLAY_PANEL_SURFACE, HOWTOPLAY_TITLE_TEXT, HOWTOPLAY_INSTRUCTION_TEXTS, HOWTOPLAY_BACK_BTN_SURFACE, HOWTOPLAY_BACK_TEXT
    global LEADERBOARD_PANEL_SURFACE, BACK_BUTTON_SURFACE
    global COUNTDOWN_BG_SURF, STATS_BG_SURF

    PLAYER_FRAMES_RIGHT, PLAYER_FRAMES_LEFT, PLAYER_MASKS_RIGHT, PLAYER_MASKS_LEFT = _build_frame_cache(load_player_frames())
    FROG_FRAMES, FROG_FRAMES_FLIPPED, FROG_MASKS, FROG_MASKS_FLIPPED = _build_frame_cache(load_frog_frames())
    GHOUL_FRAMES, GHOUL_FRAMES_FLIPPED, GHOUL_MASKS, GHOUL_MASKS_FLIPPED = _build_frame_cache(load_ghoul_frames())
    AXOLOTL_FRAMES, AXOLOTL_FRAMES_FLIPPED, AXOLOTL_MASKS, AXOLOTL_MASKS_FLIPPED = _build_frame_cache(load_axolotl_frames())
    WITCH_FRAMES, WITCH_FRAMES_FLIPPED, WITCH_MASKS, WITCH_MASKS_FLIPPED = _build_frame_cache(load_witch_frames())
    BAT_FRAMES, BAT_FRAMES_FLIPPED, BAT_MASKS, BAT_MASKS_FLIPPED = _build_frame_cache(load_bat_frames())
    REAPER_FRAMES, REAPER_FRAMES_FLIPPED, REAPER_MASKS, REAPER_MASKS_FLIPPED = _build_frame_cache(load_reaper_frames())
    ROCKET_FRAMES, ROCKET_FRAMES_FLIPPED, ROCKET_MASKS, ROCKET_MASKS_FLIPPED = _build_frame_cache(load_rocket_frames())
    ALLY_FRAMES, ALLY_FRAMES_FLIPPED, ALLY_MASKS, ALLY_MASKS_FLIPPED = _build_frame_cache(load_ally_frames())
    DRAGON_FRAMES, DRAGON_FRAMES_FLIPPED, DRAGON_MASKS, DRAGON_MASKS_FLIPPED = _build_frame_cache(load_dragon_frames())

    raw_fire_boss = load_fire_boss_frames()
    scaled_fire_boss = [
        pygame.transform.scale(f, (int(f.get_width() * 1.5), int(f.get_height() * 1.8)))
        for f in raw_fire_boss
    ]
    FIRE_BOSS_FRAMES, FIRE_BOSS_FRAMES_FLIPPED, FIRE_BOSS_MASKS, FIRE_BOSS_MASKS_FLIPPED = _build_frame_cache(scaled_fire_boss)

    WITCH_PROJECTILE_IMAGE = load_witch_projectile_image()
    WITCH_PROJECTILE_MASK = pygame.mask.from_surface(WITCH_PROJECTILE_IMAGE)

    PLATFORM_IMAGE = load_platform_image()
    PLATFORM_MASK = pygame.mask.from_surface(PLATFORM_IMAGE)

    BLAST_RADIUS_IMAGE = load_blast_radius_image()
    BLAST_RADIUS_MASK = pygame.mask.from_surface(BLAST_RADIUS_IMAGE)

    raw_title_bg = load_image("titleScreenBackground.png")
    scaled_title_bg = pygame.transform.scale(raw_title_bg, (WIDTH, HEIGHT))
    TITLE_BG_IMAGE = scaled_title_bg.convert() if pygame.display.get_surface() is not None else scaled_title_bg

    raw_crown = load_image("topCrown.png")
    CROWN_IMAGE = pygame.transform.scale(raw_crown, (30, 30))

    # Menu panel surface and texts
    TITLE_MENU_SURFACE = pygame.Surface((300, 160), pygame.SRCALPHA)
    pygame.draw.rect(TITLE_MENU_SURFACE, (0, 0, 64, 220), TITLE_MENU_SURFACE.get_rect(), border_radius=10)
    pygame.draw.rect(TITLE_MENU_SURFACE, (255, 255, 255, 120), TITLE_MENU_SURFACE.get_rect(), 3, border_radius=10)

    font = CUSTOM_FONT_BOLD or pygame.font.Font(None, 18)
    white = (255, 255, 255)
    TITLE_START_TEXT = font.render("START", True, white)
    TITLE_LEADERBOARD_TEXT = font.render("LEADERBOARD", True, white)
    TITLE_HOWTOPLAY_TEXT = font.render("HOW TO PLAY", True, white)

    # Leaderboard panels
    panel_rect = pygame.Rect(WIDTH//2 - 310, 100, 620, 340)
    LEADERBOARD_PANEL_SURFACE = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(LEADERBOARD_PANEL_SURFACE, (0, 0, 64, 230), LEADERBOARD_PANEL_SURFACE.get_rect(), border_radius=15)
    pygame.draw.rect(LEADERBOARD_PANEL_SURFACE, (255, 255, 255, 140), LEADERBOARD_PANEL_SURFACE.get_rect(), 3, border_radius=15)

    back_rect = LEADERBOARD_BACK_BTN
    BACK_BUTTON_SURFACE = pygame.Surface((back_rect.width, back_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(BACK_BUTTON_SURFACE, (0, 0, 64, 220), BACK_BUTTON_SURFACE.get_rect(), border_radius=10)
    pygame.draw.rect(BACK_BUTTON_SURFACE, (255, 255, 255, 140), BACK_BUTTON_SURFACE.get_rect(), 3, border_radius=10)

    # How to play panels
    HOWTOPLAY_PANEL_SURFACE = pygame.Surface((700, 400), pygame.SRCALPHA)
    pygame.draw.rect(HOWTOPLAY_PANEL_SURFACE, (0, 0, 64, 230), HOWTOPLAY_PANEL_SURFACE.get_rect(), border_radius=15)
    pygame.draw.rect(HOWTOPLAY_PANEL_SURFACE, (255, 255, 255, 140), HOWTOPLAY_PANEL_SURFACE.get_rect(), 3, border_radius=15)

    title_f = CUSTOM_FONT_TITLE or pygame.font.Font(None, 32)
    reg_f = CUSTOM_FONT_REGULAR or pygame.font.Font(None, 16)
    HOWTOPLAY_TITLE_TEXT = title_f.render("HOW TO PLAY", True, white)
    instructions = [
        "WASD  : Movement",
        "Left Click : Shoot",
        "Right Click : Knockback Attack",
        "Q : Switch Weapon",
        "ESC : Return to Menu"
    ]
    HOWTOPLAY_INSTRUCTION_TEXTS = [reg_f.render(line, True, white) for line in instructions]

    hp_back = HOWTOPLAY_BACK_BTN
    HOWTOPLAY_BACK_BTN_SURFACE = pygame.Surface((hp_back.width, hp_back.height), pygame.SRCALPHA)
    pygame.draw.rect(HOWTOPLAY_BACK_BTN_SURFACE, (0, 0, 64, 220), HOWTOPLAY_BACK_BTN_SURFACE.get_rect(), border_radius=10)
    pygame.draw.rect(HOWTOPLAY_BACK_BTN_SURFACE, (255, 255, 255, 140), HOWTOPLAY_BACK_BTN_SURFACE.get_rect(), 3, border_radius=10)
    HOWTOPLAY_BACK_TEXT = reg_f.render("BACK TO MENU", True, white)

    COUNTDOWN_BG_SURF = pygame.Surface((400, 80))
    COUNTDOWN_BG_SURF.fill((0, 0, 0))
    COUNTDOWN_BG_SURF.set_alpha(180)

    STATS_BG_SURF = pygame.Surface((200, 160))
    STATS_BG_SURF.fill((0, 0, 0))
    STATS_BG_SURF.set_alpha(180)

    refresh_leaderboard_data()
