import math
import random
import pygame
from constants import WIDTH, HEIGHT, GROUND_LEVEL
from state import trigger_screen_shake
import assets
import state

class Bat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = assets.BAT_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = assets.BAT_MASKS[self.current_frame]
        
        self.speed_x = random.choice([-2, -1, 1, 2])
        self.speed_y = random.choice([-2, -1, 1, 2])
        self.anim_timer = 0
        self.anim_delay = 10
        self.health = 1
        self.float_timer = 0
        self.float_speed = 0.5
        self.damage = 1
        self.contact_cooldown = 0

    def update(self, player=None):
        # Movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Floating effect
        self.float_timer += 1
        self.rect.y += math.sin(self.float_timer * 0.1) * self.float_speed
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = abs(self.speed_x)
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.speed_x = -abs(self.speed_x)
            
        if self.rect.top < 50:
            self.rect.top = 50
            self.speed_y = abs(self.speed_y)
        elif self.rect.bottom > HEIGHT - 100:
            self.rect.bottom = HEIGHT - 100
            self.speed_y = -abs(self.speed_y)
        
        # Random direction changes
        if random.random() < 0.01:
            self.speed_x = random.choice([-2, -1, 1, 2])
            self.speed_y = random.choice([-2, -1, 1, 2])
        
        # Animation
        self.anim_timer += 1
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Flip based on direction
        if self.speed_x > 0:
            self.image = assets.BAT_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.BAT_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.BAT_FRAMES[self.current_frame]
            self.mask = assets.BAT_MASKS[self.current_frame]
            
        if self.contact_cooldown > 0:
            self.contact_cooldown -= 1

# Frog Enemy Class - Eto yung ground enemy na frog
class Frog(pygame.sprite.Sprite):
    def __init__(self, x, y, spawn_on_ground=True):
        super().__init__()
        self.frames = assets.FROG_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        if spawn_on_ground:
            self.rect = self.image.get_rect(midbottom=(x, GROUND_LEVEL))
        else:
            self.rect = self.image.get_rect(midbottom=(x, y))
            
        self.mask = assets.FROG_MASKS[self.current_frame]
        
        # AI states: "walk", "attack", "idle"
        self.state = "walk"
        self.anim_timer = 0
        self.anim_delay = 8
        self.frame_counter = 0
        self.attack_cooldown = 0
        self.speed = 2
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = spawn_on_ground
        self.on_platform = not spawn_on_ground
        self.current_platform = None
        self.facing_right = False
        self.health = 3
        self.idle_timer = 0
        self.idle_duration = 60
        self.last_player_x = 0
        self.spawn_y = y if not spawn_on_ground else GROUND_LEVEL

    def update(self, player):
        # Face player
        if player.rect.centerx > self.rect.centerx:
            self.facing_right = True
        else:
            self.facing_right = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # State machine
        if self.state == "walk":
            self.walk_behavior(player)
        elif self.state == "attack":
            self.attack_behavior(player)
        elif self.state == "idle":
            self.idle_behavior(player)

        # Apply gravity if not on platform
        if not self.on_platform:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

        # Platform collision
        was_on_platform = self.on_platform
        self.on_platform = False
        self.current_platform = None

        if self.vel_y >= 0:
            for platform in (state.platform_group or []):
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.bottom <= platform.rect.top + 20 and
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_platform = True
                    self.current_platform = platform
                    break

        # Ground collision
        if not self.on_platform and self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        # Fall off platform if at edge
        if self.on_platform and self.current_platform:
            if (self.rect.bottom != self.current_platform.rect.top or
                self.rect.right <= self.current_platform.rect.left or 
                self.rect.left >= self.current_platform.rect.right):
                self.on_platform = False
                self.current_platform = None
                self.vel_y = 0

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.facing_right = True
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.facing_right = False

        self.update_animation()

    def walk_behavior(self, player):
        player_on_platform = player.on_platform
        player_above = player.rect.bottom < self.rect.top
        
        # Go idle if player is on platform above
        if player_on_platform and player_above and abs(player.rect.centerx - self.rect.centerx) < 150:
            self.state = "idle"
            self.idle_timer = 0
            return

        # Move toward player
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        # Attack if close enough
        if abs(player.rect.centerx - self.rect.centerx) < 120 and self.attack_cooldown == 0:
            self.state = "attack"
            self.frame_counter = 4

    def idle_behavior(self, player):
        self.idle_timer += 1
        
        player_moved = abs(player.rect.centerx - self.last_player_x) > 50
        player_still_above = player.on_platform and player.rect.bottom < self.rect.top
        player_close = abs(player.rect.centerx - self.rect.centerx) < 150
        
        # Return to walking if conditions change
        if self.idle_timer >= self.idle_duration or not player_still_above or not player_close or player_moved:
            self.state = "walk"
            self.idle_timer = 0
        
        self.last_player_x = player.rect.centerx

    def attack_behavior(self, player):
        self.frame_counter += 1

        # Attack animation sequence
        if self.frame_counter == 5:
            self.current_frame = 4
        elif self.frame_counter == 6:
            if self.on_ground:
                self.vel_y = -10
            self.current_frame = 5
        elif self.frame_counter == 7:
            lunge = 6 if self.facing_right else -6
            self.rect.x += lunge
            self.current_frame = 6

            # Damage player on contact
            if player.invincible_timer == 0 and not player.god_mode:
                if pygame.sprite.collide_mask(self, player):
                    player.health -= 1
                    player.invincible_timer = 180
                    trigger_screen_shake(8, 15)
                    
                    if assets.player_hit_sound:
                        assets.player_hit_sound.play()
                    print(f"[HIT] Player health: {player.health}")
        elif self.frame_counter == 8:
            self.current_frame = 7
        elif self.frame_counter > 8:
            self.state = "walk"
            self.frame_counter = 0
            self.attack_cooldown = random.randint(180, 300)

    def update_animation(self):
        if self.state == "walk":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
        elif self.state == "idle":
            self.current_frame = 0

        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if self.facing_right:
            self.image = assets.FROG_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.FROG_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.FROG_FRAMES[self.current_frame]
            self.mask = assets.FROG_MASKS[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))

