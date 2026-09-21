"""Regression tests for bugs found in the September 2026 codebase review."""

import json
import os
import sys
import types
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from jazz import Application, Body, GameObject, Globals, Label, Scene, Sprite, TextBox, VBox, Vec2
from jazz.engine.serializer import Serializer
from jazz.engine.sound_manager import SoundManager


class TestRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Other test modules leave mocks in Globals, so save it and use a real Application
        cls._saved_globals = {k: v for k, v in vars(Globals).items() if not k.startswith("_")}
        app = Globals.app
        if not isinstance(app, Application):
            app = Application(200, 200)
        cls.app = app

    @classmethod
    def tearDownClass(cls):
        for key, value in cls._saved_globals.items():
            setattr(Globals, key, value)

    def setUp(self):
        Globals.app = self.app
        Globals.resource = self.app._resource
        Globals.sound = self.app._sound
        Globals.renderer = self.app._renderer
        Globals.display = self.app._display
        self.scene = Scene()
        Globals.scene = self.scene

    # Serializer round trip
    def test_scene_to_json_with_objects(self):
        parent = GameObject("parent", pos=(1, 2))
        parent.add_child(GameObject("child"))
        self.scene.add_object(parent)

        data = json.loads(self.scene.to_json())
        self.assertEqual(len(data["Objects"]), 1)
        self.assertEqual(data["Objects"][0]["options"]["name"], "parent")
        self.assertEqual(len(data["Objects"][0]["children"]), 1)

    def test_script_path_survives_roundtrip(self):
        calls = []
        hooks = types.ModuleType("regression_hooks")
        hooks.upd = lambda obj, delta: calls.append((obj.name, delta))
        sys.modules["regression_hooks"] = hooks
        try:
            data = {
                "SceneClass": "Scene",
                "name": "ScriptScene",
                "Objects": [
                    {"Class": "GameObject", "options": {"name": "a"}, "scripts": {"update": "regression_hooks.upd"}}
                ],
            }
            scene = Scene.from_dict(data)()
            obj = scene["a"]
            obj.update(0.5)
            self.assertEqual(calls, [("a", 0.5)])

            out = json.loads(scene.to_json())
            self.assertEqual(out["Objects"][0]["scripts"], {"update": "regression_hooks.upd"})
        finally:
            del sys.modules["regression_hooks"]

    def test_textbox_callback_path_survives_serialization(self):
        hooks = types.ModuleType("regression_hooks")
        hooks.submit = lambda text: None
        sys.modules["regression_hooks"] = hooks
        try:
            box = TextBox(size=(100, 30), on_submit="regression_hooks.submit")
            self.assertIs(box._on_submit, hooks.submit)
            options = Serializer.serialize_object(box)["options"]
            self.assertEqual(options["on_submit"], "regression_hooks.submit")
            json.dumps(options)
        finally:
            del sys.modules["regression_hooks"]

    def test_runtime_callable_scripts_are_not_serialized(self):
        obj = GameObject("a")
        obj.assign_script("update", lambda self, delta: None)
        self.assertEqual(Serializer.serialize_object(obj)["scripts"], {})

    # Camera
    def test_camera_set_target_game_object(self):
        target = GameObject(pos=(10, 10))
        self.scene.camera.set_target(target)
        self.assertIs(self.scene.camera.target, target)

    # Sound
    def test_volume_changes_with_cached_sounds(self):
        sm = SoundManager()
        fake = mock.Mock()
        sm._sounds["x"] = fake
        sm.set_master_volume(0.5)
        sm.set_sound_volume(0.5)
        self.assertEqual(fake.set_volume.call_count, 2)

    def test_sound_resource_handler_registers_alias(self):
        sm = SoundManager()
        old_sound = Globals.sound
        Globals.sound = sm
        try:
            with mock.patch("jazz.engine.sound_manager.mix.Sound") as sound_cls:
                Serializer.process_resources([{"type": "sound", "id": "jump", "path": "jump.wav"}])
            sound_cls.assert_called_once_with("jump.wav")
            self.assertIs(sm._sounds["jump"], sm._sounds["jump.wav"])
        finally:
            Globals.sound = old_sound

    # UI containers
    def test_bg_container_survives_losing_last_child(self):
        box = VBox(bg_color=(50, 50, 50))
        self.scene.add_object(box)
        label = Label(text="hi")
        box.add_child(label)
        self.assertIsNotNone(box.texture)

        box.remove_child(label)
        self.assertIsNone(box.texture)
        box._render(Vec2())

    def test_empty_bg_container_has_no_placeholder_texture(self):
        box = VBox(bg_color=(50, 50, 50))
        self.scene.add_object(box)
        self.assertIsNone(box.texture)

    # Engine registration independent of user on_load
    def test_sprite_on_load_override_still_registers(self):
        class QuietSprite(Sprite):
            def on_load(self):
                pass

        sprite = self.scene.add_object(QuietSprite())
        self.assertIn(sprite, self.scene._sprites_set)

    def test_body_on_load_override_can_add_collider(self):
        class QuietBody(Body):
            def on_load(self):
                self.add_collider("Rect", w=10, h=10)

        body = self.scene.add_object(QuietBody())
        self.assertTrue(any(body in grid._objects for grid in self.scene._physics_world.values()))

    # Child process and kill flags
    def test_child_queue_kill(self):
        parent = GameObject()
        child = Sprite()
        parent.add_child(child)
        self.scene.add_object(parent)

        child.queue_kill()
        self.scene._game_update(0.016)
        self.assertNotIn(child.id, parent._children)
        self.assertNotIn(child, self.scene._sprites_set)

    def test_child_game_process_flag(self):
        class Counter(GameObject):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.count = 0

            def update(self, delta):
                self.count += 1

        parent = GameObject()
        active = parent.add_child(Counter())
        inactive = parent.add_child(Counter(game_process=False))
        self.scene.add_object(parent)

        self.scene._game_update(0.016)
        self.assertEqual(active.count, 1)
        self.assertEqual(inactive.count, 0)


if __name__ == "__main__":
    unittest.main()
