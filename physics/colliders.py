import pygame

from ..baseObject import GameObject
from ..utils import Rect, Vec2, direction_to, dist_to, line_circle, line_intersection


class Collider(GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Collider")
        super().__init__(**kwargs)
        self.collider = self
        self.collider_type = None
        if not hasattr(self, "_vertices"):
            self._vertices = [Vec2(0, 0)]
        self._edges = []
        self._normals = []
        if not hasattr(self, "_radius"):
            self._radius = 0
        self.color = "white"

        self._left = 0
        self._right = 0
        self._top = 0
        self._bottom = 0
        self._center = Vec2()
        self._rot_cache = 1000000

        self._size = len(self._vertices)
        if self._size > 1:
            for i, vert in enumerate(self._vertices):
                vert = Vec2(vert)
                self._center += vert
                self._vertices[i] = vert
                self._radius = max(self._radius, vert.magnitude())
            self._center /= self._size
            if self._size > 2:
                for i in range(self._size):
                    j = (i + 1) % self._size
                    self._edges.append((i, j))
            else:
                self._center = Vec2()
                self._edges.append((0, 1))
        self.get_rect()

    def _debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vec2()
        for edge in self.edges:
            pygame.draw.aaline(
                surface,
                self.color,
                edge[0] + offset,
                edge[1] + offset,
            )
        pygame.draw.aaline(
            surface,
            "red",
            self.center + offset,
            self.center + self.facing * 5 + offset,
        )
        for vert in self.vertices:
            pygame.draw.circle(surface, "gray", vert + offset, 2, 1)
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

    def project(self, axis):
        min_v, max_v = None, None
        for vert in self.vertices:
            proj = (vert).dot(axis)
            if min_v is None:
                min_v = proj
                max_v = proj
            if proj < min_v:
                min_v = proj
            if proj > max_v:
                max_v = proj
        return min_v, max_v

    def collide_circle(self, collider):
        return dist_to(self.center, collider.center) <= self._radius + collider._radius

    def collide_rect(self, collider):
        return self.rect.colliderect(collider.rect)

    def __collide_rect(self, collider):
        if (
            (self.top) < (collider.bottom)
            and (self.bottom) > (collider.top)
            and (self.left) < (collider.right)
            and (self.right) > (collider.left)
        ):
            return True
        else:
            return False

    def get_rect(self):
        if self._rot_cache == self.rotation:
            return pygame.Rect(
                self.left,
                self.top,
                self.right - self.left,
                self.bottom - self.top,
            )
        left, right, top, bottom = (
            self.x,
            self.x,
            self.y,
            self.y,
        )
        vertices = self.vertices
        for vert in vertices:
            left = min(vert.x, left)
            right = max(vert.x, right)
            top = min(vert.y, top)
            bottom = max(vert.y, bottom)
        self._left = left - self.x
        self._right = right - self.x
        self._top = top - self.y
        self._bottom = bottom - self.y
        self._rot_cache = self.rotation
        return pygame.Rect(
            self.left,
            self.top,
            self.right - self.left,
            self.bottom - self.top,
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
            normal = Vec2()
            min_dist = 1000000.0
            for vert in collider.vertices:
                dist = vert - self.center
                length = dist.length()
                if length < min_dist and length != 0:
                    min_dist = dist.length()
                    normal = dist.normalize()
            axes.append(normal)
        elif collider._size == 1:
            normal = Vec2()
            min_dist = 1000000.0
            for vert in self.vertices:
                dist = vert - collider.center
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
    def vertices(self):
        return [self.pos + vert.rotate(self.rotation) for vert in self._vertices]

    @property
    def edges(self):
        vertices = self.vertices
        return [(vertices[edge[0]], vertices[edge[1]]) for edge in self._edges]

    @property
    def normals(self):
        normals = []
        edges = self.edges
        for edge in edges:
            new = True
            new_normal = Vec2(edge[1] - edge[0]).normalize().rotate(90)
            for normal in normals:
                if abs(new_normal.dot(normal)) == 1:
                    new = False
                    break
            if new:
                normals.append(Vec2(edge[1] - edge[0]).normalize().rotate(90))
        return normals

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
        return self.get_rect()

    @property
    def size(self):
        return Vec2(self.right - self.left, self.bottom - self.top)


class RectCollider(Collider):
    def __init__(self, w, h, **kwargs):
        self._vertices = [
            Vec2(w / 2, h / 2),
            Vec2(w / 2, -h / 2),
            Vec2(-w / 2, -h / 2),
            Vec2(-w / 2, h / 2),
        ]
        super().__init__(**kwargs)
        self.collider_type = "Rect"

    @staticmethod
    def from_rect(rect: Rect, **kwargs):
        kwargs.setdefault("pos", rect.center)
        return RectCollider(rect.w, rect.h, **kwargs)


class CircleCollider(Collider):
    def __init__(self, radius, **kwargs):
        self._radius = radius
        super().__init__(**kwargs)
        self.collider_type = "Circle"
        self._left = -self._radius
        self._right = self._radius
        self._top = -self._radius
        self._bottom = self._radius

    def project(self, axis):
        proj = (self.pos).dot(axis)
        min_v = proj - self._radius
        max_v = proj + self._radius
        if min_v > max_v:
            min_v, max_v = max_v, min_v
        return min_v, max_v

    def _debug_draw(self, surface, offset=None):
        if offset is None:
            offset = Vec2()
        pygame.draw.circle(surface, self.color, self.pos + offset, self._radius, 1)
        pygame.draw.circle(surface, "red", self.pos + offset, 3, 2)
        pygame.draw.circle(surface, "gray", self.pos + self._center + offset, 2, 1)
        pygame.draw.rect(
            surface,
            "yellow",
            (self.left + offset.x, self.top + offset.y, self.size[0], self.size[1]),
            1,
        )

    def get_rect(self):
        return pygame.Rect(
            self.left,
            self.top,
            self.right - self.left,
            self.bottom - self.top,
        )


class PolyCollider(Collider):
    def __init__(self, vertices=None, **kwargs):
        if vertices is None or len(vertices) < 3:
            raise Exception("A shape must be defined for Polygon collider")
        self._vertices = vertices
        super().__init__(**kwargs)
        self.collider_type = "Polygon"

    def recenter(self):
        if self.center != Vec2():
            for i, vert in enumerate(self._vertices):
                vert = Vec2(vert) - self._center
                self._vertices[i] = vert
            self._center = Vec2()


class RayCollider(Collider):
    def __init__(self, **kwargs):
        length = kwargs.get("length", 1)
        self._vertices = [Vec2(0, 0), Vec2(length, 0)]
        self._length = length
        super().__init__(**kwargs)
        self.collider_type = "Ray"

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length
        self._vertices[1] = Vec2(length, 0)

    def collide_ray(self, collider):
        if isinstance(collider, CircleCollider):
            return line_circle(
                self.pos, self.pos + self.vertices[1], collider.pos, collider.radius
            )
        else:
            collisions = []
            ray = self.vertices
            for edge in collider.edges:
                point = line_intersection(
                    ray[0],
                    ray[1],
                    edge[0],
                    edge[1],
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

    def get_rect(self):
        if self._rot_cache == self.rotation:
            return pygame.Rect(
                self.left,
                self.top,
                self.right - self.left + 1,
                self.bottom - self.top + 1,
            )
        left, right, top, bottom = (
            self.x,
            self.x,
            self.y,
            self.y,
        )
        vertices = self.vertices
        for vert in vertices:
            left = min(vert.x, left)
            right = max(vert.x, right)
            top = min(vert.y, top)
            bottom = max(vert.y, bottom)
        self._left = left - self.x
        self._right = right - self.x
        self._top = top - self.y
        self._bottom = bottom - self.y
        self._rot_cache = self.rotation
        return pygame.Rect(
            self.left,
            self.top,
            self.right - self.left + 1,
            self.bottom - self.top + 1,
        )
