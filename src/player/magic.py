from random import randint

import pygame

from src.settings import *
from src.player.player import Player

class MagicPlayer:
    def __init__(self, animation_player) -> None:
        self.animation_player = animation_player

    def heal(self, player: Player, strength, magic_cost, groups):
        if player.energy >= magic_cost:
            player.health += strength
            player.energy -= magic_cost

            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            
            self.animation_player.create_particles(
                animation_type='aura',
                position=player.rect.center,
                groups=groups
            )
            self.animation_player.create_particles(
                animation_type='heal',
                position=player.rect.center,
                groups=groups
            )

    def flame(self, player: Player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
        
            if player.status.split('_')[0] == 'right':
                direction = pygame.math.Vector2(1,0)
            elif player.status.split('_')[0] == 'left':
                direction = pygame.math.Vector2(-1,0)
            elif player.status.split('_')[0] == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0,1)

            for i in range(1, 6):
                if direction.x: # horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x,y), groups)
                else: # vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x,y), groups)
