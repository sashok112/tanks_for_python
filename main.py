import os
import sys
import pygame
import threading
import time
from collections import deque

direction = {"down": [0, 1, 2, 12, 13, 14, 24, 25, 26],
             "right": [3, 4, 5, 15, 16, 17, 27, 28, 29],
             "left": [6, 7, 8, 18, 19, 20, 30, 31, 32],
             "up": [9, 10, 11, 21, 22, 23, 33, 34, 35]}

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 1280
HEIGHT = 720
STEP = 50
cols, rows = 0, 0
graph = {}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

level_preposition = []

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bots_group = pygame.sprite.Group()

bots = []


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    global level_preposition
    level_preposition = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    for i in range(len(level_preposition)):
        level_preposition[i] = list(level_preposition[i])
    global cols, rows
    cols, rows = len(level_preposition[0]), len(level_preposition)
    global graph
    for y, row in enumerate(level_preposition):
        for x, col in enumerate(row):
            if col == "." or col == "@" or col == "B":
                graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(x, y)
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                new_bot = Bot(x, y)
                bots.append(new_bot)

    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Танчики", "",
                  "Игра создана на идеи ретро 2д танков",
                  "Для вас будут появляться на карте боевые танки противников",
                  "Вы должны, убивая их, уничтожить всю вражескую комманду"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('tanks1.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.image = player_image
        # self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.cut_sheet(player_image, 12, 3)
        self.image = self.frames[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 5, tile_height * pos_y + 5)
        self.x_map = pos_x
        self.y_map = pos_y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


class Bot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bots_group, all_sprites)
        self.frames = []
        self.image = player_image
        # self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

        self.cut_sheet(player_image, 12, 3)
        self.image = self.frames[24]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.x_map = pos_x
        self.y_map = pos_y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


def bfs(start, goal, graph):
    queue = deque([start])
    visited = {start: None}
    while queue:
        cur_node = queue.popleft()
        if cur_node == goal:
            break
        next_nodes = graph[cur_node]
        for next_node in next_nodes:
            if next_node not in visited:
                queue.append(next_node)
                visited[next_node] = cur_node
    return queue, visited


def get_next_nodes(x, y):
    check_next_node = lambda x, y: True if 0 <= x < cols and 0 <= y < rows and (level_preposition[y][x] == "." or level_preposition[y][x] == "@" or level_preposition[y][x] == "B") else False
    ways = [-1, 0], [0, -1], [1, 0], [0, 1]
    return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]


class Camera:
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    def apply(self, obj):
        obj.rect.x += self.dx
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
        obj.rect.y += self.dy
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
            obj.rect.y += -obj.rect.height * (1 + self.field_size[1])

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def go_bot():
    count = 0
    while True:
        time.sleep(1)
        count += 1

        for i in bots:
            # if i.x_map == player.x_map:
            #     flag_shoot = True
            #     for j in range(min(i.y_map, player.y_map), max(i.y_map, player.y_map)):
            #         if level_preposition[j][i.x_map] == "#":
            #             flag_shoot = False
            #             break
            #     if flag_shoot:
            #         shoot()
            #         print("Streliat")
            # if i.y_map == player.y_map:
            #     flag_shoot = True
            #     for j in range(min(i.x_map, player.x_map), max(i.x_map, player.x_map)):
            #         if level_preposition[i.y_map][j] == "#":
            #             flag_shoot = False
            #             break
            #     if flag_shoot:
            #         shoot()
            #         print("Streliat")

            queue, visited = bfs((i.x_map, i.y_map), (player.x_map, player.y_map), graph)
            path_head, path_segment = (player.x_map, player.y_map), (player.x_map, player.y_map)
            next_node = (-1, -1)
            while path_segment and path_segment in visited:
                if path_segment != (i.x_map, i.y_map):
                    next_node = path_segment
                path_segment = visited[path_segment]
            print(next_node)
            if next_node == (-1, -1):
                print("error")
            if next_node[0] > i.x_map:
                i.rect.x += STEP
                i.x_map += 1
            elif next_node[0] < i.x_map:
                i.rect.x -= STEP
                i.x_map -= 1
            elif next_node[1] > i.y_map:
                i.rect.y += STEP
                i.y_map += 1
            elif next_node[1] < i.y_map:
                i.rect.y -= STEP
                i.y_map -= 1
            i.image = player.frames[29]
            level_preposition[i.y_map][i.x_map] = "."
            level_preposition[next_node[0]][next_node[1]] = "B"


def shoot():
    ind = player.frames.index(player.image)
    for i in direction:
        if ind in direction[i]:
            if i == "up":
                y = player.rect.y
                x = player.rect.x
                while y != 0:
                    pass
                pass
            if i == "down":
                pass
            if i == "left":
                pass
            if i == "right":
                pass
            break


start_screen()

player, level_x, level_y = generate_level(load_level("levelex.txt"))
camera = Camera((level_x, level_y))

running = True

try:
    t1 = threading.Thread(target=go_bot)
    t1.start()
except:
    print("Error: unable to start thread")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.image = player.frames[8]
                if level_preposition[player.y_map][player.x_map - 1] != "#":
                    player.rect.x -= STEP
                    level_preposition[player.y_map][player.x_map] = "."
                    level_preposition[player.y_map][player.x_map - 1] = "@"
                    player.x_map -= 1
            if event.key == pygame.K_RIGHT:
                player.image = player.frames[27]
                if level_preposition[player.y_map][player.x_map + 1] != "#":
                    player.rect.x += STEP
                    level_preposition[player.y_map][player.x_map] = "."
                    level_preposition[player.y_map][player.x_map + 1] = "@"
                    player.x_map += 1

            if event.key == pygame.K_UP:

                player.image = player.frames[35]
                if level_preposition[player.y_map - 1][player.x_map] != "#":
                    player.rect.y -= STEP
                    level_preposition[player.y_map][player.x_map] = "."
                    level_preposition[player.y_map - 1][player.x_map] = "@"
                    player.y_map -= 1

            if event.key == pygame.K_DOWN:
                player.image = player.frames[0]
                if level_preposition[player.y_map + 1][player.x_map] != "#":
                    player.rect.y += STEP
                    level_preposition[player.y_map][player.x_map] = "."
                    level_preposition[player.y_map + 1][player.x_map] = "@"
                    player.y_map += 1

            if event.key == pygame.K_SPACE:
                shoot()

    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    screen.fill(pygame.Color(255, 255, 255))
    tiles_group.draw(screen)
    bots_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)

terminate()

# TODO изменение в лвле позицию танчиков
# TODO когда ломаетмя коробка или уезжает танк, то образуется травка
