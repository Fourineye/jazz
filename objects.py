"""
Module to provide a base for active game entities.
"""

from random import randint

import pygame
from pygame import Vector2

from pygame_engine.input_handler import InputHandler
from pygame_engine.utils import dist_to, load_image


class ComplexCollider:
    def __init__(self, pos, vertices):
        self.screen_layer = True
        self._initial_vertices = vertices
        self.vertices = []
        self.max_radius = 0
        self._left = vertices[0][0]
        self._right = vertices[0][0]
        self._top = vertices[0][1]
        self._bottom = vertices[0][1]
        self._center = Vector2()

        for vert in vertices:
            vert = Vector2(vert)
            self._center += vert
            self.vertices.append(vert)
            self.max_radius = max(self.max_radius, vert.magnitude())
            self._left = min(self._left, vert.x)
            self._right = max(self._right, vert.x)
            self._top = min(self._top, vert.y)
            self._bottom = max(self._bottom, vert.y)
        self.size = len(vertices)
        self._center /= self.size
        self.edges = []
        for i in range(self.size):
            j = (i + 1) % self.size
            self.edges.append([self.vertices[i], self.vertices[j]])
        self.normals = []
        for edge in self.edges:
            self.normals.append(Vector2(edge[1] - edge[0]).normalize().rotate(90))
        self.pos = Vector2(pos)
        self.color = "green"

    def move(self, direction):
        self.pos += Vector2(direction)

    def rotate(self, degrees):
        self._left = self._center.x
        self._right = self._center.x
        self._top = self._center.y
        self._bottom = self._center.y
        self._center = Vector2()
        for vert in self.vertices:
            vert.rotate_ip(degrees)
            self._center += vert
            self._left = min(self._left, vert.x)
            self._right = max(self._right, vert.x)
            self._top = min(self._top, vert.y)
            self._bottom = max(self._bottom, vert.y)
        self._center /= self.size
        self.normals = []
        for edge in self.edges:
            self.normals.append(Vector2(edge[1] - edge[0]).normalize().rotate(90))

    def rotate_around(self, degrees, center):
        center = Vector2(center)
        arm = self.pos - center
        arm.rotate_ip(degrees)
        self.pos = center + arm
        self.rotate(degrees)

    def set_rotation(self, degrees):
        self.vertices = []
        for vert in self._initial_vertices:
            vert = Vector2(vert)
            self.vertices.append(vert)
        self.edges = []
        for i in range(self.size):
            j = (i + 1) % self.size
            self.edges.append([self.vertices[i], self.vertices[j]])
        self.rotate(degrees)

    def draw(self, surface, offset=None):
        if offset is None:
            offset = Vector2()
        for edge in self.edges:
            pygame.draw.aaline(
                surface,
                self.color,
                self.pos + edge[0] + offset,
                self.pos + edge[1] + offset,
            )

    def debug_draw(self, surface, offset=None):
        for i, edge in enumerate(self.edges):
            start = edge[0] + (edge[1] - edge[0]) / 2
            end = start + self.normals[i] * 10
            pygame.draw.aaline(
                surface, "red", self.pos + start + offset, self.pos + end + offset
            )
        pygame.draw.aaline(
            surface,
            "red",
            self.pos,
            self.pos + (self.edges[-1][1] - self.edges[-1][0]) / 2,
        )
        for vert in self.vertices:
            pygame.draw.circle(surface, "gray", self.pos + vert + offset, 3)
        pygame.draw.circle(surface, self.color, self.pos + offset, 5)
        pygame.draw.circle(surface, "red", self.pos + self._center + offset, 3)
        pygame.draw.rect(surface, "yellow", self.rect, 2)

    def project(self, axis):
        min_v, max_v = None, None
        for vert in self.vertices:
            proj = (self.pos + vert).dot(axis)
            if min_v is None:
                min_v = proj
                max_v = proj
            if proj < min_v:
                min_v = proj
            if proj > max_v:
                max_v = proj
        return min_v, max_v

    def collide_sat(self, collider):
        if isinstance(collider, pygame.Rect):
            temp_rect = pygame.Rect(collider)
            collider = ComplexCollider(
                temp_rect.topleft,
                [
                    temp_rect.topleft,
                    temp_rect.topright,
                    temp_rect.bottomright,
                    temp_rect.bottomleft,
                ],
            )

        axes = self.normals + collider.normals
        depth = 1000000.0
        normal = Vector2()
        for axis in axes:
            p1 = self.project(axis)
            p2 = collider.project(axis)
            if p1[1] < p2[0] or p2[1] < p1[0]:
                return False
            axis_depth = min(p2[1] - p1[0], p1[1] - p2[0])
            if axis_depth < depth:
                depth = axis_depth
                normal = axis
        return depth, normal

    def collide_circle(self, collider):
        return dist_to(self.center, collider.center) <= self.max_radius + collider.max_radius

    def collide_rect(self, collider):
        return (
            self.top < collider.bottom
            and self.bottom > collider.top
            and self.left < collider.right
            and self.right > collider.left
        )

    @property
    def top(self):
        return self.pos.y + self._top

    @property
    def right(self):
        return self.pos.x + self._right

    @property
    def bottom(self):
        return self.pos.y + self._bottom

    @property
    def left(self):
        return self.pos.x + self._left

    @property
    def center(self):
        return self.pos + self._center

    @property
    def rect(self):
        return pygame.Rect(
            self.left, self.top, self.right - self.left, self.bottom - self.top
        )


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
        self._pos = pos
        self._z = kwargs.get("z", 0)
        self.color = kwargs.get("color", (255, 255, 255))
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
        pygame.draw.circle(surface, self.color, self.pos + offset, 10)

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


