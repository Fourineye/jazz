import unittest
import pygame
import sys
import os

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jazz.physics.colliders import RectCollider, Collider
from jazz.physics._physics_object import PhysicsObject
from jazz.physics.body import Body
from jazz.physics.area import Area
from jazz.physics.ray import Ray
from jazz.engine.scene import Scene
from jazz.global_dict import Globals
from jazz.utils import Vec2

class MockApplication:
    def __init__(self):
        pass

class TestPhysicsOptimizations(unittest.TestCase):
    def setUp(self):
        # Setup clean globals
        class MockResource:
            def clear(self): pass
        class MockSound:
            def clear_sounds(self): pass
        class MockDisplay:
            def get_width(self): return 800
            def get_height(self): return 600
            
        Globals.resource = MockResource()
        Globals.sound = MockSound()
        Globals.display = MockDisplay()
        Globals.scene = Scene()
        Globals.app = MockApplication()

    def test_collider_caching(self):
        # Create a collider
        collider = RectCollider(10, 10, pos=(0, 0))
        
        # Access vertices/edges/normals to cache them
        v1 = collider.vertices
        e1 = collider.edges
        n1 = collider.normals
        
        # Check cache is used (vertices should refer to same object if not dirty)
        self.assertIs(collider.vertices, v1)
        self.assertIs(collider.edges, e1)
        self.assertIs(collider.normals, n1)
        
        # Dirty the collider by rotating the object
        collider.rotation = 90
        
        # Cache should be cleared/re-evaluated
        v2 = collider.vertices
        self.assertIsNot(v2, v1)
        
        # Access again, should be cached again
        self.assertIs(collider.vertices, v2)

    def test_integer_mask_layers(self):
        # Verify mask layer conversion from string to integer
        obj = PhysicsObject(layers="0011", collision_layers="0101")
        self.assertEqual(obj._layers, 3) # 0b0011 = 3
        self.assertEqual(obj.collision_layers, 5) # 0b0101 = 5
        
        # Verify direct integer values are also accepted
        obj2 = PhysicsObject(layers=12, collision_layers=15)
        self.assertEqual(obj2._layers, 12)
        self.assertEqual(obj2.collision_layers, 15)

    def test_area_sat_cache(self):
        # Create an Area and a body
        area = Area(pos=(0, 0), layers="0000", collision_layers="0001")
        area.add_collider(0, w=10, h=10) # RectCollider
        
        body = Body(pos=(2, 2), layers="0001", collision_layers="0000")
        body.add_collider(0, w=5, h=5) # RectCollider
        
        # Add to scene
        Globals.scene.add_object(area)
        Globals.scene.add_object(body)
        
        # Simulate loading
        area.on_load()
        body.on_load()
        
        # Build grid
        for grid in Globals.scene._physics_world.values():
            grid.build_grid()
            
        # Simulate one frame update
        area._moved_this_frame = True
        body._moved_this_frame = True
        
        entered = area.get_entered()
        self.assertIn(body, entered)
        
        # In second frame, neither has moved
        Globals.scene._game_update(0.1) # this clears _moved_this_frame at end of frame
        
        # Verify _moved_this_frame is False
        self.assertFalse(area._moved_this_frame)
        self.assertFalse(body._moved_this_frame)
        
        # Mock collide_sat to count calls to verify caching
        original_sat = area.collider.collide_sat
        sat_calls = 0
        def mock_sat(*args, **kwargs):
            nonlocal sat_calls
            sat_calls += 1
            return original_sat(*args, **kwargs)
        area.collider.collide_sat = mock_sat
        
        # Call get_entered again - should use cache instead of collide_sat!
        entered2 = area.get_entered()
        self.assertIn(body, entered2)
        self.assertEqual(sat_calls, 0)
        
        # Move body slightly so it still overlaps in AABB but moves
        body.pos = Vec2(3, 3)
        self.assertTrue(body._moved_this_frame)
        
        entered3 = area.get_entered()
        self.assertIn(body, entered3)
        self.assertEqual(sat_calls, 1)

    def test_edges_no_accumulation(self):
        # Create a collider
        collider = RectCollider(10, 10, pos=(0, 0))
        
        # Populate edges and center
        collider.on_transform_change()
        
        # Verify initial size of local edges
        self.assertEqual(len(collider._edges), 4)
        
        # Dirty the collider multiple times by rotating
        for i in range(100):
            collider.rotation = i
            collider.on_transform_change()
            
        # The number of local edges must remain exactly 4 (no duplicates accumulated!)
        self.assertEqual(len(collider._edges), 4)

    def test_circle_collider_radius(self):
        from jazz.physics.colliders import CircleCollider
        collider = CircleCollider(radius=15, pos=(0, 0))
        self.assertEqual(collider._radius, 15)
        
        # Trigger transform change
        collider.on_transform_change()
        self.assertEqual(collider._radius, 15)

    def test_recursive_collisions(self):
        # Create two overlapping dynamic bodies
        body1 = Body(pos=(400, 400))
        body1.add_collider(0, w=100, h=100) # RectCollider
        body2 = Body(pos=(410, 400))
        body2.add_collider(0, w=100, h=100) # RectCollider
        
        Globals.scene.add_object(body1)
        Globals.scene.add_object(body2)
        body1.on_load()
        body2.on_load()
        
        # Initialize grid
        for grid in Globals.scene._physics_world.values():
            grid.build_grid()
            
        # Verify that calling move_and_collide resolves without RecursionError
        try:
            body1.move_and_collide(Vec2(5, 0))
        except RecursionError:
            self.fail("move_and_collide raised RecursionError on overlapping bodies")

    def test_dynamic_body_settling(self):
        from jazz._in_dev._in_dev import DynamicBody
        from jazz import COLLIDER_RECT
        
        Globals.scene.gravity_enabled = True
        Globals.scene.gravity_accel = 500.0
        
        # Create floor (static)
        floor = Body(static=True, pos=(400, 500))
        floor.add_collider(COLLIDER_RECT, w=800, h=20)
        Globals.scene.add_object(floor)
        floor.on_load()
        
        # Create dynamic body
        body = DynamicBody(pos=(400, 483), velocity=Vec2(0, 0))
        body.add_collider(COLLIDER_RECT, w=20, h=20)
        Globals.scene.add_object(body)
        body.on_load()
        
        # Rebuild grid
        for grid in Globals.scene._physics_world.values():
            grid.build_grid()
            
        # Update body once - it should collide and settle
        body.update(0.016)
        self.assertTrue(body.on_ground)
        self.assertEqual(body.velocity.y, 0)
        
        # Update body a second time - it should remain settled on the ground
        body.update(0.016)
        self.assertTrue(body.on_ground)
        self.assertEqual(body.velocity.y, 0)
        
        # Wake up check
        body.move_and_collide(Vec2(0, -5))
        self.assertFalse(body.on_ground)

if __name__ == "__main__":
    unittest.main()
