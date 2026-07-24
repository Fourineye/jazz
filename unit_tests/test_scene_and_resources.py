import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from jazz import GameObject
from jazz.components import Sprite
from jazz.engine.resource_manager import ResourceManager
from jazz.engine.scene import Scene
from jazz.engine.sound_manager import SoundManager
from jazz.global_dict import Globals
from jazz.physics.physics import PhysicsGrid
from jazz.physics._physics_object import PhysicsObject
from jazz.physics.colliders import CircleCollider


class MockTexture:
    def __init__(self, size=(32, 32)):
        self.width = size[0]
        self.height = size[1]
    def draw(self, *args, **kwargs):
        pass

class MockResource:
    def __init__(self):
        self._textures = {}
    def clear(self):
        pass
    def get_texture(self, name):
        if isinstance(name, MockTexture):
            return name
        return MockTexture()
    def add_texture(self, texture, id, force=False):
        self._textures[id] = texture
        return texture
    def purge_sprite_textures(self, sprite_id):
        keys_to_remove = [
            k for k in self._textures if k == sprite_id or k.startswith(f"{sprite_id}:")
        ]
        for k in keys_to_remove:
            self._textures.pop(k, None)


class TestSceneAndResources(unittest.TestCase):
    def setUp(self):
        self.old_resource = Globals.resource
        Globals.resource = MockResource()

    def tearDown(self):
        Globals.resource = self.old_resource

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
        old_scene = Globals.scene
        old_resource = Globals.resource
        try:
            scene = Scene()
            res = MockResource()
            Globals.scene = scene
            Globals.resource = res

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
        finally:
            Globals.scene = old_scene
            Globals.resource = old_resource

    def test_scene_sprite_o1_storage_and_sorting(self):
        old_resource = Globals.resource
        try:
            scene = Scene()
            Globals.resource = MockResource()

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
        finally:
            Globals.resource = old_resource


if __name__ == "__main__":
    unittest.main()
