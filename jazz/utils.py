"""Shared constants, math helpers, file loaders, and pygame type re-exports for Jazz Engine."""

import importlib.resources
import math
import os
import sys
from configparser import ConfigParser
from csv import reader
from random import randint
from typing import Any

import pygame
from pygame import Color, Rect, Surface
from pygame._sdl2 import Image, Texture  # noqa: F401  (Image is re-exported)

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


class JazzException(Exception):
    """Custom exception class for the Jazz Engine."""


def default_ini_path() -> str:
    """Returns the default settings file path: `.jini` next to the game's main script.

    Falls back to the working directory when there is no main script file,
    e.g. in an interactive session.

    Returns:
        str: Absolute path of the default `.jini` file.
    """
    script = sys.argv[0] if sys.argv else ""
    if script and os.path.isfile(script):
        game_dir = os.path.dirname(os.path.abspath(script))
    else:
        game_dir = os.getcwd()
    return os.path.join(game_dir, ".jini")


def _parse_ini_value(raw: str) -> Any:
    """Converts an INI string value back to an int, float, or bool where possible.

    Args:
        raw (str): The value as stored in the INI file.

    Returns:
        Any: The int, float, or bool the string represents, or the string itself.
    """
    for convert in (int, float):
        try:
            return convert(raw)
        except ValueError:
            pass
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    return raw


def load_ini(path: str | None = None) -> None:
    """Loads configuration settings from an INI file into the global settings.

    Each section is merged into `SETTINGS`, so keys missing from the file keep
    their defaults. Numbers and booleans are converted back from strings. If the
    file does not exist, the current settings are written to it.

    Args:
        path (str, optional): The file path to the configuration INI. Defaults to
            None, which uses `default_ini_path()`.
    """
    if path is None:
        path = default_ini_path()
    settings = ConfigParser()
    try:
        with open(path) as ini:
            settings.read_file(ini)
    except FileNotFoundError:
        save_ini(path)
        return
    for section in settings.sections():
        values = SETTINGS.setdefault(section, {})
        for key, raw in settings.items(section):
            values[key] = _parse_ini_value(raw)


def save_ini(path: str | None = None) -> None:
    """Saves current global settings dict into an INI file.

    Args:
        path (str, optional): The target file path to save the INI. Defaults to
            None, which uses `default_ini_path()`.
    """
    if path is None:
        path = default_ini_path()
    settings = ConfigParser()
    settings.read_dict(SETTINGS)
    with open(path, "w") as ini:
        settings.write(ini)


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


def clamp(n: float, smallest: float, largest: float) -> float | int:
    """Clamps a numeric value between a minimum and maximum bound.

    Args:
        n (float): The number to clamp.
        smallest (float): The lower bound.
        largest (float): The upper bound.

    Returns:
        float | int: The clamped value.
    """
    return max(smallest, min(n, largest))


def map_range(x: float, a: float, b: float, c: float, d: float) -> float:
    """Maps a value x from range [a, b] linearily to range [c, d].

    Args:
        x (float): Value to map.
        a (float): Lower bound of the source range.
        b (float): Upper bound of the source range.
        c (float): Lower bound of the target range.
        d (float): Upper bound of the target range.

    Returns:
        float: The mapped value.
    """
    y = (x - a) / (b - a) * (d - c) + c
    return y


def sign(x: float) -> float | int:
    """Returns the mathematical sign of a number (-1, 0, or 1).

    Args:
        x (float): Numeric value.

    Returns:
        float | int: -1 if negative, 1 if positive, 0 if zero.
    """
    if x == 0:
        return 0
    return x / abs(x)


def build_rect(x1: float, y1: float, x2: float, y2: float) -> Rect:
    """Builds a Rect object from any two corner coordinates.

    Args:
        x1 (float): X coordinate of first point.
        y1 (float): Y coordinate of first point.
        x2 (float): X coordinate of second point.
        y2 (float): Y coordinate of second point.

    Returns:
        Rect: The constructed Rect object.
    """
    left = min(x1, x2)
    top = min(y1, y2)
    width = max(x1, x2) - left
    height = max(y1, y2) - top
    return Rect(left, top, width, height)


