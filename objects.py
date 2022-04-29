"""
Module to provide a base for active game entities.
"""

from random import randint

import pygame
from pygame import Vector2

from pygame_engine.colliders import (CircleCollider, Collider, PolyCollider,
                                     RectCollider)
from pygame_engine.input_handler import InputHandler
from pygame_engine.utils import dist_to, load_image


class GameObject:
    """Simplest object in pygame_engine"""

    def __init__(self, pos: Vector2, name="Object", final=True, **kwargs):
        # Engine Attributes
        self.name = name
        self.scene = None
        self.root = None

        # Engine flags
        self.pause_process = kwargs.get("pause_process", False)
        self.game_process = kwargs.get("game_process", True)
        self.game_input = kwargs.get("game_input", True)
        self.do_kill = False

        # Rendering flags
        self.visible = kwargs.get("visible", True)
        self.background_layer = kwargs.get("background_layer", False)
        self.screen_layer = kwargs.get("screen_layer", False)

        # Basic positional Attributes
        self._pos = Vector2(pos)
        self._facing = Vector2(1, 0)
        self._z = kwargs.get("z", 0)
        self._color = kwargs.get("color", (255, 255, 255))
        if final:
            self.on_init(**kwargs)

    def __repr__(self):
        return f"{self.name} at {self.x}, {self.y}"

    def on_init(self, **kwargs):
        """
        Method called on creation, for user to add custom attributes.
        """

    def input(self, INPUT: InputHandler):
        """
        Method called once per frame to handle user input. Called before process.

        Args:
            INPUT (InputHandler): InputHandler passed from the main game instance.
        """

    def process(self, delta: float):
        """
        Method called once per frame to handle game logic. Called before draw.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vector2()
        pygame.draw.circle(surface, self._color, self.pos + offset, 10)

    def collide(self, collider):
        """Checks if the object is in an AABB.

        Args:
            collider (GameObject): The rect to check.

        Returns:
            bool: Whether the object is in the rect.
        """
        rect = collider.collider
        return (
            self.x > rect.left
            and self.x < rect.right
            and self.y > rect.top
            and self.y < rect.bottom
        )

    def rotate(self, degrees):
        self.facing.rotate_ip(degrees)

    def rotate_around(self, degrees, center):
        center = Vector2(center)
        arm = self.pos - center
        arm.rotate_ip(degrees)
        self.pos = center + arm
        self.rotate(degrees)

    def set_rotation(self, degrees):
        angle = self._facing.angle_to(Vector2(1, 0).rotate(degrees))
        self.rotate(angle)

    # Properties

    @property
    def pos(self):
        """Returns _pos attribute."""
        return self._pos

    @pos.setter
    def pos(self, pos):
        """Sets the _pos attribute"""
        self._pos = Vector2(pos)

    @property
    def y(self):
        """Returns y component of the _pos attribute."""
        return self._pos.y

    @y.setter
    def y(self, y):
        """Sets y component of the _pos attribute."""
        self.pos = Vector2(self._pos.x, y)

    @property
    def x(self):
        """Returns x component of the _pos attribute."""
        return self._pos.x

    @x.setter
    def x(self, x):
        """Sets x component of the _pos attribute."""
        self.pos = Vector2(x, self._pos.y)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, 1, 1)

    @property
    def top(self):
        return self.rect.top

    @property
    def right(self):
        return self.rect.right

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def left(self):
        return self.rect.left

    @property
    def center(self):
        return self.rect.center

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, new_facing):
        angle = new_facing.angle_to(Vector2(1, 0))
        self.set_rotation(angle)


class Entity(GameObject):
    """Basic active object in the game space"""

    def __init__(self, pos: Vector2, name="Entity", final=True, **kwargs):
        GameObject.__init__(self, pos, name, False, **kwargs)
        collider_type = kwargs.get("collider", "Rectangle")
        self.static = kwargs.get("static", True)

        self.groups = kwargs.get("groups", [])
        for group in self.groups:
            if self not in group._entities:
                group.add(self)

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
            self.collider.recenter()

        self.source = pygame.Surface(self.collider.size)
        self.source.fill((255, 0, 255))
        self.source.set_colorkey((255, 0, 255))
        self.asset = kwargs.get("asset", None)

        if self.asset is None:
            self.collider.color = self._color
            self.collider.draw(self.source, -(self.pos) + self.collider.size / 2)
        else:
            if isinstance(self.asset, list):
                self.frame = 0
                self.frames = []
                for frame in self.asset:
                    if isinstance(frame, pygame.Surface):
                        self.frames.append(frame)
                    else:
                        self.frames.append(load_image(frame))
                self.source = self.frames[self.frame]
            if isinstance(self.asset, pygame.Surface):
                self.source = self.asset
            else:
                self.source = load_image(self.asset)

        self.image = self.source.copy()
        # self.old_collider = self.collider.copy()
        self._draw_offset = Vector2(
            -self.image.get_width() / 2, -self.image.get_height() / 2
        )
        if final:
            self.on_init(**kwargs)

    def draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vector2()
        surface.blit(self.image, self.draw_pos + Vector2(offset))

    def debug_draw(self, surface, offset):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vector2()
        self.collider.debug_draw(surface, offset)

    def add_group(self, group):
        """
        Add Group to Entity and insure that Entity is in Group.

        Args:
            group (EntityGroup): The EntityGroup to add.
        """
        self.groups.append(group)
        if self not in group:
            group.add(self)

    def remove_group(self, group):
        """
        Remove group from Entity and insure that Entity is not in Group.

        Args:
            group (EntityGroup): The EntityGroup to remove.
        """
        if group not in self.groups:
            print("group not found")
        else:
            self.groups.remove(group)
            if self in group:
                group.remove(self)

    def kill(self):
        """Removes the Entity from all groups and queues it for deletion."""
        for group in self.groups[::-1]:
            self.remove_group(group)
        self.game_process = False
        self.pause_process = False
        self.game_input = False
        self.do_kill = True

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
                return False
        elif isinstance(collider, Collider):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(collider)
            else:
                return False
        elif isinstance(collider, pygame.Rect):
            if self.collider.collide_rect(collider):
                return self.collider.collide_sat(
                    RectCollider(collider.center, collider.w, collider.h)
                )
            else:
                return False
        else:
            print("Invalid Collider:", collider)

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

    def move(self, direction: Vector2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vector2): The vector to move along.
        """
        self.pos = self.pos + direction

    def rotate(self, degrees):
        self._facing.rotate_ip(degrees)
        self.collider.rotate(-degrees)
        self.image = pygame.transform.rotate(
            self.source, -self._facing.angle_to((1, 0))
        )
        self._draw_offset = -Vector2(
            self.image.get_width() / 2, self.image.get_height() / 2
        )

    # Properties

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vector2(self._pos)

    @pos.setter
    def pos(self, pos: Vector2):
        """Sets the _pos attribute and moves the collider to the new pos."""
        self._pos = Vector2(pos)
        self.collider.pos = Vector2(pos)

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vector2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vector2(new_offset)

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


