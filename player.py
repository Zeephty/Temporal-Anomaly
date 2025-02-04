import pygame
from additionally import load_image


# Класс игрока
class Player(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, pos, *groups, image=None):
        super().__init__(*groups)

        self.image_def = image if image else load_image("player_default.png", 1)
        self.image = self.image_def

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
    
    # Перемещение
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
    
    # Копируем игрока с новыми координатами
    def copy_player_move(self, x, y, image):
        return Player((self.rect.x + x, self.rect.y + y), image=image)