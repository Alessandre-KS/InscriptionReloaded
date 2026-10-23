# INSCRIPTION RELOADED - PyGame Platform Shooter
# Modular entry point and main game loop

import os
import math
import random
import pygame

# Initialize Pygame and audio mixer
pygame.init()
pygame.mixer.init()

# Import project modules
from constants import (
    WIDTH, HEIGHT, GROUND_LEVEL, DEBUG_START_WAVE, AUDIO_VOLUMES,
    TITLE_SCREEN, GAME_ACTIVE, LEADERBOARD, NAME_ENTRY, PAUSED, HOW_TO_PLAY,
    BACKGROUND_MARGIN_BOTTOM, platform_positions,
    TITLE_START_BTN, TITLE_LEADERBOARD_BTN, TITLE_HOWTOPLAY_BTN,
    LEADERBOARD_BACK_BTN, HOWTOPLAY_BACK_BTN, NAME_ENTRY_SUBMIT_BTN, NAME_ENTRY_INPUT_BOX
)

from database import init_database, get_leaderboard_data, save_score
import state
from state import trigger_screen_shake, update_screen_shake

import assets
from assets import (
    load_font, initialize_fonts,
    load_sound, load_sounds, play_music, stop_music, update_music_for_state,
    load_background, update_background_for_wave, draw_background,
    load_image, load_player_frames, load_frog_frames, load_rocket_frames,
    load_ghoul_frames, load_axolotl_frames, load_bat_frames, load_reaper_frames,
    load_ally_frames, load_witch_frames, load_witch_projectile_image,
    load_dragon_frames, load_fire_boss_frames, load_ak_image, load_pistol_image,
    load_shotgun_image, load_blast_radius_image, load_platform_image,
    get_cached_text, refresh_leaderboard_data, initialize_assets
)

from weapons import Bullet, Gun, Knife
from player import Platform, Player, Ally
from enemies import (
    Bat, Frog, Ghoul, Axolotl, Witch, WitchProjectile,
    FireBoss, DragonBoss, RocketEnemy, Reaper
)
from systems import WaveSystem, EnemySpawner, ScoreSystem
from ui import draw_title_screen, draw_leaderboard, draw_how_to_play, draw_name_entry

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Inscription RELOADED")

# Assets & fonts startup
initialize_fonts()
load_sounds()
load_background()
initialize_assets()

# Expose asset cache variables at module level for compatibility
PLAYER_FRAMES_RIGHT = assets.PLAYER_FRAMES_RIGHT
PLAYER_FRAMES_LEFT = assets.PLAYER_FRAMES_LEFT
PLAYER_MASKS_RIGHT = assets.PLAYER_MASKS_RIGHT
PLAYER_MASKS_LEFT = assets.PLAYER_MASKS_LEFT

FROG_FRAMES = assets.FROG_FRAMES
FROG_FRAMES_FLIPPED = assets.FROG_FRAMES_FLIPPED
FROG_MASKS = assets.FROG_MASKS
FROG_MASKS_FLIPPED = assets.FROG_MASKS_FLIPPED

GHOUL_FRAMES = assets.GHOUL_FRAMES
GHOUL_FRAMES_FLIPPED = assets.GHOUL_FRAMES_FLIPPED
GHOUL_MASKS = assets.GHOUL_MASKS
GHOUL_MASKS_FLIPPED = assets.GHOUL_MASKS_FLIPPED

AXOLOTL_FRAMES = assets.AXOLOTL_FRAMES
AXOLOTL_FRAMES_FLIPPED = assets.AXOLOTL_FRAMES_FLIPPED
AXOLOTL_MASKS = assets.AXOLOTL_MASKS
AXOLOTL_MASKS_FLIPPED = assets.AXOLOTL_MASKS_FLIPPED

WITCH_FRAMES = assets.WITCH_FRAMES
WITCH_FRAMES_FLIPPED = assets.WITCH_FRAMES_FLIPPED
WITCH_MASKS = assets.WITCH_MASKS
WITCH_MASKS_FLIPPED = assets.WITCH_MASKS_FLIPPED

BAT_FRAMES = assets.BAT_FRAMES
BAT_FRAMES_FLIPPED = assets.BAT_FRAMES_FLIPPED
BAT_MASKS = assets.BAT_MASKS
BAT_MASKS_FLIPPED = assets.BAT_MASKS_FLIPPED

