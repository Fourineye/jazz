import pygame

from Jazz.baseObject import GameObject
from Jazz.utils import (Vec2, direction_to, dist_to, line_circle,
                        line_intersection)


class Collider(GameObject):
    def __init__(self, **kwargs):
        super().__init__("collider", **kwargs)
        self.collider_type = None
        if not hasattr(self, "vertices"):
            self.vertices = [Vec2(0, 0)]
        self.edges = []
        self.normals = []
        if not hasattr(self, "radius"):
            self.radius = 0
        self.color = "white"

        self._facing = Vec2(1, 0)
        self._left = 0
        self._right = 0
        self._top = 0
        self._bottom = 0
        self._center = Vec2()

        self._size = len(self.vertices)
        if self._size > 1:
            for i, vert in enumerate(self.vertices):
                vert = Vec2(vert)
                self._center += vert
                self.vertices[i] = vert
                self.radius = max(self.radius, vert.magnitude())
                self._left = min(self._left, vert.x)
                self._right = max(self._right, vert.x)
                self._top = min(self._top, vert.y)
                self._bottom = max(self._bottom, vert.y)
            self._center /= self._size
            if self._size > 2:
                for i in range(self._size):
                    j = (i + 1) % self._size
                    self.edges.append([self.vertices[i], self.vertices[j]])
            else:
                self.edges.append([self.vertices[0], self.vertices[1]])
            for edge in self.edges:
                new = True
                new_normal = Vec2(edge[1] - edge[0]).normalize().rotate(90)
                for normal in self.normals:
                    if abs(new_normal.dot(normal)) == 1:
                        new = False
                        break
                if new:
                    self.normals.append(Vec2(edge[1] - edge[0]).normalize().rotate(90))
        else:
            self._left = -self.radius
            self._right = self.radius
            self._top = -self.radius
            self._bottom = self.radius

    def _debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vec2()
        for edge in self.edges:
            pygame.draw.aaline(
                surface,
                self.color,
                self.pos + edge[0] + offset,
                self.pos + edge[1] + offset,
            )
        pygame.draw.aaline(
            surface,
            "red",
            self.center + offset,
            self.center + self.facing * 5 + offset,
        )
        for vert in self.vertices:
            pygame.draw.circle(surface, "gray", self.pos + vert + offset, 2, 1)
        pygame.draw.circle(surface, "red", self.pos + offset, 2, 1)
        pygame.draw.circle(surface, "gray", self.pos + self._center + offset, 2, 1)
        pygame.draw.rect(
            surface,
            "yellow",
            pygame.Rect(
                self.rect.topleft + offset,
                Vec2(self.size[0], self.size[1]),
            ),
            1,
        )

    def rotate(self, degrees):
        self._facing.rotate_ip(degrees)
        self._left = 0
        self._right = 0
        self._top = 0
        self._bottom = 0
        self._center = Vec2()
        for vert in self.vertices:
            vert.rotate_ip(degrees)
            self._center += vert
            self._left = min(self._left, vert.x)
            self._right = max(self._right, vert.x)
            self._top = min(self._top, vert.y)
            self._bottom = max(self._bottom, vert.y)
        self._center /= self._size
        self.normals = []
        if self.edges:
            for edge in self.edges:
                new = True
                new_normal = Vec2(edge[1] - edge[0]).normalize().rotate(90)
                for normal in self.normals:
                    if abs(new_normal.dot(normal)) == 1:
                        new = False
                        break
                if new:
                    self.normals.append(Vec2(edge[1] - edge[0]).normalize().rotate(90))

    def rotate_around(self, degrees, center):
        center = Vec2(center)
        arm = self._pos - center
        arm.rotate_ip(degrees)
        self._pos = center + arm
        self.rotate(degrees)

    def set_rotation(self, degrees):
        angle = self._facing.angle_to(Vec2(1, 0).rotate(degrees))
        self.rotate(angle)

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

    def collide_circle(self, collider):
        return (
            dist_to(self.center, collider.center) <= self.radius + collider.radius + 10
        )

    def collide_rect(self, collider):
        if (
            (self.top) < (collider.bottom)
            and (self.bottom) > (collider.top)
            and (self.left) < (collider.right)
            and (self.right) > (collider.left)
        ):
            return True
        else:
            return False

    def collide_sat(self, collider):
        if not isinstance(collider, Collider):
            collider = getattr(collider, "collider", None)
        if isinstance(collider, pygame.Rect):
            collider = RectCollider(collider.center, collider.width, collider.height)
        if collider is None:
            print("Invalid collider")
            return False

        axes = self.normals + collider.normals
        if self._size == 1:
            normal = Vec2()
            min_dist = 1000000.0
            for vert in collider.vertices:
                dist = collider.pos + vert - self.center
                length = dist.length()
                if length < min_dist and length != 0:
                    min_dist = dist.length()
                    normal = dist.normalize()
            axes.append(normal)
        elif collider._size == 1:
            normal = Vec2()
            min_dist = 1000000.0
            for vert in self.vertices:
                dist = self.pos + vert - collider.center
                length = dist.length()
                if length < min_dist and length != 0:
                    min_dist = dist.length()
                    normal = dist.normalize()
            axes.append(normal)

        depth = 1000000.0
        normal = Vec2()
        for axis in axes:
            p1 = self.project(axis)
            p2 = collider.project(axis)
            if p1[1] < p2[0] or p2[1] < p1[0]:
                return 0, Vec2()
            axis_depth = min(p2[1] - p1[0], p1[1] - p2[0])
            if axis_depth < depth:
                depth = axis_depth
                normal = axis
        normal.normalize_ip()
        if normal.dot(direction_to(self.center, collider.center)) > 0:
            return depth, normal
        else:
            return depth, -normal

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
            self.left,
            self.top,
            self.right - self.left,
            self.bottom - self.top,
        )

    @property
    def size(self):
        return Vec2(self.right - self.left, self.bottom - self.top)

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, new_facing):
        angle = new_facing.angle_to(Vec2(1, 0))
        self.set_rotation(angle)

    @property
    def angle(self):
        return self._facing.angle_to(Vec2(1, 0))

    @angle.setter
    def angle(self, new_angle):
        self.set_rotation(new_angle)


