import pygame     

# s = (rect.get_x(), rect.get_y(), rect.get_x() + rect.get_w(), rect.get_y() + rect.get_h())
# (0 if (self.x + self.w <= s[0] or self.x >= s[2]) and (self.y + self.h >= s[1] or self.y <= s[3]) else 1)

class Collision:
    def __init__(self, poses, sizes):
        self.poses = poses
        self.sizes = sizes

    def is_collision(self, pos, size):
        s = (pos[0], pos[1] - size[1], pos[0] + size[0], pos[1])
        for pose, size in zip(self.poses, self.sizes):
            if not ((pose[1] >= s[1] or pose[1] + size[1] <= s[3]) and (pose[0] + size[0] <= s[0] or pose[0] >= s[2])):
                return True
        return False


class Object:
    def __init__(self, win, pos, size, color):
        self.win = win
        self.x, self.y = pos
        self.size = size
        self.color = color
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_w(self):
        return self.size[0]

    def get_h(self):
        return self.size[1]


class Player(Object):
    def __init__(self, win, pos, size, color):
        super().__init__(win, pos, size, color)

        self.v = 40

        self.stopmove = False
        # self.clock = pygame.time.Clock()    

    def __call__(self):
        self.draw()

    def draw(self):
        pygame.draw.ellipse(self.win, self.color, (int(self.x), int(self.y), self.size[0] * 2, self.size[1] * 2))
    
    def move(self, x, y, type=0):
        if not self.stopmove:
            if type == 0:
                self.x += x * self.v / 1000
                self.y += y * self.v / 1000
            else:
                self.x, self.y = x, y

    def get_move(self, x, y):
        return int(self.x + x * self.v / 1000), int(self.y + y * self.v / 1000)
    
    def get_size(self):
        return self.size

class Rect(Object):
    def __init__(self, win, pos, size, color, 
                 width = 0,
                 border_radius=-1,
                 border_t_l_radius=-1,
                 border_t_r_radius=-1,
                 border_b_l_radius=-1,
                 border_b_r_radius=-1):
        super().__init__(win, pos, size, color)

        self.width = width
        self.border_rad = [
            border_radius, 
            border_t_l_radius, 
            border_t_r_radius, 
            border_b_l_radius, 
            border_b_r_radius
            ]

    def __call__(self):
        self.draw()

    def draw(self):
        pygame.draw.rect(
            self.win, 
            self.color, 
            (self.x, self.y, self.size[0], self.size[1]), 
            self.width,
            self.border_rad[0], 
            self.border_rad[1], 
            self.border_rad[2], 
            self.border_rad[3], 
            self.border_rad[4]
        )


class Cage:
    def __init__(self, win, pos, size, objs={}, collision=None):
        self.x, self.y = pos
        self.win = win
        self.size = size
        self.objects = objs

        self.collision = collision

    def events(self):
        for obj in self.objects.values():
            obj()

    def is_collision(self, pos, size):
        if self.collision:
            return self.collision.is_collision(pos, size)
        return False


class DefaultField:
    def __init__(self, win, pos, size_cage, count_cage, player):
        self.x, self.y = pos
        self.win = win
        self.size_cage = size_cage
        self.count_cage = count_cage

        self.player = player

        self.cages = []
        for y in range(count_cage[1]):
            self.cages += [[]]
            for x in range(count_cage[0]):
                rect = (x * size_cage[0] + self.x, y * size_cage[1] + self.y)
                self.cages[-1] += [Cage(win, rect, self.size_cage, 
                                        {0: Rect(win, rect, self.size_cage, (255, 255, 255), 3)}, collision=Collision([rect], [self.size_cage]))]
    
    def __call__(self):
        self.draw()
        self.player()

    def draw(self):
        for cage_row in self.cages:
            for cage in cage_row:
                cage.events()

    def is_collision(self, x, y):
        for cage_row in self.cages:
            for cage in cage_row:
                if cage.is_collision(self.player.get_move(x, y), self.player.get_size()):
                    return True
        return False
        
if __name__ == '__main__':
    pygame.init()

    s = 501, 501

    run = True

    win = pygame.display.set_mode(s)
    pygame.display.set_caption("Mission Impossible")

    player = Player(win, (250, 250), (10, 10), (255, 100, 120))

    cage = Cage(win, (10, 10), (100, 100), {0: Rect(win, (10, 10), (100, 100), (255, 255, 255)),
                                            1: Rect(win, (10, 10), (50, 50), (200, 200, 200))})
    
    field1 = DefaultField(win, (50, 50), (32, 32), (5, 5), player)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_RIGHT:
                    ...
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and not field1.is_collision(0, -1):
            player.move(0, -1)
        if keys[pygame.K_s] and not field1.is_collision(0, 1):
            player.move(0, 1)
        if keys[pygame.K_a] and not field1.is_collision(-1, 0):
            player.move(-1, 0)
        if keys[pygame.K_d] and not field1.is_collision(1, 0):
            player.move(1, 0)
                
        win.fill("black")

        field1()

        pygame.display.flip()
    pygame.quit()