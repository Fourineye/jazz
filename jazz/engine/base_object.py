import uuid

from ..global_dict import Globals
from ..utils import Color, Vec2, angle_from_vec, unit_from_angle, JazzException
from ..primatives import Draw


class GameObject:
    """Base object in jazz"""

    def __init__(self, name="Object", **kwargs):
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

    # Base Methods
    def on_load(self):
        """Base method that can be overwritten. Called when the object is added to the scene."""

    def update(self, delta: float) -> None:
        """Base method that can be overwritten. Called once per frame.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def late_update(self, delta: float) -> None:
        """Base method that can be overwritten. Called after every object has run its update method

        Args:
            delta (float): Time since last frame
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

    # Engine called methods that allow object nesting
    def _update(self, delta: float) -> None:
        """Engine method that propogates the update call to it's children

        Args:
            delta (float): Time in seconds since the last frame
        """
        for child in self._children.values():
            child._update(delta)
        self.update(delta)

    def _late_update(self, delta: float) -> None:
        """Engine method that propogates the late_update call to it's children

        Args:
            delta (float): Time in seconds since the last frame
        """
        for child in self._children.values():
            child._late_update(delta)
        self.late_update(delta)

    def _render_debug(self, offset: Vec2) -> None:
        """Engine method that propogates the render_debug call to it's children.

        Args:
            offset (Vec2): Screen offset for drawing
        """
        if self.visible:
            self.render_debug(offset)
            for child in self._children.values():
                child._render_debug(offset)

    def _on_load(self) -> None:
        """Engine method that propogates the on_load call to it's children."""
        self.on_load()
        for child in self._children.values():
            child._on_load()

    # Child management
    def add_child(self, obj: "GameObject") -> "GameObject":
        """Adds an object to the child tree.

        Args:
            obj (GameObject): Object to add

        Raises:
            JazzException: If obj is already a child

        Returns:
            GameObject: obj to allow for chaining
        """
        if obj.id not in self._children.keys():
            obj._parent = self
            obj._depth = self._depth + 1
            self._children[obj.id] = obj
            return obj
        else:
            raise JazzException(
                f"{obj.id}:{obj.name} is already a child of {self.id}:{self.name}"
            )

    def remove_child(self, obj: "GameObject", kill=True) -> None:
        """Removes the object from the child tree, optionally deleting it from the scene.

        Args:
            obj (GameObject): Object to remove
            kill (bool, optional): Delete from scene after removing. Defaults to True.

        Raises:
            JazzException: If obj is not a child of the calling object
        """
        if obj.id in self._children:
            self._children.pop(obj.id)
            if kill:
                obj.kill()
        else:
            raise JazzException(
                f"{obj.id}:{obj.name} not found as child of {self.id}:{self.name}"
            )

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

    def queue_kill(self) -> None:
        """Marks the object for destruction at the end of the frame."""
        self.game_process = False
        self.pause_process = False
        self.game_input = False
        self.do_kill = True

    def kill(self) -> None:
        """Destroy's the object and any children."""

        Globals.scene.remove_physics_object(self)
        Globals.scene.remove_object(self)
        if self._parent is not None:
            self._parent.remove_child(self, False)

        for child in self._children.copy().values():
            self.remove_child(child)

    @property
    def root(self) -> "GameObject":
        """Returns the root of the object's children tree.

        Returns:
            GameObject: The root of the object's children tree
        """
        if self._parent is None:
            return self
        else:
            return self._parent.root

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

    @property
    def pos(self) -> Vec2:
        """Returns the object's global position.

        Returns:
            Vec2: THe object's global position
        """
        if self._parent is not None:
            if -0.001 < self._parent.rotation < 0.001:
                return self._parent.pos + self._pos
            else:
                return self._parent.pos + self._pos.rotate(
                    self._parent.rotation
                )
        else:
            return Vec2(self._pos)

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

    @property
    def rotation(self) -> float:
        """Returns the object's global rotation.

        Returns:
            float: The object's global rotation
        """
        if self._parent is not None:
            return self._parent.rotation + self._rotation
        else:
            return self._rotation

    @rotation.setter
    def rotation(self, degrees: float) -> None:
        """Sets the object's global rotation.

        Args:
            degrees (float): The object's global rotation
        """
        if self._parent is not None:
            self._rotation = degrees - self._parent.rotation
        else:
            self._rotation = degrees

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

    def __repr__(self):
        children = ""
        for _, child in self._children.items():
            children += f" {child}"
        return (
            "-" * self._depth
            + f"{self.name} at {round(self.x, 2)}, {round(self.y, 2)}\n"
            + children
        )
