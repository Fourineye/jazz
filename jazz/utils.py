import importlib.resources
import math
from configparser import ConfigParser
from csv import reader
from random import randint

import pygame
from pygame import Color, Rect, Surface
from pygame._sdl2 import Image, Texture

from .global_dict import SETTINGS, Globals

# Bringing pygame constants into jazz Namespace
Vec2 = pygame.Vector2


# Constants
INTERNAL_PATH = str(importlib.resources.files("jazz"))
FOLLOW_STRICT = 0
FOLLOW_SMOOTH = 1
COLLIDER_RECT = 0
COLLIDER_POLY = 1
COLLIDER_CIRCLE = 2
COLLIDER_RAY = 3
SURFACE = 0
SPRITE_SHEET = 1
TEXTURE = 2


from typing import Any

class JazzException(Exception):
    """Custom exception class for the Jazz Engine."""


def load_ini(path: str = "./.jini") -> None:
    """Loads configuration settings from an INI file into the global settings.

    Args:
        path (str, optional): The file path to the configuration INI. Defaults to "./.jini".
    """
    settings = ConfigParser()
    try:
        with open(path, "r") as ini:
            settings.read(ini)
        for key, value in settings.items():
            SETTINGS[key] = value
    except FileNotFoundError:
        save_ini()


def save_ini(path: str = "./.jini") -> None:
    """Saves current global settings dict into an INI file.

    Args:
        path (str, optional): The target file path to save the INI. Defaults to "./.jini".
    """
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


def import_csv_layout(path: str) -> list[list[str]]:
    """Imports a grid/tile layout from a comma-separated CSV file.

    Args:
        path (str): File path to the CSV.

    Returns:
        list[list[str]]: A 2D list containing row and cell values as strings.
    """
    data = []
    with open(path) as data_file:
        layout = reader(data_file, delimiter=",")
        for row in layout:
            data.append(list(row))
        return data


def load_image(path: str) -> Surface:
    """Loads an image from the filesystem and converts it for optimized rendering.

    Args:
        path (str): File path to the image.

    Returns:
        Surface: The converted Pygame Surface.
    """
    tmp_surf = pygame.image.load(path)
    if tmp_surf.get_alpha() is not None:
        return tmp_surf.convert_alpha()
    else:
        return tmp_surf.convert()


def load_texture(path: str) -> Texture:
    """Loads an image and creates a hardware-accelerated SDL2 Texture.

    Args:
        path (str): File path to the image.

    Returns:
        Texture: The hardware-accelerated Texture object.
    """
    return Texture.from_surface(Globals.renderer, load_image(path))


def clamp(n: float | int, smallest: float | int, largest: float | int) -> float | int:
    """Clamps a numeric value between a minimum and maximum bound.

    Args:
        n (float | int): The number to clamp.
        smallest (float | int): The lower bound.
        largest (float | int): The upper bound.

    Returns:
        float | int: The clamped value.
    """
    return max(smallest, min(n, largest))


def map_range(x: float | int, a: float | int, b: float | int, c: float | int, d: float | int) -> float:
    """Maps a value x from range [a, b] linearily to range [c, d].

    Args:
        x (float | int): Value to map.
        a (float | int): Lower bound of the source range.
        b (float | int): Upper bound of the source range.
        c (float | int): Lower bound of the target range.
        d (float | int): Upper bound of the target range.

    Returns:
        float: The mapped value.
    """
    y = (x - a) / (b - a) * (d - c) + c
    return y


def sign(x: float | int) -> float | int:
    """Returns the mathematical sign of a number (-1, 0, or 1).

    Args:
        x (float | int): Numeric value.

    Returns:
        float | int: -1 if negative, 1 if positive, 0 if zero.
    """
    if x == 0:
        return 0
    return x / abs(x)


def build_rect(x1: float | int, y1: float | int, x2: float | int, y2: float | int) -> Rect:
    """Builds a Rect object from any two corner coordinates.

    Args:
        x1 (float | int): X coordinate of first point.
        y1 (float | int): Y coordinate of first point.
        x2 (float | int): X coordinate of second point.
        y2 (float | int): Y coordinate of second point.

    Returns:
        Rect: The constructed Rect object.
    """
    left = min(x1, x2)
    top = min(y1, y2)
    width = max(x1, x2) - left
    height = max(y1, y2) - top
    return Rect(left, top, width, height)


