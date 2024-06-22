import pygame
from settings import *
from particles import AnimationPlayer
from re import sub
from random import randint

class MagicPlayer:
    def __init__(self, animation_player: AnimationPlayer) -> None:
        self.animation_player = animation_player
    
    def heal(self, player, cost, strength, *groups):
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
        
            self.animation_player.generate_particles('aura', player.rect.center, *groups, speed=.2)
            self.animation_player.generate_particles('heal', player.rect.center, *groups, speed=.2)

    
    def flame(self, player, cost, *groups, **kwargs):
        if player.energy >= cost:
            player.energy -= cost

            status = sub(r'_\w+$', '', player.status)
            print(status)
            if status == 'right': direction = pygame.math.Vector2(1, 0)
            elif status == 'left': direction = pygame.math.Vector2(-1, 0)
                
            elif status == 'up': direction = pygame.math.Vector2(0, -1)
            elif status == 'down': direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x:
                    offset_x = direction.x * i * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.generate_particles('flame', (x,y), *groups)
                
                else:
                    offset_y = direction.y * i * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.generate_particles('flame', (x,y), *groups)


