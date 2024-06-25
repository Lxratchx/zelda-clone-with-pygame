import os
from typing import Any
import pygame
from settings import *
from support import *
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        # graphics setup
        self.import_player_animations()
        self.status = 'down'
        
        # attack
        self.attacking_time = 0
        self.attacking = False
        self.attacking_cooldown = 400
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.attack_sound = pygame.mixer.Sound('audio/sword.wav')
        self.attack_sound.set_volume(.2)

        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.weapon_index = 0
        self.weapons = list(weapon_settings.keys())
        self.weapon = self.weapons[self.weapon_index]
        self.weapon_switch_time = 0
        self.weapon_can_switch = True
        self.weapon_switch_cooldown = 400

        # magic
        self.magic_index = 0
        self.magics = list(magic_settings.keys())
        self.magic = self.magics[self.magic_index]
        self.magic_switch_time = 0
        self.magic_can_switch = True
        self.magic_switch_cooldown = 400
        self.create_magic = create_magic
        # self.destroy_magic = destroy_magic

        # stats
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 4,
            'speed': 5
        }
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.attack = self.stats['attack']
        self.speed = self.stats['speed']
        self.exp = 5000

        # updating
        self.max_stats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 10
        }
        self.upgrade_cost = {
            'health': 100,
            'energy': 100,
            'attack': 100,
            'magic': 100,
            'speed': 100
        }

        # damage timer
        self.vulnerable = False
        self.hurt_time = 0
        self.invulnerable_cooldown = 400

    
    def import_player_animations(self):
        graphics_folder = 'graphics/player'
        self.animations = {
            'up': [],
            'down': [],
            'left': [],
            'right': [],
            'up_idle': [],
            'down_idle': [],
            'left_idle': [],
            'right_idle': [],
            'up_attack': [],
            'down_attack': [],
            'left_attack': [],
            'right_attack': [],
        }
        for animation in self.animations.keys():
            path = os.path.join(graphics_folder, animation)
            folder = import_folder(path)
            self.animations[animation] = folder

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += .01 * self.stats['magic']
        
        else:
            self.energy = self.stats['energy']

    def animate(self):
        if self.status not in self.animations:
            return
        
        animation = self.animations[self.status]
        animation_size = len(animation)

        self.frame_index += self.animation_speed
        if self.frame_index >= animation_size:
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_status(self):
        was_idle = 'idle' in self.status
        was_attacking = 'attack' in self.status
        is_not_moving = (self.direction.x == 0) and (self.direction.y == 0)
        if is_not_moving and not was_idle and not was_attacking:
            self.status += '_idle'
        
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            
            if was_idle:
                self.status = self.status.replace('_idle', '') + '_attack'

            elif not was_idle and not was_attacking:
                self.status += '_attack'
            
        elif was_attacking:
            self.status = self.status.replace('_attack', '_idle')

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_settings[self.weapon]['damage']
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        weapon_damage = magic_settings[self.magic]['strength']
        return base_damage + weapon_damage

    def input(self):
        if self.attacking:
            return
        
        keys = pygame.key.get_pressed()

        # movement
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'

        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'

        else:
            self.direction.y = 0
        
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'

        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'

        else:
            self.direction.x = 0
        
        # attacking
        if keys[pygame.K_SPACE]:
            self.attacking_time = pygame.time.get_ticks()
            self.attacking = True
            self.create_attack()
            self.attack_sound.play()
        
        # magic
        if keys[pygame.K_LALT]:
            self.attacking_time = pygame.time.get_ticks()
            self.attacking = True

            strength = magic_settings[self.magic]['strength'] + self.stats['magic']
            cost = magic_settings[self.magic]['cost']
            self.create_magic(self.magic, strength, cost)
        
        # switch weapon
        if keys[pygame.K_q] and self.weapon_can_switch:
            self.weapon_can_switch = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon_index += 1
            nweapons = len(self.weapons)
            if self.weapon_index >= nweapons:
                self.weapon_index = 0

            self.weapon = self.weapons[self.weapon_index]
        
        # switch magic
        if keys[pygame.K_e] and self.magic_can_switch:
            self.magic_can_switch = False
            self.magic_switch_time = pygame.time.get_ticks()
            self.magic_index += 1
            nmagics = len(self.magics)
            if self.magic_index >= nmagics:
                self.magic_index = 0

            self.magic = self.magics[self.magic_index]
            
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        cooldown_finished = current_time - self.attacking_time >= self.attacking_cooldown + weapon_settings[self.weapon]['cooldown']
        if self.attacking and cooldown_finished:
            self.attacking = False   
            self.destroy_attack()
        
        # weapon
        switch_weapon_cooldown_finish = current_time - self.weapon_switch_time >= self.weapon_switch_cooldown
        if switch_weapon_cooldown_finish:
            self.weapon_can_switch = True
        
        # magic
        switch_magic_cooldown_finish = current_time - self.magic_switch_time >= self.magic_switch_cooldown
        if switch_magic_cooldown_finish:
            self.magic_can_switch = True
        
        # vulnerability
        vulnerability_cooldown_finish = current_time - self.hurt_time >= self.invulnerable_cooldown
        if vulnerability_cooldown_finish:
            self.vulnerable = True
   
    def update(self) -> None:
        self.input()
        self.get_status()
        self.cooldowns()
        self.move(self.stats['speed'])
        self.animate()
        self.energy_recovery()
