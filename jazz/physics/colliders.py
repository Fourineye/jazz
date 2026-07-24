import pygame

from ..engine.base_object import GameObject
from ..utils import (
    Rect,
    Vec2,
    Color,
    direction_to,
    dist_to,
    line_circle,
    line_intersection,
)
from ..primatives import Draw


class Collider(GameObject):
    """Base class for collision shapes in the Jazz Engine scene graph."""

    def __init__(self, **kwargs) -> None:
        """Initializes the Collider component.

        Sets up vertices, edges, normals, and cached values for transformation checks.
        """
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

        self._vertices_dirty = True
        self._cached_vertices = []
        self._cached_edges = []
        self._cached_normals = []

    def on_transform_change(self) -> None:
        """Updates internal dirty flags, recalculates world bounding box, and computes local shape properties if not already cached."""
        self._vertices_dirty = True
        if self._parent is not None:
            if hasattr(self._parent, "_moved_this_frame"):
                self._parent._moved_this_frame = True

        if not self._edges:
            self._size = len(self._vertices)
            if self._size > 1:
                self._center = Vec2()
                self._radius = 0
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

    def render_debug(self, offset: Vec2):
        """Renders the outline edges, vertices, center, and bounding box of the collider.

        Args:
            offset (Vec2): Viewport offset for debug rendering.
        """
        super().render_debug(offset)
        for edge in self.edges:
            Draw.line(edge[0] + offset, edge[1] + offset, Color("white"), 2)

        for vert in self.vertices:
            Draw.circle(vert + offset, 2, Color("white"))
        Draw.circle(self.pos + self._center + offset, 2, Color("grey"))

        Draw.rect(
            pygame.Rect(
                self.rect.topleft + offset,
                Vec2(self.size[0], self.size[1]),
            ),
            Color("yellow"),
            2,
        )

    def project(self, axis: Vec2) -> tuple[float, float]:
        """Projects the vertices of the collider onto a target axis.

        Args:
            axis (Vec2): The axis vector to project onto.

        Returns:
            tuple[float, float]: The minimum and maximum projected values.
        """
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

    def collide_circle(self, collider: "Collider") -> bool:
        """Performs a quick bounding-radius collision test against another collider.

        Args:
            collider (Collider): The other collider.

        Returns:
            bool: True if bounding circles overlap, otherwise False.
        """
        return (
            (collider.center - self.center).magnitude_squared()
            <= (self._radius + collider._radius) ** 2
        )

    def collide_rect(self, collider: "Collider") -> bool:
        """Performs a quick bounding-box collision test against another collider's bounding box.

        Args:
            collider (Collider): The other collider.

        Returns:
            bool: True if bounding rectangles overlap, otherwise False.
        """
        return self.rect.colliderect(collider.rect)

    def __collide_rect(self, collider: "Collider") -> bool:
        """Internal helper to test bounding box overlaps."""
        if (
            (self.top) < (collider.bottom)
            and (self.bottom) > (collider.top)
            and (self.left) < (collider.right)
            and (self.right) > (collider.left)
        ):
            return True
        else:
            return False

    def get_rect(self) -> pygame.Rect:
        """Calculates and returns the bounding pygame.Rect of the collider.

        Uses cached bounds if rotation hasn't changed.

        Returns:
            Rect: Bounding rectangle in world coordinates.
        """
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

    def collide_sat(self, collider: "Collider | pygame.Rect") -> tuple[float, Vec2]:
        """Runs the Separating Axis Theorem (SAT) algorithm against another collider.

        Args:
            collider (Collider): The other collider to check.

        Returns:
            tuple[float, Vec2]: Minimum penetration depth and the normalized collision normal pointing towards the other collider. Returns (0, Vec2()) if not colliding.
        """
        if not isinstance(collider, Collider):
            collider = getattr(collider, "collider", None)
        if isinstance(collider, pygame.Rect):
            collider = RectCollider(
                collider.center, collider.width, collider.height
            )
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
        if normal.length() == 0:
            normal = Vec2(1, 0)
        else:
            normal.normalize_ip()
        if normal.dot(direction_to(self.center, collider.center)) > 0:
            return depth, normal
        else:
            return depth, -normal

    @property
    def vertices(self):
        """list[Vec2]: Gets the list of vertices rotated and translated in world space."""
        if self._vertices_dirty:
            self._cached_vertices = [
                self.pos + vert.rotate(self.rotation) for vert in self._vertices
            ]
            self._cached_edges = None
            self._cached_normals = None
            self._vertices_dirty = False
        return self._cached_vertices

    @property
    def edges(self):
        """list[tuple[Vec2, Vec2]]: Gets the list of edges in world coordinates."""
        verts = self.vertices
        if self._cached_edges is None:
            self._cached_edges = [(verts[edge[0]], verts[edge[1]]) for edge in self._edges]
        return self._cached_edges

    @property
    def normals(self):
        """list[Vec2]: Gets the list of unique edge normals of the shape."""
        _ = self.edges
        if self._cached_normals is None:
            normals = []
            for edge in self._cached_edges:
                new = True
                new_normal = Vec2(edge[1] - edge[0]).normalize().rotate(90)
                for normal in normals:
                    if abs(new_normal.dot(normal)) == 1:
                        new = False
                        break
                if new:
                    normals.append(new_normal)
            self._cached_normals = normals
        return self._cached_normals

    @property
    def top(self):
        """float: Gets the top Y coordinate boundary in world space."""
        return self.pos.y + self._top

    @property
    def right(self):
        """float: Gets the right X coordinate boundary in world space."""
        return self.pos.x + self._right

    @property
    def bottom(self):
        """float: Gets the bottom Y coordinate boundary in world space."""
        return self.pos.y + self._bottom

    @property
    def left(self):
        """float: Gets the left X coordinate boundary in world space."""
        return self.pos.x + self._left

    @property
    def center(self):
        """Vec2: Gets the center coordinate in world space."""
        return self.pos + self._center

    @property
    def rect(self):
        """Rect: Gets the bounding Rect object."""
        return self.get_rect()

    @property
    def size(self):
        """Vec2: Gets the width and height of the bounding box."""
        return Vec2(self.right - self.left, self.bottom - self.top)