# Ghoul Enemy Class - Eto yung ground enemy na ghoul
class Ghoul(pygame.sprite.Sprite):
    def __init__(self, x, y, spawn_on_ground=True):
        super().__init__()
        self.frames = assets.GHOUL_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        if spawn_on_ground:
            self.rect = self.image.get_rect(midbottom=(x, GROUND_LEVEL))
        else:
            self.rect = self.image.get_rect(midbottom=(x, y))
            
        self.mask = assets.GHOUL_MASKS[self.current_frame]
        
        self.state = "walk"
        self.anim_timer = 0
        self.anim_delay = 10
        self.frame_counter = 0
        self.attack_cooldown = 0
        self.speed = 1.5
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = spawn_on_ground
        self.on_platform = not spawn_on_ground
        self.current_platform = None
        self.facing_right = False
        self.health = 4
        self.idle_timer = 0
        self.idle_duration = 80
        self.last_player_x = 0
        self.spawn_y = y if not spawn_on_ground else GROUND_LEVEL

    def update(self, player):
        # Face player
        if player.rect.centerx > self.rect.centerx:
            self.facing_right = True
        else:
            self.facing_right = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # State machine
        if self.state == "walk":
            self.walk_behavior(player)
        elif self.state == "attack":
            self.attack_behavior(player)
        elif self.state == "idle":
            self.idle_behavior(player)

        # Apply gravity
        if not self.on_platform:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

        # Platform collision
        was_on_platform = self.on_platform
        self.on_platform = False
        self.current_platform = None

        if self.vel_y >= 0:
            for platform in (state.platform_group or []):
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.bottom <= platform.rect.top + 20 and
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_platform = True
                    self.current_platform = platform
                    break

        # Ground collision
        if not self.on_platform and self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        # Fall off platform
        if self.on_platform and self.current_platform:
            if (self.rect.bottom != self.current_platform.rect.top or
                self.rect.right <= self.current_platform.rect.left or 
                self.rect.left >= self.current_platform.rect.right):
                self.on_platform = False
                self.current_platform = None
                self.vel_y = 0

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.facing_right = True
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.facing_right = False

        self.update_animation()

    def walk_behavior(self, player):
        player_on_platform = player.on_platform
        player_above = player.rect.bottom < self.rect.top
        
        # Go idle if player is above on platform
        if player_on_platform and player_above and abs(player.rect.centerx - self.rect.centerx) < 150:
            self.state = "idle"
            self.idle_timer = 0
            return

        # Move toward player
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        # Attack if close
        if abs(player.rect.centerx - self.rect.centerx) < 100 and self.attack_cooldown == 0:
            self.state = "attack"
            self.frame_counter = 4

    def idle_behavior(self, player):
        self.idle_timer += 1
        
        player_moved = abs(player.rect.centerx - self.last_player_x) > 50
        player_still_above = player.on_platform and player.rect.bottom < self.rect.top
        player_close = abs(player.rect.centerx - self.rect.centerx) < 150
        
        # Return to walking
        if self.idle_timer >= self.idle_duration or not player_still_above or not player_close or player_moved:
            self.state = "walk"
            self.idle_timer = 0
        
        self.last_player_x = player.rect.centerx

    def attack_behavior(self, player):
        self.frame_counter += 1

        # Attack animation
        if self.frame_counter == 1:
            self.current_frame = 4
        elif self.frame_counter == 3:
            self.current_frame = 5
        elif self.frame_counter == 5:
            self.current_frame = 6
            # Damage player
            if player.invincible_timer == 0 and not player.god_mode:
                if pygame.sprite.collide_mask(self, player):
                    player.health -= 1
                    player.invincible_timer = 180
                    trigger_screen_shake(8, 15)
                    
                    if assets.player_hit_sound:
                        assets.player_hit_sound.play()
                    print(f"[GHOUL HIT] Player health: {player.health}")
        elif self.frame_counter == 7:
            self.current_frame = 6
        elif self.frame_counter > 8:
            self.state = "walk"
            self.frame_counter = 0
            self.attack_cooldown = random.randint(200, 350)

    def update_animation(self):
        if self.state == "walk":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
        elif self.state == "idle":
            self.current_frame = 0

        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if self.facing_right:
            self.image = assets.GHOUL_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.GHOUL_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.GHOUL_FRAMES[self.current_frame]
            self.mask = assets.GHOUL_MASKS[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))