class RectCollider(Collider):
    def __init__(self, w, h, **kwargs):
        self.vertices = [
            (w / 2, h / 2),
            (w / 2, -h / 2),
            (-w / 2, -h / 2),
            (-w / 2, h / 2),
        ]
        Collider.__init__(self, **kwargs)
        self.collider_type = "Rect"


class CircleCollider(Collider):
    def __init__(self, radius, **kwargs):
        self.radius = radius
        Collider.__init__(self, **kwargs)
        self.collider_type = "Circle"

    def project(self, axis):
        proj = (self.pos).dot(axis)
        min_v = proj - self.radius
        max_v = proj + self.radius
        if min_v > max_v:
            min_v, max_v = max_v, min_v
        return min_v, max_v

    def _debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vec2()
        pygame.draw.circle(surface, self.color, self.pos + offset, self.radius, 1)
        pygame.draw.circle(surface, "red", self.pos + offset, 3, 2)
        pygame.draw.circle(surface, "gray", self.pos + self._center + offset, 2, 1)
        pygame.draw.rect(
            surface,
            "yellow",
            (self.left + offset.x, self.top + offset.y, self.size[0], self.size[1]),
            1,
        )


class PolyCollider(Collider):
    def __init__(self, vertices=None, **kwargs):
        if vertices is None or len(vertices) < 3:
            raise Exception("A shape must be defined for Polygon collider")
        self.vertices = vertices
        Collider.__init__(self, pos)
        self.collider_type = "Polygon"

    def recenter(self):
        if self.center != self.pos:
            for i, vert in enumerate(self.vertices):
                vert = Vec2(vert) - self._center
                self.vertices[i] = vert
            self._center = Vec2()
            self.edges = []
            for i in range(self._size):
                j = (i + 1) % self._size
                self.edges.append([self.vertices[i], self.vertices[j]])


class RayCollider(Collider):
    def __init__(self, length=1, **kwargs):
        self.vertices = [Vec2(0, 0), Vec2(length, 0)]
        self._length = length
        Collider.__init__(self, **kwargs)
        self.collider_type = "Ray"

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length
        self.vertices[1] = direction_to(self.vertices[0], self.facing) * length
        self.edges[0] = (self.vertices[0], self.vertices[1])

    def collide_ray(self, collider):
        col_type = type(collider)
        if not isinstance(collider, Collider):
            collider = getattr(collider, "collider", None)
        if isinstance(collider, pygame.Rect):
            collider = RectCollider(collider.center, collider.width, collider.height)
        if collider is None:
            raise TypeError(f"{col_type} is an invalid collider")

        if isinstance(collider, CircleCollider):
            return line_circle(
                self.pos, self.pos + self.vertices[1], collider.pos, collider.radius
            )
        else:
            collisions = []
            for edge in collider.edges:
                point = line_intersection(
                    self.pos,
                    self.pos + self.vertices[1],
                    collider.pos + edge[0],
                    collider.pos + edge[1],
                )
                if point is not None:
                    collisions.append(point)
            if collisions:
                closest_dist = self.length * 2
                closest_collision = Vec2()
                for point in collisions:
                    if dist_to(self.pos, point) < closest_dist:
                        closest_collision = point
                        closest_dist = dist_to(self.pos, point)
                return closest_collision
        return None
