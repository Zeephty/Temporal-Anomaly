import pygame
import os
from math import acos, degrees


def load_image(name, alpha=False):
    fullname = os.path.join("data", "images", name)
    if os.path.isfile(fullname):
        image = pygame.image.load(fullname)
        if alpha:
            image.convert_alpha()
        return image


class Side(pygame.sprite.Sprite):
    def __init__(self, pos, sprite_group, all_sprites, type_side, angle_side):
        super().__init__(sprite_group, all_sprites)
        self.image = pygame.transform.rotate(all_images["side_" + str(type_side + 1)], angle_side)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Bot(pygame.sprite.Sprite):
    def __init__(self, current_point, wypoints, *groups):
        super().__init__(*groups)
        
        self.wypoints = wypoints
        self.image = all_images["bot"]

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.current_number = current_point

        self.rect.x, self.rect.y = self.wypoints[self.current_number]
    
    def update(self):
        ...


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups, image=None):
        if groups:
            super().__init__(*groups)

        self.image_def = image if image else all_images["player_default"]
        self.image = self.image_def

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
    
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        
    def copy_player_move(self, x, y, image):
        return Player((self.rect.x + x, self.rect.y + y), image=image)
    
    def tracking_mouse(self, x, y):
        x_player, y_player = self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2

        self.image = pygame.transform.rotate(self.image_def, 90 + ((-1) ** (y - y_player > 0)) * degrees(acos(((x - x_player) / ((x - x_player) ** 2 + (y - y_player) ** 2) ** 0.5))))
        self.rect = self.image.get_rect(center = self.image.get_rect(center = (x_player, y_player)).center)
        self.mask = pygame.mask.from_surface(self.image)


class Text:
    def __init__(self, pos, text, max_width=200, font_name=None, font_size=26, text_color=(245, 245, 245), bg_color=(0, 0, 0)):
        self.font = pygame.font.SysFont(font_name, font_size)
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
                    
    def draw_text(self, win):
        pygame.draw.rect(win, self.bg_color, (self.x - 10, self.y - 10, self.max_width + 20, self.max_height + 20))

        for word in self.text_list:
            win.blit(*word)


class List(pygame.sprite.Sprite):
    def __init__(self, pos, text, *groups):
        super().__init__(*groups)

        self.image = all_images["list"]
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)

        self.active = 0
        self.text = text

        self.text = Text((size[0] // 2 - 150, 20), text, max_width=300)

    def draw(self, win):
        if self.active:
            self.text.draw_text(win)

    def open(self):
        if not self.active:
            self.active = 1
    
    def close(self):
        if self.active:
            self.active = 0


class FolderFields:
    def __init__(self, win, filename):
        self.win = win
        self.fields = {}

        self.size = 32

        fullname = os.path.join("data", "maps", filename)

        with open(fullname, "r", encoding="utf8") as file:
            n, self.namemap = file.readline().split()
            for _ in range(int(n)):
                name, count_cage, count_commands = file.readline().split("||")
                pos = file.readline()

                count_cage = list(map(int, count_cage.split()))

                all_sprites = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                side_group = pygame.sprite.Group()
                items_group = pygame.sprite.Group()
                bot_group = pygame.sprite.Group()

                player = Player(list(map(lambda coordinate: int(coordinate) * self.size, pos.split())), player_group, all_sprites)

                if self.namemap:
                    self.namemap = name
                
                for y in range(count_cage[1]):
                    s = file.readline().split()

                    for x in range(count_cage[0]):
                        if s[x][0] == "#":
                            type_side, rotate_side = map(int, s[x][1:].split("."))
                            Side((self.size * x, self.size * y), side_group, all_sprites, type_side, rotate_side * 90)

                for _ in range(int(count_commands)):
                    name_com, *args = file.readline().split("||")
                    if name_com == "list":
                        List(list(map(lambda x: int(x) * self.size, args[0].split())), args[1], all_sprites, items_group)
                    if name_com == "bot":
                        Bot(int(args[0]), list(map(lambda coords: list(map(lambda coord: int(coord) * self.size, coords.split())), args[1].split(", "))), bot_group, all_sprites)

                self.fields[name] = Field(win, all_sprites, player_group, side_group, items_group, bot_group, player)

    def __call__(self):
        self.draw()

    def draw(self):
        self.fields[self.namemap]()
    
    def move_player(self, x, y):
        self.fields[self.namemap].move_player(x, y)

    def tracking_mouse(self, x, y):
        self.fields[self.namemap].tracking_mouse(x, y)

    def open_close_list(self):
        self.fields[self.namemap].open_list()

    # def is_collision(self, x, y):
    #     return self.fields[self.namemap].is_collision(x, y)
    
    # def go_button(self, keys):
    #     self.fields[self.namemap].go_button(keys)


class Field:
    def __init__(self, win, all_sprites, player_group, side_group, items_group, bot_group, player):
        self.win = win
        self.all_sprites = all_sprites
        self.player_group = player_group
        self.side_group = side_group
        self.items_group = items_group
        self.bot_group = bot_group
        self.player = player
        self.camera = Camera()
        
    def __call__(self):
        self.draw()
        self.update()

    def draw(self):
        self.items_group.draw(self.win)
        self.player_group.draw(self.win)
        self.side_group.draw(self.win)
        self.bot_group.draw(self.win)

        for sprite in self.items_group.sprites():
            if isinstance(sprite, List):
                sprite.draw(self.win)

    def update(self):
        self.camera.update(self.player)
        self.bot_group.update()
        for sprite in self.all_sprites.sprites():
            self.camera.apply(sprite)

    def open_list(self):
        for sprite in self.items_group.sprites():
            if isinstance(sprite, List) and pygame.sprite.collide_rect(self.player, sprite):
                sprite.open()

    def close_list(self):
        for sprite in self.items_group.sprites():
            if isinstance(sprite, List) and not pygame.sprite.collide_rect(self.player, sprite):
                sprite.close()
    
    def move_player(self, x, y):
        for sprite in self.side_group:
            if pygame.sprite.collide_mask(sprite, self.player.copy_player_move(x, y, self.player.image)):
                return
        self.player.move(x, y)
        self.close_list()
        
    def tracking_mouse(self, x, y):
        self.player.tracking_mouse(x, y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
    
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - size[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - size[1] // 2)


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()

    run = True
    size = pygame.display.Info().current_w, pygame.display.Info().current_h

    win = pygame.display.set_mode(size)
    pygame.display.set_caption("Mission Impossible")

    all_images = {
        "side_1": load_image("side_1.png", 1),
        "side_2": load_image("side_2.png", 1),
        "side_3": load_image("side_3.png", 1),
        "side_4": load_image("side_4.png", 1),
        "side_5": load_image("side_5.png", 1),
        "side_6": load_image("side_6.png", 1),
        "player_default": load_image("player_default.png", 1),
        "list": load_image("list.png", 1),
        "bot": load_image("bot.png", 1)
    }

    fps = 60

    fields = FolderFields(win, "map1.txt")

    # text = Text((100, 100), "")


    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEMOTION:
                fields.tracking_mouse(*event.pos)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    fields.open_close_list()
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            fields.move_player(0, -1)
        if keys[pygame.K_s]:
            fields.move_player(0, 1)
        if keys[pygame.K_a]:
            fields.move_player(-1, 0)
        if keys[pygame.K_d]:
            fields.move_player(1, 0)
        win.fill((144, 144, 144))

        fields()
        # text.draw_text(win)

        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()