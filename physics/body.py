from ..global_dict import GAME_GLOBALS
from ..utils import Vec2, dist_to
from ._physics_object import PhysicsObject


class Body(PhysicsObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Body")
        super().__init__(**kwargs)
        self.static = kwargs.get("static", False)

    def move_and_collide(self, direction: Vec2):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vec2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        self.pos = self.pos + direction
        collisions = GAME_GLOBALS["Scene"].get_AABB_collisions(self)
        precise_collisions = []

        if collisions:
            collisions.sort(key=lambda obj: dist_to(self.pos, obj.pos))
            for obj in collisions:
                depth, normal = self.collider.collide_sat(obj.collider)
                if depth != 0:
                    precise_collisions.append((obj, (depth, normal)))
                    if not self.static and not obj.static:
                        self.move(-normal * (depth + 1) / 2)
                        obj.move_and_collide(normal * (depth + 1) / 2)
                    elif self.static and not obj.static:
                        obj.move_and_collide(normal * (depth + 1))
                    elif obj.static:
                        self.move(-normal * (depth + 1))
        return precise_collisions
