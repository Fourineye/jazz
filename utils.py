from csv import reader
from os import walk

import math
import pygame

Vec2 = pygame.Vector2

def import_csv_layout(path):
    data = []
    with open(path) as data_file:
        layout = reader(data_file, delimiter=",")
        for row in layout:
            data.append(list(row))
        return data


def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list


def load_image(path):
    return pygame.image.load(path).convert_alpha()


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def map_range(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    return y


def sign(x):
    if x == 0:
        return 0
    return x / abs(x)


def build_rect(x1, y1, x2, y2):
    left = min(x1, x2)
    top = min(y1, y2)
    width = max(x1, x2) - left
    height = max(y1, y2) - top
    return (left, top, width, height)


def color_mult(color, mult):
    new_color = map(lambda x: clamp(x * mult, 0, 255), color)
    return tuple(new_color)


def dist_to(vec1, vec2):
    dist = vec2 - vec1
    return dist.magnitude()


def direction_to(vec1, vec2):
    direction = vec2 - vec1
    if direction.magnitude() != 1:
        direction.normalize_ip()
    return direction


def key_from_value(search_dict, search_value):
    for key, value in search_dict.items():
        if value == search_value:
            return key
    return False


def scale_double(surface):
    width, height = surface.get_size()
    return pygame.transform.scale(surface, (width * 2, height * 2))

def line_intersection(p_0, p_1, p_2, p_3):
    '''
    '''
    p_0 = pygame.Vector2(p_0)
    p_1 = pygame.Vector2(p_1)
    p_2 = pygame.Vector2(p_2)
    p_3 = pygame.Vector2(p_3)
    
    s_1 = pygame.Vector2(p_1 - p_0)
    s_2 = pygame.Vector2(p_3 - p_2)
    
    if abs(s_1.normalize().dot(s_2.normalize())) == 1:
        return None
        
    s = (-s_1.y * (p_0.x - p_2.x) + s_1.x * (p_0.y - p_2.y)) / (-s_2.x * s_1.y + s_1.x * s_2.y)
    t = ( s_2.x * (p_0.y - p_2.y) - s_2.y * (p_0.x - p_2.x)) / (-s_2.x * s_1.y + s_1.x * s_2.y)
    
    if 0 <= s <= 1 and 0 <= t <= 1:
        i = p_0 + (t * s_1)
        return pygame.Vector2(i)
    else:
        return None
    
def line_circle(a, b, c, r):
    '''
    '''
    a = pygame.Vector2(a)
    b = pygame.Vector2(b)
    c = pygame.Vector2(c)
    
    ac = c - a
    ab = b - a
    abab = ab.dot(ab)
    acab = ac.dot(ab)
    t = acab / abab
    h = ab * t + a - c
    hh = h.dot(h)
    if hh <= r * r:
        pen = math.sqrt(r*r - hh)
        return a + ab * t + pen * direction_to(c + h, a)
