from os import walk
from csv import reader
from typing import List

import pygame
from pygame.surface import Surface

def import_csv_layout(path: str) -> List[List]:
    terrain_map = []

    with(open(path)) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))

        return terrain_map

def import_folder_imgs(path: str) -> List[Surface]:
    surface_list = []

    for _, _, img_files in walk(path):
        if 'objects' in path:
            img_files = sorted(img_files, key=lambda filename: int(filename.split('.')[0]))
        else:
            img_files.sort()


        for img in img_files:
            full_path = path + '/' + img
            img_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surface)

    return surface_list
