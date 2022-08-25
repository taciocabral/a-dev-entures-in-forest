from typing import Union
import pygame

from src.settings import *
from src.support import import_folder_imgs
from src.entity import Entity


class Player(Entity):
    def __init__(
        self,
        pos,
        groups,
        obstacle_sprites,
        create_attack,
        destroy_attack,
        create_magic
    ) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load('./graphics/player/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -50 )

        # Graphics Setup
        self.import_player_assets()
        self.status = 'down'

        # Movement
        self.attaking = False
        self.attack_cooldown = 400 
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        # Weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(WEAPON_DATA.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None

        # Magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(MAGIC_DATA.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        self.switch_duration_cooldown = 200

        # Stats
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 4,
            'speed': 5,
        }
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.speed = self.stats['speed']
        self.exp = 123

        # Damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

    def import_player_assets(self) -> None:
        player_path = './graphics/player/'
        self.animations = {
            'up': [],
            'down': [],
            'left': [],
            'right': [],
            'up_idle': [],
            'down_idle': [],
            'left_idle': [],
            'right_idle': [],
            'up_attack': [],
            'down_attack': [],
            'left_attack': [],
            'right_attack': [],
        }

        for animation in self.animations.keys():
            full_path = player_path + animation
            self.animations[animation] = import_folder_imgs(full_path)
    
    def key_input(self) -> None:
        """Map the keyboard key to generate an action on player"""

        if not self.attaking:
            keys = pygame.key.get_pressed()

            # movement input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # attack input
            if keys[pygame.K_SPACE]:
                self.attaking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attaking = True
                self.attack_time = pygame.time.get_ticks()

                style = list(MAGIC_DATA.keys())[self.magic_index]
                strength = list(MAGIC_DATA.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(MAGIC_DATA.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            # select weapon
            if keys[pygame.K_w] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(list(WEAPON_DATA.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                self.weapon = list(WEAPON_DATA.keys())[self.weapon_index]

            # select magic
            if keys[pygame.K_m] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                if self.magic_index < len(list(MAGIC_DATA.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0
                self.magic = list(MAGIC_DATA.keys())[self.magic_index]

    def get_status(self) -> None:
        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attaking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    # overwrite idle
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def cooldowns(self) -> None:
        """Check the time of attack and magic actions to cooldown the actions"""
        current_time = pygame.time.get_ticks()
        if self.attaking:
            if current_time - self.attack_time >= self.attack_cooldown + WEAPON_DATA[self.weapon]['cooldown']:
                self.attaking = False
                self.destroy_attack()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True
        
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self) -> None:
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        # Flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        

    def get_full_weapon_damage(self) -> Union[float, int]:
        base_damage = self.stats['attack']
        weapon_damage =  WEAPON_DATA[self.weapon]['damage']

        return base_damage + weapon_damage

    def update(self) -> None:
        self.key_input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)