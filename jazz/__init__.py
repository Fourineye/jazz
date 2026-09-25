"""Jazz: a pygame-ce wrapper with a scene graph, sprites, UI, physics, and tweens.

Names are re-exported with `import X as X` instead of an `__all__`, so that
`from jazz import *` keeps exporting the pygame constants (e.g. `K_SPACE`) and
the easing functions that come in through the wildcard imports.
"""

import pygame

# pygame's key, event, and flag constants, available as jazz.K_SPACE and so on
from pygame.locals import *  # pyright: ignore[reportWildcardImportFromLibrary]

from .animation import *
from .components import AnimatedSprite as AnimatedSprite
from .components import Button as Button
from .components import DrawableObject as DrawableObject
from .components import HBox as HBox
from .components import Label as Label
from .components import ProgressBar as ProgressBar
from .components import Sprite as Sprite
from .components import TextBox as TextBox
from .components import UIContainer as UIContainer
from .components import VBox as VBox
from .engine import Application as Application
from .engine import BaseObject as BaseObject
from .engine import GameObject as GameObject
from .engine import Scene as Scene
from .engine import Serializer as Serializer
from .engine import register_class as register_class
from .global_dict import SETTINGS as SETTINGS
from .global_dict import Globals as Globals
from .physics import Area as Area
from .physics import Body as Body
from .physics import CircleCollider as CircleCollider
from .physics import Collider as Collider
from .physics import PhysicsObject as PhysicsObject
from .physics import PolyCollider as PolyCollider
from .physics import Ray as Ray
from .physics import RayCollider as RayCollider
from .physics import RectCollider as RectCollider
from .primatives import Draw as Draw
from .utils import COLLIDER_CIRCLE as COLLIDER_CIRCLE
from .utils import COLLIDER_POLY as COLLIDER_POLY
from .utils import COLLIDER_RAY as COLLIDER_RAY
from .utils import COLLIDER_RECT as COLLIDER_RECT
from .utils import FOLLOW_SMOOTH as FOLLOW_SMOOTH
from .utils import FOLLOW_STRICT as FOLLOW_STRICT
from .utils import Color as Color
from .utils import Image as Image
from .utils import Rect as Rect
from .utils import Surface as Surface
from .utils import Texture as Texture
from .utils import Vec2 as Vec2

__version__ = "1.2.0"

pygame.init()
print(f"Thank you for using jazz {__version__}")
