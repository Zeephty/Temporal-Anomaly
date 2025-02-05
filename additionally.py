import os
import pygame


# Функция загрузки изображения
def load_image(name, alpha=False):
    fullname = os.path.join("data", "images", name)
    if os.path.isfile(fullname):
        image = pygame.image.load(fullname)
        if alpha:
            image.convert_alpha()
        return image


# Функция загрузки музыки
def load_music(name):
    fullname = os.path.join("data", "music", name)
    if os.path.isfile(fullname):
        sound = pygame.mixer.Sound(fullname)
        return sound
    

# Функция загрузки достижений
def load_achievement(name):
    fullname = os.path.join("data", name)
    if os.path.isfile(fullname):
        return open(fullname, "r", encoding="utf8")
    

# Функция записи достижений
def rep_achievement(name, text):
    fullname = os.path.join("data", name)
    list_achievement = []
    with load_achievement(name) as f:
        list_achievement = [i.strip() for i in f]
    with open(fullname, "w", encoding="utf8") as file:
        for i in list_achievement:
            file.write(i + "\n")
        file.write(text)