from .colliders import CircleCollider, PolyCollider, RayCollider, RectCollider, Collider
from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import COLLIDER_RECT, COLLIDER_POLY, COLLIDER_CIRCLE, COLLIDER_RAY, JazzException


class PhysicsObject(GameObject):
    """Base physical object component that integrates with the engine's 2D physics layers and colliders."""

    def __init__(self, **kwargs) -> None:
        """Initializes the PhysicsObject component.

        Args:
            layers (str | int, optional): Binary string or int mask indicating active physics layers. Defaults to "0001".
            collision_layers (str | int, optional): Binary string or int mask of layers this object collides with. Defaults to "0001".
        """
        kwargs.setdefault("name", "PhysicsObject")
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
            
        self.collider: Collider | None = None
        self._moved_this_frame = True

    def on_transform_change(self) -> None:
        """Updates internal frame movement dirty flags when position/rotation updates."""
        super().on_transform_change()
        self._moved_this_frame = True

    def on_load(self) -> None:
        """Mounts and registers this object with the active scene's physics simulation grids.

        Raises:
            JazzException: If the object is loaded without registering a collider.
        """
        if self.collider is None:
            raise (JazzException("Physics Object does not have collider"))
        Globals.scene.add_physics_object(self, self._layers)

    def add_collider(self, type: int, **kwargs) -> None:
        """Adds a collider to the object

        Args:
            type (int): Collider type, one of the constants COLLIDER_RECT, COLLIDER_POLY, COLLIDER_CIRCLE, COLLIDER_RAY

        Raises:
            JazzException: Raises an exception if an invalid type is given
        """
        if type == COLLIDER_RECT:
            self.collider = RectCollider(**kwargs)
        elif type == COLLIDER_CIRCLE:
            self.collider = CircleCollider(**kwargs)
        elif type == COLLIDER_POLY:
            self.collider = PolyCollider(**kwargs)
        elif type == COLLIDER_RAY:
            self.collider = RayCollider(**kwargs)
        else:
            raise JazzException("Invalid collider type")
        self.add_child(self.collider)
