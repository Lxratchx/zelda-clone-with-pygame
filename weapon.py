import pygame
from player import Player
from re import sub
from settings import *
from os import path

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player: Player, *groups) -> None:
        super().__init__(*groups)
        direction = sub(r'_\w+$', '', player.status)
        graphics = f'graphics/weapons/{player.weapon}'

        # graphics
        full_path = path.join(graphics, f'{direction}.png')
        self.image = pygame.image.load(full_path).convert_alpha()
        directions = {
            'right': self.image.get_rect(midleft=player.rect.midright+pygame.math.Vector2(0, 16)),
            'left': self.image.get_rect(midright=player.rect.midleft+pygame.math.Vector2(0, 16)),
            'up': self.image.get_rect(midbottom=player.rect.midtop - pygame.math.Vector2(10, 0)),
            'down': self.image.get_rect(midtop=player.rect.midbottom - pygame.math.Vector2(10, 0))
        }

        # placement
        try:
            self.rect = directions[direction]

        except KeyError:
            self.rect = self.image.get_rect(center=player.rect.center)
