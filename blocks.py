import pygame
from additionally import load_image


# Класс картинки
class Image(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, pos, filename, *groups):
        super().__init__(*groups)
        self.image = load_image(filename, 1)
        self.rect = self.image.get_rect().move(*pos)


# Класс стен
class Side(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, pos, sprite_group, all_sprites, type_side, angle_side):
        super().__init__(sprite_group, all_sprites)
        all_images = {
            "side_1": load_image("side_1.png", 1),
            "side_2": load_image("side_2.png", 1),
            "side_3": load_image("glass.png", 1),
            "side_4": load_image("door.png", 1),
            "side_5": load_image("side_3.png", 1)
        }
        self.image = pygame.transform.rotate(all_images["side_" + str(type_side + 1)], angle_side)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos