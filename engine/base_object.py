import math
import uuid

import pygame

from ..global_dict import Globals
from ..utils import Vec2, angle_from_vec, rotated_pos, unit_from_angle

config_dict = {
    "pause_process": False,
    "game_process": True,
    "visible": True,
    "screen_space": False,
    "pos": (0, 0),
    "rotation": 0,
    "z": 0,
    "color": (255, 255, 255),
    "groups": (),
}


class GameObject:
    """Base object in jazz"""

    def __init__(self, name="Object", **kwargs):
        """Base object in jazz.

        Args:
            name (str, optional): sets name property. Defaults to "Object".
            pause_process (bool, optional): Sets whether the object will run
                the update method while the scene is paused. Defaults to False.
            game_process (bool, optional): Sets whether the object will run the
                update method. Defaults to True.
            visible (bool, optional): Sets whether the object will run the draw
                method. Defaults to True
            screen_space (bool, optional): Sets whether the object is drawn in
                screen space or world space. Defaults to False
            z (int, optional): Sets the z-index of the object to determine draw order.
            pos (tuple[float], optional): Sets the local space position of the
                object. Defaults to (0, 0).
            rotation (float, optional): Sets the local rotation of the object. Defaults
                to 0.
            color (pygame.Color, tuple[int], optional): Sets the color that the debug graphics
                will be drawn in. Defaults to (255, 255, 255).
            groups (list[str], optional): The list of groups to add the object to. Defaults to [].
        """
        # Engine Attributes
        self.name = name
        self.id = str(uuid.uuid1())

        # Child properties
        self._children = {}
        self._parent = None
        self._depth = 0

        # Engine flags
        self.pause_process = kwargs.get("pause_process", False)
        self.game_process = kwargs.get("game_process", True)
        self.do_kill = False

        # Rendering flags
        self._visible = kwargs.get("visible", True)
        self._screen_space = kwargs.get("screen_space", False)
        self._z = kwargs.get("z", 0)

        # Basic positional Attributes
        self._pos = Vec2(kwargs.get("pos", (0, 0)))
        self._rotation = kwargs.get("rotation", 0)
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
            + f"{self.name} at {round(self.x,2)}, {round(self.y,2)}\n"
            + children
        )

    def _on_load(self):
        self.on_load()
        for child in self._children.values():
            child._on_load()

    def on_load(self):
        """Called after the object is added to the scene."""

    def update(self, delta: float):
        """
        Method called once per frame to handle game logic. Called before draw.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def late_update(self, delta):
        """Called after every object has run its' update method

        Args:
            delta (float): time since last frame
        """

    def _draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """

    def _debug_draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        pygame.draw.circle(surface, self._color, self.pos + offset, 3, 2)
        pygame.draw.aaline(
            surface, self._color, self.pos + offset, self.pos + offset + self.facing * 5
        )

    # Engine called methods that allow object nesting
    def _update(self, delta):
        for child in self._children.values():
            child._update(delta)
        self.update(delta)

    def _late_update(self, delta):
        for child in self._children.values():
            child._late_update(delta)
        self.late_update(delta)

    def draw(self, surface: pygame.Surface, offset=None):
        if self.visible:
            self._draw(surface, offset)
            for child in self._children.values():
                child.draw(surface, offset)

    def debug_draw(self, surface: pygame.Surface, offset=None):
        if self.visible:
            self._debug_draw(surface, offset)
            for child in self._children.values():
                child.debug_draw(surface, offset)

    # Child management
    def add_child(self, obj, name=None):
        """Add a child to the object.

        Args:
            obj (jazz.GameObject): The object to add
            name (str, optional): If this argument is given the parent will
                have an attribute added of the given name. Defaults to None.
        """
        if obj.id not in self._children.keys():
            obj._parent = self
            obj._depth = self._depth + 1
            self._children[obj.id] = obj

        if name is not None and name not in self.__dict__.keys():
            name = name.split(" ")[0]
            obj.name = name
            self.__dict__.setdefault(name, obj)

    def remove_child(self, obj, kill=True):
        """Removes a child from the object.

        Args:
            obj (_type_): _description_
            kill (bool, optional): _description_. Defaults to True.
        """
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

    # movement methods
    def move(self, movement):
        """Moves the object in the world.

        Args:
            movement (Vector2, tuple): The amount to move
        """
        self.pos += movement

    def rotate(self, degrees):
        """Rotates the object by the given amount

        Args:
            degrees (float): The angle in degrees to rotate the object by.
        """
        self._rotation = (self._rotation + degrees) % 360

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

    def queue_kill(self):
        """Marks the object for deletion at the end of the frame."""
        self.game_process = False
        self.pause_process = False
        self.game_input = False
        self.do_kill = True

    def kill(self):
        """Destroys the object and all of its children"""

        Globals.scene.remove_physics_object(self)
        Globals.scene.remove_object(self)
        if self._parent is not None:
            self._parent.remove_child(self, False)

        for group in self.groups[::-1]:
            self.remove_group(group)
        for child in self._children.copy().values():
            self.remove_child(child)

    @property
    def root(self):
        """Returns the object at the top of the parent-child tree.

        Returns:
            jazz.GameObject: The object at the top of the parent-child tree.
        """
        if self._parent is None:
            return self
        else:
            return self._parent.root

    @property
    def local_pos(self):
        """The position of an object in it's local space

        Returns:
            jazz.Vec2: The local position of the object
        """
        return Vec2(self._pos)

    @local_pos.setter
    def local_pos(self, pos):
        self._pos = Vec2(pos)

    @property
    def pos(self):
        """The position of an object in world space

        Returns:
            jazz.Vec2: The world position of the object
        """
        if self._parent is not None:
            if -0.001 < self._parent.rotation < 0.001:
                return self._parent.pos + self._pos
            else:
                return self._parent.pos + self._pos.rotate(self._parent.rotation)
        else:
            return Vec2(self._pos)

    @pos.setter
    def pos(self, pos):
        """Sets the _pos attribute"""
        if self._parent is not None:
            self._pos = Vec2(pos - self._parent.pos).rotate(-self._parent.rotation)
        else:
            self._pos = Vec2(pos)

    @property
    def local_rotation(self):
        """The local rotation of the object.

        Returns:
            float: The local rotation of the object.
        """
        return self._rotation

    @local_rotation.setter
    def local_rotation(self, angle):
        self._rotation = angle % 360

    @property
    def rotation(self):
        """The world rotation of the object.

        Returns:
            float: The world rotation of the object.
        """
        if self._parent is not None:
            return self._parent.rotation + self._rotation
        else:
            return self._rotation

    @rotation.setter
    def rotation(self, degrees):
        if self._parent is not None:
            self._rotation = degrees - self._parent.rotation
        else:
            self._rotation = degrees

    @property
    def y(self):
        """Returns y component of the _pos attribute."""
        return self.pos.y

    @property
    def x(self):
        """Returns x component of the _pos attribute."""
        return self.pos.x

    @property
    def facing(self):
        """The unit vector facing forrward relative to the object.

        Returns:
            jazz.Vec2: The unit vector facing forward from the object.
        """
        if self._parent is not None:
            return unit_from_angle(self._parent.rotation + self._rotation)
        else:
            return unit_from_angle(self._rotation)

    @facing.setter
    def facing(self, new_facing):
        angle = angle_from_vec(new_facing)
        self.rotation = angle

    @property
    def visible(self):
        """The flag to determine if the object draws.

        Returns:
            bool: visibility of the object.
        """
        if self._parent is not None:
            return self._visible and self._parent.visible
        else:
            return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility

    @property
    def screen_space(self):
        """The flag to determine if the object draws with the camera offset.

        Returns:
            bool: if the object ignores the camera offset.
        """
        if self._parent is not None:
            return self._screen_space or self._parent.screen_space
        else:
            return self._screen_space

    @screen_space.setter
    def screen_space(self, screen_space):
        self._screen_space = screen_space

    @property
    def child_count(self):
        count = 0
        if self._children:
            for child in self._children.values():
                count += 1
                count += child.child_count
        return count
