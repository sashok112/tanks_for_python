FPS = 50
import os
import sys
import pygame

from itertools import cycle

VISITOR_TTF_FILENAME = 'fonts/Mandelfilled.ttf'
BLINK_EVENT = pygame.USEREVENT + 0

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 800
HEIGHT = 600
STEP = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen_rect = screen.get_rect()
    intro_text = ["Nasty-Game", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('images/background_start.jpg'), (WIDTH, HEIGHT))
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

    font = pygame.font.Font(os.path.join('data', VISITOR_TTF_FILENAME), 50)
    on_text_surface = font.render(
        'Press Any Key To Start', True, pygame.Color('gray9')
    )
    blink_rect = on_text_surface.get_rect()
    blink_rect.bottomright = screen_rect.bottomright
    off_text_surface = pygame.Surface(blink_rect.size)
    blink_surfaces = cycle([on_text_surface, off_text_surface])
    blink_surface = next(blink_surfaces)
    pygame.time.set_timer(BLINK_EVENT, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == BLINK_EVENT:
                blink_surface = next(blink_surfaces)
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        screen.blit(blink_surface, blink_rect)
        pygame.display.update()
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
