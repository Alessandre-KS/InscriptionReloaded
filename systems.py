import random
from constants import WIDTH, HEIGHT, GROUND_LEVEL, DEBUG_START_WAVE
import assets
import state
from enemies import FireBoss, DragonBoss, Frog, Ghoul, Axolotl, RocketEnemy, Reaper, Bat

class WaveSystem:
    def __init__(self):
        self.current_wave = DEBUG_START_WAVE
        self.wave_timer = 0
        self.wave_duration = 1800
        self.bosses_spawned_this_wave = False
        self.fire_boss_count = 0
        self.max_fire_bosses = 2
        self.total_bosses_spawned = 0
        
        self.wave_state = "break"  # "break" or "active"
        self.break_timer = 0
        self.break_duration = 300  # 5 seconds at 60 FPS
        self.enemies_remaining = 0
        self.wave_enemies_spawned = 0
        self.wave_enemies_total = 0
        
        # Boss minion spawning
        self.boss_minion_timer = 0
        self.boss_minion_delay = 210  # 3.5 seconds
        self.boss_minions_spawned = 0
        self.max_boss_minions = 15
        
    def update(self):
        if self.wave_state == "break":
            self.break_timer += 1
            if self.break_timer == 1:
                assets.update_background_for_wave(self.current_wave)
                if self.is_boss_wave():
                    assets.play_music("boss")
                    print("[SOUND] Boss music started during countdown!")
            if self.break_timer >= self.break_duration:
                self.start_wave()
                
        elif self.wave_state == "active":
            self.wave_timer += 1
            if self.is_boss_wave() and self.bosses_spawned_this_wave:
                self.boss_minion_timer += 1
                if (self.boss_minion_timer >= self.boss_minion_delay and 
                    self.boss_minions_spawned < self.max_boss_minions):
                    self.spawn_boss_minions()
                    self.boss_minion_timer = 0
            
            ground_count = len(state.ground_enemy_group) if state.ground_enemy_group is not None else 0
            flying_count = len(state.flying_enemy_group) if state.flying_enemy_group is not None else 0
            current_enemies = ground_count + flying_count
            
            if (self.wave_enemies_spawned >= self.wave_enemies_total and current_enemies == 0):
                self.complete_wave()
                
    def start_wave(self):
        state.boss_music_playing = False
        state.dragon_roar_played = False
        
        self.wave_state = "active"
        self.break_timer = 0
        self.wave_timer = 0
        self.bosses_spawned_this_wave = False
        self.wave_enemies_spawned = 0
        self.boss_minion_timer = 0
        self.boss_minions_spawned = 0
        
        if not self.is_boss_wave() and assets.current_music != "gameplay":
            assets.play_music("gameplay")
        
        gun = state.gun
        player = state.player
        if gun:
            if self.current_wave > 1:
                bonus_waves = self.current_wave - 1
                gun.ak_ammo = max(gun.ak_ammo, 15 + (bonus_waves * 2))
                gun.shotgun_ammo = max(gun.shotgun_ammo, 8 + (bonus_waves * 1))
                if player:
                    player.health = player.max_health
                print(f"[BALANCE] Starting wave {self.current_wave} with balanced ammo!")
            elif gun.ak_ammo < 10 and self.is_boss_wave():
                gun.ak_ammo = 15
            elif gun.ak_ammo < 5:
                gun.ak_ammo = 10
            
        if self.is_boss_wave():
            self.wave_enemies_total = 1
            self.enemies_remaining = self.wave_enemies_total
            print(f"[WAVE SYSTEM] BOSS WAVE {self.current_wave} started! Boss spawning immediately.")
        else:
            base_enemies = 5 + (self.current_wave * 2)
            self.wave_enemies_total = min(base_enemies, 35)
            self.enemies_remaining = self.wave_enemies_total
            print(f"[WAVE SYSTEM] Wave {self.current_wave} started! Enemies: {self.wave_enemies_total}")
        
    def is_boss_wave(self):
        return self.current_wave >= 10 and self.current_wave % 10 == 0
                
    def complete_wave(self):
        state.boss_music_playing = False
        self.wave_state = "break"
        self.break_timer = 0
        
        just_completed_boss_wave = (self.current_wave >= 10 and self.current_wave % 10 == 0)
        if just_completed_boss_wave:
            assets.play_music("gameplay")
            print("[SOUND] Switching back to gameplay music after boss victory")
        
        player = state.player
        gun = state.gun
        score_system = state.score_system

        if self.is_boss_wave():
            if player:
                player.health = player.max_health
            if score_system:
                score_system.add_boss_victory_bonus(self.current_wave)
            ak_reward = 20
            shotgun_reward = 10
            if gun:
                gun.ak_ammo = min(gun.ak_ammo + ak_reward, 50)
                gun.shotgun_ammo = min(gun.shotgun_ammo + shotgun_reward, 25)
            print("[BOSS VICTORY] Player fully healed!")
            print(f"[BOSS BONUS] +{ak_reward} AK ammo! +{shotgun_reward} Shotgun ammo!")
            
            minions_killed = 0
            all_enemies = []
            if state.ground_enemy_group:
                all_enemies.extend(list(state.ground_enemy_group))
            if state.flying_enemy_group:
                all_enemies.extend(list(state.flying_enemy_group))

            for enemy in all_enemies:
                if not isinstance(enemy, (FireBoss, DragonBoss)):
                    enemy.kill()
                    minions_killed += 1
            if minions_killed > 0:
                print(f"[BOSS CLEANUP] Despawned {minions_killed} remaining minions")
        else:
            if player:
                player.heal_between_waves()
            if score_system:
                score_system.add_wave_completion_bonus(self.current_wave)
            
            ak_reward = 8 + min(self.current_wave, 10)
            shotgun_reward = 4 + min(self.current_wave // 2, 5)
            if gun:
                gun.ak_ammo = min(gun.ak_ammo + ak_reward, 50)
                gun.shotgun_ammo = min(gun.shotgun_ammo + shotgun_reward, 25)
            print(f"[WAVE COMPLETION] +{ak_reward} AK ammo! +{shotgun_reward} Shotgun ammo!")

        if score_system:
            score_system.update_highest_wave(self.current_wave)
        
        self.current_wave += 1
        self.wave_timer = 0
        print(f"[WAVE SYSTEM] Wave {self.current_wave-1} completed! Moving to Wave {self.current_wave}")
        
    def spawn_boss_minions(self):
        if self.boss_minions_spawned >= self.max_boss_minions:
            return
            
        if self.current_wave >= 50:
            max_spawn = 1
        elif self.current_wave >= 30:
            max_spawn = 2
        else:
            max_spawn = 3
            
        minion_count = random.randint(1, max_spawn)
        
        for _ in range(minion_count):
            if self.boss_minions_spawned >= self.max_boss_minions:
                break
                
            if random.random() < 0.7:
                enemy_type = random.choice(["frog", "ghoul", "axolotl"])
                spawn_on_platform = random.random() < 0.3
                
                if spawn_on_platform and state.platform_group:
                    platform = random.choice(list(state.platform_group))
                    spawn_x = random.randint(platform.rect.left + 20, platform.rect.right - 20)
                    spawn_y = platform.rect.top
                else:
                    spawn_x = random.randint(100, WIDTH - 100)
                    spawn_y = GROUND_LEVEL
                    
                if enemy_type == "frog":
                    enemy = Frog(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                elif enemy_type == "ghoul":
                    enemy = Ghoul(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                else:
                    enemy = Axolotl(spawn_x, spawn_y, spawn_on_ground=not spawn_on_platform)
                    
                if state.ground_enemy_group is not None:
                    state.ground_enemy_group.add(enemy)
                if state.all_sprites is not None:
                    state.all_sprites.add(enemy)
            else:
                enemy_type = random.choice(["rocket", "reaper", "bat"])
                spawn_x = random.randint(100, WIDTH - 100)
                spawn_y = random.randint(100, HEIGHT - 200)
                
                if enemy_type == "rocket":
                    enemy = RocketEnemy(spawn_x, spawn_y, state.player)
                elif enemy_type == "reaper":
                    enemy = Reaper(spawn_x, spawn_y, state.player)
                else:
                    enemy = Bat(spawn_x, spawn_y)
                    
                if state.flying_enemy_group is not None:
                    state.flying_enemy_group.add(enemy)
                if state.all_sprites is not None:
                    state.all_sprites.add(enemy)
            
            self.boss_minions_spawned += 1
            self.wave_enemies_spawned += 1
            self.wave_enemies_total += 1
            self.enemies_remaining += 1
            
        print(f"[BOSS MINIONS] Spawned {minion_count} minions ({self.boss_minions_spawned}/{self.max_boss_minions} total)")
            
    def should_spawn_enemies(self):
        if self.is_boss_wave() and self.bosses_spawned_this_wave:
            return False
        return (self.wave_state == "active" and 
                self.wave_enemies_spawned < self.wave_enemies_total and
                self.enemies_remaining > 0)
        
    def should_spawn_bosses(self):
        if (self.wave_state == "active" and 
            not self.bosses_spawned_this_wave and
            self.current_wave >= 10 and 
            self.current_wave % 10 == 0):
            
            self.bosses_spawned_this_wave = True
            return True
        return False
        
    def get_bosses_to_spawn(self):
        bosses_to_spawn = []
        wave = self.current_wave
        
        if wave == 10 and self.fire_boss_count < self.max_fire_bosses:
            bosses_to_spawn.append(("fire", "left"))
            self.fire_boss_count += 1
            
        elif wave == 20:
            bosses_to_spawn.append(("dragon", "right"))
            
        elif wave >= 30 and wave % 10 == 0:
            if self.fire_boss_count < self.max_fire_bosses:
                side = "left" if self.fire_boss_count == 0 else "right"
                bosses_to_spawn.append(("fire", side))
                self.fire_boss_count += 1
                
            dragon_count = 1 + ((wave - 30) // 10)
            for i in range(dragon_count):
                bosses_to_spawn.append(("dragon", f"position_{i}"))
                
        self.total_bosses_spawned += len(bosses_to_spawn)
        return bosses_to_spawn

class EnemySpawner:
    def __init__(self, wave_system):
        self.wave_system = wave_system
        self.ground_spawn_timer = 0
        self.flying_spawn_timer = 0
        self.bat_spawn_timer = 0
        
        self.base_ground_delay = 90
        self.base_flying_delay = 180
        self.base_bat_delay = 150
        
        self.cached_wave = -1
        self.cached_delays = None
        self.cached_limits = None
        self.cached_weights = None
        
    def _update_wave_cache(self):
        wave = self.wave_system.current_wave
        if wave == self.cached_wave:
            return
        self.cached_wave = wave
        speed_factor = max(0.3, 1.0 - (min(wave, 50) * 0.012))
        self.cached_delays = {
            'ground': max(30, int(self.base_ground_delay * speed_factor)),
            'flying': max(50, int(self.base_flying_delay * speed_factor)),
            'bat': max(70, int(self.base_bat_delay * speed_factor))
        }
        ground_limit = min(8 + wave // 2, 20)
        flying_limit = min(4 + wave // 3, 12)
        self.cached_limits = {
            'ground': ground_limit,
            'flying': flying_limit,
            'total': min(ground_limit + flying_limit, 30)
        }
        self.cached_weights = {
            'ground': {
                'frog': max(0.2, 0.5 - (wave * 0.015)),
                'ghoul': min(0.5, 0.2 + (wave * 0.008)),
                'axolotl': min(0.4, 0.15 + (wave * 0.006)),
                'witch': min(0.4, 0.1 + (wave * 0.01))
            },
            'flying': {
                'rocket': max(0.3, 0.6 - (wave * 0.01)),
                'reaper': min(0.6, 0.2 + (wave * 0.012)),
                'bat': max(0.1, 0.3 - (wave * 0.005))
            }
        }
        
    def get_spawn_delays(self):
        self._update_wave_cache()
        return self.cached_delays
        
    def get_enemy_limits(self):
        self._update_wave_cache()
        return self.cached_limits
        
    def get_enemy_types(self):
        self._update_wave_cache()
        return self.cached_weights

class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.highest_wave = 1
        
    def update_highest_wave(self, wave):
        if wave > self.highest_wave:
            self.highest_wave = wave
            
    def add_wave_completion_bonus(self, wave):
        wave_bonus = 10
        self.score += wave_bonus
        return wave_bonus
        
    def add_boss_victory_bonus(self, wave):
        boss_bonus = 50
        self.score += boss_bonus
        return boss_bonus
        
    def get_final_score(self):
        return self.score
