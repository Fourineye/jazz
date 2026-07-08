from ..global_dict import Globals
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
        self._entered_cache = {}

    def update(self, _delta):
        if self._active:
            self.entered = self.get_entered()

    def get_entered(self):
        entered = []
        collisions = Globals.scene.get_AABB_collisions(self)
        if collisions:
            collisions.sort(key=lambda obj: (obj.pos - self.pos).magnitude_squared())
            for obj in collisions:
                test = True
                if self.target_group is not None:
                    test = obj in self.target_group

                test = test and obj.root != self.root
                if test:
                    if not self._moved_this_frame and not getattr(obj, "_moved_this_frame", True) and obj in self._entered_cache:
                        is_colliding = self._entered_cache[obj]
                    else:
                        depth, _ = self.collider.collide_sat(obj.collider)
                        is_colliding = (depth != 0)
                        self._entered_cache[obj] = is_colliding

                    if is_colliding:
                        entered.append(obj)
            self._entered_cache = {obj: val for obj, val in self._entered_cache.items() if obj in collisions}
        else:
            self._entered_cache.clear()
        return entered