# Axolotl Enemy Class - Eto yung ground enemy na axolotl
class Axolotl(pygame.sprite.Sprite):
    def __init__(self, x, y, spawn_on_ground=True):
        super().__init__()
        self.frames = assets.AXOLOTL_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        if spawn_on_ground:
            self.rect = self.image.get_rect(midbottom=(x, GROUND_LEVEL))
        else:
            self.rect = self.image.get_rect(midbottom=(x, y))
            
        self.mask = assets.AXOLOTL_MASKS[self.current_frame]
        
        self.state = "idle"
        self.anim_timer = 0
        self.anim_delay = 10
        self.frame_counter = 0
        self.attack_cooldown = 0
        self.speed = 1.2
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = spawn_on_ground
        self.on_platform = not spawn_on_ground
        self.current_platform = None
        self.facing_right = False
        self.health = 3
        self.idle_timer = 0
        self.idle_duration = 90
        self.last_player_x = 0
        self.spawn_y = y if not spawn_on_ground else GROUND_LEVEL

    def update(self, player):
        # Face player
        if player.rect.centerx > self.rect.centerx:
            self.facing_right = True
        else:
            self.facing_right = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # State machine
        if self.state == "idle":
            self.idle_behavior(player)
        elif self.state == "attack":
            self.attack_behavior(player)
        elif self.state == "recovery":
            self.recovery_behavior(player)

        # Apply gravity
        if not self.on_platform:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

        # Platform collision
        was_on_platform = self.on_platform
        self.on_platform = False
        self.current_platform = None

        if self.vel_y >= 0:
            for platform in (state.platform_group or []):
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.bottom <= platform.rect.top + 20 and
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_platform = True
                    self.current_platform = platform
                    break

        # Ground collision
        if not self.on_platform and self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        # Fall off platform
        if self.on_platform and self.current_platform:
            if (self.rect.bottom != self.current_platform.rect.top or
                self.rect.right <= self.current_platform.rect.left or 
                self.rect.left >= self.current_platform.rect.right):
                self.on_platform = False
                self.current_platform = None
                self.vel_y = 0

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.facing_right = True
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.facing_right = False

        self.update_animation()

    def idle_behavior(self, player):
        self.current_frame = 0
        
        player_on_platform = player.on_platform
        player_above = player.rect.bottom < self.rect.top
        
        # Stay idle if player is above on platform
        if player_on_platform and player_above and abs(player.rect.centerx - self.rect.centerx) < 150:
            self.idle_timer += 1
            if self.idle_timer >= self.idle_duration:
                self.idle_timer = 0
                return

        # Move toward player
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        # Attack if close
        if abs(player.rect.centerx - self.rect.centerx) < 100 and self.attack_cooldown == 0:
            self.state = "attack"
            self.frame_counter = 0
            self.current_frame = 1

    def attack_behavior(self, player):
        self.frame_counter += 1

        # Attack animation sequence
        if self.frame_counter == 1:
            self.current_frame = 1
        elif self.frame_counter == 5:
            self.current_frame = 2
        elif self.frame_counter == 10:
            self.current_frame = 3
        elif self.frame_counter == 15:
            self.current_frame = 4
            # Damage player
            if player.invincible_timer == 0 and not player.god_mode:
                if pygame.sprite.collide_mask(self, player):
                    player.health -= 1
                    player.invincible_timer = 180
                    trigger_screen_shake(8, 15)
                    
                    if assets.player_hit_sound:
                        assets.player_hit_sound.play()
                    print(f"[AXOLOTL HIT] Player health: {player.health}")
        elif self.frame_counter == 20:
            self.current_frame = 5
        elif self.frame_counter == 25:
            self.current_frame = 0
        elif self.frame_counter > 30:
            self.state = "recovery"
            self.frame_counter = 0
            self.attack_cooldown = random.randint(200, 350)

    def recovery_behavior(self, player):
        self.frame_counter += 1
        if self.frame_counter >= 30:
            self.state = "idle"
            self.frame_counter = 0

    def update_animation(self):
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if self.facing_right:
            self.image = assets.AXOLOTL_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.AXOLOTL_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.AXOLOTL_FRAMES[self.current_frame]
            self.mask = assets.AXOLOTL_MASKS[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))

