import pygame
from pygame.locals import *

from .global_dict import SETTINGS, Globals
from .engine import Application, GameObject, Scene
from .components import AnimatedSprite, Button, Label, ProgressBar, Sprite
from .physics import Area, Body, Ray
from .animation.easing import *
from .animation.tween import Tween
from .utils import Rect, Surface, Vec2, Texture, Image, Color
from .primatives import Draw

__version__ = "0.1.5"

pygame.init()
print(f"Thank you for using jazz {__version__}")
