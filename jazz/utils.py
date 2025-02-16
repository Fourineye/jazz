import importlib.resources
import math
from configparser import ConfigParser
from csv import reader
from random import randint

import pygame
from pygame._sdl2 import Texture, Image
from pygame import Rect, Surface, Color

from .global_dict import SETTINGS, Globals

# Bringing pygame constants into jazz Namespace
Vec2 = pygame.Vector2


# Constants
INTERNAL_PATH = str(importlib.resources.files())
FOLLOW_STRICT = 0
FOLLOW_SMOOTH = 1
COLLIDER_RECT = 0
COLLIDER_POLY = 1
COLLIDER_CIRCLE = 2
COLLIDER_RAY = 3
SURFACE = 0
SPRITE_SHEET = 1
TEXTURE = 2


class JazzException(Exception): ...


def load_ini(path="./.jini"):
    settings = ConfigParser()
    try:
        with open(path, "r") as ini:
            settings.read(ini)
        for key, value in settings.items():
            SETTINGS[key] = value
    except FileNotFoundError:
        save_ini()


def save_ini(path="./.jini"):
    settings = ConfigParser()
    settings.read_dict(SETTINGS)
    with open(path, "w") as ini:
        settings.write(ini)


# def load_ini(path="./.jini"):
#     try:
#         with open(path, "r") as ini:
#             data = json.load(ini)
#         for key, value in data.items():
#             SETTINGS[key] = value
#     except:
#         save_ini()


# def save_ini(path="./.jini"):
#     with open(path, "w") as ini:
#         json.dump(SETTINGS, ini)


def import_csv_layout(path):
    data = []
    with open(path) as data_file:
        layout = reader(data_file, delimiter=",")
        for row in layout:
            data.append(list(row))
        return data


def load_image(path):
    tmp_surf = pygame.image.load(path)
    if tmp_surf.get_alpha() is not None:
        return tmp_surf.convert_alpha()
    else:
        return tmp_surf.convert()


def load_texture(path):
    return pygame._sdl2.Texture.from_surface(Globals.renderer, load_image(path))


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
    return Rect(left, top, width, height)


def color_mult(color, mult):
    new_color = map(lambda x: clamp(x * mult, 0, 255), color)
    return tuple(new_color)


def dist_to(vec1, vec2):
    dist = vec2 - vec1
    return dist.magnitude()


def direction_to(vec1, vec2):
    direction = vec2 - vec1
    if (
        direction.magnitude_squared() != 1
        and direction.magnitude_squared() != 0
    ):
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


def line_intersection(p_0, p_1, p_2, p_3):
    """ """
    p_0 = pygame.Vector2(p_0)
    p_1 = pygame.Vector2(p_1)
    p_2 = pygame.Vector2(p_2)
    p_3 = pygame.Vector2(p_3)

    s_1 = pygame.Vector2(p_1 - p_0)
    s_2 = pygame.Vector2(p_3 - p_2)

    if abs(s_1.normalize().dot(s_2.normalize())) == 1:
        return None

    s = (-s_1.y * (p_0.x - p_2.x) + s_1.x * (p_0.y - p_2.y)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )
    t = (s_2.x * (p_0.y - p_2.y) - s_2.y * (p_0.x - p_2.x)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )

    if 0 <= s <= 1 and 0 <= t <= 1:
        i = p_0 + (t * s_1)
        return pygame.Vector2(i)
    else:
        return None


def line_circle(a, b, c, r):
    """ """
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
        pen = math.sqrt(r * r - hh)
        return a + ab * t + pen * direction_to(c + h, a)


def rotated_pos(point, angle):
    angle = math.radians(angle)
    return Vec2(
        point.x * math.cos(angle) - point.y * math.sin(angle),
        point.x * math.sin(angle) + point.y * math.cos(angle),
    )


def unit_from_angle(angle):
    return rotated_pos(Vec2(1, 0), angle)


def angle_from_vec(vector):
    return Vec2(1, 0).angle_to(vector)