# Witch Enemy Class - Eto yung ranged enemy na witch
class Witch(pygame.sprite.Sprite):
    def __init__(self, x, y, player, spawn_on_ground=True):
        super().__init__()
        self.frames = assets.WITCH_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        if spawn_on_ground:
            self.rect = self.image.get_rect(midbottom=(x, GROUND_LEVEL))
        else:
            self.rect = self.image.get_rect(midbottom=(x, y))
            
        self.mask = assets.WITCH_MASKS[self.current_frame]
        
        self.player = player
        self.state = "idle"
        self.anim_timer = 0
        self.anim_delay = 10
        self.attack_cooldown = 0
        self.attack_range = 300
        self.buildup_timer = 0
        self.buildup_duration = 60
        self.recovery_timer = 0
        self.recovery_duration = 30
        self.speed = 1.0
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = spawn_on_ground
        self.on_platform = not spawn_on_ground
        self.current_platform = None
        self.health = 4
        self.facing_right = False
        self.spawn_y = y if not spawn_on_ground else GROUND_LEVEL

    def update(self, player):
        self.player = player
        
        # Face player
        if player.rect.centerx > self.rect.centerx:
            self.facing_right = True
        else:
            self.facing_right = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # State machine
        if self.state == "idle":
            self.idle_behavior(player)
        elif self.state == "buildup":
            self.buildup_behavior()
        elif self.state == "attack":
            self.attack_behavior()
        elif self.state == "recovery":
            self.recovery_behavior()

        # Apply gravity
        if not self.on_platform:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

        # Platform collision
        was_on_platform = self.on_platform
        self.on_platform = False
        self.current_platform = None

        if self.vel_y >= 0:
            for platform in (state.platform_group or []):
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.bottom <= platform.rect.top + 20 and
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_platform = True
                    self.current_platform = platform
                    break

        # Ground collision
        if not self.on_platform and self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True

        # Fall off platform
        if self.on_platform and self.current_platform:
            if (self.rect.bottom != self.current_platform.rect.top or
                self.rect.right <= self.current_platform.rect.left or 
                self.rect.left >= self.current_platform.rect.right):
                self.on_platform = False
                self.current_platform = None
                self.vel_y = 0

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.facing_right = True
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.facing_right = False

        self.update_animation()

    def idle_behavior(self, player):
        distance_to_player = abs(self.rect.centerx - player.rect.centerx)
        
        # Don't move if player is above on platform
        if player.on_platform and player.rect.bottom < self.rect.top and distance_to_player < 150:
            pass
        else:
            # Move toward player
            if self.facing_right:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed

        # Start attack if in range
        if distance_to_player < self.attack_range and self.attack_cooldown == 0:
            self.state = "buildup"
            self.buildup_timer = 0
            self.current_frame = 0

    def buildup_behavior(self):
        self.buildup_timer += 1
        
        # Animate buildup
        buildup_progress = min(self.buildup_timer / self.buildup_duration, 1.0)
        self.current_frame = int(buildup_progress * 4)
        
        if self.buildup_timer >= self.buildup_duration:
            self.state = "attack"
            self.current_frame = 4
            
            # Shoot projectile
            projectile = WitchProjectile(
                self.rect.center, 
                self.player.rect.center,
                speed=6
            )
            if state.enemy_projectile_group is not None:

                state.enemy_projectile_group.add(projectile)

    def attack_behavior(self):
        self.anim_timer += 1
        if self.anim_timer >= 15:
            self.current_frame = 5
            self.state = "recovery"
            self.recovery_timer = 0
            self.anim_timer = 0
            
            # Melee attack if close
            if pygame.sprite.collide_mask(self, self.player) and self.player.invincible_timer == 0 and not self.player.god_mode:
                self.player.health -= 1
                self.player.invincible_timer = 180
                trigger_screen_shake(8, 15)
                
                if assets.player_hit_sound:
                    assets.player_hit_sound.play()
                print(f"[WITCH MELEE HIT] Player health: {self.player.health}")

    def recovery_behavior(self):
        self.recovery_timer += 1
        self.current_frame = 5
        
        if self.recovery_timer >= self.recovery_duration:
            self.state = "idle"
            self.attack_cooldown = 120
            self.current_frame = 0

    def update_animation(self):
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        if self.facing_right:
            self.image = assets.WITCH_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.WITCH_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.WITCH_FRAMES[self.current_frame]
            self.mask = assets.WITCH_MASKS[self.current_frame]

        self.rect = self.image.get_rect(midbottom=(old_centerx, old_bottom))

