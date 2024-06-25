from typing import Any
import pygame
from settings import *
from entity import Entity
from support import import_folder
from os import path as PATH
from player import Player

class Enemy(Entity):
    def __init__(self, monster_name, pos, obstacle_sprites, player_damage, trigger_death_particles, add_xp, *groups):
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

        # player interaction
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 600
        
        # player interaction
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_cooldown = 300

        self.player_damage = player_damage
        self.trigger_death_particles = trigger_death_particles
        self.add_xp = add_xp

        
        self.death_sound = pygame.mixer.Sound('audio/death.wav')
        self.death_sound.set_volume(.2)
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        attack_cooldown_finish = current_time - self.attack_time >= self.attack_cooldown
        if not self.can_attack and attack_cooldown_finish:
            self.can_attack = True
        
        invincibility_cooldown_finish = current_time - self.hit_time >= self.invincibility_cooldown
        if not self.vulnerable and invincibility_cooldown_finish:
            self.vulnerable = True

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
        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()

            elif attack_type == 'magic':
                self.health -= player.get_full_magic_damage()
            
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.kill()
            self.add_xp(self.exp)
            self.death_sound.play()
    
    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.player_damage(self.damage, self.attack_type)

        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()  # stops enemy in case of player go out notice radius
    
    def animate(self):
        if self.status not in self.animations:
            return
        
        animation = self.animations[self.status]
        animation_size = len(animation)

        self.frame_index += self.animation_speed
        if self.frame_index >= animation_size:
            if self.status == 'attack':
                self.can_attack = False

            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def update(self) -> None:
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()
    
    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
