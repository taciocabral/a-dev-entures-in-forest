from typing import Tuple

import pygame
from pygame.sprite import AbstractGroup

from settings import *
from src.support import *
from src.entity import Entity
from src.player.player import Player


class Enemy(Entity):
    def __init__(
        self,
        monster_name,
        position,
        groups: AbstractGroup,
        obstacle_sprites,
        damage_player,
        trigger_death_particles,
        add_xp
    ) -> None:

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
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_xp = add_xp

        # Invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

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

    def get_status(self, player) -> None:
        distance_of_player = self.get_player_distance_direction(player)[0]

        if distance_of_player <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance_of_player <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def actions(self, player) -> None:
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(
                self.attack_damage, self.attack_type
            )
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self) -> None:
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self) -> None:
        current_time = pygame.time.get_ticks()

        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player: Player, attack_type) -> None:
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]

            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
                # magic damage
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
    
    def check_death(self) -> None:
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(
                self.rect.center,
                self.monster_name
            )
            self.add_xp(self.exp)

    def hit_reaction(self) -> None:
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self) -> None:
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()
    
    def enemy_update(self, player) -> None:
        self.get_status(player)
        self.actions(player)
