import os
import sys
import unittest

# Set SDL to use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from jazz import (
    Application,
    Globals,
    Label,
    AnimatedSprite,
    Vec2,
    Surface,
)
from jazz.camera import Camera
from jazz.utils import (
    dist_to,
    direction_to,
    unit_from_angle,
    angle_from_vec,
)



class TestOptimizationsAndRefactoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application(800, 600)
        Globals.app = cls.app

    def test_camera_display_caching_and_shake(self):
        cam = Camera()
        self.assertEqual(cam._display_width, 800)
        self.assertEqual(cam._display_height, 600)
        self.assertEqual(cam.display_center, (400.0, 300.0))

        cam.add_shake(10.0)
        self.assertEqual(cam.magnitude, 10.0)

        cam.update(0.016)
        self.assertTrue(cam.shake.x != 0 or cam.shake.y != 0 or cam.magnitude < 10.0)

        cam.magnitude = 0.05
        cam.update(0.016)
        self.assertEqual(cam.magnitude, 0.0)
        self.assertEqual(cam.shake, Vec2(0, 0))

    def test_vector_math_builtins(self):
        v1 = Vec2(10, 20)
        v2 = Vec2(40, 60)

        # Distance test
        d = dist_to(v1, v2)
        self.assertAlmostEqual(d, 50.0)

        # Direction test
        dir_vec = direction_to(v1, v2)
        self.assertAlmostEqual(dir_vec.x, 0.6)
        self.assertAlmostEqual(dir_vec.y, 0.8)

        # Zero distance direction test
        zero_dir = direction_to(v1, v1)
        self.assertEqual(zero_dir, Vec2(0, 0))

        # Angle conversions
        u = unit_from_angle(90)
        self.assertAlmostEqual(u.x, 0.0, places=5)
        self.assertAlmostEqual(u.y, 1.0, places=5)

        ang = angle_from_vec(Vec2(0, 1))
        self.assertAlmostEqual(ang, 90.0)

    def test_label_lazy_rendering(self):
        lbl = Label(text="Initial")
        _ = lbl.texture
        self.assertFalse(lbl._dirty)

        lbl.set_text("Updated 1")
        lbl.set_text("Updated 2")
        self.assertEqual(lbl.text_content, "Updated 2")
        self.assertTrue(lbl._dirty)

        # Reading texture triggers lazy render
        tex = lbl.texture
        self.assertIsNotNone(tex)
        self.assertFalse(lbl._dirty)


    def test_animated_sprite_parser_helper(self):
        s1 = Surface((32, 32))
        s2 = Surface((32, 32))
        anim = AnimatedSprite(spritesheet=[s1, s2])
        self.assertEqual(len(anim._sheet), 2)


if __name__ == "__main__":
    unittest.main()
