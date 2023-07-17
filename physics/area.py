from ..global_dict import Game_Globals
from ..utils import Vec2, dist_to
from ._physics_object import PhysicsObject

class Area(PhysicsObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Area")
        kwargs.setdefault("layers", "0000")
        super().__init__(**kwargs)

        self.target_group = kwargs.get("target_group", None)
        self.entered = []
        self._active = kwargs.get("active", True)

    def update(self, _delta):
        if self._active:
            self.entered = self.get_entered()

    def get_entered(self):
        entered = []
        collisions = Game_Globals["Scene"].get_AABB_collisions(self)
        if collisions:
            collisions.sort(key=lambda obj: dist_to(self.pos, obj.pos))
            for obj in collisions:
                test = True
                if self.target_group is not None:
                    test = obj in self.target_group

                test = test and obj.root != self.root
                if test:
                    depth, _ = self.collider.collide_sat(obj.collider)
                    if depth != 0:
                        entered.append(obj)
        return entered