import math
import pygame
from constants import WIDTH, HEIGHT
import assets
import state

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, speed=12, is_pistol=False, is_shotgun=False, damage=1):
        super().__init__()
        if is_pistol:
            self.image = pygame.Surface((6, 3), pygame.SRCALPHA)
            color = (200, 200, 255)
            pygame.draw.rect(self.image, color, (0, 0, 6, 3))
        elif is_shotgun:
            self.image = pygame.Surface((10, 6), pygame.SRCALPHA)
            color = (255, 165, 0)
            pygame.draw.ellipse(self.image, color, (0, 0, 10, 6))
        else:
            self.image = pygame.Surface((8, 4), pygame.SRCALPHA)
            color = (255, 220, 100)
            pygame.draw.rect(self.image, color, (0, 0, 8, 4))
        
        self.image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.lifetime = 90
        self.is_pistol = is_pistol
        self.is_shotgun = is_shotgun
        self.damage = damage

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, bullet_group):
        super().__init__()
        self.player = player
        self.bullet_group = bullet_group
        self.radius = 60
        
        self.ak_image = self.load_scaled_gun(assets.load_ak_image(), 0.09)
        self.pistol_image = self.load_scaled_gun(assets.load_pistol_image(), 0.07)
        self.shotgun_image = self.load_scaled_gun(assets.load_shotgun_image(), 0.12)
        
        self.current_gun = "ak"
        self.original_image = self.ak_image
        self.image = self.original_image
        self.rect = self.image.get_rect(center=player.rect.center)

        self.cooldown = 0
        self.switch_cooldown = 0
        
        self.ak_ammo = 25
        self.shotgun_ammo = 12
        self.pistol_unlimited = True

    def load_scaled_gun(self, original, scale):
        w, h = original.get_size()
        new_size = (int(w * scale), int(h * scale))
        return pygame.transform.scale(original, new_size)

    def switch_weapon(self):
        if self.switch_cooldown == 0:
            if self.current_gun == "pistol":
                print("[SWITCH] Switching from unlimited pistol!")
            elif self.current_gun == "ak" and self.ak_ammo < 10:
                print("[LOW AMMO] AK running low, consider using pistol!")
            elif self.current_gun == "shotgun" and self.shotgun_ammo < 5:
                print("[LOW AMMO] Shotgun running low, consider using pistol!")
            
            if self.current_gun == "ak":
                self.current_gun = "pistol"
                self.original_image = self.pistol_image
            elif self.current_gun == "pistol":
                self.current_gun = "shotgun"
                self.original_image = self.shotgun_image
            else:
                self.current_gun = "ak"
                self.original_image = self.ak_image
            self.switch_cooldown = 20

    def update_keyboard(self):
        if state.knife and state.knife.active:
            return

        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1

        px, py = self.player.rect.center
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - px, my - py
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        self.update_gun_position(px, py, angle_rad, angle_deg)
        
        barrel_length = self.original_image.get_width() * 0.5
        barrel_tip_x = self.rect.centerx + math.cos(angle_rad) * barrel_length
        barrel_tip_y = self.rect.centery + math.sin(angle_rad) * barrel_length

        if pygame.mouse.get_pressed()[0] and self.cooldown == 0:
            self.shoot(barrel_tip_x, barrel_tip_y, angle_rad)

        if self.cooldown > 0:
            self.cooldown -= 1

    def update_gun_position(self, px, py, angle_rad, angle_deg):
        offset_x = math.cos(angle_rad) * self.radius
        offset_y = math.sin(angle_rad) * self.radius
        gun_x = px + offset_x
        gun_y = py + offset_y

        rotated_image = pygame.transform.rotate(self.original_image, -angle_deg)
        if math.cos(angle_rad) < 0:
            rotated_image = pygame.transform.flip(rotated_image, False, True)

        self.image = rotated_image
        self.rect = self.image.get_rect(center=(gun_x, gun_y))

    def shoot(self, barrel_tip_x, barrel_tip_y, angle_rad):
        ws = state.wave_system
        if ws and ws.is_boss_wave():
            boss_damage = 1 + (ws.current_wave // 20)
            damage = boss_damage
        else:
            wave_bonus_damage = (ws.current_wave - 1) // 10 if ws else 0
            damage = 1 + wave_bonus_damage
        
        if self.current_gun == "ak" and self.ak_ammo > 0:
            bullet = Bullet((barrel_tip_x, barrel_tip_y), angle_rad, speed=12, is_pistol=False, damage=damage)
            self.bullet_group.add(bullet)
            self.cooldown = 10
            self.ak_ammo -= 1
            if assets.gun_sound:
                assets.gun_sound.play()
            print(f"[AK SHOT] Ammo: {self.ak_ammo}, Damage: {damage}")
        elif self.current_gun == "pistol":
            bullet = Bullet((barrel_tip_x, barrel_tip_y), angle_rad, speed=14, is_pistol=True, damage=damage)
            self.bullet_group.add(bullet)
            self.cooldown = 20
            if assets.gun_sound:
                assets.gun_sound.play()
            print(f"[PISTOL SHOT] Damage: {damage}")
        elif self.current_gun == "shotgun" and self.shotgun_ammo > 0:
            spread_angle = 0.2
            angles = [angle_rad - spread_angle, angle_rad, angle_rad + spread_angle]
            for angle in angles:
                bullet = Bullet((barrel_tip_x, barrel_tip_y), angle, speed=10, is_pistol=False, is_shotgun=True, damage=damage)
                self.bullet_group.add(bullet)
            self.cooldown = 30
            self.shotgun_ammo -= 1
            if assets.gun_sound:
                assets.gun_sound.play()
            print(f"[SHOTGUN SHOT] Ammo: {self.shotgun_ammo}, Damage: {damage}")
        else:
            if assets.gun_empty_sound:
                assets.gun_empty_sound.play()
            print(f"[EMPTY GUN] No ammo for {self.current_gun}!")

class Knife(pygame.sprite.Sprite):
    def __init__(self, player, ground_enemy_group, flying_enemy_group):
        super().__init__()
        self.player = player
        self.ground_enemy_group = ground_enemy_group
        self.flying_enemy_group = flying_enemy_group
        self.radius = 80
        self.duration = 40
        self.timer = 0
        self.active = False
        self.cooldown = 0
        self.cooldown_max = 90
        self.hit_enemies = set()
        
        self.original_image = assets.BLAST_RADIUS_IMAGE
        self.image = self.original_image
        self.rect = self.image.get_rect(center=player.rect.center)
        self.mask = assets.BLAST_RADIUS_MASK

    def create_circular_mask(self):
        mask_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255), (self.radius, self.radius), self.radius)
        return pygame.mask.from_surface(mask_surface)

    def update_keyboard(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if pygame.mouse.get_pressed()[2] and not self.active and self.cooldown == 0:
            self.activate_knife()
        self.update_knife_state()

    def activate_knife(self):
        self.active = True
        self.timer = self.duration
        self.cooldown = self.cooldown_max
        self.hit_enemies.clear()
        if assets.player_blast_sound:
            assets.player_blast_sound.play()

    def update_knife_state(self):
        if self.active:
            self.rect.center = self.player.rect.center
            pulse = math.sin(pygame.time.get_ticks() * 0.1) * 0.2 + 0.8
            scaled_width = int(self.original_image.get_width() * pulse)
            scaled_height = int(self.original_image.get_height() * pulse)
            self.image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
            self.rect = self.image.get_rect(center=self.player.rect.center)

            r_sq = self.radius * self.radius
            px, py = self.player.rect.centerx, self.player.rect.centery

            for enemy in self.ground_enemy_group:
                if enemy not in self.hit_enemies:
                    dx = enemy.rect.centerx - px
                    dy = enemy.rect.centery - py
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= r_sq:
                        self.hit_enemies.add(enemy)
                        self.apply_knockback(enemy, math.sqrt(dist_sq) if dist_sq > 0 else 1)
            
            for enemy in self.flying_enemy_group:
                if enemy not in self.hit_enemies:
                    dx = enemy.rect.centerx - px
                    dy = enemy.rect.centery - py
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= r_sq:
                        self.hit_enemies.add(enemy)
                        self.apply_knockback(enemy, math.sqrt(dist_sq) if dist_sq > 0 else 1)
                        
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
                self.image.set_alpha(0)

    def apply_knockback(self, enemy, distance):
        dx = enemy.rect.centerx - self.player.rect.centerx
        dy = enemy.rect.centery - self.player.rect.centery
        if dx != 0 or dy != 0:
            norm_x, norm_y = dx / distance, dy / distance
            knockback_strength = 40
            enemy.rect.x += int(norm_x * knockback_strength)
            enemy.rect.y += int(norm_y * knockback_strength)
            
            if hasattr(enemy, 'on_platform') and enemy.on_platform:
                enemy.on_platform = False
                if hasattr(enemy, 'current_platform'):
                    enemy.current_platform = None
                if hasattr(enemy, 'vel_y'):
                    enemy.vel_y = -12
            elif hasattr(enemy, 'vel_y'):
                enemy.vel_y = -15
            
            if hasattr(enemy, 'state') and enemy.state == "attack":
                if hasattr(enemy, 'reset_to_hover'):
                    enemy.reset_to_hover()
