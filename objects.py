"""
Module to provide a base for active game entities.
"""

from random import randint

from .baseObject import GameObject
from .colliders import (CircleCollider, Collider, PolyCollider, RayCollider,
                        RectCollider)
from .global_dict import Game_Globals
from .input_handler import InputHandler
from .utils import Vec2, direction_to, dist_to, load_image


class PhysicsObject(GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "PhysicsObject")
        super().__init__(**kwargs)
        self._layers = kwargs.get("layers", "0001")
        self.collision_layers = kwargs.get("collision_layers", "0001")

    def on_load(self):
        if not hasattr(self, "collider"):
            raise (Exception("Body does not have collider"))
        Game_Globals["Scene"].add_physics_object(self, self._layers)

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
        collisions = Game_Globals["Scene"].get_AABB_collisions(self)
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


class Group:
    """A container for Entities that allows for checking of collisions and other methods"""

    def __init__(self, initial_items=None, name="group"):
        self.name = name
        self._entities = []
        if initial_items:
            self.add_entities(initial_items)

    def __len__(self):
        return len(self._entities)

    def __iter__(self):
        return iter(self._entities)

    def __getitem__(self, i):
        return self._entities[i]

    def __setitem__(self, i, val):
        self._entities[i] = val

    def __delitem__(self, i):
        self.remove(self._entities[i])

    def __contains__(self, key):
        return key in self._entities

    def add(self, entity: GameObject):
        """
        Add an Entity to the group and ensure that the group is referenced
        in the entity's groups attribute.

        Args:
            entity (Entity): The entity to be added to the group.
        """
        if not isinstance(entity, GameObject):
            raise ValueError("Only Entity objects may be added to an EntityGroup")
        if entity not in self._entities:
            self._entities.append(entity)
            if self not in entity.groups:
                entity.add_group(self)
        else:
            print("Entity already in group")

    def remove(self, entity: GameObject):
        """
        Remove an Entity from the group and ensure that the group is no longer
        referenced in the entity's groups attribute.

        Args:
            entity (Entity): The entity to be removed to the group.
        """
        if entity not in self._entities:
            print("Entity not in group")
        else:
            if self in entity.groups:
                entity.remove_group(self)
            self._entities.remove(entity)

    def add_entities(self, entities):
        """
        Iterates through a list of Entities and adds them to the group.

        Args:
            entities (list): List of entities to be added to the group.
        """
        for entity in entities:
            self.add(entity)


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
        collisions = self.scene.get_AABB_collisions(self)
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
