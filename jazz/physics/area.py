from ..global_dict import Globals
from ..utils import Vec2, dist_to
from ._physics_object import PhysicsObject


class Area(PhysicsObject):
    """Sensor zone component that detects overlapping physical objects without resolution checks."""

    def __init__(self, **kwargs) -> None:
        """Initializes the Area component.

        Args:
            target_group (Group, optional): Filter overlaps against a specific Entity Group. Defaults to None.
            active (bool, optional): Active status check flag. Defaults to True.
        """
        kwargs.setdefault("name", "Area")
        kwargs.setdefault("layers", "0000")
        super().__init__(**kwargs)

        self.target_group = kwargs.get("target_group", None)
        self.entered = []
        self._active = kwargs.get("active", True)
        self._entered_cache = {}

    def update(self, _delta: float) -> None:
        """Updates and queries overlapping candidates each frame if sensor is active."""
        if self._active:
            self.entered = self.get_entered()

    def get_entered(self) -> list[PhysicsObject]:
        """Queries and returns a sorted list of physics objects currently overlapping this area.

        Returns:
            list[PhysicsObject]: Sensed physics objects, sorted by proximity to the area center.
        """
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