def color_mult(color: Color | tuple[int, ...], mult: float) -> tuple[int, ...]:
    """Multiplies each channel of a color by a multiplier, clamped to 0-255.

    Args:
        color (Color | tuple[int, ...]): Source color. Every channel is multiplied,
            including alpha when present.
        mult (float): Multiplier factor.

    Returns:
        tuple[int, ...]: The modified color, with as many channels as the input.
    """
    return tuple(int(clamp(channel * mult, 0, 255)) for channel in color)


_AXIS_X = Vec2(1, 0)


def dist_to(vec1: Vec2, vec2: Vec2) -> float:
    """Computes the Euclidean distance between two vectors.

    Args:
        vec1 (Vec2): The first coordinate vector.
        vec2 (Vec2): The second coordinate vector.

    Returns:
        float: The Euclidean distance.
    """
    return Vec2(vec1).distance_to(vec2)


def direction_to(vec1: Vec2, vec2: Vec2) -> Vec2:
    """Computes the normalized direction unit vector from vec1 to vec2.

    Args:
        vec1 (Vec2): The origin coordinate.
        vec2 (Vec2): The target coordinate.

    Returns:
        Vec2: The normalized direction vector. Returns zero or non-normalized vector if magnitude is 0.
    """
    direction = Vec2(vec2) - Vec2(vec1)
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
    p_0 = Vec2(p_0)
    p_1 = Vec2(p_1)
    p_2 = Vec2(p_2)
    p_3 = Vec2(p_3)

    s_1 = p_1 - p_0
    s_2 = p_3 - p_2

    if abs(s_1.normalize().dot(s_2.normalize())) == 1:
        return None

    s = (-s_1.y * (p_0.x - p_2.x) + s_1.x * (p_0.y - p_2.y)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )
    t = (s_2.x * (p_0.y - p_2.y) - s_2.y * (p_0.x - p_2.x)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )

    if 0 <= s <= 1 and 0 <= t <= 1:
        return p_0 + (t * s_1)
    else:
        return None


def line_circle(a: Vec2 | tuple[float, float], b: Vec2 | tuple[float, float], c: Vec2 | tuple[float, float], r: float) -> Vec2 | None:
    """Finds the point on line segment a-b closest to circle c, resolving penetration.

    Args:
        a (Vec2 | tuple): Start of line segment.
        b (Vec2 | tuple): End of line segment.
        c (Vec2 | tuple): Center of circle.
        r (float): Radius of circle.

    Returns:
        Vec2 | None: The corrected intersection point resolving penetration, or None if no collision.
    """
    a = Vec2(a)
    b = Vec2(b)
    c = Vec2(c)

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


def rotated_pos(point: Vec2, angle: float) -> Vec2:
    """Rotates a coordinate point around the origin (0, 0) by a given angle in degrees.

    Args:
        point (Vec2): The coordinate point to rotate.
        angle (float): The angle in degrees.

    Returns:
        Vec2: The rotated coordinate vector.
    """
    angle = math.radians(angle)
    return Vec2(
        point.x * math.cos(angle) - point.y * math.sin(angle),
        point.x * math.sin(angle) + point.y * math.cos(angle),
    )


def unit_from_angle(angle: float) -> Vec2:
    """Calculates a unit direction vector pointing in a given angle direction.

    Args:
        angle (float): The direction angle in degrees.

    Returns:
        Vec2: The normalized unit direction vector.
    """
    return _AXIS_X.rotate(angle)


def angle_from_vec(vector: Vec2) -> float:
    """Calculates the angle of a vector relative to the positive X-axis vector (1, 0).

    Args:
        vector (Vec2): The input vector.

    Returns:
        float: The angle in degrees.
    """
    return _AXIS_X.angle_to(vector)

_DEFAULT_SHADOW_COLOR = Color(0, 0, 0, 80)


