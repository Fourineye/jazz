


class PhysicsGrid:
    def __init__(self):
        self._objects = []
        self._grid_size = 1
        self.grid = {}

    def __repr__(self):
        return f'\nGrid: {self._objects}'

    def resize_grid(self):
        max_size = 1
        for physics_object in self._objects:
            size = physics_object.collider.size
            max_size = max(max_size, size.x, size.y)
        self._grid_size = max_size
    
    def add_to_grid(self, physics_object):
        grid_x = int(physics_object.collider.x // self._grid_size)
        grid_y = int(physics_object.collider.y // self._grid_size)

        x = self.grid.get(grid_x, None)
        if x is None:
            self.grid.setdefault(grid_x, {grid_y: [physics_object]})
        else:
            y = x.get(grid_y, None)
            if y is None:
                x.setdefault(grid_y, [physics_object])
            else:
                y.append(physics_object)
    
    def add_object(self, physics_object):
        if physics_object not in self._objects:
            self._objects.append(physics_object)

    def remove_object(self, physics_object):
        if physics_object in self._objects:
            self._objects.remove(physics_object)

    def build_grid(self):
        self.grid = {}
        self.resize_grid()
        for physics_object in self._objects:
            self.add_to_grid(physics_object)

    def get_grid_cell(self, x, y):
        return self.grid.get(int(x), {}).get(int(y), [])

    def get_grid_cells(self, x, y, w, h):
        cells = []
        for x_offset in range(int(w)):
            for y_offset in range(int(h)):
                cells += self.get_grid_cell(int(x) + x_offset, int(y) + y_offset)
        return cells

    def get_AABB_collisions(self, collider):
        collisions = []
        x = int(collider.collider.left // self._grid_size)
        y = int(collider.collider.top // self._grid_size)
        w = int(collider.collider.right // self._grid_size - x)
        h = int(collider.collider.bottom // self._grid_size - y)
        physics_objects = self.get_grid_cells(x - 1, y - 1, w + 3, h + 3)
        for physics_object in physics_objects:
            if physics_object is not collider:
                if physics_object.collider.collide_rect(collider.collider):
                    collisions.append(physics_object)
        #print(collisions)
        return collisions