def color_mult(color: Color | tuple[int, int, int], mult: float) -> tuple[int, int, int]:
    """Multiplies RGB channels of a color by a multiplier.

    Args:
        color (tuple[int, int, int] | Color): Source color.
        mult (float): Multiplier factor.

    Returns:
        tuple[int, int, int]: The modified RGB color tuple.
    """
    new_color = map(lambda x: clamp(x * mult, 0, 255), color)
    return tuple(new_color)


def dist_to(vec1: Vec2, vec2: Vec2) -> float:
    """Computes the Euclidean distance between two vectors.

    Args:
        vec1 (Vec2): The first coordinate vector.
        vec2 (Vec2): The second coordinate vector.

    Returns:
        float: The Euclidean distance.
    """
    dist = vec2 - vec1
    return dist.magnitude()


def direction_to(vec1: Vec2, vec2: Vec2) -> Vec2:
    """Computes the normalized direction unit vector from vec1 to vec2.

    Args:
        vec1 (Vec2): The origin coordinate.
        vec2 (Vec2): The target coordinate.

    Returns:
        Vec2: The normalized direction vector. Returns zero or non-normalized vector if magnitude is 0.
    """
    direction = vec2 - vec1
    if (
        direction.magnitude_squared() != 1
        and direction.magnitude_squared() != 0
    ):
        direction.normalize_ip()
    return direction


def key_from_value(search_dict: dict[Any, Any], search_value: Any) -> Any:
    """Finds the first key in a dictionary associated with a given value.

    Args:
        search_dict (dict): Dictionary to search.
        search_value: The value to lookup.

    Returns:
        Any | bool: The matching key if found, otherwise False.
    """
    for key, value in search_dict.items():
        if value == search_value:
            return key
    return False


def scale_double(surface: Surface) -> Surface:
    """Scales a Surface to exactly double its width and height.

    Args:
        surface (Surface): Source Pygame Surface.

    Returns:
        Surface: The scaled Pygame Surface.
    """
    width, height = surface.get_size()
    return pygame.transform.scale(surface, (width * 2, height * 2))


def random_color() -> tuple[int, int, int]:
    """Generates a random RGB color tuple.

    Returns:
        tuple[int, int, int]: A tuple containing random R, G, and B values between 0 and 255.
    """
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return (r, g, b)


def line_intersection(p_0: Vec2 | tuple[float, float], p_1: Vec2 | tuple[float, float], p_2: Vec2 | tuple[float, float], p_3: Vec2 | tuple[float, float]) -> Vec2 | None:
    """Finds the intersection point of two line segments (p0-p1 and p2-p3).

    Args:
        p_0 (Vec2 | tuple): Start of first line segment.
        p_1 (Vec2 | tuple): End of first line segment.
        p_2 (Vec2 | tuple): Start of second line segment.
        p_3 (Vec2 | tuple): End of second line segment.

    Returns:
        Vec2 | None: The intersection coordinate vector, or None if lines are parallel or do not intersect.
    """
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


def line_circle(a: Vec2 | tuple[float, float], b: Vec2 | tuple[float, float], c: Vec2 | tuple[float, float], r: float | int) -> Vec2 | None:
    """Finds the point on line segment a-b closest to circle c, resolving penetration.

    Args:
        a (Vec2 | tuple): Start of line segment.
        b (Vec2 | tuple): End of line segment.
        c (Vec2 | tuple): Center of circle.
        r (float | int): Radius of circle.

    Returns:
        Vec2 | None: The corrected intersection point resolving penetration, or None if no collision.
    """
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


def rotated_pos(point: Vec2, angle: float | int) -> Vec2:
    """Rotates a coordinate point around the origin (0, 0) by a given angle in degrees.

    Args:
        point (Vec2): The coordinate point to rotate.
        angle (float | int): The angle in degrees.

    Returns:
        Vec2: The rotated coordinate vector.
    """
    angle = math.radians(angle)
    return Vec2(
        point.x * math.cos(angle) - point.y * math.sin(angle),
        point.x * math.sin(angle) + point.y * math.cos(angle),
    )


def unit_from_angle(angle: float | int) -> Vec2:
    """Calculates a unit direction vector pointing in a given angle direction.

    Args:
        angle (float | int): The direction angle in degrees.

    Returns:
        Vec2: The normalized unit direction vector.
    """
    return rotated_pos(Vec2(1, 0), angle)


def angle_from_vec(vector: Vec2) -> float:
    """Calculates the angle of a vector relative to the positive X-axis vector (1, 0).

    Args:
        vector (Vec2): The input vector.

    Returns:
        float: The angle in degrees.
    """
    return Vec2(1, 0).angle_to(vector)
