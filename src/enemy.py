from typing import Tuple
import pygame
from pygame.sprite import AbstractGroup

from src.settings import *
from src.support import *
from src.entity import Entity


class Enemy(Entity):
    def __init__(self, monster_name, position, groups: AbstractGroup, obstacle_sprites) -> None:

        # General setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # Graphics Setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # Movement
        self.rect = self.image.get_rect(topleft = position)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # Stats
        self.monster_name = monster_name
        monster_info = ENEMY_MONSTERS_DATA[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # Player Interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400


    def import_graphics(self, monster_name: str) -> None:
        self.animations = {
            'idle': [],
            'move': [],
            'attack': []
        }

        main_path = f'./graphics/monsters/{monster_name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder_imgs(
                main_path + animation
            )

    def get_player_distance_direction(self, player) -> Tuple[int, int]:
        enemy_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(player.rect.center)

        distance = (player_vector - enemy_vector).magnitude()

        if distance > 0:
            direction = (player_vector - enemy_vector).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player):
        distance_of_player = self.get_player_distance_direction(player)[0]

        if distance_of_player <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance_of_player <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def cooldown(self):
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

    def update(self):
        self.move(self.speed)
        self.animate()
        self.cooldown()
    
    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
