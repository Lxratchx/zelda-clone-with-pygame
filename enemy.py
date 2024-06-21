from typing import Any
import pygame
from settings import *
from entity import Entity
from support import import_folder
from os import path as PATH
from player import Player

class Enemy(Entity):
    def __init__(self, monster_name, pos, obstacle_sprites, *groups):
        super().__init__(*groups)
        self.sprite_type = 'enemy'
        
        # graphics
        self.animations = self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # movement
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.speed = monster_info['speed']
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

    def import_graphics(self, monster_name):
        animations = {}.fromkeys(['idle', 'move', 'attack'], [])
        main_path = f'graphics/monsters/{monster_name}'
        for animation in animations:
            animations[animation] = import_folder(PATH.join(main_path, animation))
        return animations
    
    def get_player_distance_direction(self, player: Player):
        player_vec = pygame.math.Vector2(player.hitbox.center)
        enemy_vec = pygame.math.Vector2(self.hitbox.center)

        distance = (player_vec - enemy_vec).magnitude()
        if distance != 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)
        
    def get_status(self, player: Player):
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.attack_radius:
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def actions(self, player):
        if self.status == 'attack':
            ...
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()  # stops enemy in case of player go out notice radius
    
    def update(self) -> None:
        self.move(self.speed)
    
    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
