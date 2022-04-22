import pygame
from pygame import Vector2

from pygame_engine.utils import dist_to


class Collider:
    def __init__(self, pos):
        self._pos = Vector2(pos)
        if not hasattr(self, "vertices"):
            self.vertices = [Vector2(0, 0)]
        self.edges = []
        self.normals = []
        self.radius = 0
        self.color = "white"

        self._facing = Vector2(1, 0)
        self._left = self.vertices[0][0]
        self._right = self.vertices[0][0]
        self._top = self.vertices[0][1]
        self._bottom = self.vertices[0][1]
        self._center = Vector2()

        self._size = len(self.vertices)
        if self._size > 1:
            for i, vert in enumerate(self.vertices):
                vert = Vector2(vert)
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
                self.normals.append(Vector2(edge[1] - edge[0]).normalize().rotate(90))

    def draw(self, surface, offset=None):
        draw_verts = [self.pos + vert + offset for vert in self.vertices]
        pygame.draw.polygon(surface, self.color, draw_verts)

    def debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vector2()
        for edge in self.edges:
            pygame.draw.aaline(
                surface,
                self.color,
                self.pos + edge[0] + offset,
                self.pos + edge[1] + offset,
            )
        for i, edge in enumerate(self.edges):
            start = edge[0] + (edge[1] - edge[0]) / 2
            end = start + self.normals[i] * 10
            pygame.draw.aaline(
                surface, "red", self.pos + start + offset, self.pos + end + offset
            )
        pygame.draw.aaline(
            surface,
            "red",
            self.center + offset,
            self.center + self.facing * 20 + offset,
        )
        for vert in self.vertices:
            pygame.draw.circle(surface, "gray", self.pos + vert + offset, 2)
        pygame.draw.circle(surface, "red", self.pos + offset, 5)
        pygame.draw.circle(surface, "gray", self.pos + self._center + offset, 2)
        pygame.draw.rect(surface, "yellow", self.rect, 1)

    def move(self, direction):
        self._pos += Vector2(direction)

    def rotate(self, degrees):
        self._facing.rotate_ip(degrees)
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
        self._center /= self._size
        self.normals = []
        if self.edges:
            for edge in self.edges:
                self.normals.append(Vector2(edge[1] - edge[0]).normalize().rotate(90))

    def rotate_around(self, degrees, center):
        center = Vector2(center)
        arm = self._pos - center
        arm.rotate_ip(degrees)
        self._pos = center + arm
        self.rotate(degrees)

    def set_rotation(self, degrees):
        angle = self._facing.angle_to(Vector2(1, 0).rotate(degrees))
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
        return dist_to(self.center, collider.center) <= self.radius + collider.radius

    def collide_rect(self, collider):
        return (
            self.top < collider.bottom
            and self.bottom > collider.top
            and self.left < collider.right
            and self.right > collider.left
        )

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
            normal = Vector2()
            min_dist = 1000000.0
            for vert in collider.vertices:
                dist = collider.pos + vert - self.center
                if dist.length() < min_dist:
                    min_dist = dist.length()
                    normal = dist.normalize()
            axes.append(normal)
        elif collider._size == 1:
            normal = Vector2()
            min_dist = 1000000.0
            for vert in self.vertices:
                dist = self.pos + vert - collider.center
                if dist.length() < min_dist:
                    min_dist = dist.length()
                    normal = dist.normalize()
            axes.append(normal)

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

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_pos):
        self._pos = Vector2(new_pos)

    @property
    def top(self):
        return self._pos.y + self._top

    @property
    def right(self):
        return self._pos.x + self._right

    @property
    def bottom(self):
        return self._pos.y + self._bottom

    @property
    def left(self):
        return self._pos.x + self._left

    @property
    def center(self):
        return self._pos + self._center

    @property
    def rect(self):
        return pygame.Rect(
            self.left, self.top, self.right - self.left, self.bottom - self.top
        )

    @property
    def size(self):
        return Vector2(self.right - self.left, self.bottom - self.top)

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, new_facing):
        angle = new_facing.angle_to(Vector2(1, 0))
        self.set_rotation(angle)

    @property
    def angle(self):
        return self._facing.angle_to(Vector2(1, 0))

    @angle.setter
    def angle(self, new_angle):
        self.set_rotation(new_angle)


class RectCollider(Collider):
    def __init__(self, pos, w, h):
        self.vertices = [
            (w / 2, h / 2),
            (w / 2, -h / 2),
            (-w / 2, -h / 2),
            (-w / 2, h / 2),
        ]
        Collider.__init__(self, pos)


class CircleCollider(Collider):
    def __init__(self, pos, radius):
        Collider.__init__(self, pos)
        self.radius = radius

    def project(self, axis):
        proj = (self.pos).dot(axis)
        min_v = proj - self.radius
        max_v = proj + self.radius
        return min_v, max_v

    def draw(self, surface, offset=None):
        pygame.draw.circle(surface, self.color, self.pos, self.radius)

    def debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vector2()
        pygame.draw.circle(surface, self.color, self._pos + offset, self.radius, 1)
        pygame.draw.circle(surface, "red", self.pos + offset, 5)
        pygame.draw.circle(surface, "gray", self.pos + self._center + offset, 2)
        pygame.draw.rect(surface, "yellow", self.rect, 1)

    @property
    def top(self):
        return self._pos.y - self.radius

    @property
    def right(self):
        return self._pos.x + self.radius

    @property
    def bottom(self):
        return self._pos.y + self.radius

    @property
    def left(self):
        return self._pos.x - self.radius


class PolyCollider(Collider):
    def __init__(self, pos, vertices=None):
        if vertices is None or len(vertices) < 3:
            raise Exception("A shape must be defnined for complex collider")
        self.vertices = vertices
        Collider.__init__(self, pos)

    def recenter(self):
        if self.center != self.pos:
            for i, vert in enumerate(self.vertices):
                vert = Vector2(vert) - self._center
                self.vertices[i] = vert
            self._center = Vector2()
            self.edges = []
            for i in range(self._size):
                j = (i + 1) % self._size
                self.edges.append([self.vertices[i], self.vertices[j]])
