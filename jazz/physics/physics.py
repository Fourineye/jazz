from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._physics_object import PhysicsObject
    from .colliders import Collider

class PhysicsGrid:
    """A spatial hashing grid that groups physics objects into cell coordinates to optimize collision detection."""

    def __init__(self) -> None:
        """Initializes the PhysicsGrid with default size, objects list, bounds, and cell registry."""
        self._objects: list["PhysicsObject"] = []
        self._grid_size = 50
        self.grid = {}
        self._object_bounds = {}
        self._object_cells = {}

    def __repr__(self) -> str:
        return f"\nGrid: {self._objects}"

    def set_bounds(self, x_min: float | int, y_min: float | int, x_max: float | int, y_max: float | int) -> None:
        """Sets bounding box limits for the grid area.

        Args:
            x_min (float | int): Left boundary.
            y_min (float | int): Top boundary.
            x_max (float | int): Right boundary.
            y_max (float | int): Bottom boundary.
        """
        self._bounds = (x_min, y_min, x_max, y_max)

    def add_to_grid(self, physics_object: "PhysicsObject", bounds: tuple[int, int, int, int] | None = None, cells: set[str] | None = None) -> None:
        """Places a physical object inside cell lists matching its bounding box coordinates.

        Args:
            physics_object (PhysicsObject): The target object to index.
            bounds (tuple, optional): Pre-calculated cell bounds coordinates. Defaults to None.
            cells (set, optional): Pre-calculated set of cell coordinate strings. Defaults to None.
        """
        if bounds is None or cells is None:
            rect = physics_object.collider.get_rect()
            g_top = int(rect.top // self._grid_size)
            g_bottom = int(rect.bottom // self._grid_size)
            g_left = int(rect.left // self._grid_size)
            g_right = int(rect.right // self._grid_size)
            bounds = (g_left, g_right, g_top, g_bottom)
            cells = {
                f"{g_left + x}.{g_top + y}"
                for x in range(g_right - g_left + 1)
                for y in range(g_bottom - g_top + 1)
            }

        old_cells = self._object_cells.get(physics_object, set())

        # Remove from old cells that are not in new cells
        for cell_key in old_cells - cells:
            cell = self.grid.get(cell_key)
            if cell is not None:
                if physics_object in cell:
                    cell.remove(physics_object)
                if not cell:
                    self.grid.pop(cell_key, None)

        # Add to new cells that were not in old cells
        for cell_key in cells - old_cells:
            cell = self.grid.get(cell_key)
            if cell is None:
                self.grid[cell_key] = [physics_object]
            else:
                cell.append(physics_object)

        self._object_bounds[physics_object] = bounds
        self._object_cells[physics_object] = cells

    def add_object(self, physics_object: "PhysicsObject") -> None:
        """Adds a physical object to the simulation objects tracking list.

        Args:
            physics_object (PhysicsObject): The object to add.
        """
        if physics_object not in self._objects:
            self._objects.append(physics_object)

    def remove_object(self, physics_object: "PhysicsObject") -> None:
        """Removes a physical object from all tracked grid cells and list.

        Args:
            physics_object (PhysicsObject): The object to remove.
        """
        if physics_object in self._objects:
            self._objects.remove(physics_object)
        self._object_bounds.pop(physics_object, None)
        old_cells = self._object_cells.pop(physics_object, None)
        if old_cells is not None:
            for cell_key in old_cells:
                cell = self.grid.get(cell_key)
                if cell is not None:
                    if physics_object in cell:
                        cell.remove(physics_object)
                    if not cell:
                        self.grid.pop(cell_key, None)

    def build_grid(self) -> None:
        """Rebuilds/updates grid mapping coordinates for all tracked objects whose bounding boxes changed."""
        for physics_object in self._objects:
            rect = physics_object.collider.get_rect()
            g_top = int(rect.top // self._grid_size)
            g_bottom = int(rect.bottom // self._grid_size)
            g_left = int(rect.left // self._grid_size)
            g_right = int(rect.right // self._grid_size)

            new_bounds = (g_left, g_right, g_top, g_bottom)
            old_bounds = self._object_bounds.get(physics_object)

            if old_bounds == new_bounds:
                continue

            new_cells = {
                f"{g_left + x}.{g_top + y}"
                for x in range(g_right - g_left + 1)
                for y in range(g_bottom - g_top + 1)
            }
            self.add_to_grid(physics_object, bounds=new_bounds, cells=new_cells)

    def get_grid_cell(self, x: float | int, y: float | int) -> list["PhysicsObject"]:
        """Retrieves list of physics objects indexed inside a specific cell coordinate.

        Args:
            x (float | int): X coordinate cell block index.
            y (float | int): Y coordinate cell block index.

        Returns:
            list[PhysicsObject]: List of registered objects in the cell.
        """
        return self.grid.get(f"{int(x)}.{int(y)}", [])

    def get_grid_cells(self, x: float | int, y: float | int, w: float | int, h: float | int) -> list["PhysicsObject"]:
        """Retrieves list of unique physics objects registered in a rectangular block of cells.

        Args:
            x (float | int): Start column cell block index.
            y (float | int): Start row cell block index.
            w (float | int): Column span width.
            h (float | int): Row span height.

        Returns:
            list[PhysicsObject]: Sensed physics objects.
        """
        cells = set()
        if not self._objects:
            return cells
        for x_offset in range(int(w)):
            for y_offset in range(int(h)):
                # print(x + x_offset, y + y_offset)
                for obj in self.get_grid_cell(int(x) + x_offset, int(y) + y_offset):
                    cells.add(obj)
        # print(cells)
        return list(cells)

    def get_AABB_collisions(self, collider: "PhysicsObject") -> list["PhysicsObject"]:
        """Finds candidate collisions overlapping the bounds of a query collider.

        Args:
            collider (PhysicsObject): The object querying collisions.

        Returns:
            list[PhysicsObject]: Candidate objects whose bounding boxes overlap.
        """
        collisions = set()
        rect = collider.collider.get_rect()
        x = int(rect.left // self._grid_size)
        y = int(rect.top // self._grid_size)
        w = int(rect.right // self._grid_size - x)
        h = int(rect.bottom // self._grid_size - y)
        physics_objects = self.get_grid_cells(x - 1, y - 1, w + 3, h + 3)
        for physics_object in physics_objects:
            if physics_object is not collider:
                if physics_object.collider.collide_rect(collider.collider):
                    collisions.add(physics_object)
        # print(collisions)
        return list(collisions)

    def get_simple_AABB_collisions(self, collider: "Collider") -> list["PhysicsObject"]:
        """Finds candidate collisions overlapping a basic Collider object bounds.

        Args:
            collider (Collider): The shape collider to check.

        Returns:
            list[PhysicsObject]: Candidate overlapping objects.
        """
        collisions = set()
        x = int(collider.left // self._grid_size)
        y = int(collider.top // self._grid_size)
        w = int(collider.right // self._grid_size - x)
        h = int(collider.bottom // self._grid_size - y)
        physics_objects = self.get_grid_cells(x - 1, y - 1, w + 3, h + 3)
        for physics_object in physics_objects:
            if physics_object.collider is not collider:
                if physics_object.collider.collide_rect(collider):
                    collisions.add(physics_object)
        # print(collisions)
        return list(collisions)
