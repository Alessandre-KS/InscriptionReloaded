import pygame
from constants import WIDTH, HEIGHT, GROUND_LEVEL
import assets
import state

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=120, height=20):
        super().__init__()
        self.original_image = assets.PLATFORM_IMAGE
        self.image = assets.PLATFORM_IMAGE
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = assets.PLATFORM_MASK

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = assets.PLAYER_FRAMES_RIGHT
        self.current_frame = 3
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midbottom=(x, GROUND_LEVEL))
        self.mask = assets.PLAYER_MASKS_RIGHT[self.current_frame]

        self.speed = 5
        self.vel_y = 0
        self.gravity = 0.8
        self.on_ground = False
        self.on_platform = False
        self.current_platform = None
        self.facing_right = True
        self.anim_timer = 0
        self.anim_delay = 6

        self.max_health = 25
        self.health = self.max_health
        self.invincible_timer = 0
        self.god_mode = False

        self.wave_heal_amount = 5
        self.min_health_for_heal = 30

    def update_keyboard(self, keys, platforms):
        dx = 0
        if keys[pygame.K_a]:
            dx = -self.speed
            self.facing_right = False
        if keys[pygame.K_d]:
            dx = self.speed
            self.facing_right = True

        self.rect.x += dx

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and (self.on_ground or self.on_platform):
            self.vel_y = -15
            self.on_ground = False
            self.on_platform = False
            self.current_platform = None

        self.update_physics(platforms)
        self.update_animation(dx)

    def update_physics(self, platforms):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        self.on_ground = False
        self.on_platform = False
        self.current_platform = None

        if self.vel_y >= 0:
            for platform in platforms:
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.bottom <= platform.rect.top + 20 and
                    self.rect.right > platform.rect.left + 5 and
                    self.rect.left < platform.rect.right - 5):
                    
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_platform = True
                    self.current_platform = platform
                    break

        if not self.on_platform and self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def update_animation(self, dx):
        if dx != 0:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 3
        else:
            self.current_frame = 3

        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if self.facing_right:
            self.image = assets.PLAYER_FRAMES_RIGHT[self.current_frame]
            self.mask = assets.PLAYER_MASKS_RIGHT[self.current_frame]
        else:
            self.image = assets.PLAYER_FRAMES_LEFT[self.current_frame]
            self.mask = assets.PLAYER_MASKS_LEFT[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))

        if self.god_mode:
            if pygame.time.get_ticks() % 1000 < 500:
                self.image = self.image.copy()
                self.image.set_alpha(150)
        elif self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer % 30 < 15:
                self.image = self.image.copy()
                self.image.set_alpha(150)

    def heal_between_waves(self):
        if self.health < self.min_health_for_heal:
            self.health = min(self.max_health, self.health + self.wave_heal_amount)
            print(f"[HEAL] Player healed to {self.health} HP")

    def toggle_god_mode(self):
        self.god_mode = not self.god_mode
        print(f"[GOD MODE] {'ON' if self.god_mode else 'OFF'}")

