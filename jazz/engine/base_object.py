"""BaseObject and GameObject: the scene-graph node, lifecycle hooks, and transforms."""

from abc import ABC
from typing import Any
import uuid
from typing import TypeVar

from ..global_dict import Globals
from ..utils import Color, Vec2, angle_from_vec, unit_from_angle, JazzException
from ..primatives import Draw


T = TypeVar("T", bound="GameObject")


class BaseObject(ABC):
    """Base class for all objects in the scene"""

    def __new__(cls, *args, **kwargs):
        if cls is BaseObject:
            raise TypeError("BaseObject is an abstract base class and cannot be instantiated directly.")
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__init__" in cls.__dict__:
            orig_init = cls.__init__

            def wrapped_init(self, *args, **kwargs):
                depth = self.__dict__.get("_init_depth", 0)
                object.__setattr__(self, "_init_depth", depth + 1)
                try:
                    orig_init(self, *args, **kwargs)
                finally:
                    depth = self.__dict__.get("_init_depth", 1)
                    object.__setattr__(self, "_init_depth", max(0, depth - 1))

            cls.__init__ = wrapped_init

    def __init__(self, name="BaseObject", **kwargs) -> None:
        """Initializes base object lifecycle and tree attributes."""
        depth = self.__dict__.get("_init_depth", 0)
        object.__setattr__(self, "_init_depth", depth + 1)
        try:
            # Saving args
            self._kwargs = kwargs.copy()
            self._scripts: dict[str, str] = {}

            # Engine Attributes
            self.name = name
            self.id = str(uuid.uuid1())

            # Child properties
            self._children: dict[str, Any] = {}
            self._parent: BaseObject | None = None
            self._depth = 0

            # Custom Properties dict
            raw_props = kwargs.get("properties", {})
            if isinstance(raw_props, (list, tuple, set)):
                self._properties: dict[str, Any] = {str(p): None for p in raw_props}
            elif isinstance(raw_props, dict):
                self._properties: dict[str, Any] = dict(raw_props)
            else:
                self._properties: dict[str, Any] = {}

            # Engine flags
            self._pause_process = kwargs.get("pause_process", False)
            self._game_process = kwargs.get("game_process", True)
            self._kill = False

            self._loaded: bool = False
        finally:
            depth = self.__dict__.get("_init_depth", 1)
            object.__setattr__(self, "_init_depth", max(0, depth - 1))

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets an attribute, checking properties if necessary.

        Allows creating new attributes during __init__, but outside of __init__
        only allows updating existing attributes or custom properties.

        Args:
            name (str): The attribute name
            value (Any): The attribute value

        Raises:
            AttributeError: If attempting to add a new attribute outside of __init__.
        """
        props = self.__dict__.get("_properties")
        if props is not None and name in props:
            props[name] = value
            return

        if (
            name in self.__dict__
            or hasattr(type(self), name)
            or self.__dict__.get("_init_depth", 0) > 0
        ):
            super().__setattr__(name, value)
        else:
            raise AttributeError(
                f"Cannot add new attribute '{name}' to '{type(self).__name__}' outside of __init__"
            )

    def __getattr__(self, name: str) -> Any:
        """Returns the attribute value, checking properties if necessary.

        Args:
            name (str): The attribute name

        Returns:
            Any: The attribute value

        Raises:
            AttributeError: If the attribute is not found in properties.
        """
        props = self.__dict__.get("_properties")
        if props is not None and name in props:
            return props[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __repr__(self) -> str:
        children = ""
        for _, child in self._children.items():
            children += f" {child}"
        return (
            "-" * self._depth
            + f"{self.name} at {round(self.x, 2)}, {round(self.y, 2)}\n"
            + children
        )

    def assign_script(self, hook: str, path: Any) -> None:
        """Assigns a script path or callable to a specific hook method on the game object.

        Args:
            hook (str): The hook method name (e.g., 'update', 'on_load').
            path (Any): The script file path, function reference string, or callable.
        """
        from .serializer import Serializer
        if hasattr(self, "_scripts"):
            self._scripts[hook] = path
        else:
            self._scripts = {hook: path}

        resolved = Serializer.resolve_script(path) if isinstance(path, str) else path
        setattr(self, hook, Serializer.make_script_wrapper(self, resolved))

    # Base Methods
    def on_load(self) -> None:
        """Base method that can be overwritten. Called when the object is added to the scene."""

    def update(self, delta: float) -> None:
        """Base method that can be overwritten. Called once per frame.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def late_update(self, delta: float) -> None:
        """Base method that can be overwritten. Called after every object has run its update method

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def render_debug(self, offset: Vec2) -> None:
        """Base method that can be overwritten. Called to draw debug visuals.

        Args:
            offset (Vec2): Screen offset for drawing.
        """

    # Engine called methods that allow object nesting
    def _update(self, delta: float) -> None:
        """Engine method that propogates the update call to it's children.

        Children marked for deletion are handed to the scene to be killed at the end
        of the frame, and children with game_process disabled are skipped. Pause
        behaviour is inherited from the top-level object.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        for child in list(self._children.values()):
            if child._kill:
                Globals.scene.queue_object_kill(child)
            elif child._game_process:
                child._update(delta)
        self._engine_update(delta)
        self.update(delta)

    def _engine_update(self, delta: float) -> None:
        """Engine method method that can be overwritten for engine classes. Called in the update loop

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def _late_update(self, delta: float) -> None:
        """Engine method that propogates the late_update call to it's children

        Args:
            delta (float): Time in seconds since the last frame.
        """
        for child in list(self._children.values()):
            if child._kill:
                Globals.scene.queue_object_kill(child)
            elif child._game_process:
                child._late_update(delta)
        self._engine_late_update(delta)
        self.late_update(delta)

    def _engine_late_update(self, delta: float) -> None:
        """Engine method method that can be overwritten for engine classes. Called in the late_update loop

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def _render_debug(self, offset: Vec2) -> None:
        """Engine method that propogates the render_debug call to it's children.

        Args:
            offset (Vec2): Screen offset for drawing.
        """
        if getattr(self, "visible", True):
            self.render_debug(offset)
            for child in self._children.values():
                child._render_debug(offset)

    def _on_load(self) -> None:
        """Engine method that propogates the on_load call to it's children."""
        self._loaded = True
        self.on_load()
        for child in self._children.values():
            child._on_load()

    def _on_tree_change(self) -> None:
        """Engine method that that can be overwritten for engine classes."""

    # Child management
    def add_child(self, obj: T) -> T:
        """Adds an object to the child tree.

        Args:
            obj (T): Object to add

        Raises:
            JazzException: If obj is already a child

        Returns:
            T: obj to allow for chaining
        """
        if obj.id not in self._children.keys():
            obj._parent = self
            obj._depth = self._depth + 1
            self._children[obj.id] = obj
            obj._on_tree_change()
            if getattr(self, "_loaded", False):
                obj._on_load()
            return obj
        else:
            raise JazzException(
                f"{obj.id}:{obj.name} is already a child of {self.id}:{self.name}"
            )

    def remove_child(self, obj: "BaseObject", kill=True) -> None:
        """Removes the object from the child tree, optionally deleting it from the scene.

        Args:
            obj (BaseObject): Object to remove
            kill (bool, optional): Delete from scene after removing. Defaults to True.

        Raises:
            JazzException: If obj is not a child of the calling object
        """
        if obj.id in self._children:
            self._children.pop(obj.id)
            obj._parent = None
            if kill:
                obj.kill()
                return
            obj._on_tree_change()
        else:
            raise JazzException(
                f"{obj.id}:{obj.name} not found as child of {self.id}:{self.name}"
            )

    def queue_kill(self) -> None:
        """Marks the object for destruction at the end of the frame."""
        self._game_process = False
        self._pause_process = False
        self._kill = True

    def kill(self) -> None:
        """Destroys the object and any children."""

        Globals.scene.remove_physics_object(self)
        Globals.scene.remove_object(self)
        if self._parent is not None:
            self._parent.remove_child(self, False)

        for child in self._children.copy().values():
            self.remove_child(child)

    @property
    def root(self) -> "BaseObject":
        """Returns the root of the object's children tree.

        Returns:
            BaseObject: The root of the object's children tree
        """
        if self._parent is None:
            return self
        else:
            return self._parent.root