def generate_styled_texture(
    size: tuple[int, int] | Vec2,
    color: Color | tuple | str,
    radius: int = 0,
    shadow_offset: tuple[int, int] = (0, 0),
    shadow_color: Color | tuple | str = _DEFAULT_SHADOW_COLOR,
    shadow_blur: int = 0,
    style: str = "flat",
    border_color: Color | tuple | str | None = None,
    border_width: int = 0,
) -> Surface:
    """Generates and returns a styled UI container background Surface.

    Args:
        size (tuple[int, int] | Vec2): Dimensions of the main container.
        color (Color | tuple | str): Base fill color.
        radius (int, optional): Corner rounding radius. Defaults to 0.
        shadow_offset (tuple[int, int], optional): X and Y offset for the drop shadow. Defaults to (0, 0).
        shadow_color (Color | tuple | str, optional): Color of the drop shadow. Defaults to black with alpha 80.
        shadow_blur (int, optional): Soft blur step size of the drop shadow. Defaults to 0.
        style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
        border_color (Color | tuple | str | None, optional): Border outline color. Defaults to None.
        border_width (int, optional): Border stroke thickness. Defaults to 0.

    Returns:
        Surface: The rendered Pygame Surface asset.
    """
    w, h = int(size[0]), int(size[1])
    color = Color(color)
    shadow_color = Color(shadow_color)

    pad_x = abs(shadow_offset[0]) + shadow_blur * 2
    pad_y = abs(shadow_offset[1]) + shadow_blur * 2

    canvas_w = w + pad_x * 2
    canvas_h = h + pad_y * 2
    canvas = Surface((canvas_w, canvas_h), pygame.SRCALPHA)

    rect_x = pad_x
    rect_y = pad_y
    if shadow_offset[0] < 0:
        rect_x -= shadow_offset[0]
    if shadow_offset[1] < 0:
        rect_y -= shadow_offset[1]

    rect = Rect(rect_x, rect_y, w, h)

    # 1. Draw shadow first
    if shadow_color.a > 0 and (shadow_offset != (0, 0) or shadow_blur > 0):
        shadow_rect = Rect(rect.x + shadow_offset[0], rect.y + shadow_offset[1], w, h)
        if shadow_blur > 0:
            steps = shadow_blur
            for i in range(steps, 0, -1):
                alpha = int(shadow_color.a * (1.0 - (i / (steps + 1))))
                c = Color(shadow_color.r, shadow_color.g, shadow_color.b, alpha)
                r = shadow_rect.inflate(i * 2, i * 2)
                pygame.draw.rect(canvas, c, r, border_radius=radius + i)
        else:
            pygame.draw.rect(canvas, shadow_color, shadow_rect, border_radius=radius)

    # 2. Draw background
    temp_surf = Surface((w, h), pygame.SRCALPHA)

    if style in ["skeuomorphic", "gradient", "glossy"] and h > 1:
        shift = 15 if style == "gradient" else 25
        color_light = Color(
            min(255, color.r + shift),
            min(255, color.g + shift),
            min(255, color.b + shift),
            color.a
        )
        color_dark = Color(
            max(0, color.r - shift),
            max(0, color.g - shift),
            max(0, color.b - shift),
            color.a
        )

        for y in range(h):
            ratio = y / (h - 1)
            r = int(color_light.r + (color_dark.r - color_light.r) * ratio)
            g = int(color_light.g + (color_dark.g - color_light.g) * ratio)
            b = int(color_light.b + (color_dark.b - color_light.b) * ratio)
            pygame.draw.line(temp_surf, Color(r, g, b, color.a), (0, y), (w, y))

        if style == "skeuomorphic":
            bevel_light = Color(255, 255, 255, 60)
            bevel_dark = Color(0, 0, 0, 80)

            pygame.draw.line(temp_surf, bevel_light, (0, 0), (w, 0), 1)
            pygame.draw.line(temp_surf, bevel_light, (0, 0), (0, h), 1)
            pygame.draw.line(temp_surf, bevel_dark, (0, h - 1), (w, h - 1), 1)
            pygame.draw.line(temp_surf, bevel_dark, (w - 1, 0), (w - 1, h), 1)
        elif style == "glossy":
            gloss_h = h // 2
            gloss_surf = Surface((w, gloss_h), pygame.SRCALPHA)
            gloss_surf.fill((255, 255, 255, 25))
            temp_surf.blit(gloss_surf, (0, 0))

            pygame.draw.rect(temp_surf, (255, 255, 255, 50), (0, 0, w, h), 1)
    else:
        temp_surf.fill(color)

    if radius > 0:
        mask = Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        temp_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    canvas.blit(temp_surf, (rect.x, rect.y))

    # 3. Draw border
    if border_color is not None and border_width > 0:
        pygame.draw.rect(canvas, Color(border_color), rect, border_width, border_radius=radius)

    return canvas
