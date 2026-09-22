import unittest

from jazz import DrawableObject, GameObject, Globals, Sprite, Vec2
from unit_tests.support import JazzTestCase


class TestDrawableObject(JazzTestCase):
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
