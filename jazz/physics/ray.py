"""
Module to provide a base for active game entities.
"""
from typing import TYPE_CHECKING

from ..global_dict import Globals
from ..utils import JazzException, Vec2
from ._physics_object import PhysicsObject
from .colliders import Collider, RayCollider

if TYPE_CHECKING:
    from .. import GameObject


class Ray(PhysicsObject):
    """Raycast component representing a straight projection line for detecting physical overlaps."""

    def __init__(self, **kwargs) -> None:
        """Initializes the Ray component.

        Args:
            length (float | int, optional): The casting distance. Defaults to 1.
            active (bool, optional): Auto-update and cast flag. Defaults to True.
        """
        kwargs.setdefault("name", "Ray")
        super().__init__(**kwargs)
        self._ray_collider = RayCollider(length=kwargs.get("length", 1))
        self.add_child(self._ray_collider)
        self._active = kwargs.get("active", True)
        self.collision_point = None
        self.collision_object = None

    @property
    def collider(self) -> RayCollider:
        """RayCollider: The line segment collider created in __init__.

        Raises:
            JazzException: If set to a collider that is not a RayCollider.
        """
        return self._ray_collider

    @collider.setter
    def collider(self, collider: Collider) -> None:
        if not isinstance(collider, RayCollider):
            raise JazzException(f"{self.name}'s collider must be a RayCollider, not {type(collider).__name__}")
        self._ray_collider = collider
        self._collider = collider

    def _engine_update(self, delta: float) -> None:
        """Triggers raycast collision check if marked active.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        if self._active:
            self.collision_object, self.collision_point = self.cast()

    def cast_all(self, blacklist: list[PhysicsObject] | None = None) -> list[tuple["GameObject", Vec2]]:
        """
        Method that returns all collisions with the ray that are not in the blacklist
        :param blacklist: A list of objects to ignore
        :return: A list of collisions sorted closest to farthest
        """
        if blacklist is None:
            blacklist = []
        collisions = Globals.scene.get_AABB_collisions(self)
        precise_collisions: list[tuple[GameObject, Vec2]] = []
        for collider in collisions:
            if collider not in blacklist:
                point = self.collider.collide_ray(collider.collider)
                if point is not None:
                    precise_collisions.append((collider, point))
        precise_collisions.sort(
            key=lambda collision: (collision[1] - self.pos).magnitude_squared()
        )
        return precise_collisions

    def cast(self, blacklist: list[PhysicsObject] | None = None) -> "tuple[GameObject | None, Vec2 | None]":
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vec2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        if blacklist is None:
            blacklist = []
        collisions = Globals.scene.get_AABB_collisions(self)
        precise_collisions = []
        for collider in collisions:
            if collider not in blacklist:
                point = self.collider.collide_ray(collider.collider)
                if point is not None:
                    precise_collisions.append((collider, point))
        if precise_collisions:
            precise_collisions.sort(
                key=lambda collision: (collision[1] - self.pos).magnitude_squared()
            )
            closest_collision = (None, Vec2(self.collider.vertices[1]))
            closest_dist_sq = self.length ** 2
            for obj, point in precise_collisions:
                test = obj.root != self.root
                if test:
                    dist_sq = (point - self.pos).magnitude_squared()
                    if closest_dist_sq >= dist_sq >= 0:
                        closest_collision = (obj, point)
                        closest_dist_sq = dist_sq
            return closest_collision
        return None, None

    @property
    def length(self) -> float | int:
        """float: Gets the length of the ray segment."""
        return self.collider.length

    @length.setter
    def length(self, length: float) -> None:
        self.collider.length = length


from ..engine.serializer import Serializer

Serializer.register_class(Ray)
