import pygame

from debug import debug
from src.settings import *
from src.tile import Tile
from src.player import Player


class Level:
    def __init__(self) -> None:
        # Get display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups setup
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
    
        # Sprite setup
        self.create_world_map()

    def create_world_map(self):
        """Map the WORLD_MAP to generate the graphics"""

        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if col == 'x':
                    Tile(
                        pos=(x,y),
                        groups=[self.visible_sprites, self.obstacle_sprites]
                    )
                if col == 'p':
                    self.player = Player(
                        pos=(x,y),
                        groups=[self.visible_sprites],
                        obstacle_sprites=self.obstacle_sprites
                    )

    def run(self) -> None:
        self.visible_sprites.draw(self.display_surface)
        self.visible_sprites.update()
        debug(self.player.direction)