# Witch Projectile Class - Eto yung projectile na pinapaputok ng witch
class WitchProjectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, speed=6):
        super().__init__()
        self.image = assets.WITCH_PROJECTILE_IMAGE
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = assets.WITCH_PROJECTILE_MASK
        
        # Calculate direction
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.vel_x = (dx / distance) * speed
            self.vel_y = (dy / distance) * speed
        else:
            self.vel_x = 0
            self.vel_y = -speed
            
        self.lifetime = 180

    def update(self):
        # Move projectile
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.lifetime -= 1
        
        # Remove when lifetime expires or off screen
        if self.lifetime <= 0:
            self.kill()
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Fire Boss Class - Eto yung unang boss sa wave 10
class FireBoss(pygame.sprite.Sprite):
    def __init__(self, spawn_left=True, player=None):
        super().__init__()
        self.frames = assets.FIRE_BOSS_FRAMES
        self.scaled_frames = assets.FIRE_BOSS_FRAMES
        self.current_frame = 0
        self.spawn_left = spawn_left
        
        # Position based on spawn side
        if spawn_left:
            self.image = assets.FIRE_BOSS_FRAMES_FLIPPED[self.current_frame]
            self.rect = self.image.get_rect(midbottom=(50, GROUND_LEVEL))
            self.facing_right = True
            self.mask = assets.FIRE_BOSS_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.FIRE_BOSS_FRAMES[self.current_frame]
            self.rect = self.image.get_rect(midright=(WIDTH - 50, GROUND_LEVEL))
            self.facing_right = False
            self.mask = assets.FIRE_BOSS_MASKS[self.current_frame]
        
        self.player = player
        self.state = "idle"
        self.anim_timer = 0
        self.anim_delay = 10
        
        # Health scaling with wave
        wave_bonus_health = ((state.wave_system.current_wave if state.wave_system else 1) - 10) // 10 * 50  # +50 HP every 10 waves after wave 10
        self.health = 60 + wave_bonus_health  # Base health + scaling
        self.attack_cooldown = 0
        self.attack_range = 400
        
        self.buildup_duration = 120
        self.attack_duration = 90
        self.recovery_duration = 120
        self.attack_damage = 4
        
        self.contact_damage = 1
        self.contact_cooldown = 0
        self.contact_cooldown_max = 60
        
        self.normal_attack_range_width = 500
        self.enhanced_attack_range_width = 700
        self.attack_range_height = 200
        
        self.spawn_left = spawn_left
        
    def update(self, player=None):
        if player:
            self.player = player
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.contact_cooldown > 0:
            self.contact_cooldown -= 1
            
        self.check_contact_damage()
            
        # State machine
        if self.state == "idle":
            self.idle_behavior()
        elif self.state == "buildup":
            self.buildup_behavior()
        elif self.state == "attack":
            self.attack_behavior()
        elif self.state == "recovery":
            self.recovery_behavior()
            
        self.update_animation()
        
    def check_contact_damage(self):
        # Damage player on contact
        if (self.player and 
            self.contact_cooldown == 0 and 
            self.player.invincible_timer == 0 and 
            not self.player.god_mode and
            pygame.sprite.collide_mask(self, self.player)):
            
            self.player.health -= self.contact_damage
            self.player.invincible_timer = 180
            self.contact_cooldown = self.contact_cooldown_max
            trigger_screen_shake(12, 20)
            
            if assets.player_hit_sound:
                assets.player_hit_sound.play()
            print(f"[FIRE BOSS CONTACT] Player health: {self.player.health}")
        
    def idle_behavior(self):
        self.current_frame = 0
        
        if self.player and self.attack_cooldown == 0:
            if self.spawn_left:
                player_in_front = self.player.rect.centerx > self.rect.left
                player_in_range = abs(self.player.rect.centerx - self.rect.centerx) < self.attack_range
            else:
                player_in_front = self.player.rect.centerx < self.rect.right
                player_in_range = abs(self.player.rect.centerx - self.rect.centerx) < self.attack_range
            
            if player_in_front and player_in_range:
                self.state = "buildup"
                self.anim_timer = 0
                print("[FIRE BOSS] Starting attack buildup!")
                    
    def buildup_behavior(self):
        self.anim_timer += 1
        
        # Animate buildup
        buildup_progress = min(self.anim_timer / self.buildup_duration, 1.0)
        self.current_frame = 1 + int(buildup_progress * 3)
        
        if self.anim_timer >= self.buildup_duration:
            self.state = "attack"
            self.anim_timer = 0
            self.current_frame = 4
            print("[FIRE BOSS] ATTACKING!")
            
    def attack_behavior(self):
        self.anim_timer += 1
        self.current_frame = 4
        
        # Damage player if in attack range
        if self.player and self.player.invincible_timer == 0 and not self.player.god_mode:
            current_attack_range = self.enhanced_attack_range_width
            
            # Create attack hitbox
            if self.spawn_left:
                attack_rect = pygame.Rect(
                    self.rect.right, 
                    self.rect.top - self.attack_range_height,
                    current_attack_range,
                    self.attack_range_height + self.rect.height
                )
            else:
                attack_rect = pygame.Rect(
                    self.rect.left - current_attack_range,
                    self.rect.top - self.attack_range_height,
                    current_attack_range,
                    self.attack_range_height + self.rect.height
                )
            
            if attack_rect.colliderect(self.player.rect):
                self.player.health -= self.attack_damage
                self.player.invincible_timer = 180
                trigger_screen_shake(15, 25)
                
                if assets.player_hit_sound:
                    assets.player_hit_sound.play()
                print(f"[FIRE BOSS HIT] Player health: {self.player.health}")
                
        if self.anim_timer >= self.attack_duration:
            self.state = "recovery"
            self.anim_timer = 0
            print("[FIRE BOSS] Attack finished, recovering...")
            
    def recovery_behavior(self):
        self.anim_timer += 1
        self.current_frame = 0
        
        if self.anim_timer >= self.recovery_duration:
            self.state = "idle"
            self.attack_cooldown = 180
            self.anim_timer = 0
            print("[FIRE BOSS] Ready for next attack!")
            
    def update_animation(self):
        if self.spawn_left:
            old_left = self.rect.left
            self.image = assets.FIRE_BOSS_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.FIRE_BOSS_MASKS_FLIPPED[self.current_frame]
            self.rect = self.image.get_rect(bottomleft=(old_left, GROUND_LEVEL))
        else:
            old_right = self.rect.right
            self.image = assets.FIRE_BOSS_FRAMES[self.current_frame]
            self.mask = assets.FIRE_BOSS_MASKS[self.current_frame]
            self.rect = self.image.get_rect(bottomright=(old_right, GROUND_LEVEL))