REAPER_FRAMES = assets.REAPER_FRAMES
REAPER_FRAMES_FLIPPED = assets.REAPER_FRAMES_FLIPPED
REAPER_MASKS = assets.REAPER_MASKS
REAPER_MASKS_FLIPPED = assets.REAPER_MASKS_FLIPPED

ROCKET_FRAMES = assets.ROCKET_FRAMES
ROCKET_FRAMES_FLIPPED = assets.ROCKET_FRAMES_FLIPPED
ROCKET_MASKS = assets.ROCKET_MASKS
ROCKET_MASKS_FLIPPED = assets.ROCKET_MASKS_FLIPPED

ALLY_FRAMES = assets.ALLY_FRAMES
ALLY_FRAMES_FLIPPED = assets.ALLY_FRAMES_FLIPPED
ALLY_MASKS = assets.ALLY_MASKS
ALLY_MASKS_FLIPPED = assets.ALLY_MASKS_FLIPPED

DRAGON_FRAMES = assets.DRAGON_FRAMES
DRAGON_FRAMES_FLIPPED = assets.DRAGON_FRAMES_FLIPPED
DRAGON_MASKS = assets.DRAGON_MASKS
DRAGON_MASKS_FLIPPED = assets.DRAGON_MASKS_FLIPPED

FIRE_BOSS_FRAMES = assets.FIRE_BOSS_FRAMES
FIRE_BOSS_FRAMES_FLIPPED = assets.FIRE_BOSS_FRAMES_FLIPPED
FIRE_BOSS_MASKS = assets.FIRE_BOSS_MASKS
FIRE_BOSS_MASKS_FLIPPED = assets.FIRE_BOSS_MASKS_FLIPPED

WITCH_PROJECTILE_IMAGE = assets.WITCH_PROJECTILE_IMAGE
WITCH_PROJECTILE_MASK = assets.WITCH_PROJECTILE_MASK

PLATFORM_IMAGE = assets.PLATFORM_IMAGE
PLATFORM_MASK = assets.PLATFORM_MASK

BLAST_RADIUS_IMAGE = assets.BLAST_RADIUS_IMAGE
BLAST_RADIUS_MASK = assets.BLAST_RADIUS_MASK

TITLE_BG_IMAGE = assets.TITLE_BG_IMAGE
CROWN_IMAGE = assets.CROWN_IMAGE

# Module-level sprite groups and systems
wave_system = WaveSystem()
enemy_spawner = EnemySpawner(wave_system)
score_system = ScoreSystem()

all_sprites = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_projectile_group = pygame.sprite.Group()
ground_enemy_group = pygame.sprite.Group()
flying_enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

# Bind sprite groups to state
state.wave_system = wave_system
state.enemy_spawner = enemy_spawner
state.score_system = score_system
state.all_sprites = all_sprites
state.bullet_group = bullet_group
state.enemy_projectile_group = enemy_projectile_group
state.ground_enemy_group = ground_enemy_group
state.flying_enemy_group = flying_enemy_group
state.platform_group = platform_group

player = None
gun = None
knife = None
ally = None

