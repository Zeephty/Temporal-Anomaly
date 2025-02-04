import pygame
from extra import SeekerPos, Button, TimeLimit, End, Music
from gamef import FolderFields


# Пустая сцена
class EmptyScene:
    # Конструктор
    def __init__(self, funct_set_scene):
        # Присваиваем переменной функцию смены сцены
        self.set_scene = funct_set_scene

    # Рисуем сцену
    def draw(self, win):
        ...

    # Обновляем сцену
    def update(self):
        ...
    
    # Действие движения мыши
    def mouse_motion(self, x, y):
        ...

    # Действие нажатия мыши 
    def mouse_down(self, x, y):
        ...

    # Действие отпускания мыши
    def mouse_up(self, x, y):
        ...

    # Действие дополнительных событий
    def event_additional(self, event):
        ...


# Главный центр всех сцен
class StageCenter:
    def __init__(self, win):
        self.win = win
        self.seeker = SeekerPos()

        self.music = Music("x.mp3")
        self.music.play()

        # Словарик сцен
        self.scenes = {
            "MainMenu": MainMenu(self.set_scene),
            "Game": Game(self.set_scene, self.seeker, win),
            "GameMenu": GameMenu(self.set_scene)
        }

        # Текущая сцена
        self.current_scene = "MainMenu"

    # Рисуем сцены
    def draw(self, win):
        win.fill((15, 45, 50))

        self.scenes[self.current_scene].draw(win)
        self.seeker.draw(win)

    # Обновляем сцены
    def update(self):
        self.scenes[self.current_scene].update()

    # Действие движения мыши
    def mouse_motion(self, x, y):
        self.seeker.set_text(pygame.mouse.get_pos())
        self.scenes[self.current_scene].mouse_motion(x, y)

    # Действие нажатия мыши
    def mouse_down(self, x, y):
        self.scenes[self.current_scene].mouse_down(x, y)

    # Действие отжатия мыши
    def mouse_up(self, x, y):
        self.scenes[self.current_scene].mouse_up(x, y)

    # Функция проверки отдельных параметров для определенных сцен
    def event_additional(self, event):
        self.scenes[self.current_scene].event_additional(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.music.stop()
            if event.key == pygame.K_o:
                self.music.play()

    # Меняем сцену
    def set_scene(self, scene):
        self.current_scene = scene


# Игровая сцена
class Game(EmptyScene):
    def __init__(self, funct_set_scene, seeker, win):
        self.seeker = seeker
        self.win = win

        self.end = End("", self.set_map)

        self.timelimit = TimeLimit((30, 30))
        self.timelimit.connect(self.set_map)

        # Создаем папку с картами
        self.fields = FolderFields(self.win, "map1.txt", self.seeker, self.end)

        super().__init__(funct_set_scene)
    
    # Рисуем сцену игры
    def draw(self, win):
        self.end.draw(win)
        if self.end.active:
            return
        self.fields()
        self.fields.is_camera().apply_mode(self.seeker)
        self.timelimit.draw(win)
    
    # Обновляем сцену
    def update(self):
        if self.end.active:
            return
        
        self.timelimit.update()

        keys = pygame.key.get_pressed()

        # перемещение персонажа
        if keys[pygame.K_w]:
            self.fields.move_player(0, -2)
            self.seeker.set_text(pygame.mouse.get_pos())
        if keys[pygame.K_s]:
            self.fields.move_player(0, 2)
            self.seeker.set_text(pygame.mouse.get_pos())
        if keys[pygame.K_a]:
            self.fields.move_player(-2, 0)
            self.seeker.set_text(pygame.mouse.get_pos())
        if keys[pygame.K_d]:
            self.fields.move_player(2, 0)
            self.seeker.set_text(pygame.mouse.get_pos())
    
    def event_additional(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_scene("GameMenu")
            if event.key == pygame.K_SPACE:
                self.end.end()
            
    # Изменяем карту
    def set_map(self):
        self.timelimit = TimeLimit((30, 30))
        self.timelimit.connect(self.set_map)
        
        self.fields = FolderFields(self.win, "map1.txt", self.seeker, self.end)


# Сцена главного меню
class GameMenu(EmptyScene):
    def __init__(self, funct_set_scene):
        size = pygame.display.Info().current_w, pygame.display.Info().current_h

        self.button_play = Button((size[0] - 300, size[1] - 300), "Играть", 220, font_size=90)
        self.button_play.connect(self.play_click)

        self.button_exit = Button((size[0] - 300, size[1] - 200), "Выход в меню", 150, font_size=30)
        self.button_exit.connect(self.close_menu_click)
        
        super().__init__(funct_set_scene)

    # Рисуем сцену
    def draw(self, win):
        self.button_play.draw(win)
        self.button_exit.draw(win)

    # Отслеживаем передвижение мыши
    def mouse_motion(self, x, y):
        self.button_play.mouse_motion(x, y)
        self.button_exit.mouse_motion(x, y)

    # Отслеживаем нажатие ммыши
    def mouse_down(self, x, y):
        self.button_play.mouse_down(x, y)
        self.button_exit.mouse_down(x, y)

    # Отслеживаем отжатие мыши
    def mouse_up(self, x, y):
        self.button_play.mouse_up(x, y)
        self.button_exit.mouse_up(x, y)

    # Функция нажатия на кнопку играть
    def play_click(self):
        self.set_scene("Game")

    # Функция нажатия на кнопку выход
    def close_menu_click(self):
        self.set_scene("MainMenu")


# Сцена главного меню
class MainMenu(EmptyScene):
    def __init__(self, funct_set_scene):
        size = pygame.display.Info().current_w, pygame.display.Info().current_h

        self.button_play = Button((size[0] - 300, size[1] - 300), "Играть", 220, font_size=90)
        self.button_play.connect(self.play_click)

        self.button_exit = Button((size[0] - 200, size[1] - 200), "Выход", 100, font_size=30)
        self.button_exit.connect(self.close_click)
        
        super().__init__(funct_set_scene)

    # Рисуем сцену
    def draw(self, win):
        self.button_play.draw(win)
        self.button_exit.draw(win)

    # Отслеживаем передвижение мыши
    def mouse_motion(self, x, y):
        self.button_play.mouse_motion(x, y)
        self.button_exit.mouse_motion(x, y)

    # Отслеживаем нажатие ммыши
    def mouse_down(self, x, y):
        self.button_play.mouse_down(x, y)
        self.button_exit.mouse_down(x, y)

    # Отслеживаем отжатие мыши
    def mouse_up(self, x, y):
        self.button_play.mouse_up(x, y)
        self.button_exit.mouse_up(x, y)

    # Функция нажатия на кнопку играть
    def play_click(self):
        self.set_scene("Game")

    # Функция нажатия на кнопку выход
    def close_click(self):
        exit()