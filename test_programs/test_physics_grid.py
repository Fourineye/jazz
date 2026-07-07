import unittest
import pygame
import sys
import os

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jazz.physics.physics import PhysicsGrid

class MockCollider:
    def __init__(self, rect):
        self.rect = rect

    def get_rect(self):
        return self.rect

    def collide_rect(self, other_collider):
        # Handle if other_collider is MockCollider, a standard Collider, or a pygame.Rect
        if hasattr(other_collider, "get_rect"):
            other_rect = other_collider.get_rect()
        else:
            other_rect = other_collider
        return self.rect.colliderect(other_rect)


class MockPhysicsObject:
    def __init__(self, rect, name="MockPhysics"):
        self.name = name
        self.collider = MockCollider(rect)


class TestPhysicsGrid(unittest.TestCase):
    def setUp(self):
        self.grid = PhysicsGrid()
        # default grid size is 50

    def test_initial_state(self):
        self.assertEqual(self.grid._objects, [])
        self.assertEqual(self.grid.grid, {})

    def test_add_and_build(self):
        # Create an object in cell (0, 0)
        obj1 = MockPhysicsObject(pygame.Rect(10, 10, 20, 20), "obj1")
        self.grid.add_object(obj1)
        self.grid.build_grid()

        # obj1 should be in cell "0.0"
        self.assertIn(obj1, self.grid._objects)
        self.assertIn("0.0", self.grid.grid)
        self.assertEqual(self.grid.grid["0.0"], [obj1])

    def test_span_multiple_cells(self):
        # Create an object spanning from cell (0, 0) to (1, 1)
        # (top-left 10,10; bottom-right 70,70 -> bounds 0..1, 0..1)
        obj = MockPhysicsObject(pygame.Rect(10, 10, 60, 60), "obj")
        self.grid.add_object(obj)
        self.grid.build_grid()

        expected_cells = {"0.0", "0.1", "1.0", "1.1"}
        for cell_key in expected_cells:
            self.assertIn(cell_key, self.grid.grid)
            self.assertIn(obj, self.grid.grid[cell_key])

    def test_move_object(self):
        obj = MockPhysicsObject(pygame.Rect(10, 10, 20, 20), "obj")
        self.grid.add_object(obj)
        self.grid.build_grid()

        self.assertEqual(self.grid.grid["0.0"], [obj])
        self.assertNotIn("1.1", self.grid.grid)

        # Move object to cell (1, 1) -> rect (60, 60, 20, 20)
        obj.collider.rect = pygame.Rect(60, 60, 20, 20)
        self.grid.build_grid()

        # obj should now be in cell "1.1", and cell "0.0" should be cleaned up (empty/removed)
        self.assertNotIn("0.0", self.grid.grid)
        self.assertEqual(self.grid.grid["1.1"], [obj])

    def test_remove_object(self):
        obj = MockPhysicsObject(pygame.Rect(10, 10, 20, 20), "obj")
        self.grid.add_object(obj)
        self.grid.build_grid()

        self.assertEqual(self.grid.grid["0.0"], [obj])

        self.grid.remove_object(obj)
        self.assertNotIn(obj, self.grid._objects)
        self.assertNotIn("0.0", self.grid.grid)

    def test_aabb_collisions(self):
        obj1 = MockPhysicsObject(pygame.Rect(10, 10, 20, 20), "obj1")
        obj2 = MockPhysicsObject(pygame.Rect(25, 10, 20, 20), "obj2") # collides with obj1
        obj3 = MockPhysicsObject(pygame.Rect(100, 100, 20, 20), "obj3") # too far away

        self.grid.add_object(obj1)
        self.grid.add_object(obj2)
        self.grid.add_object(obj3)
        self.grid.build_grid()

        # Check collisions for obj1
        collisions = self.grid.get_AABB_collisions(obj1)
        self.assertIn(obj2, collisions)
        self.assertNotIn(obj3, collisions)
        self.assertNotIn(obj1, collisions)

        # Check simple AABB collisions
        simple_collisions = self.grid.get_simple_AABB_collisions(pygame.Rect(5, 5, 10, 10))
        self.assertIn(obj1, simple_collisions)
        self.assertNotIn(obj2, simple_collisions)
        self.assertNotIn(obj3, simple_collisions)


if __name__ == "__main__":
    unittest.main()
