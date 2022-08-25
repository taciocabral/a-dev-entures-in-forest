from typing import List
from random import choice

import pygame
from pygame.sprite  import AbstractGroup

from src.support import import_folder_imgs


class AnimationPlayer:
    def __init__(self) -> None:
        self.frames = {
            # magic
            'flame': import_folder_imgs('./graphics/particles/flame/frames'),
            'aura': import_folder_imgs('./graphics/particles/aura'),
            'heal': import_folder_imgs('./graphics/particles/heal/frames'),
            
            # attacks 
            'claw': import_folder_imgs('./graphics/particles/claw'),
            'slash': import_folder_imgs('./graphics/particles/slash'),
            'sparkle': import_folder_imgs('./graphics/particles/sparkle'),
            'leaf_attack': import_folder_imgs('./graphics/particles/leaf_attack'),
            'thunder': import_folder_imgs('./graphics/particles/thunder'),
 
            # monster deaths
            'squid': import_folder_imgs('./graphics/particles/smoke_orange'),
            'raccoon': import_folder_imgs('./graphics/particles/raccoon'),
            'spirit': import_folder_imgs('./graphics/particles/nova'),
            'bamboo': import_folder_imgs('./graphics/particles/bamboo'),
            
            # leafs 
            'leaf': (
                import_folder_imgs('./graphics/particles/leaf1'),
                import_folder_imgs('./graphics/particles/leaf2'),
                import_folder_imgs('./graphics/particles/leaf3'),
                import_folder_imgs('./graphics/particles/leaf4'),
                import_folder_imgs('./graphics/particles/leaf5'),
                import_folder_imgs('./graphics/particles/leaf6'),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf1')),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf2')),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf3')),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf4')),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf5')),
                self.reflect_images(import_folder_imgs('./graphics/particles/leaf6'))
            )
        }

    def reflect_images(self, frames) -> List:
        new_frames = []

        for frame in frames:
            flipped_frame = pygame.transform.flip(
                surface=frame,
                flip_x=True,
                flip_y=False
            )
            new_frames.append(flipped_frame)
        
        return new_frames

    def create_grass_particles(self, position, groups: List):
        animation_frames = choice(self.frames['leaf'])
        PartcileEffect(position, animation_frames, groups)
    
    def create_particles(self, animation_type, position, groups):
        animation_frames = self.frames[animation_type]
        PartcileEffect(position, animation_frames, groups)


class PartcileEffect(pygame.sprite.Sprite):
    def __init__(self, position, animation_frames, *groups: AbstractGroup) -> None:
        super().__init__(*groups)

        self.sprite_type = 'magic'
        self.frame_index = 0
        self.animation_speed = .15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = position)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames) :
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self) -> None:
        self.animate()