class Entity(GameObject):
    """Basic active object in the game space"""

    def __init__(self, pos: Vector2, name="Entity", final=True, **kwargs):
        GameObject.__init__(self, pos, name, False, **kwargs)

        self.groups = kwargs.get("groups", [])
        for group in self.groups:
            if self not in group._entities:
                group.add(self)

        self.color = kwargs.get("color", (255, 0, 255))

        asset = kwargs.get("asset", None)
        size = kwargs.get("size", None)
        if asset is None and size is None:
            raise Exception("Entity must have either a texture or a size")

        if asset is None and (isinstance(size, (Vector2, tuple))):
            self.image = pygame.Surface(size)
            self.image.fill(self.color)
        elif size is None:
            if isinstance(asset, list):
                self.frame = 0
                self.frames = []
                for frame in asset:
                    if isinstance(frame, pygame.Surface):
                        self.frames.append(frame)
                    else:
                        self.frames.append(load_image(frame))
                self.image = self.frames[self.frame]
            if isinstance(asset, pygame.Surface):
                self.image = asset
            else:
                self.image = load_image(asset)

        self.rect = self.image.get_rect(center=self._pos)
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
        pygame.draw.rect(
            surface, "red", (self.rect.topleft + offset, self.rect.size), width=1
        )

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

    # Properties

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vector2(self._pos)

    @pos.setter
    def pos(self, pos: Vector2):
        """Sets the _pos attribute and moves the rect to the new pos."""
        self._pos = Vector2(pos)
        self.rect.center = Vector2(pos)

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vector2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vector2(new_offset)