class KinematicEntity(Entity):
    """A Entity that is intended to be moved with code."""

    def __init__(self, pos: Vector2, name="KinematicEntity", final=True, **kwargs):
        Entity.__init__(self, pos, name, False, **kwargs)
        self.static = kwargs.get("static", False)
        collision_groups = kwargs.get("collision_groups", None)
        if collision_groups is None:
            self._collision_groups = []
        elif not isinstance(collision_groups, list):
            self._collision_groups = [collision_groups]
        else:
            self._collision_groups = collision_groups
        if final:
            self.on_init(**kwargs)

    def add_collision_group(self, group):
        """
        Adds a group to the Entities collision groups attribute.

        Args:
            group (EntityGroup): The group to add.
        """
        self._collision_groups.append(group)

    def move(self, direction: Vector2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vector2): The vector to move along.
        """
        self.pos = self.pos + direction

    def move_and_collide(self, direction: Vector2, collision_group=None):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vector2): The vector to move along.
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

    def add(self, entity: Entity):
        """
        Add an Entity to the group and ensure that the group is referenced
        in the entity's groups attribute.

        Args:
            entity (Entity): The entity to be added to the group.
        """
        if not isinstance(entity, Entity):
            raise ValueError("Only Entity objects may be added to an EntityGroup")
        if entity not in self._entities:
            self._entities.append(entity)
            if self not in entity.groups:
                entity.add_group(self)
        else:
            print("Entity already in group")

    def remove(self, entity: Entity):
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


class KinematicEntityDefunct(Entity):
    """A Entity that is intended to be moved with code."""

    def __init__(self, pos: Vector2, name="KinematicEntity", final=True, **kwargs):
        Entity.__init__(self, pos, name, False, **kwargs)
        collision_groups = kwargs.get("collision_groups", None)
        if collision_groups is None:
            self._collision_groups = []
        elif not isinstance(collision_groups, list):
            self._collision_groups = [collision_groups]
        else:
            self._collision_groups = collision_groups
        if final:
            self.on_init(**kwargs)

    def add_collision_group(self, group):
        """
        Adds a group to the Entities collision groups attribute.

        Args:
            group (EntityGroup): The group to add.
        """
        self._collision_groups.append(group)

    def move(self, direction: Vector2):
        """
        A function to move the Entity and store the previous position.

        Args:
            direction (Vector2): The vector to move along.
        """
        self.old_collider = self.collider.copy()
        self.pos = self.pos + direction

    def move_and_collide(self, direction: Vector2, collision_group=None):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vector2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        self.collider = self.collider.copy()
        self.pos = self.pos + direction
        collisions = []
        if collision_group is None:
            for group in self._collision_groups:
                collisions += group.collide_object(self)
        else:
            collisions = collision_group.collide_entity(self)

        if collisions:
            shortest_time = 1
            actual_move = Vector2(self.old_pos)
            new_direction = Vector2()
            for entity in collisions:
                dx, dy = 0, 0
                if self.old_collider.left <= entity.collider.left:
                    dx = entity.collider.left - self.old_collider.right
                elif self.old_collider.left > entity.collider.left:
                    dx = self.old_collider.left - entity.collider.right

                if self.old_collider.top <= entity.collider.top:
                    dy = entity.collider.top - self.old_collider.bottom
                elif self.old_collider.top > entity.collider.top:
                    dy = self.old_collider.top - entity.collider.bottom

                x_time, y_time = 0, 0

                if direction.x != 0:
                    x_time = abs(dx / direction.x)
                if direction.y != 0:
                    y_time = abs(dy / direction.y)

                if direction.x != 0 and direction.y == 0:
                    shortest_time = min(x_time, shortest_time)
                    new_direction.x = direction.x * shortest_time
                elif direction.y != 0 and direction.x == 0:
                    shortest_time = min(y_time, shortest_time)
                    new_direction.y = direction.y * shortest_time
                else:
                    shortest_time = min(x_time, y_time, shortest_time)
                    new_direction.x = direction.x * shortest_time
                    new_direction.y = direction.y * shortest_time

            actual_move += new_direction
            self.pos = Vector2(actual_move)

    def move_and_slide(self, direction: Vector2, collision_group=None):
        """
        A function to move the Entity checking for collsions, sliding along any collisions.

        Args:
            direction (Vector2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        self.old_collider = self.collider.copy()
        self.pos = self.pos + direction
        collisions = []

        if collision_group is None:
            for layer in self._collision_groups:
                collisions += layer.collide_entity(self)
        else:
            collisions = collision_group.collide_entity(self)

        if collisions:
            shortest_time = 1
            actual_move = Vector2(self.old_pos)
            new_direction = Vector2()
            next_dir = Vector2()
            vertical_wall, horizontal_wall = False, False
            for entity in collisions:
                dx, dy = 0, 0
                if self.old_collider.left <= entity.collider.left:
                    dx = entity.collider.left - self.old_collider.right
                elif self.old_collider.left > entity.collider.left:
                    dx = self.old_collider.left - entity.collider.right

                if self.old_collider.top <= entity.collider.top:
                    dy = entity.collider.top - self.old_collider.bottom
                elif self.old_collider.top > entity.collider.top:
                    dy = self.old_collider.top - entity.collider.bottom

                x_time, y_time = 0, 0

                if direction.x != 0:
                    x_time = abs(dx / direction.x)
                if direction.y != 0:
                    y_time = abs(dy / direction.y)

                if direction.x != 0 and direction.y == 0:
                    shortest_time = min(x_time, shortest_time)
                    new_direction.x = direction.x * shortest_time
                elif direction.y != 0 and direction.x == 0:
                    shortest_time = min(y_time, shortest_time)
                    new_direction.y = direction.y * shortest_time
                else:
                    shortest_time = min(x_time, y_time, shortest_time)
                    new_direction.x = direction.x * shortest_time
                    new_direction.y = direction.y * shortest_time
                    if x_time < y_time:
                        vertical_wall = True
                    if y_time < x_time:
                        horizontal_wall = True

            if vertical_wall:
                next_dir.y = direction.y * (1 - shortest_time)
            if horizontal_wall:
                next_dir.x = direction.x * (1 - shortest_time)
            actual_move += new_direction
            self.pos = Vector2(actual_move)
            if next_dir.magnitude() != 0:
                self.move_and_collide(next_dir, collision_group)

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vector2(self._pos)

    @pos.setter
    def pos(self, pos: Vector2):
        self.old_pos = Vector2(self.pos)
        self._pos = Vector2(pos)
        self.collider.center = Vector2(pos)
