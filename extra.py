import pygame
import random
from additionally import load_music


# Класс для работы с музыкой
class Music:
    # Задаем начальные параметры
    def __init__(self, filename):
        self.sound = load_music(filename)
        self.sound.set_volume(0.25)
        self.active = 0

    # Воспроизводим
    def play(self):
        if self.sound and not self.active:
            self.sound.play(loops=-1)
            self.active = 1
    
    # Останавливаем
    def stop(self):
        if self.sound:
            self.sound.stop()
            self.active = 0
    

# Класс для конца одной линии
class End:
    # Задаем начальные параметры
    def __init__(self, text, funct):
        self.text = Text((20, 20), text, 400, font_size=40)
        self.active = 0
        self.functinon = funct
    
    # Изменяем текст
    def set_text(self, text):
        self.text = self.text.is_copy_retext(text)

    # Изменяем активность
    def set_active(self, active):
        self.active = active

    # Отрисовываем
    def draw(self, win):
        if self.active:
            self.text.draw_text(win)

    # Заканчиваем
    def end(self):
        if not self.active:
            return
        self.active = 0
        if self.functinon:
            self.functinon()


# Класс для работы с сумашедшими теньками
class ShadowBall(pygame.sprite.Sprite):
    # Задаем начальные параметры
    def __init__(self, pos, size, end, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.image.set_alpha(150)
        self.end = end
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.vect = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.v = [random.randrange(1, 20) / 5, random.randint(1, 20) / 5]

    # Копируем объект со смещением
    def copy_shadowball_move(self, pos):
        return ShadowBall((self.rect.x + pos[0], self.rect.y + pos[1]), self.rect.size, None)

    # Обновляем
    def update(self, player, solids_group):
        if pygame.sprite.collide_mask(self, player):
            self.end.set_text(
                "Вы попали в тень временной аномалии и вас вернуло обратно..\n[нажмите пробел чтобы продолжить]"
                )
            self.end.set_active(1)
        if pygame.sprite.spritecollideany(
                self.copy_shadowball_move([self.vect[0] * self.v[0], self.vect[1] * self.v[1]]), 
                solids_group, 
                pygame.sprite.collide_mask
                ):
            self.vect = [random.choice([-1, 1]), random.choice([-1, 1])]
            self.v = [random.randrange(1, 10), random.randint(1, 10)]
            return
        self.rect.x += self.vect[0] * self.v[0]
        self.rect.y += self.vect[1] * self.v[1]


# Класс для работы с текстом
class Text:
    # Задаем начальные параметры
    def __init__(self, pos, text, max_width=200, font_name=None, font_size=26, 
                 text_color=(245, 245, 245), bg_color=(0, 0, 0)):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_name = font_name
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.x, self.y = pos

        self.text_list = []

        self.max_width = max_width
        
        words = [word.split(" ") for word in text.replace("\\n", "\n").splitlines()]
        space = self.font.size(" ")[0]
        line_spasing = 10
        x, y = pos
        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, self.text_color)
                word_width, word_height = word_surface.get_size()
                if x + word_width - pos[0] >= self.max_width:
                    x = pos[0]
                    y += word_height + line_spasing
                self.text_list += [(word_surface, (x, y))]
                x += word_width + space
            x = pos[0]
            y += word_height + line_spasing
        
        self.max_height = y - line_spasing - pos[1]

    # Отрисовываем      
    def draw_text(self, win):
        pygame.draw.rect(win, self.bg_color, (self.x - 5, self.y - 5, self.max_width + 10, self.max_height + 10))

        for word in self.text_list:
            win.blit(*word)

    # Перемещаем
    def move(self, x, y):
        self.text_list = [(word[0], (word[1][0] + x, word[1][1] + y)) for word in self.text_list]
        self.x += x
        self.y += y

    # Изменяем цвет
    def set_bg_color(self, color):
        self.bg_color = color

    # Получаем максимальную высоту
    def is_max_height(self):
        return self.max_height

    # Копируем объект с другим текстом
    def is_copy_retext(self, text):
        return Text((self.x, self.y), text, self.max_width, self.font_name, 
                    self.font_size, self.text_color, self.bg_color)


# Класс для работы с триггерами
class Trigger(pygame.sprite.Sprite):
    # Задаем начальные параметры
    def __init__(self, pos, size, *groups, color=(255, 255, 255)):
        super().__init__(*groups)
        self.image = pygame.Surface(size)
        self.color = color
        self.image.fill(self.color)
        self.image.set_alpha(50)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

        self.active = 0

    # Отрисовываем
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

    # Обновляем
    def update(self, obj, camera):
        self.active = pygame.sprite.collide_mask(self, obj)
        self.image.fill("red" if self.active else self.color)
        camera.apply_mode(self)

    # Перемещаем
    def move(self, x, y):
        ...


# Класс для работы с триггерами которые ведут к другому месту
class TriggerTP(Trigger):
    # Задаем начальные параметры
    def __init__(self, pos, size, time, namemap, folder, *groups, color=(255, 255, 255)):
        super().__init__(pos, size, *groups, color=color)
        self.time_const = time
        self.time = 0
        self.namemap = namemap
        self.clock = None
        self.folder = folder
        self.active_tp = 0
    
    # Обновляем
    def update(self, obj, camera):
        if pygame.sprite.collide_mask(self, obj):
            if not self.clock:
                self.active_tp = 1
                self.clock = pygame.time.Clock()
        if self.active_tp:
            self.time += self.clock.tick()
        if self.time >= self.time_const:
            self.active_tp = 0
            self.time = 0
            self.clock = None
            self.folder.set_namemap(self.namemap)
        return super().update(obj, camera)