# Dragon Boss Class - Eto yung pangalawang boss sa wave 20
class DragonBoss(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.frames = assets.DRAGON_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = assets.DRAGON_MASKS[self.current_frame]
        
        self.player = player
        self.state = "idle"
        self.anim_timer = 0
        self.anim_delay = 10
        self.attack_cooldown = 0
        
        # Health scaling with wave
        wave_bonus_health = ((state.wave_system.current_wave if state.wave_system else 1) - 10) // 10 * 40
        self.health = 50 + wave_bonus_health
        self.attack_damage = 3
        
        self.attack_range = 400
        self.attack_duration = 180
        self.buildup_duration = 90
        self.recovery_duration = 60
        
        self.speed = 4
        self.chase_speed = 5
        self.direction = -1
        self.hover_range = 50
        self.original_x = x
        self.original_y = y
        
        self.attack_active = False
        self.enraged = False
        self.enrage_health_threshold = 0.4
        self.roar_played = False
        
        # Dragon avoidance system
        self.avoidance_force = 0
        self.avoidance_timer = 0
        self.personal_space = 150  # Minimum distance between dragons
    
    def update(self, player):
                
        self.player = player
        
        # Face player
        if player.rect.centerx > self.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Enrage at low health
        if not self.enraged and self.health <= (50 + (((state.wave_system.current_wave if state.wave_system else 1) - 10) // 10 * 40)) * self.enrage_health_threshold:
            self.activate_enrage_mode()
            
        # Play roar sound when chasing
        if self.state == "chase" and assets.dragon_roar_sound and not state.dragon_roar_played and not self.roar_played:
            assets.dragon_roar_sound.play()
            state.dragon_roar_played = True
            self.roar_played = True
            print("[SOUND] Dragon roar!")
            
        # State machine
        if self.state == "idle":
            self.idle_behavior()
        elif self.state == "chase":
            self.chase_behavior()
        elif self.state == "buildup":
            self.buildup_behavior()
        elif self.state == "attack":
            self.attack_behavior()
        elif self.state == "recovery":
            self.recovery_behavior()
        
        # Avoid other dragons
        if self.state != "attack":
            self.avoid_other_dragons()
        
        self.update_animation()
    
    def avoid_other_dragons(self):
        """Prevent dragons from stacking on top of each other"""
        self.avoidance_timer += 1
        
        # Only check avoidance periodically for performance
        if self.avoidance_timer >= 10:
            self.avoidance_timer = 0
            
            # Check distance to other dragons
            for dragon in (state.ground_enemy_group or []):
                if isinstance(dragon, DragonBoss) and dragon != self:
                    distance = math.hypot(self.rect.centerx - dragon.rect.centerx,
                                        self.rect.centery - dragon.rect.centery)
                    
                    if distance < self.personal_space:
                        # Calculate push direction
                        dx = self.rect.centerx - dragon.rect.centerx
                        dy = self.rect.centery - dragon.rect.centery
                        
                        if dx != 0 or dy != 0:
                            # Normalize direction
                            norm_x, norm_y = dx / distance, dy / distance
                            push_strength = (self.personal_space - distance) * 0.1
                            
                            # Apply push
                            self.rect.x += int(norm_x * push_strength)
                            self.rect.y += int(norm_y * push_strength)
                            
                            # Keep within screen bounds
                            self.rect.left = max(50, self.rect.left)
                            self.rect.right = min(WIDTH - 50, self.rect.right)
                            self.rect.top = max(30, self.rect.top)
                            self.rect.bottom = min(HEIGHT - 80, self.rect.bottom)
    
    def activate_enrage_mode(self):
        self.enraged = True
        self.speed = 5
        self.chase_speed = 6
        self.attack_damage = 4
        self.personal_space = 200  # More personal space when enraged
        print("[DRAGON BOSS] ENRAGED! Speed and damage increased!")
    
    def idle_behavior(self):
        # Hover in place
        hover_y = math.sin(pygame.time.get_ticks() * 0.005 + self.original_x) * 20  # Smooth hovering
        self.rect.centery = self.original_y + hover_y
        
        # Gentle drifting
        drift_x = math.sin(pygame.time.get_ticks() * 0.002 + self.original_y) * 10
        self.rect.centerx = self.original_x + drift_x
        
        distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                      self.rect.centery - self.player.rect.centery)
        
        # Chase if player is far
        if distance_to_player > 300:
            self.state = "chase"
            print("[DRAGON BOSS] Player too far, chasing!")
        
        # Attack if close and ready
        elif distance_to_player < self.attack_range and self.attack_cooldown == 0:
            self.state = "buildup"
            self.anim_timer = 0
            print("[DRAGON BOSS] Starting attack buildup!")

    def chase_behavior(self):
        # Move toward player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # Speed up when far from player
            speed_multiplier = min(1.5, distance / 200)
            current_speed = self.chase_speed * speed_multiplier
            
            dx, dy = dx / distance, dy / distance
            self.rect.x += dx * current_speed
            self.rect.y += dy * current_speed
        
        # Screen boundaries
        if self.rect.left < 50:
            self.rect.left = 50
        elif self.rect.right > WIDTH - 50:
            self.rect.right = WIDTH - 50
        if self.rect.top < 30:
            self.rect.top = 30
        elif self.rect.bottom > HEIGHT - 80:
            self.rect.bottom = HEIGHT - 80
        
        distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                    self.rect.centery - self.player.rect.centery)
        
        if distance_to_player < 80:
            self.state = "idle"
            self.original_x = self.rect.centerx
            self.original_y = self.rect.centery
        elif distance_to_player < self.attack_range and self.attack_cooldown == 0:
            self.state = "buildup"
            self.anim_timer = 0
            print("[DRAGON BOSS] Close enough, starting attack buildup!")
    
    def buildup_behavior(self):
        self.anim_timer += 1
        
        buildup_progress = min(self.anim_timer / self.buildup_duration, 1.0)
        if buildup_progress < 0.5:
            self.current_frame = 2
        else:
            self.current_frame = 3
        
        if self.anim_timer >= self.buildup_duration:
            self.state = "attack"
            self.anim_timer = 0
            self.attack_active = True
            print("[DRAGON BOSS] ATTACKING!")
    
    def attack_behavior(self):
        self.anim_timer += 1
        
        # Attack animation
        if self.anim_timer < 30:
            self.current_frame = 4
        elif self.anim_timer < 60:
            self.current_frame = 5
        else:
            self.current_frame = 6
        
        # Fire breath attack
        if self.attack_active:
            # Create breath hitbox
            breath_range = 300  # How far the breath reaches
            breath_width = 150  # How wide the breath is
            
            if self.direction > 0:  # Facing right
                breath_rect = pygame.Rect(
                    self.rect.centerx,
                    self.rect.centery - breath_width//2,
                    breath_range,
                    breath_width
                )
            else:  # Facing left
                breath_rect = pygame.Rect(
                    self.rect.centerx - breath_range,
                    self.rect.centery - breath_width//2,
                    breath_range,
                    breath_width
                )
            
            # Damage player if in breath area
            if self.current_frame in [5, 6] and breath_rect.colliderect(self.player.rect):
                if self.player.invincible_timer == 0 and not self.player.god_mode:
                    self.player.health -= self.attack_damage
                    self.player.invincible_timer = 180
                    trigger_screen_shake(15, 25)
                    if assets.player_hit_sound:
                        assets.player_hit_sound.play()
                    print(f"[DRAGON BREATH HIT] Player health: {self.player.health}")
                    self.attack_active = False
        
        if self.anim_timer >= self.attack_duration:
            self.state = "recovery"
            self.anim_timer = 0
            self.attack_active = False
            print("[DRAGON BOSS] Attack finished, recovering...")
    
    def recovery_behavior(self):
        self.anim_timer += 1
        
        recovery_progress = min(self.anim_timer / self.recovery_duration, 1.0)
        if recovery_progress < 0.33:
            self.current_frame = 6
        elif recovery_progress < 0.66:
            self.current_frame = 7
        else:
            self.current_frame = 8
        
        if self.anim_timer >= self.recovery_duration:
            # Decide next state based on distance to player
            distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                          self.rect.centery - self.player.rect.centery)
            
            if distance_to_player > 200:  # Player moved away
                self.state = "chase"
                print("[DRAGON BOSS] Player moved away, chasing!")
            else:
                self.state = "idle"  # Stay idle if player is close
            
            self.attack_cooldown = 120  # Cooldown before next attack
            self.anim_timer = 0
    
    def update_animation(self):
        # Idle and chase animations
        if self.state == "idle":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 3
        elif self.state == "chase":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 3
        
        old_center = self.rect.center
        if self.direction > 0:
            self.image = assets.DRAGON_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.DRAGON_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.DRAGON_FRAMES[self.current_frame]
            self.mask = assets.DRAGON_MASKS[self.current_frame]
        self.rect = self.image.get_rect(center=old_center)