class KinematicEntity(Entity):
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
        self.old_rect = self.rect.copy()
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
        self.old_rect = self.rect.copy()
        self.pos = self.pos + direction

    def move_and_collide(self, direction: Vector2, collision_group=None):
        """
        A function to move the Entity and check for collisions, stopping if one is found.

        Args:
            direction (Vector2): The vector to move along.
            collision_group (EntityGroup, optional): An optional group to check collisions against,
                if left blank it will default to the Entity's collision_groups. Defaults to None.
        """
        self.old_rect = self.rect.copy()
        self.pos = self.pos + direction
        collisions = []
        if collision_group is None:
            for group in self._collision_groups:
                collisions += group.collide_entity(self)
        else:
            collisions = collision_group.collide_entity(self)

        if collisions:
            shortest_time = 1
            actual_move = Vector2(self.old_pos)
            new_direction = Vector2()
            for entity in collisions:
                dx, dy = 0, 0
                if self.old_rect.left <= entity.rect.left:
                    dx = entity.rect.left - self.old_rect.right
                elif self.old_rect.left > entity.rect.left:
                    dx = self.old_rect.left - entity.rect.right

                if self.old_rect.top <= entity.rect.top:
                    dy = entity.rect.top - self.old_rect.bottom
                elif self.old_rect.top > entity.rect.top:
                    dy = self.old_rect.top - entity.rect.bottom

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
        self.old_rect = self.rect.copy()
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
                if self.old_rect.left <= entity.rect.left:
                    dx = entity.rect.left - self.old_rect.right
                elif self.old_rect.left > entity.rect.left:
                    dx = self.old_rect.left - entity.rect.right

                if self.old_rect.top <= entity.rect.top:
                    dy = entity.rect.top - self.old_rect.bottom
                elif self.old_rect.top > entity.rect.top:
                    dy = self.old_rect.top - entity.rect.bottom

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
        self.rect.center = Vector2(pos)


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

    def collide_entity(self, collider: Entity, do_kill=False):
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
                if collider.rect.colliderect(entity.rect):
                    collisions.append(entity)
                    if do_kill:
                        self.remove(entity)
                        entity.remove_group(self)
        return collisions

    def collide_rect(self, collider: pygame.Rect, do_kill=False):
        """
        Checks a Rect for collision with all Entities in group.

        Args:
            collider (pygame.Rect): Rect to check collision with.
            do_kill (bool, optional): Whether Entities that collide with the collider are
                removed from the group. Defaults to False.

        Returns:
            list: List of all Entities that collide with the collider.
        """
        collisions = []
        for entity in self._entities:
            if entity.rect is not collider:
                if collider.colliderect(entity.rect):
                    collisions.append(entity)
                    if do_kill:
                        self.remove(entity)
                        entity.remove_group(self)
        return collisions


class Particle:
    """Basic Particle class, intended to be extended."""

    def __init__(
        self,
        pos: Vector2,
        vel: Vector2,
        life: float,
        color=(255, 255, 255),
    ):
        self._pos = pos
        self._vel = vel
        self._acc = Vector2(0, 100)
        self._life = life
        self.color = color

    def draw(self, surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vector2()
        pygame.draw.circle(
            surface, self.color, self._pos + Vector2(offset), int(self._life * 5)
        )

    def process(self, delta: float):
        """
        Method called once per frame to handle game logic. Called before render.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        self._pos += self._vel * delta
        self._vel += self._acc * delta
        self._life -= delta
        if self._life <= 0:
            return True
        return False


class ParticleEmitter(GameObject):
    """An object that handles particles"""

    def __init__(
        self, pos: Vector2, name="ParticleEmitter", active=False, rate=1, **kwargs
    ):
        GameObject.__init__(self, pos, name)
        self._pos = pos
        self._particles = []
        self.active = active
        self.rate = rate

    def emit_particles(self, num: int):
        """
        Creates particles at the current position.

        Args:
            num (int): The number of particles to create.
        """
        for _ in range(num):
            self._particles.append(
                Particle(
                    Vector2(self._pos),
                    Vector2(randint(25, 100), 0).rotate(randint(0, 365)),
                    2,
                    self.color,
                )
            )

    def draw(self, surface, offset=None):
        """
        Called once per frame, draws all particles currently in the object.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        for particle in self._particles:
            particle.draw(surface, offset)

    def process(self, delta: float):
        """
        Called once per frame, updates all Particle objects currently in the object.

        Args:
            delta (float): Time in seconds since last frame.
        """
        if self.active:
            self.emit_particles(self.rate)
        for particle in self._particles[::-1]:
            if particle.process(delta):
                del particle

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vector2(self._pos)

    @pos.setter
    def pos(self, pos: Vector2):
        """Sets _pos attribute."""
        self._pos = Vector2(pos)
