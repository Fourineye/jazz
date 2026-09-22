import unittest

from jazz import GameObject, Vec2
from jazz.components.sprite import Sprite
from unit_tests.support import JazzTestCase, MockResource

class TestTransforms(JazzTestCase):
    def test_flat_coordinates(self):
        obj = GameObject(pos=(100, 200), rotation=45)
        self.assertEqual(obj.local_pos, Vec2(100, 200))
        self.assertEqual(obj.pos, Vec2(100, 200))
        self.assertEqual(obj.local_rotation, 45)
        self.assertEqual(obj.rotation, 45)
        self.assertEqual(obj.x, 100)
        self.assertEqual(obj.y, 200)

    def test_nested_coordinates(self):
        parent = GameObject(pos=(10, 20), rotation=90)
        child = GameObject(pos=(50, 0), rotation=30)
        parent.add_child(child)
        
        # rotation calculation:
        # child.rotation = parent.rotation + child.local_rotation = 90 + 30 = 120
        self.assertEqual(child.rotation, 120)
        
        # position calculation:
        # parent.pos + child.local_pos rotated by parent.rotation
        # child.local_pos = (50, 0)
        # rotated by 90 degrees: (0, 50)
        # parent.pos = (10, 20)
        # child.pos = (10, 20) + (0, 50) = (10, 70)
        self.assertAlmostEqual(child.pos.x, 10, places=2)
        self.assertAlmostEqual(child.pos.y, 70, places=2)

    def test_dirty_flag_propagation(self):
        parent = GameObject(pos=(0, 0), rotation=0)
        child = GameObject(pos=(10, 0), rotation=0)
        parent.add_child(child)
        
        # Check initial pos
        self.assertEqual(child.pos, Vec2(10, 0))
        
        # Move parent
        parent.pos = Vec2(100, 100)
        
        # Child's global pos should update
        self.assertEqual(child.pos, Vec2(110, 100))

        # Rotate parent
        parent.rotation = 90
        # child.local_pos = (10, 0) rotated by 90 degrees -> (0, 10)
        # child.pos = parent.pos + (0, 10) = (100, 110)
        self.assertAlmostEqual(child.pos.x, 100, places=2)
        self.assertAlmostEqual(child.pos.y, 110, places=2)
        self.assertEqual(child.rotation, 90)

    def test_child_set_global_pos(self):
        parent = GameObject(pos=(100, 100), rotation=90)
        child = GameObject(pos=(0, 0), rotation=0)
        parent.add_child(child)
        
        # Set child global pos
        child.pos = Vec2(100, 150)
        
        # Child's global pos should be (100, 150)
        self.assertAlmostEqual(child.pos.x, 100, places=2)
        self.assertAlmostEqual(child.pos.y, 150, places=2)
        
        # Child's local pos should be updated relative to parent:
        # parent pos = (100, 100), parent rotation = 90
        # target child.pos - parent.pos = (0, 50)
        # rotate (0, 50) by -parent.rotation (-90):
        # (0, 50) rotated by -90 degrees -> (50, 0)
        self.assertAlmostEqual(child.local_pos.x, 50, places=2)
        self.assertAlmostEqual(child.local_pos.y, 0, places=2)

    def test_sprite_hook(self):
        self.patch_globals(resource=MockResource())

        sprite = Sprite(pos=(0, 0))
        sprite._img_dirty = False

        sprite.local_pos = Vec2(10, 10)
        self.assertTrue(sprite._img_dirty)

if __name__ == "__main__":
    unittest.main()
