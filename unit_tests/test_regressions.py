"""Regression tests for bugs found in the September 2026 codebase review."""

import json
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

import pygame

from jazz import (
    AnimatedSprite,
    Application,
    Area,
    Body,
    Button,
    GameObject,
    Label,
    ProgressBar,
    Ray,
    Scene,
    Sprite,
    TextBox,
    Timer,
    Tween,
    VBox,
    Vec2,
)
from jazz.camera import Camera
from jazz.engine.input_handler import InputHandler, Keyboard
from jazz.engine.resource_manager import ResourceManager
from jazz.engine.serializer import Serializer
from jazz.engine.sound_manager import SoundManager
from jazz.global_dict import SETTINGS
from jazz.utils import Color, Image, JazzException, Surface, Texture, color_mult, default_ini_path, load_ini
from unit_tests.support import JazzTestCase


class TestRegressions(JazzTestCase):
    # Application singleton
    def test_second_application_is_rejected(self):
        self.assertIs(Application.instance, self.app)
        with self.assertRaises(JazzException):
            Application(100, 100)

    def test_run_without_scenes_raises(self):
        self.enter_patch(mock.patch.object(self.app, "_next_scene", ""))
        with self.assertRaises(JazzException):
            self.app.run()

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
        self.enter_patch(mock.patch.dict(sys.modules, regression_hooks=hooks))

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

    def test_textbox_callback_path_survives_serialization(self):
        hooks = types.ModuleType("regression_hooks")
        hooks.submit = lambda text: None
        self.enter_patch(mock.patch.dict(sys.modules, regression_hooks=hooks))

        box = TextBox(size=(100, 30), on_submit="regression_hooks.submit")
        self.assertIs(box._on_submit, hooks.submit)
        options = Serializer.serialize_object(box)["options"]
        self.assertEqual(options["on_submit"], "regression_hooks.submit")
        json.dumps(options)

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
        self.patch_globals(sound=sm)
        with mock.patch("jazz.engine.sound_manager.mix.Sound") as sound_cls:
            Serializer.process_resources([{"type": "sound", "id": "jump", "path": "jump.wav"}])
        sound_cls.assert_called_once_with("jump.wav")
        self.assertIs(sm._sounds["jump"], sm._sounds["jump.wav"])

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

    # Area overlap timing
    def test_area_sees_object_moved_in_scene_update(self):
        area = Area(pos=(0, 0), layers="0000", collision_layers="0001")
        area.add_collider(0, w=10, h=10)
        body = Body(pos=(40, 0), layers="0001", collision_layers="0000")
        body.add_collider(0, w=5, h=5)
        self.scene.add_object(area)
        self.scene.add_object(body)

        def move_body(delta):
            body.pos = Vec2(2, 2)

        self.enter_patch(mock.patch.object(self.scene, "update", move_body))
        self.scene._game_update(0.1)
        self.assertIn(body, area.entered)

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

    # Engine bug fixes from the roadmap
    def _fresh_resource(self) -> ResourceManager:
        resource = ResourceManager(self.app._renderer)
        self.patch_globals(resource=resource)
        return resource

    def test_texture_resource_alias_is_a_texture(self):
        resource = self._fresh_resource()
        tex = Texture.from_surface(self.app._renderer, Surface((4, 4)))
        with mock.patch("jazz.engine.resource_manager.load_texture", return_value=tex) as load:
            Serializer.process_resources([{"type": "texture", "id": "hero", "path": "hero.png"}])
            self.assertIs(resource.get_texture("hero"), tex)
        load.assert_called_once_with("hero.png")

    def test_constructor_children_are_not_serialized(self):
        box = TextBox(size=(100, 30))
        data = Serializer.serialize_object(box)
        self.assertEqual(data["children"], [])
        json.dumps(data)

        for obj in (Button(text="go"), Ray(length=5)):
            loaded = Serializer.deserialize_object(json.loads(json.dumps(Serializer.serialize_object(obj))))
            self.assertEqual(len(loaded._children), len(obj._children))

    def test_children_added_after_construction_are_serialized(self):
        parent = GameObject("parent")
        parent.add_child(GameObject("child"))
        self.assertEqual(len(Serializer.serialize_object(parent)["children"]), 1)

    def test_deserializer_does_not_retry_failing_constructor(self):
        calls = []

        class Exploding(GameObject):
            def __init__(self, **kwargs):
                calls.append(kwargs)
                super().__init__(**kwargs)
                raise TypeError("real error")

        self.enter_patch(mock.patch.dict(Serializer._class_registry, Exploding=Exploding))
        with self.assertRaisesRegex(TypeError, "real error"):
            Serializer.deserialize_object({"Class": "Exploding", "options": {"name": "x"}})
        self.assertEqual(len(calls), 1)

    def test_physics_raycast_uses_layers(self):
        body = Body(pos=(50, 0), layers="0010", collision_layers="0000")
        body.add_collider(0, w=10, h=10)
        self.scene.add_object(body)
        self.scene._game_update(0)

        hit, _ = self.scene.physics_raycast(Vec2(0, 0), Vec2(100, 0), layers="0010")
        self.assertIs(hit, body)
        miss, _ = self.scene.physics_raycast(Vec2(0, 0), Vec2(100, 0), layers="0001")
        self.assertIsNone(miss)

    def test_scene_constructor_keeps_resources(self):
        resource = self._fresh_resource()
        resource.add_surface(Surface((1, 1)), "kept")
        Scene()
        self.assertIn("kept", resource._surfaces)

    def test_loading_scene_class_clears_cache_without_stopping_sounds(self):
        resource = self.app._resource
        resource.add_surface(Surface((1, 1)), "old")
        sound = mock.Mock()
        self.app._sound._sounds["old"] = sound

        class NextScene(Scene):
            name = "next"

        self.enter_patch(mock.patch.dict(self.app._scenes, next=NextScene))
        self.assertIsInstance(self.app._load_scene("next"), NextScene)
        self.assertNotIn("old", resource._surfaces)
        self.assertNotIn("old", self.app._sound._sounds)
        sound.stop.assert_not_called()

    def test_create_timer_returns_cancellable_timer(self):
        timer = self.scene.create_timer(1.0, lambda: None, one_shot=False)
        self.assertIsInstance(timer, Timer)
        timer.queue_kill()
        self.scene._game_update(0.016)
        self.assertNotIn(timer.id, self.scene._objects)

    def test_text_input_keeps_every_character(self):
        keyboard = Keyboard()
        events = [pygame.event.Event(pygame.TEXTINPUT, text=c) for c in "abc"]
        keyboard.update(events)
        self.assertEqual(keyboard.text, "abc")

    def test_event_handler_sees_keyboard_and_mouse_events(self):
        handler = InputHandler()
        seen = []
        handler.set_event_handler(lambda event: seen.append(event.type))
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=0, unicode="a", scancode=0))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
        handler.update()
        self.assertIn(pygame.KEYDOWN, seen)
        self.assertIn(pygame.MOUSEBUTTONDOWN, seen)
        self.assertTrue(handler.key.press("a"))
        self.assertTrue(handler.mouse.click("left"))

    def test_base_object_repr(self):
        timer = Timer(time_left=1, callback=lambda: None, name="t")
        self.assertIn("t", repr(timer))
        self.assertIn("at 1.0, 2.0", repr(GameObject(pos=(1, 2))))

    def test_resource_clear_empties_styled_textures(self):
        resource = self._fresh_resource()
        resource.get_styled_texture((4, 4), Color("red"))
        resource.clear()
        self.assertEqual(resource._styled_textures, {})

    def test_sprite_sheet_spacing(self):
        resource = self._fresh_resource()
        resource.add_texture(Surface((34, 16)), "sheet")
        frames = resource.make_sprite_sheet("sheet", (16, 16), spacing=(2, 0))
        self.assertEqual([frame.srcrect.x for frame in frames], [0, 18])

    # Component bug fixes from the roadmap
    def _texture(self, size=(8, 8)) -> Texture:
        return Texture.from_surface(self.app._renderer, Surface(size))

    def test_animated_sprite_keeps_name(self):
        self.assertEqual(AnimatedSprite(name="bird", texture=self._texture()).name, "bird")
        self.assertEqual(AnimatedSprite(texture=self._texture()).name, "AnimatedSprite")

    def test_sprite_applies_alpha_to_plain_texture(self):
        texture = self._texture()
        self.assertEqual(texture.blend_mode, pygame.BLENDMODE_NONE)
        sprite = Sprite(texture=texture, alpha=100)
        sprite._render(Vec2())
        self.assertEqual(texture.alpha, 100)
        self.assertEqual(texture.blend_mode, pygame.BLENDMODE_BLEND)

    def test_texture_and_image_rotate_the_same_way(self):
        sprite = Sprite(texture=self._texture(), rotation=30)
        fake = mock.Mock(spec=Texture, blend_mode=pygame.BLENDMODE_BLEND)
        sprite._draw_texture(fake, sprite.rect, -sprite._draw_offset)
        self.assertEqual(fake.draw.call_args.args[2], 30)

        top_left = Sprite(texture=self._texture(), rotation=30, anchor=("left", "top"))
        top_left._draw_texture(fake, top_left.rect, -top_left._draw_offset)
        self.assertEqual(tuple(fake.draw.call_args.args[3]), (0, 0))

        image = Image(self._texture())
        image_sprite = Sprite(texture=image, rotation=30, anchor=("left", "top"))
        image_sprite._render(Vec2())
        self.assertEqual(image.angle, 30)
        self.assertEqual(image.origin, (0, 0))

    def test_draw_pos_setter_survives_offset_recalculation(self):
        sprite = Sprite(texture=self._texture((10, 10)))
        sprite.draw_pos = Vec2(100, 50)
        sprite.scale = (2, 2)
        sprite._render(Vec2())
        self.assertEqual(sprite.pos, Vec2(105, 55))
        self.assertEqual(sprite.rect.topleft, (95, 45))

    def test_alpha_setter_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            Sprite(texture=self._texture()).alpha = 300

    def test_progress_bar_clamps_value(self):
        with mock.patch("jazz.components.ui.progress_bar.map_range", wraps=lambda *a: a[0] * 0) as mapped:
            ProgressBar(value=150, max_value=100)
            ProgressBar(value=5, max_value=0)
        self.assertEqual(mapped.call_count, 1)
        self.assertEqual(mapped.call_args.args[0], 100)

    # Animation and top-level module fixes from the roadmap
    def test_tween_plays_from_json_with_named_target(self):
        data = {
            "SceneClass": "Scene",
            "name": "TweenScene",
            "Objects": [
                {"Class": "GameObject", "options": {"name": "ball", "pos": [0, 0]}},
                {
                    "Class": "Tween",
                    "options": {
                        "name": "t",
                        "target_object": "ball",
                        "target_value": [100, 0],
                        "time": 1.0,
                        "play": True,
                    },
                },
            ],
        }
        scene = Scene.from_dict(data)()
        tween = scene["t"]
        assert isinstance(tween, Tween)
        self.assertIs(tween.target_object, scene["ball"])
        self.assertTrue(tween.playing)

    def test_tween_defaults_to_parent_and_waits_for_load(self):
        parent = GameObject(pos=(0, 0))
        tween = parent.add_child(Tween(target_value=Vec2(10, 0), time=1.0, play=True))
        self.assertFalse(tween.playing)
        self.scene.add_object(parent)
        self.assertIs(tween.target_object, parent)
        self.assertTrue(tween.playing)

    def test_tween_with_missing_target_raises(self):
        tween = self.scene.add_object(Tween("nowhere", play=True))
        with self.assertRaises(JazzException):
            tween.update(0.1)

    def test_tween_serializes_target_by_name(self):
        target = GameObject("hero")
        data = Serializer.serialize_object(Tween(target, "pos", Vec2(5, 5)))
        self.assertEqual(data["options"]["target_object"], "hero")

    def test_load_ini_restores_types_without_default_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, ".jini")
            with open(path, "w") as ini:
                ini.write("[AUDIO]\nmaster_volume = 0.5\n[DISPLAY]\nwidth = 800\nfullscreen = True\nname = x\n")
            load_ini(path)
        self.assertEqual(SETTINGS["AUDIO"]["master_volume"], 0.5)
        self.assertEqual(SETTINGS["AUDIO"]["music_volume"], 1.0)
        self.assertEqual(SETTINGS["DISPLAY"], {"width": 800, "fullscreen": True, "name": "x"})
        self.assertNotIn("DEFAULT", SETTINGS)

    def test_load_ini_creates_missing_file_at_given_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "settings.jini")
            load_ini(path)
            self.assertTrue(os.path.exists(path))

    def test_default_ini_path_is_next_to_main_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(tmp, "game.py")
            open(script, "w").close()
            with mock.patch.object(sys, "argv", [script]):
                self.assertEqual(default_ini_path(), os.path.join(tmp, ".jini"))

    def test_camera_shake_stacks(self):
        camera = Camera()
        camera.add_shake(2.0)
        camera.add_shake(3.0)
        self.assertEqual(camera.magnitude, 5.0)

    def test_color_mult_returns_ints(self):
        self.assertEqual(color_mult((100, 200, 250), 1.1), (110, 220, 255))


if __name__ == "__main__":
    unittest.main()
