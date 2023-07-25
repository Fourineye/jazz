"""
Module to provide a base for active game entities.
"""
from ..global_dict import GAME_GLOBALS
from ..utils import Vec2, dist_to
from ._physics_object import PhysicsObject
from .colliders import RayCollider


class Ray(PhysicsObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Ray")
        super().__init__(**kwargs)
        length = kwargs.get("length", 1)
        self.add_child(RayCollider(length=length), "collider")
        self._active = kwargs.get("active", True)
        self.collision_point = None
        self.collision_object = None

    def update(self, _delta: float):
        if self._active:
            self.collision_object, self.collision_point = self.cast()

    def cast(self):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vec2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        collisions = GAME_GLOBALS["Scene"].get_AABB_collisions(self)
        precise_collisions = []
        for collider in collisions:
            point = self.collider.collide_ray(collider.collider)
            if point is not None:
                precise_collisions.append((collider, point))
        if precise_collisions:
            precise_collisions.sort(
                key=lambda collision: dist_to(self.pos, collision[1])
            )
            closest_collision = (None, Vec2(self.collider.vertices[1]))
            for obj, point in precise_collisions:
                test = obj.root != self.root
                if test:
                    if self.length**2 >= dist_to(self.pos, point) >= 0:
                        if dist_to(self.pos, point) < dist_to(
                            self.pos, closest_collision[1]
                        ):
                            closest_collision = (obj, point)
            return closest_collision
        return None, None

    @property
    def length(self):
        return self.collider.length

    @length.setter
    def length(self, length):
        self.collider.length = length
