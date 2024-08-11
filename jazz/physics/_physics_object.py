from .colliders import CircleCollider, PolyCollider, RayCollider, RectCollider, Collider
from ..engine.base_object import GameObject
from ..global_dict import Globals


class PhysicsObject(GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "PhysicsObject")
        super().__init__(**kwargs)
        self._layers = kwargs.get("layers", "0001")
        self.collision_layers = kwargs.get("collision_layers", "0001")
        self.collider: Collider | None = None

    def on_load(self):
        if self.collider is None:
            raise (Exception("Body does not have collider"))
        Globals.scene.add_physics_object(self, self._layers)

    def add_collider(self, type, **kwargs):
        if type == "Rect":
            self.collider = RectCollider(**kwargs)
        elif type == "Circle":
            self.collider = CircleCollider(**kwargs)
        elif type == "Poly":
            self.collider = PolyCollider(**kwargs)
        elif type == "Ray":
            self.collider = RayCollider(**kwargs)
        else:
            raise Exception("Invalid collider type")
        self.add_child(self.collider)
