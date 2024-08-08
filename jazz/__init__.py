import pygame
from pygame.locals import *

from .global_dict import SETTINGS, Globals
from .engine import Application, GameObject, Scene
from .components import AnimatedSprite, Button, Label, ProgressBar, Sprite
from .physics import Area, Body, Ray
from .animation.easing import *
from .animation.tween import Tween
from .utils import Rect, Surface, Vec2

pygame.init()
