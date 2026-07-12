from ..global_dict import Globals
from ..utils import Vec2, dist_to
from ._physics_object import PhysicsObject



class Body(PhysicsObject):
    """Rigid body physical component that handles rigid collisions and positional corrections."""

    def __init__(self, **kwargs) -> None:
        """Initializes the Body component.

        Args:
            static (bool, optional): If True, the object is static (immovable) and acts as an obstacle. Defaults to False.
        """
        kwargs.setdefault("name", "Body")
        super().__init__(**kwargs)
        self.static = kwargs.get("static", False)

    def move_and_collide(self, direction: Vec2, _visited: set[str] | None = None) -> list[tuple[PhysicsObject, tuple[float, Vec2]]]:
        """Moves the physical body along a direction vector, detects overlaps, resolves penetrations, and handles propagation.

        Args:
            direction (Vec2): The displacement vector for this frame.
            _visited (set[str], optional): Set of object IDs already processed in the current recursive chain to prevent infinite loops. Defaults to None.

        Returns:
            list[tuple[PhysicsObject, tuple[float, Vec2]]]: List of collision tuples containing the hit object and (depth, normal).
        """
        if _visited is None:
            _visited = set()
        if self.id in _visited:
            return []
        _visited.add(self.id)

        self.pos = self.pos + direction
        collisions = Globals.scene.get_AABB_collisions(self)
        precise_collisions = []

        if collisions:
            collisions.sort(key=lambda obj: (obj.pos - self.pos).magnitude_squared())
            penetrations = []
            for obj in collisions:
                depth, normal = self.collider.collide_sat(obj.collider)
                if depth != 0:
                    penetrations.append((obj, depth, normal))
                    precise_collisions.append((obj, (depth, normal)))

            if penetrations:
                self_correction = Vec2(0, 0)
                for obj, depth, normal in penetrations:
                    if not self.static:
                        if not obj.static:
                            self_correction += -normal * (depth + 1) / 2
                        else:
                            self_correction += -normal * (depth + 1)

                if not self.static and self_correction != Vec2(0, 0):
                    self.move(self_correction)

                for obj, depth, normal in penetrations:
                    if not obj.static:
                        if not self.static:
                            obj.move_and_collide(normal * (depth + 1) / 2, _visited)
                        else:
                            obj.move_and_collide(normal * (depth + 1), _visited)
        return precise_collisions


