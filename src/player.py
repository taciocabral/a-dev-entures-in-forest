import pygame

from src.settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(*groups)

        self.image = pygame.image.load('./graphics/player/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)