import math
import uuid

import pygame

from Jazz.input_handler import InputHandler
from Jazz.utils import Vec2


class GameObject:
    """Simplest object in pygame_engine"""

    def __init__(self, pos: Vec2, name="Object", **kwargs):
        # Engine Attributes
        self.name = name
        self.id = str(uuid.uuid1())
        self.scene = None
        self.app = None

        # Child properties
        self._children = {}
        self._parent = None
        self._depth = 0

        # Engine flags
        self.pause_process = kwargs.get("pause_process", False)
        self.game_process = kwargs.get("game_process", True)
        self.game_input = kwargs.get("game_input", True)
        self.do_kill = False

        # Rendering flags
        self.visible = kwargs.get("visible", True)
        self.background_layer = kwargs.get("background_layer", False)
        self.screen_layer = kwargs.get("screen_layer", False)

        # Basic positional Attributes
        self._pos = Vec2(pos)
        self._facing = Vec2(1, 0)
        self._z = kwargs.get("z", 0)
        self._color = kwargs.get("color", (255, 255, 255))

        # Grouping
        self.groups = kwargs.get("groups", [])
        for group in self.groups:
            if self not in group._entities:
                group.add(self)

    def __repr__(self):
        children = ""
        for _, child in self._children.items():
            children += f" {child}"
        return (
            "-" * self._depth
            + f"{self.name} at {round(self.x,2)}, {round(self.y,2)}"
            + children
        )

    def _input(self, INPUT: InputHandler):
        """
        Method called once per frame to handle user input. Called before process.

        Args:
            INPUT (InputHandler): InputHandler passed from the main game instance.
        """

    def _process(self, delta: float):
        """
        Method called once per frame to handle game logic. Called before draw.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def _draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        pygame.draw.circle(surface, self._color, self.pos + offset, 10)

    # Engine called methods that allow object nesting
    def input(self, INPUT: InputHandler):
        for child in self._children.values():
            child.input(INPUT)
        self._input(INPUT)

    def process(self, delta):
        for child in self._children.values():
            child.process(delta)
        self._process(delta)

    def draw(self, surface: pygame.Surface, offset=None):
        for child in self._children.values():
            child.draw(surface, offset)
        self._draw(surface, offset)

    def add_child(self, obj, name=None):
        if obj.id not in self._children.keys():
            obj._parent = self
            obj._depth = self._depth + 1
            obj.app = self.app
            self._children[obj.id] = obj

        if name is not None and name not in self.__dict__.keys():
            name = name.split(" ")[0]
            obj.name = name
            self.__dict__.setdefault(name, obj)

    def remove_child(self, obj, kill=True):
        if isinstance(obj, str):
            child = self._children.pop(obj, None)
            if child is None:
                child = getattr(self, obj, None)
            if child is None:
                print("child not found")
            else:
                self._children.pop(child.id)
                delattr(self, child.name)
                if kill:
                    child.kill()
        else:
            for name, child in self._children.copy().items():
                if obj is child:
                    obj = self._children.pop(name)
                    if obj.name in self.__dict__:
                        delattr(self, obj.name)
                    if kill:
                        obj.kill()
                    return

    def collide(self, collider):
        """Checks if the object is in an AABB.

        Args:
            collider (GameObject): The rect to check.

        Returns:
            bool: Whether the object is in the rect.
        """
        rect = collider.collider
        return (
            self.x > rect.left
            and self.x < rect.right
            and self.y > rect.top
            and self.y < rect.bottom
        )

    # movement methods
    def rotate(self, degrees):
        self.facing.rotate_ip(degrees)

    def rotate_around(self, degrees, center):
        center = Vec2(center)
        arm = self._pos - center
        arm.rotate_ip(degrees)
        self.pos = center + arm
        self.rotate(degrees)

    def set_rotation(self, degrees):
        angle = self._facing.angle_to(Vec2(1, 0).rotate(degrees))
        self.rotate(angle)

    def add_group(self, group):
        """
        Add Group to Entity and insure that Entity is in Group.

        Args:
            group (EntityGroup): The EntityGroup to add.
        """
        self.groups.append(group)
        if self not in group:
            group.add(self)

    def remove_group(self, group):
        """
        Remove group from Entity and insure that Entity is not in Group.

        Args:
            group (EntityGroup): The EntityGroup to remove.
        """
        if group not in self.groups:
            print("group not found")
        else:
            self.groups.remove(group)
            if self in group:
                group.remove(self)

    def kill(self):
        """Destroys the entity"""
        self.game_process = False
        self.pause_process = False
        self.game_input = False
        if self._parent is not None:
            self._parent.remove_child(self, False)

        for group in self.groups[::-1]:
            self.remove_group(group)
        for child in self._children.copy().values():
            self.remove_child(child)
        if self.scene is not None:
            self.scene.remove_object(self)

    def _rotated_pos(self, angle):
        angle = math.radians(angle)
        return Vec2(
            self.x * math.cos(angle) - self.y * math.sin(angle),
            self.x * math.sin(angle) + self.y * math.cos(angle),
        )

    @property
    def local_pos(self):
        return Vec2(self._pos)

    @property
    def pos(self):
        """Returns _pos attribute."""
        if self._parent is not None:
            return self._parent.pos + self._pos
        else:
            return Vec2(self._pos)

    @pos.setter
    def pos(self, pos):
        """Sets the _pos attribute"""
        self._pos = Vec2(pos)

    @property
    def y(self):
        """Returns y component of the _pos attribute."""
        return self._pos.y

    @y.setter
    def y(self, y):
        """Sets y component of the _pos attribute."""
        self.pos = Vec2(self._pos.x, y)

    @property
    def x(self):
        """Returns x component of the _pos attribute."""
        return self._pos.x

    @x.setter
    def x(self, x):
        """Sets x component of the _pos attribute."""
        self.pos = Vec2(x, self._pos.y)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, 1, 1)

    @property
    def top(self):
        return self.rect.top

    @property
    def right(self):
        return self.rect.right

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def left(self):
        return self.rect.left

    @property
    def center(self):
        return self.rect.center

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, new_facing):
        angle = self._facing.angle_to(new_facing)
        self.rotate(angle)
