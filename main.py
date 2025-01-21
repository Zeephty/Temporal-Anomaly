import pygame
import os


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


# class Bot(pygame.sprite.Sprite):
#     def __init__(self, current_point, wypoints, *groups):
#         super().__init__(*groups)
        
#         self.wypoints = wypoints
#         self.image = all_images["bot"]

#         self.rect = self.image.get_rect()
#         self.mask = pygame.mask.from_surface(self.image)

#         self.current_number = current_point

#         self.rect.x, self.rect.y = self.wypoints[self.current_number]
    
#     def update(self):
#         ...


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups, image=None):
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
        pygame.draw.rect(win, self.bg_color, (self.x - 5, self.y - 5, self.max_width + 10, self.max_height + 10))

        for word in self.text_list:
            win.blit(*word)

    def move(self, x, y):
        self.text_list = [(word[0], (word[1][0] + x, word[1][1] + y)) for word in self.text_list]
        self.x += x
        self.y += y
            


class TriggerText(pygame.sprite.Sprite):
    def __init__(self, pos, size, text, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.image.set_alpha(50)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.text = text

        self.active = 0
    
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))
        if self.active:
            self.text.draw_text(win)
    
    def update(self, obj, camera):
        self.active = pygame.sprite.collide_mask(self, obj)
        self.image.fill("red" if self.active else (255, 255, 255))
        camera.apply_mode(self)

    def move(self, x, y):
        self.text.move(x, y)


class Item(pygame.sprite.Sprite):
    def __init__(self, pos, filename, *groups):
        super().__init__(*groups)
        self.image = load_image(filename, 1)
        self.rect = self.image.get_rect().move(*pos)
        
        self.active = 0


class Image(pygame.sprite.Sprite):
    def __init__(self, pos, filename, *groups):
        super().__init__(*groups)
        self.image = load_image(filename, 1)
        self.rect = self.image.get_rect().move(*pos)


class FolderFields:
    def __init__(self, win, filename):
        self.win = win
        self.fields = {}

        self.size = 64

        fullname = os.path.join("data", "maps", filename)

        with open(fullname, "r", encoding="utf8") as file:
            n, self.namemap = file.readline().split()
            for _ in range(int(n)):
                name, count_cage, count_commands = file.readline().split("||")
                pos = file.readline()

                count_cage = list(map(int, count_cage.split()))

                all_sprites = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                solids_group = pygame.sprite.Group()
                triggers_group = pygame.sprite.Group()
                bot_group = pygame.sprite.Group()
                background_group = pygame.sprite.Group()

                player = Player(list(map(lambda coordinate: int(coordinate) * self.size, pos.split())), player_group, all_sprites)

                if self.namemap:
                    self.namemap = name
                
                for y in range(count_cage[1]):
                    s = file.readline().split()

                    for x in range(count_cage[0]):
                        if s[x][0] == "#":
                            type_side, rotate_side = map(int, s[x][1:].split("."))
                            Side((self.size * x, self.size * y), solids_group, all_sprites, type_side, rotate_side * 90)

                for _ in range(int(count_commands)):
                    name_com, *args = file.readline().split("||")
                    if name_com == "image":
                        Image(list(map(int, args[0].split())), args[1].strip(), all_sprites, background_group)
                    elif name_com == "item":
                        Item(list(map(int, args[0].split())), args[1].strip(), all_sprites, solids_group)
                    elif name_com == "item+":
                        x_i, y_i = list(map(int, args[0].split()))
                        pos_trigger, size_trigger = [list(map(int, i.split())) for i in args[2].split("|")]
                        pos_text = list(map(int, args[3].split()))
                        text = Text((x_i + pos_text[0], y_i + pos_text[1]), args[4], font_size=22)
                        TriggerText((x_i + pos_trigger[0], y_i + pos_trigger[1]), 
                                    size_trigger, text, all_sprites, triggers_group)
                        Item((x_i, y_i), args[1].strip(), all_sprites, solids_group)

                self.fields[name] = Field(win, all_sprites, player_group, solids_group, triggers_group, background_group, player)

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
    def __init__(self, win, all_sprites, player_group, solids_group, triggers_group, background_group, player):
        self.win = win
        self.all_sprites = all_sprites
        self.player_group = player_group
        self.solids_group = solids_group
        self.triggers_group = triggers_group
        self.background_group = background_group
        self.player = player
        self.camera = Camera()
        
    def __call__(self):
        self.draw()
        self.update()

    def draw(self):
        self.background_group.draw(self.win)
        self.solids_group.draw(self.win)

        for sprite in self.triggers_group.sprites():
            sprite.draw(self.win)

        self.player_group.draw(self.win)

        self.triggers_group.update(self.player, self.camera)

    def update(self):
        self.camera.update(self.player)
        for sprite in self.all_sprites.sprites():
            self.camera.apply(sprite)
    
    def move_player(self, x, y):
        for sprite in self.solids_group:
            if pygame.sprite.collide_mask(sprite, self.player.copy_player_move(x, y, self.player.image)):
                return
        self.player.move(x, y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def apply_mode(self, obj):
        obj.move(self.dx, self.dy)
    
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
        "side_3": load_image("glass.png", 1),
        "player_default": load_image("player_default.png", 1),
        "bot": load_image("bot.png", 1)
    }

    fps = 120

    fields = FolderFields(win, "map1.txt")

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                  
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            fields.move_player(0, -1)
        if keys[pygame.K_s]:
            fields.move_player(0, 1)
        if keys[pygame.K_a]:
            fields.move_player(-1, 0)
        if keys[pygame.K_d]:
            fields.move_player(1, 0)
        win.fill((205, 235, 240))

        fields()

        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()