class RectCollider(Collider):
    """Collider shape representing a rectangle."""

    def __init__(self, w: float | int, h: float | int, **kwargs) -> None:
        """Initializes the RectCollider.

        Args:
            w (float | int): Width of the rectangle.
            h (float | int): Height of the rectangle.
        """
        self._vertices = [
            Vec2(w / 2, h / 2),
            Vec2(w / 2, -h / 2),
            Vec2(-w / 2, -h / 2),
            Vec2(-w / 2, h / 2),
        ]
        super().__init__(**kwargs)
        self.collider_type = "Rect"

    @staticmethod
    def from_rect(rect: Rect, **kwargs) -> "RectCollider":
        """Creates a RectCollider from an existing Rect object.

        Args:
            rect (Rect): The source rectangle.

        Returns:
            RectCollider: The constructed rectangle collider.
        """
        kwargs.setdefault("pos", rect.center)
        return RectCollider(rect.w, rect.h, **kwargs)


class CircleCollider(Collider):
    """Collider shape representing a circle."""

    def __init__(self, radius: float | int, **kwargs) -> None:
        """Initializes the CircleCollider.

        Args:
            radius (float | int): The radius of the circle.
        """
        self._radius = radius
        super().__init__(**kwargs)
        self.collider_type = "Circle"
        self._left = -self._radius
        self._right = self._radius
        self._top = -self._radius
        self._bottom = self._radius

    def project(self, axis: Vec2) -> tuple[float, float]:
        """Projects the circle bounds onto a target axis.

        Args:
            axis (Vec2): Projection axis.

        Returns:
            tuple[float, float]: Projection boundaries.
        """
        proj = (self.pos).dot(axis)
        min_v = proj - self._radius
        max_v = proj + self._radius
        if min_v > max_v:
            min_v, max_v = max_v, min_v
        return min_v, max_v

    def render_debug(self, offset: Vec2) -> None:
        """Renders circle bounds in debug mode.

        Args:
            offset (Vec2): Viewport offset.
        """
        super().render_debug(offset)
        Draw.circle(self.pos + offset, self._radius, Color("white"), 2)

    def get_rect(self) -> pygame.Rect:
        """Calculates bounding box of the circle.

        Returns:
            Rect: The bounding rectangle in world space.
        """
        return pygame.Rect(
            self.left,
            self.top,
            self.right - self.left,
            self.bottom - self.top,
        )


class PolyCollider(Collider):
    """Collider shape representing a convex polygon."""

    def __init__(self, vertices: list[Vec2] | None = None, **kwargs) -> None:
        """Initializes the PolyCollider.

        Args:
            vertices (list[Vec2], optional): List of vertices defining the polygon shape.

        Raises:
            Exception: If vertices are not defined or are less than 3.
        """
        if vertices is None or len(vertices) < 3:
            raise Exception("A shape must be defined for Polygon collider")
        self._vertices = vertices
        super().__init__(**kwargs)
        self.collider_type = "Polygon"

    def recenter(self) -> None:
        """Recalculates the center coordinate and offsets the local vertices to be origin-centered."""
        if self.center != Vec2():
            for i, vert in enumerate(self._vertices):
                vert = Vec2(vert) - self._center
                self._vertices[i] = vert
            self._center = Vec2()
            self._vertices_dirty = True


class RayCollider(Collider):
    """Collider representing a single line segment raycast."""

    def __init__(self, **kwargs) -> None:
        """Initializes the RayCollider.

        Args:
            length (float | int, optional): The length of the ray segment. Defaults to 1.
        """
        length = kwargs.get("length", 1)
        self._vertices = [Vec2(0, 0), Vec2(length, 0)]
        self._length = length
        super().__init__(**kwargs)
        self.collider_type = "Ray"

    @property
    def length(self):
        """float: The length of the ray segment."""
        return self._length

    @length.setter
    def length(self, length: float | int) -> None:
        self._length = length
        self._vertices[1] = Vec2(length, 0)
        self._vertices_dirty = True

    def collide_ray(self, collider: Collider) -> Vec2 | None:
        """Calculates collision intersection points of the ray segment with another collider.

        Args:
            collider (Collider): The other collider shape.

        Returns:
            Vec2 | None: The closest collision point, or None if no collision.
        """
        if isinstance(collider, CircleCollider):
            return line_circle(
                self.pos, self.vertices[1], collider.pos, collider._radius
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
                closest_dist_sq = (self.length * 2) ** 2
                closest_collision = Vec2()
                for point in collisions:
                    dist_sq = (point - self.pos).magnitude_squared()
                    if dist_sq < closest_dist_sq:
                        closest_collision = point
                        closest_dist_sq = dist_sq
                return closest_collision
        return None

    def get_rect(self) -> pygame.Rect:
        """Calculates bounding box of the ray segment.

        Returns:
            Rect: Bounding rectangle.
        """
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
