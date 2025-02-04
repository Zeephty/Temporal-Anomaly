import os
import pygame


def load_image(name, alpha=False):
    fullname = os.path.join("data", "images", name)
    if os.path.isfile(fullname):
        image = pygame.image.load(fullname)
        if alpha:
            image.convert_alpha()
        return image


def load_music(name):
    fullname = os.path.join("data", "music", name)
    if os.path.isfile(fullname):
        sound = pygame.mixer.Sound(fullname)
        return sound