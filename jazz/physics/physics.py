class PhysicsGrid:
    def __init__(self):
        self._objects = []
        self._grid_size = 50
        self.grid = {}
        self._object_bounds = {}
        self._object_cells = {}

    def __repr__(self):
        return f"\nGrid: {self._objects}"

    def set_bounds(self, x_min, y_min, x_max, y_max):
        self._bounds = (x_min, y_min, x_max, y_max)

    def add_to_grid(self, physics_object, bounds=None, cells=None):
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

    def add_object(self, physics_object):
        if physics_object not in self._objects:
            self._objects.append(physics_object)

    def remove_object(self, physics_object):
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

    def build_grid(self):
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

    def get_grid_cell(self, x, y):
        return self.grid.get(f"{int(x)}.{int(y)}", [])

    def get_grid_cells(self, x, y, w, h):
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

    def get_AABB_collisions(self, collider):
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

    def get_simple_AABB_collisions(self, collider):
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