# Класс для работы с триггерами которые выводят текст
class TriggerText(Trigger):
    # Задаем начальные параметры
    def __init__(self, pos, size, text, *groups, color=(255, 255, 255)):
        super().__init__(pos, size, *groups, color=color)
        self.text = text

    # Отрисовываем
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))
        if self.active:
            self.text.draw_text(win)

    # Перемещаем
    def move(self, x, y):
        self.text.move(x, y)


# Класс для работы с триггерами которые выводят текст и ведут к другому месту
class TriggerTextTP(TriggerText):
    # Задаем начальные параметры
    def __init__(self, pos, size, text, time, namemap, folder, *groups, color=(255, 255, 255)):
        super().__init__(pos, size, text, *groups, color=color)
        self.time_const = time
        self.time = 0
        self.namemap = namemap
        self.clock = None
        self.folder = folder
        self.active_tp = 0
    
    # Обновляем
    def update(self, obj, camera):
        if pygame.sprite.collide_mask(self, obj):
            if not self.clock:
                self.active_tp = 1
                self.clock = pygame.time.Clock()
        if self.active_tp:
            self.time += self.clock.tick()
        if self.time >= self.time_const:
            self.active_tp = 0
            self.time = 0
            self.clock = None
            self.folder.set_namemap(self.namemap)
        return super().update(obj, camera)


# Класс для работы со временем
class TimeLimit:
    # Задаем начальные параметры
    def __init__(self, pos):
        self.text = Text(pos, "", 100, font_size=40)

        self.time_end_const = 1342000
        self.time_const = 1340000
        self.time = 1000000
        self.clock = pygame.time.Clock()

        size = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.image = pygame.Surface(size)
        self.image.fill((0, 0, 0))
        self.image.set_alpha(0)

        self.function = None

    # Отрисовываем
    def draw(self, win):
        win.blit(self.image, (0, 0))
        self.text.draw_text(win)

    # Обновляем
    def update(self):
        self.time += self.clock.tick()
        self.text = self.text.is_copy_retext(f"{self.time // 60000:0>2}:{self.time // 1000 % 60:0>2}")
        if self.time / 1000 < self.time_const // 1000:
            return
        self.image.set_alpha((self.time - 1340000) * 255 // (self.time_end_const - 1340000))
        if self.time / 1000 < self.time_end_const // 1000:
            return
        if not self.function:
            return
        self.function()
    
    # Получаем время
    def is_time(self):
        return self.time
    
    # Подключаем функцию
    def connect(self, function):
        self.function = function


# Класс для работы с камерой
class Camera:
    # Зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    # Сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # Сдвинуть объект obj на смещение камеры
    def apply_mode(self, obj):
        obj.move(self.dx, self.dy)
    
    # Позиционировать камеру на объекте target
    def update(self, target):
        size = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.dx = -(target.rect.x + target.rect.w // 2 - size[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - size[1] // 2)


# Класс для работы с выводом координат на мышке
class SeekerPos:
    # Задаем начальные параметры
    def __init__(self):
        self.text = Text((0, 0), "")
        self.real_pos = [0, 0]
    
    # Перемещаем
    def move(self, x, y):
        self.real_pos[0] += x
        self.real_pos[1] += y

    # Изменяем позицию
    def set_pos(self, pos):
        self.real_pos = pos

    # Изменяем текст
    def set_text(self, pos):
        self.text = Text((pos[0], pos[1] - 20), f"(x: {pos[0] - self.real_pos[0]}; y: {pos[1] - self.real_pos[1]})", 
                         max_width=100, font_size=16)

    # Отрисовываем
    def draw(self, win):
        self.text.draw_text(win)


# Класс для работы с кнопками
class Button:
    # Задаем начальные параметры
    def __init__(self, pos, text, max_width, font_size=20):
        self.pos = pos
        self.text = Text((self.pos[0] + 5, self.pos[1] + 5), text, max_width, 
                         font_size=font_size, bg_color=(100, 100, 100))

        self.size = (max_width + 10, self.text.is_max_height() + 10)
        self.current_btn = 0
        self.not_induced_btn = [(100, 100, 100)]
        self.induced_btn = [(80, 80, 80)]
        self.squeezed_btn = [(60, 60, 60)]

        self.function = None

    # Отрисовываем
    def draw(self, win):
        if self.current_btn == 0:
            self.text.set_bg_color(self.not_induced_btn[0])
        elif self.current_btn == 1:
            self.text.set_bg_color(self.induced_btn[0])
        elif self.current_btn == 2:
            self.text.set_bg_color(self.squeezed_btn[0])
        self.text.draw_text(win)
    
    # Проверяем находится ли мышка на кнопке
    def examination(self, x, y):
        if not self.pos[0] <= x <= self.pos[0] + self.size[0]:
            return False
        if not self.pos[1] <= y <= self.pos[1] + self.size[1]:
            return False
        return True

    # Обрабатываем наведение
    def mouse_motion(self, x, y):
        if not self.examination(x, y):
            if self.current_btn == 2:
                return
            self.current_btn = 0
            return
        if self.current_btn == 2:
            return
        self.current_btn = 1
    
    # Обрабатываем нажатие
    def mouse_down(self, x, y):
        if not self.examination(x, y):
            self.current_btn = 0
            return
        self.current_btn = 2
    
    # Обрабатываем отпускание
    def mouse_up(self, x, y):
        if not self.examination(x, y):
            self.current_btn = 0
            return
        if self.current_btn != 2:
            return
        self.current_btn = 0
        if self.function:
            self.function()
    
    # Подключаем функцию
    def connect(self, function):
        self.function = function