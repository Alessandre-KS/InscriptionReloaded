import os
import sys

# Headless mode for automated tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

print("--- Testing Modular Structure ---")

# 1. Test constants
import constants
assert constants.WIDTH == 960
assert constants.HEIGHT == 540
assert len(constants.platform_positions) == 7
print("1. constants.py imported and verified!")

# 2. Test database
import database
database.init_database()
data = database.get_leaderboard_data()
assert isinstance(data, list)
print("2. database.py imported and verified!")

# 3. Test state
import state
assert state.current_game_state == constants.TITLE_SCREEN
state.trigger_screen_shake(5, 10)
assert state.screen_shake_intensity == 5
ox, oy = state.update_screen_shake()
assert state.screen_shake_duration == 9
print("3. state.py imported and verified!")

# 4. Test assets
import pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
import assets
assets.initialize_fonts()
assets.load_sounds()
assets.load_background()
assets.initialize_assets()
assert len(assets.PLAYER_FRAMES_RIGHT) == 4
assert len(assets.FROG_FRAMES) == 8
print("4. assets.py imported and verified!")

# 5. Test weapons
import weapons
bullet = weapons.Bullet((100, 100), 0)
assert bullet.rect is not None
print("5. weapons.py imported and verified!")

# 6. Test player
import player
p = player.Player(480, constants.GROUND_LEVEL)
plat = player.Platform(100, 100)
ally = player.Ally(pygame.sprite.Group())
assert p.rect is not None and plat.rect is not None and ally.rect is not None
print("6. player.py imported and verified!")

# 7. Test enemies
import enemies
frog = enemies.Frog(200, constants.GROUND_LEVEL)
ghoul = enemies.Ghoul(300, constants.GROUND_LEVEL)
dragon = enemies.DragonBoss(500, 150, p)
assert frog.rect is not None and ghoul.rect is not None and dragon.rect is not None
print("7. enemies.py imported and verified!")

# 8. Test systems
import systems
ws = systems.WaveSystem()
spawner = systems.EnemySpawner(ws)
score = systems.ScoreSystem()
assert ws.current_wave == 1
assert spawner.get_spawn_delays() is not None
assert score.get_final_score() == 0
print("8. systems.py imported and verified!")

# 9. Test ui
import ui
start_btn, lb_btn, htp_btn = ui.draw_title_screen()
assert start_btn is not None
print("9. ui.py imported and verified!")

# 10. Test main entry point and re-exports
import main
assert main.Player is player.Player
assert main.Frog is enemies.Frog
assert main.WaveSystem is systems.WaveSystem
assert main.Bullet is weapons.Bullet
print("10. main.py imported and verified (all re-exports intact)!")

print("\n>>> ALL 10 MODULES TESTED AND VERIFIED SUCCESSFULLY! <<<")
