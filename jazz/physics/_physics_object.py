from .colliders import CircleCollider, PolyCollider, RayCollider, RectCollider, Collider
from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import COLLIDER_RECT, COLLIDER_POLY, COLLIDER_CIRCLE, COLLIDER_RAY, JazzException


class PhysicsObject(GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "PhysicsObject")
        super().__init__(**kwargs)
        self._layers = kwargs.get("layers", "0001")
        self.collision_layers = kwargs.get("collision_layers", "0001")
        self.collider: Collider | None = None

    def on_load(self):
        if self.collider is None:
            raise (JazzException("Physics Object does not have collider"))
        Globals.scene.add_physics_object(self, self._layers)

    def add_collider(self, type: int, **kwargs):
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