def initialize_game():
    global player, gun, knife, ally
    
    all_sprites.empty()
    platform_group.empty()
    ground_enemy_group.empty()
    flying_enemy_group.empty()
    bullet_group.empty()
    enemy_projectile_group.empty()
    
    state.dragon_roar_played = False
    state.boss_music_playing = False
    stop_music()
    
    player = Player(WIDTH // 2, GROUND_LEVEL)
    all_sprites.add(player)
    
    for pos in platform_positions:
        platform = Platform(pos[0], pos[1], width=120, height=20)
        platform_group.add(platform)
        all_sprites.add(platform)
    
    knife = Knife(player, ground_enemy_group, flying_enemy_group)
    all_sprites.add(knife)
    
    gun = Gun(player, bullet_group)
    all_sprites.add(gun)
    
    ally = Ally(ground_enemy_group)
    all_sprites.add(ally)
    
    # Update state bindings
    state.player = player
    state.gun = gun
    state.knife = knife
    state.ally = ally

initialize_game()

# Main game loop setup
clock = pygame.time.Clock()
running = True
show_hitboxes = False
switch_weapon_pressed = False
show_stats = False

update_music_for_state()

# Headless guard for tests/imports
if __name__ != "__main__":
    running = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if state.current_game_state == TITLE_SCREEN:
                if TITLE_START_BTN.collidepoint(mouse_pos):
                    state.current_game_state = GAME_ACTIVE
                    wave_system = WaveSystem()
                    enemy_spawner = EnemySpawner(wave_system)
                    score_system = ScoreSystem()
                    state.wave_system = wave_system
                    state.enemy_spawner = enemy_spawner
                    state.score_system = score_system
                    
                    initialize_game()
                    update_background_for_wave(wave_system.current_wave)
                    update_music_for_state()
                    
                elif TITLE_LEADERBOARD_BTN.collidepoint(mouse_pos):
                    refresh_leaderboard_data()
                    state.current_game_state = LEADERBOARD
                    update_music_for_state()
                
                elif TITLE_HOWTOPLAY_BTN.collidepoint(mouse_pos):
                    state.current_game_state = HOW_TO_PLAY
                    update_music_for_state()

            elif state.current_game_state == LEADERBOARD:
                if LEADERBOARD_BACK_BTN.collidepoint(mouse_pos):
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()

            elif state.current_game_state == HOW_TO_PLAY:
                if HOWTOPLAY_BACK_BTN.collidepoint(mouse_pos):
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()

            elif state.current_game_state == NAME_ENTRY:
                clean_name = state.player_name.strip()
                if NAME_ENTRY_SUBMIT_BTN.collidepoint(mouse_pos) and len(clean_name) > 0:
                    save_score(clean_name, state.final_wave, state.final_score)
                    refresh_leaderboard_data()
                    state.player_name = ""
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()
        
        if event.type == pygame.KEYDOWN:
            if state.current_game_state == NAME_ENTRY:
                clean_name = state.player_name.strip()
                if event.key == pygame.K_RETURN and len(clean_name) > 0:
                    save_score(clean_name, state.final_wave, state.final_score)
                    refresh_leaderboard_data()
                    state.player_name = ""
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()
                elif event.key == pygame.K_BACKSPACE:
                    state.player_name = state.player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    state.player_name = ""
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()
                elif len(state.player_name) < 12:
                    if event.unicode.isalnum() or event.unicode == ' ':
                        state.player_name += event.unicode
            
            elif state.current_game_state == GAME_ACTIVE:
                if event.key == pygame.K_h:
                    show_hitboxes = not show_hitboxes
                if event.key == pygame.K_q:
                    if not switch_weapon_pressed and gun:
                        gun.switch_weapon()
                        switch_weapon_pressed = True
                if event.key == pygame.K_i and player:
                    player.toggle_god_mode()
                if event.key == pygame.K_m:
                    show_stats = not show_stats
                if event.key == pygame.K_ESCAPE:
                    state.current_game_state = TITLE_SCREEN
                    update_music_for_state()
        
        if event.type == pygame.KEYUP and state.current_game_state == GAME_ACTIVE:
            if event.key == pygame.K_q:
                switch_weapon_pressed = False

    update_music_for_state()

    if state.current_game_state == TITLE_SCREEN:
        draw_title_screen(screen)
    
    elif state.current_game_state == LEADERBOARD:
        draw_leaderboard(screen)
    
    elif state.current_game_state == HOW_TO_PLAY:
        draw_how_to_play(screen)
    
    elif state.current_game_state == NAME_ENTRY:
        draw_name_entry(screen)
    
    elif state.current_game_state == GAME_ACTIVE:
        keys = pygame.key.get_pressed()
        
        player.update_keyboard(keys, platform_group)
        gun.update_keyboard()
        knife.update_keyboard()
        ground_enemy_group.update(player)
        flying_enemy_group.update(player)
        ally.update()
        bullet_group.update()
        enemy_projectile_group.update()

        offset_x, offset_y = update_screen_shake()
        wave_system.update()

        # Boss spawning
        if wave_system.should_spawn_bosses():
            bosses_to_spawn = wave_system.get_bosses_to_spawn()
            for boss_type, position in bosses_to_spawn:
                if boss_type == "fire":
                    spawn_left = (position == "left")
                    fire_boss = FireBoss(spawn_left=spawn_left, player=player)
                    all_sprites.add(fire_boss)
                    ground_enemy_group.add(fire_boss)
                    wave_system.wave_enemies_spawned += 1
                    wave_system.enemies_remaining -= 1
                    print(f"[BOSS SPAWN] Fire Boss (Wave {wave_system.current_wave})")
                elif boss_type == "dragon":
                    if isinstance(position, str) and position.startswith("position_"):
                        index = int(position.split("_")[1])
                        x_pos = WIDTH - 150 - (index * 200)
                        if x_pos < 100:
                            x_pos = 100
                    else:
                        x_pos = WIDTH - 150
                        
                    dragon_boss = DragonBoss(x_pos, 150, player)
                    all_sprites.add(dragon_boss)
                    ground_enemy_group.add(dragon_boss)
                    flying_enemy_group.add(dragon_boss)
                    wave_system.wave_enemies_spawned += 1
                    wave_system.enemies_remaining -= 1
                    print(f"[BOSS SPAWN] Dragon Boss (Wave {wave_system.current_wave})")

        # Regular enemy spawning
        if wave_system.should_spawn_enemies():
            spawn_delays = enemy_spawner.get_spawn_delays()
            enemy_limits = enemy_spawner.get_enemy_limits()
            enemy_weights = enemy_spawner.get_enemy_types()
            
            current_total_enemies = len(ground_enemy_group) + len(flying_enemy_group)
            
            enemy_spawner.ground_spawn_timer += 1
            if (enemy_spawner.ground_spawn_timer >= spawn_delays['ground'] and 
                len(ground_enemy_group) < enemy_limits['ground'] and
                current_total_enemies < enemy_limits['total'] and
                wave_system.enemies_remaining > 0):
                
                enemy_type = random.choices(
                    list(enemy_weights['ground'].keys()),
                    weights=list(enemy_weights['ground'].values())
                )[0]
                
                spawn_on_platform = random.random() < 0.3
                if spawn_on_platform and platform_group:
                    platform = random.choice(list(platform_group))
                    spawn_x = random.randint(platform.rect.left + 20, platform.rect.right - 20)
                    spawn_y = platform.rect.top
                else:
                    spawn_x = random.randint(100, WIDTH - 100)
                    spawn_y = GROUND_LEVEL
                    
                if enemy_type == "frog":
                    enemy = Frog(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                elif enemy_type == "ghoul":
                    enemy = Ghoul(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                elif enemy_type == "axolotl":
                    enemy = Axolotl(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                else:
                    enemy = Witch(spawn_x, spawn_y, player, spawn_on_ground=not spawn_on_platform)
                    
                ground_enemy_group.add(enemy)
                all_sprites.add(enemy)
                enemy_spawner.ground_spawn_timer = 0
                wave_system.wave_enemies_spawned += 1
                wave_system.enemies_remaining -= 1
            
            enemy_spawner.flying_spawn_timer += 1
            if (enemy_spawner.flying_spawn_timer >= spawn_delays['flying'] and 
                len(flying_enemy_group) < enemy_limits['flying'] and
                current_total_enemies < enemy_limits['total'] and
                wave_system.enemies_remaining > 0):
                
                enemy_type = random.choices(
                    list(enemy_weights['flying'].keys()),
                    weights=list(enemy_weights['flying'].values())
                )[0]
                
                if enemy_type == "rocket":
                    enemy = RocketEnemy(random.randint(100, WIDTH - 100), random.randint(100, 300), player)
                elif enemy_type == "reaper":
                    enemy = Reaper(random.randint(100, WIDTH - 100), random.randint(100, 300), player)
                else:
                    enemy = Bat(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 200))
                    
                flying_enemy_group.add(enemy)
                all_sprites.add(enemy)
                enemy_spawner.flying_spawn_timer = 0
                wave_system.wave_enemies_spawned += 1
                wave_system.enemies_remaining -= 1

        # Bullet collisions
        for bullet in list(bullet_group):
            hit_ground = pygame.sprite.spritecollide(bullet, ground_enemy_group, False, pygame.sprite.collide_mask)
            if hit_ground:
                for enemy in hit_ground:
                    if isinstance(enemy, (FireBoss, DragonBoss)):
                        damage_taken = max(1, bullet.damage // 3)
                        enemy.health -= damage_taken
                    else:
                        enemy.health -= bullet.damage
                    
                    if enemy.health <= 0:
                        enemy.kill()
                        if bullet.is_pistol:
                            gun.ak_ammo += 1
                            gun.shotgun_ammo += 1
                        elif bullet.is_shotgun:
                            gun.shotgun_ammo += 1
                    bullet.kill()
                    break
                continue

            hit_flying = pygame.sprite.spritecollide(bullet, flying_enemy_group, False, pygame.sprite.collide_mask)
            if hit_flying:
                for enemy in hit_flying:
                    if isinstance(enemy, (FireBoss, DragonBoss)):
                        damage_taken = max(1, bullet.damage // 3)
                        enemy.health -= damage_taken
                    else:
                        enemy.health -= bullet.damage
                    
                    if enemy.health <= 0:
                        enemy.kill()
                        if bullet.is_pistol:
                            gun.ak_ammo += 1
                            gun.shotgun_ammo += 1
                        elif bullet.is_shotgun:
                            gun.shotgun_ammo += 1
                    bullet.kill()
                    break

        # Damage against player
        if player.invincible_timer == 0 and not player.god_mode:
            for projectile in enemy_projectile_group:
                if player.rect.colliderect(projectile.rect) and pygame.sprite.collide_mask(projectile, player):
                    player.health -= 1
                    player.invincible_timer = 180
                    trigger_screen_shake(8, 15)
                    if assets.player_hit_sound:
                        assets.player_hit_sound.play()
                    projectile.kill()
                    break

            if player.invincible_timer == 0:
                for enemy in ground_enemy_group:
                    if getattr(enemy, 'state', None) == "attack":
                        if player.rect.colliderect(enemy.rect) and pygame.sprite.collide_mask(enemy, player):
                            player.health -= 1
                            player.invincible_timer = 180
                            trigger_screen_shake(8, 15)
                            if assets.player_hit_sound:
                                assets.player_hit_sound.play()
                            break

            if player.invincible_timer == 0:
                for enemy in flying_enemy_group:
                    if not player.rect.colliderect(enemy.rect):
                        continue
                    if isinstance(enemy, RocketEnemy):
                        if enemy.state == "attack" and pygame.sprite.collide_mask(enemy, player):
                            player.health -= 1
                            player.invincible_timer = 180
                            trigger_screen_shake(8, 15)
                            if assets.player_hit_sound:
                                assets.player_hit_sound.play()
                            enemy.reset_to_hover()
                            break
                    elif isinstance(enemy, Bat):
                        if pygame.sprite.collide_mask(enemy, player):
                            player.health -= 1
                            player.invincible_timer = 180
                            trigger_screen_shake(8, 15)
                            if assets.player_hit_sound:
                                assets.player_hit_sound.play()
                            break
                    elif isinstance(enemy, Reaper):
                        if enemy.state == "attack" and pygame.sprite.collide_mask(enemy, player):
                            player.health -= 1
                            player.invincible_timer = 180
                            trigger_screen_shake(8, 15)
                            if assets.player_hit_sound:
                                assets.player_hit_sound.play()
                            break
                    elif isinstance(enemy, DragonBoss):
                        if enemy.state == "attack" and pygame.sprite.collide_mask(enemy, player):
                            player.health -= enemy.attack_damage
                            player.invincible_timer = 180
                            trigger_screen_shake(15, 25)
                            if assets.player_hit_sound:
                                assets.player_hit_sound.play()
                            break

        # Remove dead enemies
        for enemy in ground_enemy_group:
            if enemy.health <= 0:
                enemy.kill()
        for enemy in flying_enemy_group:
            if enemy.health <= 0:
                enemy.kill()

        # Game over check
        if player.health <= 0:
            state.final_wave = wave_system.current_wave
            state.final_score = score_system.get_final_score()
            state.current_game_state = NAME_ENTRY
            stop_music()
            print(f"[GAME OVER] Final Score: {state.final_score}, Wave: {state.final_wave}")

        # Draw game scene
        draw_background(screen)
        pygame.draw.line(screen, (100, 100, 100), (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)
        
        for sprite in all_sprites:
            if sprite is knife and not knife.active:
                continue
            screen.blit(sprite.image, (sprite.rect.x + offset_x, sprite.rect.y + offset_y))
        
        for bullet in bullet_group:
            screen.blit(bullet.image, (bullet.rect.x + offset_x, bullet.rect.y + offset_y))
        
        for projectile in enemy_projectile_group:
            screen.blit(projectile.image, (projectile.rect.x + offset_x, projectile.rect.y + offset_y))

        # HUD rendering
        font = assets.CUSTOM_FONT_REGULAR or pygame.font.Font(None, 16)
        small_font = assets.CUSTOM_FONT_SMALL or pygame.font.Font(None, 12)
        ui_y = HEIGHT - BACKGROUND_MARGIN_BOTTOM + 10
        
        player_hp_text = get_cached_text(font, f"HP: {player.health}/{player.max_health}", (255, 100, 100))
        screen.blit(player_hp_text, (20, ui_y))
        
        wave_text = get_cached_text(font, f"Wave: {wave_system.current_wave}", (255, 255, 255))
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, ui_y))
        
        if gun.current_gun == "ak":
            ammo_display = f"AK: {gun.ak_ammo}"
            ammo_color = (255, 220, 100)
        elif gun.current_gun == "shotgun":
            ammo_display = f"Shotgun: {gun.shotgun_ammo}"
            ammo_color = (255, 165, 0)
        else:
            ammo_display = "Pistol: INF"
            ammo_color = (200, 200, 255)
            
        ammo_text = get_cached_text(font, ammo_display, ammo_color)
        screen.blit(ammo_text, (WIDTH - ammo_text.get_width() - 20, ui_y))
        
        enemies_left = max(0, (wave_system.wave_enemies_total - wave_system.wave_enemies_spawned) + len(ground_enemy_group) + len(flying_enemy_group))
        enemy_text = get_cached_text(font, f"Enemies: {enemies_left}/{wave_system.wave_enemies_total}", (255, 255, 255))
        screen.blit(enemy_text, (WIDTH // 2 - enemy_text.get_width() // 2, ui_y + 20))
        
        if wave_system.wave_state == "break":
            break_time_left = (wave_system.break_duration - wave_system.break_timer) // 60 + 1
            if assets.COUNTDOWN_BG_SURF:
                screen.blit(assets.COUNTDOWN_BG_SURF, (WIDTH // 2 - 200, HEIGHT // 2 - 40))
            countdown_text = get_cached_text(font, f"Next Wave in: {break_time_left}", (255, 255, 0))
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - 10))
            
            if wave_system.is_boss_wave():
                preview_text = get_cached_text(font, "BOSS INCOMING!", (255, 50, 50))
            else:
                preview_text = get_cached_text(font, "Get Ready!", (0, 255, 255))
            screen.blit(preview_text, (WIDTH // 2 - preview_text.get_width() // 2, HEIGHT // 2 - 70))
        elif wave_system.is_boss_wave():
            boss_text = get_cached_text(font, "BOSS WAVE!", (255, 50, 50))
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, 20))

        if show_stats:
            if assets.STATS_BG_SURF:
                screen.blit(assets.STATS_BG_SURF, (10, 10))
            stats_y = 15
            screen.blit(small_font.render(f"Ground: {len(ground_enemy_group)}", True, (255, 255, 255)), (15, stats_y))
            stats_y += 25
            screen.blit(small_font.render(f"Flying: {len(flying_enemy_group)}", True, (255, 255, 255)), (15, stats_y))
            stats_y += 25
            screen.blit(small_font.render(f"Ally: {ally.combo_state.upper()}", True, (100, 255, 100)), (15, stats_y))
            stats_y += 25
            screen.blit(small_font.render(f"Platform: {'ON' if player.on_platform else 'OFF'}", True, (200, 200, 100)), (15, stats_y))
            stats_y += 25
            screen.blit(small_font.render(f"GOD MODE: {'ON' if player.god_mode else 'OFF'}", True, (255, 255, 0) if player.god_mode else (255, 255, 255)), (15, stats_y))
            stats_y += 25
            screen.blit(small_font.render("Press M to hide stats", True, (150, 150, 150)), (15, stats_y))

        escape_hint = small_font.render("Press ESC to return to menu", True, (150, 150, 150))
        screen.blit(escape_hint, (WIDTH - escape_hint.get_width() - 15, 15))

        if show_hitboxes:
            for sprite in list(all_sprites) + list(bullet_group) + list(enemy_projectile_group):
                if hasattr(sprite, "mask") and sprite.mask:
                    outline = sprite.mask.outline()
                    if outline and len(outline) >= 2:
                        outline_points = [(p[0] + sprite.rect.left + offset_x, p[1] + sprite.rect.top + offset_y) for p in outline]
                        pygame.draw.lines(screen, (255, 0, 0), True, outline_points, 2)
                pygame.draw.rect(screen, (0, 255, 0), (sprite.rect.x + offset_x, sprite.rect.y + offset_y, sprite.rect.width, sprite.rect.height), 1)

    pygame.display.flip()
    clock.tick(60)

if __name__ == "__main__":
    pygame.quit()
