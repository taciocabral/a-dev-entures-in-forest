import pygame

from src.settings import *
from src.support import import_folder_imgs


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load('./graphics/player/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -50 )

        # Graphics Setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attaking = False
        self.attack_cooldown = 400 
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites
    
    def import_player_assets(self):
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
    
    def key_input(self):
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

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attaking = True
                self.attack_time = pygame.time.get_ticks()

    def get_status(self):
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

    def move(self, speed) -> None:
        """Move the screen"""
        if self.direction.magnitude() != 0: # To player not run more faster on diagonal
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center 

    def collision(self, direction) -> None:
        """Generate the player hitbox to collisions"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self) -> None:
        """Check the time of attack and magic actions to cooldown the actions"""
        current_time = pygame.time.get_ticks()
        if self.attaking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attaking = False

    def animate(self):
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def update(self) -> None:
        self.key_input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)