class PhysicsGrid:
    def __init__(self):
        self._objects = []
        self._grid_size = 50
        self.grid = {}

    def __repr__(self):
        return f"\nGrid: {self._objects}"

    def set_bounds(self, x_min, y_min, x_max, y_max):
        self._bounds = (x_min, y_min, x_max, y_max)

    def add_to_grid(self, physics_object):
        rect = physics_object.collider.get_rect()
        g_top = int(rect.top // self._grid_size)
        g_bottom = int(rect.bottom // self._grid_size)
        g_left = int(rect.left // self._grid_size)
        g_right = int(rect.right // self._grid_size)

        for x in range(g_right - g_left + 1):
            for y in range(g_bottom - g_top + 1):
                grid_x = g_left + x
                grid_y = g_top + y

                hash_key = f"{grid_x}.{grid_y}"

                cell = self.grid.get(hash_key, None)
                if cell is None:
                    self.grid.setdefault(hash_key, [physics_object])
                else:
                    self.grid[hash_key].append(physics_object)

    def add_object(self, physics_object):
        if physics_object not in self._objects:
            self._objects.append(physics_object)

    def remove_object(self, physics_object):
        if physics_object in self._objects:
            self._objects.remove(physics_object)

    def build_grid(self):
        self.grid = {}
        for physics_object in self._objects:
            self.add_to_grid(physics_object)

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