# Rocket Enemy Class - Eto yung flying enemy na rocket
class RocketEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.frames = assets.ROCKET_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = assets.ROCKET_MASKS[self.current_frame]
        
        self.player = player
        self.state = "hover"
        self.anim_timer = 0
        self.anim_delay = 8
        self.attack_cooldown = 0
        self.hover_speed = 1
        self.hover_range = 50
        self.original_y = y
        self.original_x = x
        self.hover_direction = 1
        self.health = 2
        
        self.attack_speed = 8
        self.attack_direction = pygame.Vector2(0, 0)
        self.attack_duration = 90
        self.buildup_timer = 0
        self.buildup_duration = 70

    def update(self, player):
        self.player = player

        # State machine
        if self.state == "hover":
            self.hover_behavior()
        elif self.state == "buildup":
            self.buildup_behavior()
        elif self.state == "attack":
            self.attack_behavior()

        self.update_animation()

    def hover_behavior(self):
        # Hover up and down
        self.rect.y += self.hover_speed * self.hover_direction
        
        if self.rect.centery <= self.original_y - self.hover_range:
            self.hover_direction = 1
        elif self.rect.centery >= self.original_y + self.hover_range:
            self.hover_direction = -1
        
        # Gentle horizontal movement
        hover_x = math.sin(pygame.time.get_ticks() * 0.005) * 20
        self.rect.centerx = self.original_x + hover_x
        
        distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                      self.rect.centery - self.player.rect.centery)
        
        # Start attack if player is close
        if distance_to_player < 400 and self.attack_cooldown == 0:
            self.state = "buildup"
            self.buildup_timer = 0
            self.current_frame = 4

    def buildup_behavior(self):
        self.buildup_timer += 1
        
        # Animate buildup
        buildup_progress = self.buildup_timer / self.buildup_duration
        buildup_frame = 4 + int(buildup_progress * 7)
        self.current_frame = min(buildup_frame, 10)
        
        if self.buildup_timer >= self.buildup_duration:
            self.state = "attack"
            self.attack_duration = 90  # Reset attack duration
            self.current_frame = 11
            
            # Calculate attack direction
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.attack_direction = pygame.Vector2(dx/distance, dy/distance)
            else:
                self.attack_direction = pygame.Vector2(1, 0)

    def attack_behavior(self):
        self.current_frame = 11
        
        # Move in attack direction
        self.rect.x += self.attack_direction.x * self.attack_speed
        self.rect.y += self.attack_direction.y * self.attack_speed
        
        # Reset if off screen
        screen_padding = 100  # How far off screen before resetting
        if (self.rect.right < -screen_padding or 
            self.rect.left > WIDTH + screen_padding or 
            self.rect.bottom < -screen_padding or 
            self.rect.top > HEIGHT + screen_padding):
            self.reset_to_hover()
            return
        
        self.attack_duration -= 1
        if self.attack_duration <= 0:
            self.reset_to_hover()

    def reset_to_hover(self):
        self.state = "hover"
        self.attack_cooldown = 60  # Cooldown before next attack
        
        # Reposition to new random location
        new_x = random.randint(100, WIDTH - 100)
        new_y = random.randint(100, HEIGHT - 200)
        
        # Try to avoid spawning too close to player
        min_distance_from_player = 200
        distance_to_player = math.hypot(new_x - self.player.rect.centerx, new_y - self.player.rect.centery)
        
        # Make a few attempts to find a good spawn location
        attempts = 0
        while distance_to_player < min_distance_from_player and attempts < 5:
            new_x = random.randint(100, WIDTH - 100)
            new_y = random.randint(100, HEIGHT - 200)
            distance_to_player = math.hypot(new_x - self.player.rect.centerx, new_y - self.player.rect.centery)
            attempts += 1
        
        self.rect.center = (new_x, new_y)
        self.original_x = new_x
        self.original_y = new_y
        self.hover_direction = 1
        
        # Reset timers
        self.buildup_timer = 0
        self.attack_duration = 90
        self.current_frame = 0

    def update_animation(self):
        if self.state == "hover":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
            flip = self.player.rect.centerx > self.rect.centerx
        elif self.state == "buildup":
            flip = self.player.rect.centerx > self.rect.centerx
        elif self.state == "attack":
            flip = self.attack_direction.x > 0
        else:
            flip = False

        old_center = self.rect.center
        if flip:
            self.image = assets.ROCKET_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.ROCKET_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.ROCKET_FRAMES[self.current_frame]
            self.mask = assets.ROCKET_MASKS[self.current_frame]
        self.rect = self.image.get_rect(center=old_center)

