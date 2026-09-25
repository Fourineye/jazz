"""PhysicsObject base class that owns a collider and registers with the scene's physics grids."""

from typing import Any

from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import (
    COLLIDER_CIRCLE,
    COLLIDER_POLY,
    COLLIDER_RAY,
    COLLIDER_RECT,
    JazzException,
)
from .colliders import CircleCollider, Collider, PolyCollider, RayCollider, RectCollider


class PhysicsObject(GameObject):
    """Base physical object component that integrates with the engine's 2D physics layers and colliders."""

    def __init__(self, **kwargs) -> None:
        """Initializes the PhysicsObject component.

        Args:
            layers (str | int, optional): Binary string or int mask indicating active physics layers. Defaults to "0001".
            collision_layers (str | int, optional): Binary string or int mask of layers this object collides with. Defaults to "0001".
        """
        kwargs.setdefault("name", "PhysicsObject")
        self._collider: Collider | None = None
        super().__init__(**kwargs)
        
        layers_val = kwargs.get("layers", "0001")
        if isinstance(layers_val, str):
            self._layers = int(layers_val, 2)
        else:
            self._layers = layers_val
            
        coll_layers_val = kwargs.get("collision_layers", "0001")
        if isinstance(coll_layers_val, str):
            self.collision_layers = int(coll_layers_val, 2)
        else:
            self.collision_layers = coll_layers_val
            
        self._moved_this_frame_val: bool = True

    @property
    def collider(self) -> Collider:
        """Collider: The shape used for this object's collision checks.

        Raises:
            JazzException: If no collider has been added yet.
        """
        if self._collider is None:
            raise JazzException(f"{self.name} has no collider. Call add_collider in __init__ or on_load.")
        return self._collider

    @collider.setter
    def collider(self, collider: Collider) -> None:
        self._collider = collider

    @property
    def _moved_this_frame(self) -> bool:
        """bool: Indicates whether the object moved in the current frame."""
        return self._moved_this_frame_val

    @_moved_this_frame.setter
    def _moved_this_frame(self, val: bool) -> None:
        self._moved_this_frame_val = val
        if val:
            Globals.scene.mark_moved(self)

    def on_transform_change(self) -> None:
        """Updates internal frame movement dirty flags when position/rotation updates."""
        super().on_transform_change()
        self._moved_this_frame = True

    def _on_load(self) -> None:
        """Engine hook. Registers this object with the active scene's physics grids.

        Registration runs after on_load so colliders can be added there. It is kept
        out of on_load so subclasses can override on_load without calling super().

        Raises:
            JazzException: If the object has no collider once on_load has run.
        """
        super()._on_load()
        Globals.scene.mark_moved(self)
        if self._collider is None:
            raise JazzException(f"{self.name} has no collider. Call add_collider in __init__ or on_load.")
        Globals.scene.add_physics_object(self, self._layers)

    def add_collider(self, type: int | str, **kwargs) -> None:
        """Adds a collider to the object.

        Args:
            type (int | str): Collider type name ("Rect", "Circle", "Polygon", "Poly", "Ray") or integer constant.
            **kwargs: Custom arguments to initialize the specific collider (e.g. w, h, radius, vertices, length).

        Raises:
            JazzException: Raises an exception if an invalid type is given.
        """
        if type == COLLIDER_RECT or type == "Rect":
            self._collider = RectCollider(**kwargs)
        elif type == COLLIDER_CIRCLE or type == "Circle":
            self._collider = CircleCollider(**kwargs)
        elif type == COLLIDER_POLY or type in ("Polygon", "Poly"):
            self._collider = PolyCollider(**kwargs)
        elif type == COLLIDER_RAY or type == "Ray":
            self._collider = RayCollider(**kwargs)
        else:
            raise JazzException("Invalid collider type")
        self.add_child(self._collider)

    def add_child(self, obj: Any) -> Any:
        """Adds a child object. The first Collider added becomes this object's collider.

        Args:
            obj (Any): Object to add as a child.

        Returns:
            Any: The added child object.
        """
        res = super().add_child(obj)
        if self._collider is None and isinstance(obj, Collider):
            self._collider = obj
        return res

from ..engine.serializer import Serializer

Serializer.register_class(PhysicsObject)
