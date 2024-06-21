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
        self.exp = 123
    
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
        cooldown_finished = current_time - self.attacking_time >= self.attacking_cooldown
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
   
    # def move(self, speed):
    #     if self.direction.magnitude() != 0:
    #         self.direction = self.direction.normalize()

    #     self.hitbox.x += self.direction.x * speed
    #     self.collision('horizontal')
    #     self.hitbox.y += self.direction.y * speed
    #     self.collision('vertical')
    #     self.rect.center = self.hitbox.center
    
    # def collision(self, direction):
    #     if direction == 'horizontal':
    #         for sprite in self.obstacle_sprites:
    #             if sprite.hitbox.colliderect(self.hitbox):
    #                 if self.direction.x > 0:
    #                     self.hitbox.right = sprite.hitbox.left
                    
    #                 if self.direction.x < 0:
    #                     self.hitbox.left = sprite.hitbox.right
        
    #     if direction == 'vertical':
    #         for sprite in self.obstacle_sprites:
    #             if sprite.hitbox.colliderect(self.hitbox):
    #                 if self.direction.y > 0:
    #                     self.hitbox.bottom = sprite.hitbox.top
                    
    #                 if self.direction.y < 0:
    #                     self.hitbox.top = sprite.hitbox.bottom
    
    def update(self) -> None:
        self.input()
        self.get_status()
        self.cooldowns()
        self.move(self.speed)
        self.animate()
