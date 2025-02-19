import pygame
from pygame.locals import *

from .global_dict import SETTINGS, Globals
from .engine import Application, GameObject, Scene
from .components import AnimatedSprite, Button, Label, ProgressBar, Sprite
from .physics import Area, Body, Ray
from .animation import *
from .utils import (
    Rect,
    Surface,
    Vec2,
    Texture,
    Image,
    Color,
    FOLLOW_SMOOTH,
    FOLLOW_STRICT,
    COLLIDER_RECT,
    COLLIDER_CIRCLE,
    COLLIDER_POLY,
    COLLIDER_RAY,
)
from .primatives import Draw

__version__ = "0.2.2"

pygame.init()
print(f"Thank you for using jazz {__version__}")
