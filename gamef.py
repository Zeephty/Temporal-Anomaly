import os
import pygame
from extra import Text, Camera, TriggerText, TriggerTextTP, TriggerTP, ShadowBall, TriggerEnd
from player import Player
from blocks import Image, Side


# Класс папки с картами
class FolderFields:
    # Инициализация
    def __init__(self, win, filename, seeker, end):
        self.win = win
        self.fields = {}
        self.seeker = seeker

        self.size = 64

        fullname = os.path.join("data", "maps", filename)

        with open(fullname, "r", encoding="utf8") as file:
            n, self.namemap = file.readline().split()
            for _ in range(int(n)):
                file.readline()

                name, count_cage, count_commands = file.readline().split("||")
                pos = file.readline()

                count_cage = list(map(int, count_cage.split()))

                all_sprites = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                solids_group = pygame.sprite.Group()
                triggers_group = pygame.sprite.Group()
                background_group = pygame.sprite.Group()
                showdown_group = pygame.sprite.Group()

                player = Player(list(map(int, pos.split())), player_group, all_sprites)

                if not self.namemap:
                    self.namemap = name
                
                for y in range(count_cage[1]):
                    s = file.readline().split()

                    for x in range(count_cage[0]):
                        if s[x][0] == "#":
                            type_side, rotate_side = map(int, s[x][1:].split("."))
                            Side((self.size * x, self.size * y), solids_group, all_sprites, 
                                 type_side, rotate_side * 90)

                for _ in range(int(count_commands)):
                    name_com, *args = file.readline().split("||")
                    if name_com == "image":
                        Image(list(map(int, args[0].split())), args[1].strip(), all_sprites, background_group)
                    elif name_com == "unit":
                        Image(list(map(int, args[0].split())), args[1].strip(), all_sprites, solids_group)
                    elif name_com == "unit+":
                        x_i, y_i = list(map(int, args[0].split()))
                        pos_trigger, size_trigger = [list(map(int, i.split())) for i in args[2].split("|")]
                        pos_text = list(map(int, args[3].split()))
                        text = Text((x_i + pos_text[0], y_i + pos_text[1]), args[4], font_size=22)
                        TriggerText((x_i + pos_trigger[0], y_i + pos_trigger[1]), 
                                    size_trigger, text, all_sprites, triggers_group)
                        Image((x_i, y_i), args[1].strip(), all_sprites, solids_group)
                    elif name_com == "unitTP":
                        x_i, y_i = list(map(int, args[0].split()))
                        pos_trigger, size_trigger = [list(map(int, i.split())) for i in args[2].split("|")]
                        pos_text = list(map(int, args[3].split()))
                        text = Text((x_i + pos_text[0], y_i + pos_text[1]), args[4], font_size=22)
                        TriggerTextTP((x_i + pos_trigger[0], y_i + pos_trigger[1]), size_trigger, text, 
                                      int(args[5]), args[6].strip(), self, all_sprites, 
                                      triggers_group, color=(255, 212, 44))
                        Image((x_i, y_i), args[1].strip(), all_sprites, solids_group)
                    elif name_com == "triggerEnd":
                        pos_trigger, size_trigger = [list(map(int, i.split())) for i in args[0].split("|")]
                        TriggerEnd(pos_trigger, size_trigger, end, args[1], args[2].strip(), triggers_group, 
                                   all_sprites, color=(255, 212, 84))
                    elif name_com == "triggerTP":
                        pos_trigger, size_trigger = [list(map(int, i.split())) for i in args[0].split("|")]
                        TriggerTP((pos_trigger[0], pos_trigger[1]), size_trigger, 
                                  int(args[1]), args[2].strip(), self, all_sprites, 
                                  triggers_group, color=(255, 212, 84))
                    elif name_com == "shadowball":
                        ShadowBall(list(map(int, args[0].split())), list(map(int, args[1].split())), 
                                   end, args[2].strip(), all_sprites, showdown_group)

                self.fields[name] = Field(win, all_sprites, player_group, solids_group, triggers_group, 
                                          background_group, showdown_group, player)
    
    # Вызов
    def __call__(self):
        self.draw()

    # Рисование
    def draw(self):
        self.fields[self.namemap]()
    
    # Перемещение
    def move_player(self, x, y):
        self.fields[self.namemap].move_player(x, y)

    # Отслеживание мыши
    def tracking_mouse(self, x, y):
        self.fields[self.namemap].tracking_mouse(x, y)

    # Открытие списка
    def open_close_list(self):
        self.fields[self.namemap].open_list()

    # Изменение карты
    def set_namemap(self, namemap):
        self.namemap = namemap
        self.seeker.set_pos([0, 0])
    
    # Получение камеры
    def is_camera(self):
        return self.fields[self.namemap].is_camera()


# Игровое поле
class Field:
    # Инициализация
    def __init__(self, win, all_sprites, player_group, solids_group, 
                 triggers_group, background_group, showdown_group, player):
        self.win = win
        self.all_sprites = all_sprites
        self.player_group = player_group
        self.solids_group = solids_group
        self.triggers_group = triggers_group
        self.background_group = background_group
        self.showdown_group = showdown_group
        self.player = player

        self.camera = Camera()
        
    # Вызов
    def __call__(self):
        self.draw()
        self.update()

    # Рисование
    def draw(self):
        self.background_group.draw(self.win)
        self.solids_group.draw(self.win)
        self.showdown_group.draw(self.win)

        for sprite in self.triggers_group.sprites():
            sprite.draw(self.win)

        self.showdown_group.update(self.player, self.solids_group)
        
        self.triggers_group.update(self.player, self.camera)
        
        self.player_group.draw(self.win)

    # Обновление
    def update(self):
        self.camera.update(self.player)
        for sprite in self.all_sprites.sprites():
            self.camera.apply(sprite)
    
    # Движение
    def move_player(self, x, y):
        for sprite in self.solids_group:
            if pygame.sprite.collide_mask(sprite, self.player.copy_player_move(x, y, self.player.image)):
                return
        self.player.move(x, y)
    
    # Получение камеры
    def is_camera(self):
        return self.camera