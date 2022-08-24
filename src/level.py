from random import choice

import pygame

from src.settings import *
from src.tile import Tile
from src.player import Player
from src.support import import_csv_layout, import_folder_imgs
from src.ui import Ui
from src.weapon import Weapon

class Level:
    def __init__(self) -> None:
        # Get display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
    
        # Sprite setup
        self.create_world()

        # Attack sprites
        self.current_attack = None

        # User Interface
        self.ui = Ui()

    def create_world(self) -> None:
        layouts = {
            'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('./map/map_Grass.csv'),
            'object': import_csv_layout('./map/map_Objects.csv')
        }
        graphics = {
            'grass': import_folder_imgs('./graphics/grass'),
            'objects': import_folder_imgs('./graphics/objects')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == 'boundary':
                            Tile(
                                pos=(x,y),
                                groups=[self.obstacle_sprites],
                                sprite_type='invisible',
                            )
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile(
                                pos=(x,y),
                                groups=[self.visible_sprites, self.obstacle_sprites],
                                sprite_type='grass',
                                surface=random_grass_image
                            )
                        if style == 'object':
                            surface = graphics['objects'][int(col)]
                            Tile(
                                pos=(x,y),
                                groups=[self.visible_sprites, self.obstacle_sprites],
                                sprite_type='object',
                                surface=surface
                            )

        self.player = Player(
            pos=(2000,1500),
            groups=[self.visible_sprites],
            obstacle_sprites=self.obstacle_sprites,
            create_attack=self.create_attack,
            destroy_attack=self.destroy_attack,
            create_magic=self.create_magic
        )

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_magic(self, style, strength, cost):
        pass

    def run(self) -> None:
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        # general setup
        super().__init__(*sprites)
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating floor
        self.floor_surface = pygame.image.load('./graphics/tilemap/ground.png')
        self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))

    def custom_draw(self, player) -> None:
        # getting offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_position = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_position)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)
