from os import walk
from csv import reader
import pygame

def import_csv_layout(path):
    layouts = []
    with open(path) as f:
        layout = reader(f, delimiter=',')
        for row in layout:
            layouts.append(list(row))
    
    return layouts


def import_folder(path):
    imgs = []
    for root, _, files in walk(path):
        for file in files:
            imgs.append(pygame.image.load(f'{root}/{file}').convert_alpha())
    
    return imgs