# Reaper Enemy Class - Eto yung flying enemy na reaper
class Reaper(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.frames = assets.REAPER_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = assets.REAPER_MASKS[self.current_frame]
        
        self.player = player
        self.state = "hover"
        self.anim_timer = 0
        self.anim_delay = 8
        self.attack_cooldown = 0
        
        self.speed = 2.5
        self.hover_speed = 1
        self.hover_range = 40
        self.original_y = y
        self.hover_direction = 1
        self.health = 2
        
        self.attack_range = 200
        self.attack_speed = 3
        self.damage = 1
        self.attack_timer = 0
        self.attack_duration = 60
        
        self.float_timer = 0

    def update(self, player):
        self.player = player
        
        # State machine
        if self.state == "hover":
            self.hover_behavior()
        elif self.state == "attack":
            self.attack_behavior()

        self.update_animation()

    def hover_behavior(self):
        # Hover up and down
        self.rect.y += self.hover_speed * self.hover_direction
        
        if self.rect.centery <= self.original_y - self.hover_range:
            self.hover_direction = 1
        elif self.rect.centery >= self.original_y + self.hover_range:
            self.hover_direction = -1
        
        # Gentle horizontal drifting
        hover_x = math.sin(pygame.time.get_ticks() * 0.003) * 15
        self.rect.centerx = self.rect.centerx + hover_x * 0.1
        
        distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                      self.rect.centery - self.player.rect.centery)
        
        # Attack if player is close
        if distance_to_player < self.attack_range:
            self.state = "attack"
            self.attack_timer = 0
            self.current_frame = 1

    def attack_behavior(self):
        self.attack_timer += 1
        
        # Move toward player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.rect.x += dx * self.attack_speed
            self.rect.y += dy * self.attack_speed
            
            # Damage player on contact
            if distance < 50 and self.player.invincible_timer == 0 and not self.player.god_mode:
                self.player.health -= self.damage
                self.player.invincible_timer = 180
                trigger_screen_shake(8, 15)
                
                if assets.player_hit_sound:
                    assets.player_hit_sound.play()
                print(f"[REAPER HIT] Player health: {self.player.health}")
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 50:
            self.rect.top = 50
        elif self.rect.bottom > HEIGHT - 100:
            self.rect.bottom = HEIGHT - 100
        
        distance_to_player = math.hypot(self.rect.centerx - self.player.rect.centerx,
                                      self.rect.centery - self.player.rect.centery)
        
        # Return to hover if player is far or attack duration expires
        if distance_to_player > 300 or self.attack_timer >= self.attack_duration:
            self.state = "hover"
            self.original_y = self.rect.centery

    def reset_to_hover(self):
        self.state = "hover"
        self.attack_cooldown = 60
        self.original_y = self.rect.centery

    def update_animation(self):
        if self.state == "hover":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 2
            flip = hasattr(self, 'last_x') and self.rect.centerx > self.last_x
            self.last_x = self.rect.centerx
        elif self.state == "attack":
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.current_frame = (self.current_frame + 1) % 6
                if self.current_frame == 0:
                    self.current_frame = 1
            flip = self.player.rect.centerx > self.rect.centerx
        else:
            flip = False

        old_center = self.rect.center
        if flip:
            self.image = assets.REAPER_FRAMES_FLIPPED[self.current_frame]
            self.mask = assets.REAPER_MASKS_FLIPPED[self.current_frame]
        else:
            self.image = assets.REAPER_FRAMES[self.current_frame]
            self.mask = assets.REAPER_MASKS[self.current_frame]
        self.rect = self.image.get_rect(center=old_center)

