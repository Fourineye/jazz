import unittest

from jazz import GameObject
from jazz.components import Sprite
from jazz.engine.resource_manager import ResourceManager
from jazz.engine.scene import Scene
from jazz.engine.sound_manager import SoundManager
from jazz.global_dict import Globals
from jazz.physics._physics_object import PhysicsObject
from jazz.physics.colliders import CircleCollider
from unit_tests.support import JazzTestCase, MockResource, MockTexture


class TestSceneAndResources(JazzTestCase):
    def setUp(self):
        super().setUp()
        self.patch_globals(resource=MockResource())

    def test_sound_manager_decoupled_load_settings(self):
        sm = SoundManager()
        custom_settings = {
            "music_volume": "0.4",
            "sound_volume": 0.6,
            "master_volume": 0.8,
        }
        sm.load_settings(custom_settings)
        self.assertEqual(sm._volume_m, 0.4)
        self.assertEqual(sm._volume_s, 0.6)
        self.assertEqual(sm._master_volume, 0.8)

    def test_resource_manager_purge_sprite_textures(self):
        res = object.__new__(ResourceManager)
        res._textures = {
            "spr_1": MockTexture(),
            "spr_1:0": MockTexture(),
            "spr_1:1": MockTexture(),
            "spr_2": MockTexture(),
        }
        res._surfaces = {}
        res._sprite_sheets = {}
        res.purge_sprite_textures("spr_1")
        self.assertNotIn("spr_1", res._textures)
        self.assertNotIn("spr_1:0", res._textures)
        self.assertNotIn("spr_1:1", res._textures)
        self.assertIn("spr_2", res._textures)

    def test_scene_moved_objects_tracking(self):
        scene = Scene()
        obj = GameObject()
        obj._moved_this_frame = True

        scene.mark_moved(obj)
        self.assertIn(obj, scene._moved_objects)

        scene._game_update(0.01)
        self.assertFalse(obj._moved_this_frame)
        self.assertEqual(len(scene._moved_objects), 0)

    def test_scene_remove_object_cleanup(self):
        scene = Scene()
        Globals.scene = scene

        parent = GameObject(name="parent")
        child_sprite = Sprite(name="child_sprite", texture=MockTexture())
        child_phys = PhysicsObject(name="child_phys")
        child_phys.collider = CircleCollider(radius=10)

        parent.add_child(child_sprite)
        parent.add_child(child_phys)

        scene.add_object(parent)
        scene.add_sprite(child_sprite)
        scene.add_physics_object(child_phys, "0001")

        self.assertIn(child_sprite, scene._sprites_set)

        scene.remove_object(parent)

        self.assertNotIn(parent.id, scene._objects)
        self.assertNotIn(child_sprite, scene._sprites_set)

    def test_scene_sprite_o1_storage_and_sorting(self):
        scene = Scene()

        s1 = Sprite(name="s1", texture=MockTexture(), z=10)
        s2 = Sprite(name="s2", texture=MockTexture(), z=5)
        s3 = Sprite(name="s3", texture=MockTexture(), z=0)

        scene.add_sprite(s1)
        scene.add_sprite(s2)
        scene.add_sprite(s3)

        self.assertTrue(scene._sprites_dirty)
        scene._sync_sprites()

        self.assertEqual(scene._sprites, [s3, s2, s1])

        scene.remove_sprite(s2)
        self.assertNotIn(s2, scene._sprites_set)
        self.assertTrue(scene._sprites_dirty)

        scene._sync_sprites()
        self.assertEqual(scene._sprites, [s3, s1])


if __name__ == "__main__":
    unittest.main()
