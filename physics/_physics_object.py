from ..engine.base_object import GameObject
from ..global_dict import GAME_GLOBALS
from .colliders import CircleCollider, PolyCollider, RayCollider, RectCollider


class PhysicsObject(GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "PhysicsObject")
        super().__init__(**kwargs)
        self._layers = kwargs.get("layers", "0001")
        self.collision_layers = kwargs.get("collision_layers", "0001")

    def on_load(self):
        if not hasattr(self, "collider"):
            raise (Exception("Body does not have collider"))
        GAME_GLOBALS["Scene"].add_physics_object(self, self._layers)

    def add_collider(self, type, **kwargs):
        if type == "Rect":
            self.add_child(RectCollider(**kwargs), "collider")
        elif type == "Circle":
            self.add_child(CircleCollider(**kwargs), "collider")
        elif type == "Poly":
            self.add_child(PolyCollider(**kwargs), "collider")
        elif type == "Ray":
            self.add_child(RayCollider(**kwargs), "collider")
        else:
            raise Exception("Invalid collider type")