class Ally(pygame.sprite.Sprite):
    def __init__(self, ground_enemy_group):
        super().__init__()
        self.frames = assets.ALLY_FRAMES
        self.current_frame = 15
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, GROUND_LEVEL))
        self.mask = assets.ALLY_MASKS[self.current_frame]
        
        self.ground_enemy_group = ground_enemy_group
        
        self.combo_state = "idle"
        self.combo_step = 0
        self.combo_timer = 0
        self.attack_cooldown = 0
        
        self.speed = 3
        self.vel_y = 0
        self.gravity = 0.8
        self.on_ground = True
        
        self.attack_range = 200
        self.damage = 1
        
        self.anim_timer = 0
        self.anim_delay = 15
        self.running_frames = [15, 13, 14]
        self.running_frame_index = 0
        self.facing_right = True

        self.attack_delays = {
            0: 8, 1: 6, 2: 4, 3: 6, 4: 6, 5: 6, 6: 4, 7: 8, 8: 10, 9: 6, 10: 4
        }

        self.current_target = None
        self.target_reached = False

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        nearest_enemy = self.find_nearest_ground_level_enemy()
        
        if nearest_enemy:
            distance = abs(nearest_enemy.rect.centerx - self.rect.centerx)
            
            if distance <= self.attack_range and self.attack_cooldown == 0:
                if self.combo_state != "attacking" and self.combo_state != "recovery":
                    self.combo_state = "attacking"
                    self.combo_step = 0
                    self.combo_timer = 0
                    self.current_target = nearest_enemy
                    print(f"[ALLY] Starting combo against {nearest_enemy.__class__.__name__}!")
            elif distance > self.attack_range and self.combo_state == "idle":
                self.combo_state = "running"
                self.current_target = nearest_enemy
                self.move_toward_target()
            else:
                if self.combo_state != "attacking" and self.combo_state != "recovery":
                    self.combo_state = "idle"
                    self.current_frame = 15
        else:
            if self.combo_state != "attacking" and self.combo_state != "recovery":
                self.combo_state = "idle"
                self.current_frame = 15

        if self.combo_state == "idle":
            self.idle_behavior()
        elif self.combo_state == "running":
            self.running_behavior()
        elif self.combo_state == "attacking":
            self.attack_behavior()
        elif self.combo_state == "recovery":
            self.recovery_behavior()

        if self.current_target:
            if self.current_target.rect.centerx > self.rect.centerx:
                self.facing_right = True
            else:
                self.facing_right = False

        self.update_animation()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def find_nearest_ground_level_enemy(self):
        nearest = None
        nearest_distance = float('inf')
        for enemy in self.ground_enemy_group:
            if hasattr(enemy, 'on_ground') and enemy.on_ground and not getattr(enemy, 'on_platform', False):
                distance = abs(enemy.rect.centerx - self.rect.centerx)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest = enemy
        return nearest

    def move_toward_target(self):
        if not self.current_target:
            return
        target_x = self.current_target.rect.centerx
        distance_to_target = abs(self.rect.centerx - target_x)
        if distance_to_target > 50:
            if self.rect.centerx < target_x:
                self.rect.x += min(self.speed, distance_to_target)
            else:
                self.rect.x -= min(self.speed, distance_to_target)

    def move_toward_target_during_attack(self):
        if not self.current_target:
            return
        target_x = self.current_target.rect.centerx
        distance_to_target = abs(self.rect.centerx - target_x)
        if distance_to_target > 30:
            attack_move_speed = 2
            if self.rect.centerx < target_x:
                self.rect.x += attack_move_speed
            else:
                self.rect.x -= attack_move_speed

    def idle_behavior(self):
        self.current_frame = 15

    def running_behavior(self):
        self.anim_timer += 1
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            self.running_frame_index = (self.running_frame_index + 1) % len(self.running_frames)
            self.current_frame = self.running_frames[self.running_frame_index]
        self.move_toward_target()

    def attack_behavior(self):
        self.combo_timer += 1
        current_delay = self.attack_delays.get(self.combo_step, 4)
        
        if self.combo_step < 6 or self.combo_step > 8:
            self.move_toward_target_during_attack()
        
        if self.combo_step == 0:
            if self.combo_timer >= current_delay:
                self.combo_step = 1
                self.combo_timer = 0
                self.current_frame = 2
        elif self.combo_step == 1:
            if self.combo_timer >= current_delay:
                self.deal_damage_in_front()
                self.combo_step = 2
                self.combo_timer = 0
                self.current_frame = 4
        elif self.combo_step == 2:
            if self.combo_timer >= current_delay:
                self.combo_step = 3
                self.combo_timer = 0
                self.current_frame = 5
        elif self.combo_step == 3:
            if self.combo_timer >= current_delay:
                self.deal_damage_in_front()
                self.combo_step = 4
                self.combo_timer = 0
                self.current_frame = 7
        elif self.combo_step == 4:
            if self.combo_timer >= current_delay:
                self.combo_step = 5
                self.combo_timer = 0
                self.current_frame = 9
        elif self.combo_step == 5:
            if self.combo_timer >= current_delay:
                self.deal_damage_in_front()
                self.combo_step = 6
                self.combo_timer = 0
                self.current_frame = 11
        elif self.combo_step == 6:
            if self.combo_timer >= current_delay:
                self.combo_step = 7
                self.combo_timer = 0
                self.current_frame = 12
                if self.on_ground:
                    self.vel_y = -12
                    self.on_ground = False
                    self.deal_damage_above()
        elif self.combo_step == 7:
            if self.combo_timer >= current_delay:
                self.combo_step = 8
                self.combo_timer = 0
                self.current_frame = 14
        elif self.combo_step == 8:
            if self.current_target:
                jump_speed = 8
                if self.current_target.rect.centerx > self.rect.centerx:
                    self.rect.x += jump_speed
                else:
                    self.rect.x -= jump_speed
            if self.combo_timer >= current_delay:
                self.combo_step = 9
                self.combo_timer = 0
                self.current_frame = 17
        elif self.combo_step == 9:
            if self.combo_timer >= current_delay:
                self.deal_damage_in_front()
                self.combo_step = 10
                self.combo_timer = 0
                self.current_frame = 18
        elif self.combo_step == 10:
            if self.combo_timer >= current_delay:
                self.combo_state = "recovery"
                self.combo_timer = 0
                self.attack_cooldown = 120

    def deal_damage_in_front(self):
        for enemy in self.ground_enemy_group:
            if hasattr(enemy, 'on_ground'):
                distance = abs(enemy.rect.centerx - self.rect.centerx)
                if distance < 80:
                    enemy.health -= self.damage
                    print(f"[ALLY HIT] {enemy.__class__.__name__} HP: {enemy.health}")
                    knockback_dir = 1 if enemy.rect.centerx > self.rect.centerx else -1
                    enemy.rect.x += knockback_dir * 8
                    if hasattr(enemy, 'vel_y'):
                        enemy.vel_y = -4

    def deal_damage_above(self):
        for enemy in self.ground_enemy_group:
            if hasattr(enemy, 'on_ground'):
                if (abs(enemy.rect.centerx - self.rect.centerx) < 50 and 
                    enemy.rect.bottom < self.rect.top and 
                    enemy.rect.top > self.rect.top - 100):
                    
                    enemy.health -= self.damage
                    print(f"[ALLY UPPERCUT] {enemy.__class__.__name__} HP: {enemy.health}")
                    if hasattr(enemy, 'vel_y'):
                        enemy.vel_y = -8

    def recovery_behavior(self):
        self.combo_timer += 1
        if self.combo_timer >= 45:
            self.combo_state = "idle"
            self.combo_timer = 0
            self.current_target = None

    def update_animation(self):
        if self.current_frame == 10:
            flip = self.facing_right
        else:
            flip = not self.facing_right

        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if flip:
            self.image = assets.ALLY_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.ALLY_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.ALLY_FRAMES[self.current_frame]
            self.mask = assets.ALLY_MASKS[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))
