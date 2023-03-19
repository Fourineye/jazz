"""
Module to provide a base for active game entities.
"""

from random import randint

import pygame

from Jazz.baseObject import GameObject
from Jazz.colliders import (
    CircleCollider,
    Collider,
    PolyCollider,
    RayCollider,
    RectCollider,
)
from Jazz.input_handler import InputHandler
from Jazz.utils import Vec2, direction_to, dist_to, load_image


class Entity(GameObject):
    """Basic active object in the game space"""

    def __init__(self, pos: Vec2, name="Entity", **kwargs):
        GameObject.__init__(self, pos, name, **kwargs)
        collider_type = kwargs.get("collider", "Rectangle")
        self.static = kwargs.get("static", True)

        self._color = kwargs.get("color", (255, 0, 255))

        if collider_type == "Circle":
            radius = kwargs.get("radius", 1)
            self.collider = CircleCollider(pos, radius)
        elif collider_type == "Rectangle":
            size = kwargs.get("size", (2, 2))
            self.collider = RectCollider(pos, size[0], size[1])
        elif collider_type == "Polygon":
            vertices = kwargs.get("vertices", [(-3, -2), (3, -2), (0, 4)])
            self.collider = PolyCollider(pos, vertices)

        temp_source = pygame.Surface(self.collider.size)
        temp_source.fill((255, 0, 255))
        temp_source.set_colorkey((255, 0, 255))
        self.asset = kwargs.get("asset", None)

        if self.asset is None:
            self.collider.color = self._color
            self.collider.draw(temp_source, -(self.pos) + self.collider.size / 2)
            self.source = temp_source
        else:
            if isinstance(self.asset, pygame.Surface):
                self.source = self.asset
            else:
                self.source = load_image(self.asset)

    def _draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        surface.blit(self.image, self.draw_pos + Vec2(offset))

    def debug_draw(self, surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        self.collider.debug_draw(surface, offset)

    def collide_sat(self, collider):
        """
        Checks collision with an object.

        Args:
            collider (GameObject): The object to check.

        Returns:
            bool: Whether the Entity collides with the rect.
        """
        if isinstance(collider, Entity):
            if self.collider.collide_rect(collider.collider):
                return self.collider.collide_sat(collider.collider)
            else:
                return False, False
        elif isinstance(collider, Collider):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(collider)
            else:
                return False, False
        elif isinstance(collider, pygame.Rect):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(
                    RectCollider(collider.center, collider.w, collider.h)
                )
            else:
                return False, False
        else:
            raise ValueError(f"Invalid Collider: {collider}")

    def collide_rect(self, collider):
        if isinstance(collider, Entity):
            if self.collider.collide_rect(collider.collider):
                return True
            else:
                return False
        elif isinstance(collider, Collider):
            if self.collider.collide_rect(collider):
                return True
            else:
                return False
        elif isinstance(collider, pygame.Rect):
            if self.collider.collide_rect(collider):
                return True
            else:
                return False
        else:
            print("Invalid Collider:", collider)

    def move(self, direction: Vec2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vec2): The vector to move along.
        """
        self.pos = self.pos + direction

    def rotate(self, degrees):
        self._facing.rotate_ip(degrees)
        self.collider.rotate(degrees)
        self.image = pygame.transform.rotate(self.source, self._facing.angle_to((1, 0)))
        self._draw_offset = -Vec2(
            self.image.get_width() / 2, self.image.get_height() / 2
        )

    # Properties

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vec2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vec2(new_offset)

    @property
    def rect(self):
        if isinstance(self.collider, pygame.Rect):
            return self.collider
        elif isinstance(self.collider, Collider):
            return self.collider.rect

    @property
    def top(self):
        return self.collider.top

    @property
    def right(self):
        return self.collider.right

    @property
    def bottom(self):
        return self.collider.bottom

    @property
    def left(self):
        return self.collider.left

    @property
    def center(self):
        return self.collider.center

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        if not isinstance(new_source, pygame.Surface):
            new_source = load_image(new_source)
        self._source = new_source
        if self._facing.angle_to((1, 0)) != 0:
            self.image = pygame.transform.rotate(
                self.source, self._facing.angle_to((1, 0))
            )
        else:
            self.image = self.source.copy()

        self._draw_offset = -Vec2(
            self.image.get_width() / 2, self.image.get_height() / 2
        )


class KinematicEntity(Entity):
    """A Entity that is intended to be moved with code."""

    def __init__(self, pos: Vec2, name="KinematicEntity", **kwargs):
        Entity.__init__(self, pos, name, **kwargs)
        self.static = kwargs.get("static", False)
        collision_groups = kwargs.get("collision_groups", None)
        if collision_groups is None:
            self._collision_groups = []
        elif not isinstance(collision_groups, list):
            self._collision_groups = [collision_groups]
        else:
            self._collision_groups = collision_groups

    def add_collision_group(self, group):
        """
        Adds a group to the Entities collision groups attribute.

        Args:
            group (EntityGroup): The group to add.
        """
        self._collision_groups.append(group)

    def move(self, direction: Vec2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vec2): The vector to move along.
        """
        self.pos = self.pos + direction

    def move_and_collide(self, direction: Vec2, collision_group=None, callback=None):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vec2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        self.pos = self.pos + direction
        collisions = []
        if collision_group is None:
            for group in self._collision_groups:
                collisions += group.collide_object(self)
        else:
            collisions = collision_group.collide_object(self)

        if collisions:
            collisions.sort(key=lambda obj: dist_to(self.pos, obj.pos))
            for entity in collisions:
                depth, normal = self.collide_sat(entity)
                if depth != 0:
                    if callable(callback):
                        callback(entity)
                    if not self.static and not entity.static:
                        self.move(-normal * (depth + 1) / 2)
                        entity.move_and_collide(normal * (depth + 1) / 2)
                    elif self.static and not entity.static:
                        entity.move_and_collide(normal * (depth + 1))
                    elif entity.static:
                        self.move(-normal * (depth + 1))


class EntityGroup:
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

    def collide_object(self, collider: Entity, do_kill=False):
        """
        Checks an Entity for collision with all Entities in group.

        Args:
            collider (Entity): Entity to check collision with.
            do_kill (bool, optional): Whether Entities that collide with the collider are
                removed from the group. Defaults to False.

        Returns:
            list: List of all Entities that collide with the collider.
        """
        collisions = []
        for entity in self._entities:
            if entity is not collider:
                if isinstance(collider, pygame.Rect):
                    collision = entity.collide_rect(collider)
                else:
                    collision = collider.collide_rect(entity)
                if collision:
                    collisions.append(entity)
                    if do_kill:
                        self.remove(entity)
                        entity.remove_group(self)
        return collisions

    def collide_ray(self, ray):
        collisions = []
        for entity in self._entities:
            if entity is not ray:
                collision = ray.collider.collide_ray(entity)
                if collision is not None:
                    collisions.append((entity, collision))
        return collisions


class Ray(Entity):
    def __init__(self, pos, name, **kwargs):
        super().__init__(pos, name, **kwargs)
        self._length = kwargs.get("length", 1)
        self.collider = RayCollider(self.pos, self.length)
        initial_facing = kwargs.get("initial_facing", None)
        if initial_facing is not None:
            self.facing = initial_facing
        collision_groups = kwargs.get("collision_groups", None)
        if collision_groups is None:
            self._collision_groups = []
        elif not isinstance(collision_groups, list):
            self._collision_groups = [collision_groups]
        else:
            self._collision_groups = collision_groups
        self._color = kwargs.get("color", (255, 0, 255))

    def _draw(self, surface, offset=None):
        pass

    def debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vec2
        self.collider.debug_draw(surface, offset)

    def collide_sat(self, collider):
        """
        Checks collision with an object.

        Args:
            collider (GameObject): The object to check.

        Returns:
            bool: Whether the Entity collides with the rect.
        """
        if isinstance(collider, Entity):
            if self.collider.collide_rect(collider.collider):
                return self.collider.collide_sat(collider.collider)
            else:
                return False, False
        elif isinstance(collider, Collider):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(collider)
            else:
                return False, False
        elif isinstance(collider, pygame.Rect):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(
                    RectCollider(collider.center, collider.w, collider.h)
                )
            else:
                return False, False
        else:
            raise ValueError(f"Invalid Collider: {collider}")

    def collide_rect(self, collider):
        if isinstance(collider, Entity):
            if self.collider.collide_rect(collider.collider):
                return True
            else:
                return False
        elif isinstance(collider, Collider):
            if self.collider.collide_rect(collider):
                return True
            else:
                return False
        elif isinstance(collider, pygame.Rect):
            if self.collider.collide_rect(collider):
                return True
            else:
                return False
        else:
            print("Invalid Collider:", collider)

    def move(self, direction: Vec2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vec2): The vector to move along.
        """
        self.pos = self.pos + direction

    def rotate(self, degrees):
        self._facing.rotate_ip(degrees)
        self.collider.rotate(degrees)

    def look_at(self, target):
        if isinstance(target, tuple):
            self.facing = direction_to(self.pos, target)
        elif isinstance(target, GameObject):
            self.facing = direction_to(self.pos, target.pos)

    def cast(self, collision_group=None):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vec2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        collisions = []
        if collision_group is None:
            for group in self._collision_groups:
                collisions += group.collide_ray(self)
        else:
            collisions = collision_group.collide_ray(self)

        if collisions:
            closest_collision = (None, Vec2(self.global_end))
            collisions.sort(key=lambda collision: dist_to(self.pos, collision[1]))
            for entity, point in collisions:
                if self.length**2 >= dist_to(self.pos, point) >= 0:
                    if dist_to(self.pos, point) < dist_to(
                        self.pos, closest_collision[1]
                    ):
                        closest_collision = (entity, point)

            if closest_collision[1] != Vec2(self.global_end):
                return closest_collision
        return None

    # Properties

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vec2(self._pos)

    @pos.setter
    def pos(self, pos: Vec2):
        """Sets the _pos attribute and moves the collider to the new pos."""
        self._pos = Vec2(pos)
        self.collider.pos = Vec2(pos)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length
        self.collider.length = length

    @property
    def global_end(self):
        return Vec2(self.pos + self.facing * self.length)

    @property
    def local_end(self):
        return Vec2(self.facing * self.length)

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vec2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vec2(new_offset)

    @property
    def rect(self):
        if isinstance(self.collider, pygame.Rect):
            return self.collider
        elif isinstance(self.collider, Collider):
            return self.collider.rect

    @property
    def top(self):
        return self.collider.top

    @property
    def right(self):
        return self.collider.right

    @property
    def bottom(self):
        return self.collider.bottom

    @property
    def left(self):
        return self.collider.left

    @property
    def center(self):
        return self.collider.center
