from csv import reader
from os import walk
from random import randint

import pygame


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=",")
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


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
    if direction.magnitude():
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


def random_color():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return (r, g, b)