class GameObject(BaseObject):
    """Simplest object in jazz, has transform properties but is not directly renderable"""

    def __init__(
        self,
        name: str = "Object",
        **kwargs,
    ) -> None:
        """Base object in Jazz Engine.

        Args:
            name (str, optional): Name for the object. Defaults to "Object".
            pause_process (bool, optional): Whether the object should update when the scene is paused. Defaults to False.
            game_process (bool, optional): Whether the object should update every frame. Defaults to True.
            visible (bool, optional): Whether the object should be rendered. Defaults to True.
            screen_space (bool, optional): Whether the object is in screen space or world space. Defaults to False.
            pos (Vec2, optional): The object's local position. Defaults to Vec2(0,0).
            rotation (float, optional): The object's local rotation. Defaults to 0.

        """
        kwargs["name"] = name
        super().__init__(**kwargs)

        # Rendering flags
        self._visible = kwargs.get("visible", True)
        self._screen_space = kwargs.get("screen_space", False)
        self._z = kwargs.get("z", 0)

        # Basic positional Attributes
        self._pos = Vec2(kwargs.get("pos", (0, 0)))
        self._rotation = kwargs.get("rotation", 0)
        self._moved_this_frame = False
        self._transform_dirty = True
        self._cached_pos = Vec2()
        self._cached_rotation = 0.0

    def render(self, offset: Vec2) -> None:
        """Base method that can be overwritten. Draws the object to the screen.

        Args:
            offset (Vec2): Screen offset for drawing
        """

    def render_debug(self, offset: Vec2) -> None:
        """Base method that can be overwritten. Draws a circle at the object's world
        position and a line in it's look direction.

        Args:
            offset (Vec2): Screen offset for drawing
        """
        screen_pos = self.pos + offset
        look_pos = screen_pos + self.facing * 10
        Draw.circle(self.pos + offset, 5, Color("yellow"), 3)
        Draw.line(screen_pos, look_pos, Color("red"), 3)

    # movement methods
    def move(self, movement: Vec2) -> None:
        """Moves the object in the world.

        Args:
            movement (Vector2, tuple): The amount to move
        """
        self.pos += movement

    def rotate(self, degrees: float) -> None:
        """Rotates the object by the given amount.

        Args:
            degrees (float): The angle in degrees to rotate the object by.
        """
        self.local_rotation = self.local_rotation + degrees
    
    def _on_tree_change(self) -> None:
        self._set_transform_dirty()

    def on_transform_change(self) -> None: pass

    def _set_transform_dirty(self) -> None:
        """Marks this object and all of its descendants as transform-dirty.

        Triggers the on_transform_change event hook on this object.
        """
        self.on_transform_change()
        if not self._transform_dirty:
            self._transform_dirty = True
            for child in self._children.values():
                child._set_transform_dirty()

    def _update_transform(self) -> None:
        """Updates and caches the global position and rotation of this object.

        If marked dirty, recalculates position and rotation relative to the parent,
        propagating transform values, then marks the cache as clean.
        """
        if self._transform_dirty:
            if self._parent is not None:
                parent_pos = self._parent.pos
                parent_rot = self._parent.rotation
                self._cached_rotation = (parent_rot + self._rotation) % 360
                if -0.001 < parent_rot < 0.001:
                    self._cached_pos = parent_pos + self._pos
                else:
                    self._cached_pos = parent_pos + self._pos.rotate(parent_rot)
            else:
                self._cached_rotation = self._rotation
                self._cached_pos = Vec2(self._pos)
            self._transform_dirty = False

    @property
    def local_pos(self) -> Vec2:
        """Returns the object's local position.

        Returns:
            Vec2: The object's local position
        """
        return Vec2(self._pos)

    @local_pos.setter
    def local_pos(self, pos: Vec2) -> None:
        """Sets the object's local position.

        Args:
            pos (Vec2): The object's new local position
        """
        self._pos = Vec2(pos)
        self._set_transform_dirty()

    @property
    def pos(self) -> Vec2:
        """Returns the object's global position.

        Returns:
            Vec2: THe object's global position
        """
        self._update_transform()
        return Vec2(self._cached_pos)

    @pos.setter
    def pos(self, pos: Vec2) -> None:
        """Sets the object's global position.

        Args:
            pos (Vec2): The object's new global position
        """
        if self._parent is not None:
            self._pos = Vec2(pos - self._parent.pos).rotate(
                -self._parent.rotation
            )
        else:
            self._pos = Vec2(pos)
        self._set_transform_dirty()

    @property
    def local_rotation(self) -> float:
        """Returns the object's local rotation.

        Returns:
            float: The object's local rotation
        """
        return self._rotation

    @local_rotation.setter
    def local_rotation(self, angle: float) -> None:
        """Sets the object's local rotation.

        Args:
            angle (float): The object's new local rotation
        """
        self._rotation = angle % 360
        self._set_transform_dirty()

    @property
    def rotation(self) -> float:
        """Returns the object's global rotation.

        Returns:
            float: The object's global rotation
        """
        self._update_transform()
        return self._cached_rotation

    @rotation.setter
    def rotation(self, degrees: float) -> None:
        """Sets the object's global rotation.

        Args:
            degrees (float): The object's global rotation
        """
        if self._parent is not None:
            self._rotation = (degrees - self._parent.rotation) % 360
        else:
            self._rotation = degrees % 360
        self._set_transform_dirty()

    @property
    def y(self) -> float:
        """Returns the object's global y position.

        Returns:
            float: The object's global y position
        """
        return self.pos.y

    @property
    def x(self) -> float:
        """Returns the objects global x position.

        Returns:
            float: The object's global x position
        """
        return self.pos.x

    @property
    def z(self) -> int:
        """Returns the z index of the object.

        Returns:
            int: The object's z index
        """
        if self._parent is not None:
            return self._parent.z
        else:
            return self._z

    @property
    def facing(self) -> Vec2:
        """Returns the object's look Vector.

        Returns:
            Vec2: The object's look Vector
        """
        return unit_from_angle(self.rotation)

    @facing.setter
    def facing(self, new_facing: Vec2) -> None:
        """Sets the object's rotation to match a look Vector.

        Args:
            new_facing (Vec2): The Vector to match rotation of
        """
        angle: float = angle_from_vec(new_facing)
        self.rotation = angle

    @property
    def visible(self) -> bool:
        """Returns the draw flag of the object, taking into account it's parent's draw state.

        Returns:
            bool: Draw state of the object
        """
        if self._parent is not None:
            return self._visible and self._parent.visible
        else:
            return self._visible

    @visible.setter
    def visible(self, visibility: bool) -> None:
        """Sets if the object should be drawn or not.

        Args:
            visibility (bool): Draw state of the object
        """
        self._visible = visibility

    @property
    def screen_space(self) -> bool:
        """Returns if the object is in screen space or world space.

        Returns:
            bool: True if in screen space, False if in world space
        """
        if self._parent is not None:
            return self._screen_space or self._parent.screen_space
        else:
            return self._screen_space

    @screen_space.setter
    def screen_space(self, screen_space: bool) -> None:
        """Sets the object to screen or world space.

        Args:
            screen_space (bool): True if object is in screen space, False if in world space
        """
        self._screen_space = screen_space

    @property
    def child_count(self) -> int:
        """Returns the number of children the object has.

        Returns:
            int: The child count
        """
        count = 0
        if self._children:
            for child in self._children.values():
                count += 1
                count += child.child_count
        return count

from .serializer import Serializer

Serializer.register_class(GameObject)
