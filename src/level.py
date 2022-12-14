from random import choice, randint

import pygame

from src.enemy import Enemy 
from src.particles import AnimationPlayer
from src.player.player import Player
from src.player.magic import MagicPlayer
from settings import *
from src.support import import_csv_layout, import_folder_imgs
from src.tile import Tile
from src.ui import Ui
from src.weapon import Weapon
from src.menus.upgrade import UpgradeMenu


class Level:
    def __init__(self) -> None:
        # Get display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # Sprite groups setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
    
        # Attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Sprite setup
        self.create_world()

        # User Interface
        self.ui = Ui()
        self.upgrade_menu = UpgradeMenu(self.player)

        # Particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_world(self) -> None:
        layouts = {
            'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('./map/map_Grass.csv'),
            'object': import_csv_layout('./map/map_Objects.csv'),
            'entities': import_csv_layout('./map/map_Entities.csv')
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
                                groups=[self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
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
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    pos=(x,y),
                                    groups=[self.visible_sprites],
                                    obstacle_sprites=self.obstacle_sprites,
                                    create_attack=self.create_attack,
                                    destroy_attack=self.destroy_attack,
                                    create_magic=self.create_magic
                                )
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                else: monster_name = 'squid'

                                self.enemy = Enemy(
                                    monster_name=monster_name,
                                    position=(x, y),
                                    groups=[self.visible_sprites, self.attackable_sprites],
                                    obstacle_sprites=self.obstacle_sprites,
                                    damage_player=self.damage_player,
                                    trigger_death_particles=self.trigger_death_particles,
                                    add_xp = self.add_xp
                                )

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    sprite=attack_sprite,
                    group=self.attackable_sprites,
                    dokill=False
                )

                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            position = target_sprite.rect.center
                            offset = pygame.math.Vector2(0 ,75)

                            for _ in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(
                                    position=position - offset, groups=[self.visible_sprites]
                                )
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(
                player=self.player,
                strength=strength,
                magic_cost=cost,
                groups=[self.visible_sprites]
            )

        if style == 'flame':
            self.magic_player.flame(
                player=self.player,
                cost=cost,
                groups=[self.visible_sprites, self.attack_sprites]
            )

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(
                animation_type=attack_type,
                position=self.player.rect.center,
                groups=[self.visible_sprites]
            )

    def trigger_death_particles(self, position, particle_type):
        self.animation_player.create_particles(
            animation_type=particle_type,
            position=position,
            groups=[self.visible_sprites]
        )

    def add_xp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def run(self) -> None:
        """Update and draw the game"""
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade_menu.display()
            # display upgrade menu
        else:
            # run the game
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()


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

    def enemy_update(self, player) -> None:
        enemy_sprites = [
            sprite\
            for sprite in self.sprites()\
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy'
        ]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)