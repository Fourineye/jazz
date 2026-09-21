import os
import sys
import unittest

# Set SDL to use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

pygame.init()

from jazz import Application, DrawableObject, GameObject, Globals, Scene, Sprite, Vec2


class TestDrawableObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application(800, 800)

        class DummyScene(Scene):
            name = "Dummy"

            def on_load(self, _):
                pass

        cls.app.add_scene(DummyScene)
        cls.app._active_scene = DummyScene()
        Globals.scene = cls.app._active_scene

    def test_drawable_init_defaults(self):
        obj = DrawableObject(name="TestDrawable")
        self.assertEqual(obj.name, "TestDrawable")
        self.assertTrue(isinstance(obj, GameObject))
        self.assertEqual(obj.scale, Vec2(1, 1))
        self.assertEqual(obj.alpha, 255)
        self.assertFalse(obj.flip_x)
        self.assertFalse(obj.flip_y)

    def test_drawable_custom_kwargs(self):
        obj = DrawableObject(
            name="CustomDrawable",
            flip_x=True,
            flip_y=True,
            scale=(2, 3),
            alpha=128,
            anchor=("center", "center"),
        )
        self.assertTrue(obj.flip_x)
        self.assertTrue(obj.flip_y)
        self.assertEqual(obj.scale, Vec2(2, 3))
        self.assertEqual(obj.alpha, 128)

    def test_alpha_validation(self):
        obj = DrawableObject()
        obj.alpha = 0
        self.assertEqual(obj.alpha, 0)
        obj.alpha = 255
        self.assertEqual(obj.alpha, 255)

        with self.assertRaises(Exception):
            obj.alpha = -1

        with self.assertRaises(Exception):
            obj.alpha = 256

    def test_anchor_and_draw_pos(self):
        obj = DrawableObject(pos=(100, 200))
        obj._size = Vec2(40, 20)
        obj.set_anchor("center", "center")
        obj._hardware_offset()
        self.assertEqual(obj.draw_pos, Vec2(80, 190))

        obj.set_anchor("left", "top")
        obj._hardware_offset()
        self.assertEqual(obj.draw_pos, Vec2(100, 200))

    def test_scene_registration_and_kill(self):
        obj = DrawableObject(name="SceneDrawable")
        obj._on_load()
        self.assertIn(obj, Globals.scene._sprites_set)

        obj.kill()
        Globals.scene._sync_sprites()
        self.assertNotIn(obj, Globals.scene.sprites)
        self.assertNotIn(obj, Globals.scene._sprites_set)

    def test_sprite_inheritance(self):
        sprite = Sprite(name="TestSprite")
        self.assertTrue(isinstance(sprite, DrawableObject))
        self.assertTrue(isinstance(sprite, GameObject))


if __name__ == "__main__":
    unittest.main()
