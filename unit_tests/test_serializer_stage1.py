"""
Unit tests for Stage 1 Serializer, Resource Handlers, and Scene JSON instantiation in Jazz Engine.
"""

import json
import os
import tempfile
import unittest

from jazz import (
    Application,
    GameObject,
    Globals,
    Scene,
    Serializer,
    Vec2,
    register_class,
)
from jazz.utils import JazzException


def sample_on_load_hook() -> None:
    """Sample hook function to verify script resolution without subclassing."""
    Globals._hook_executed = True


def sample_scene_on_load(data=None) -> None:
    """Sample scene on_load hook accepting data dict."""
    Globals._scene_hook_executed = True


@register_class
class CustomTestObject(GameObject):
    """Custom GameObject subclass for testing registration."""

    def __init__(self, name: str = "CustomTest", **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.custom_val = kwargs.get("custom_val", 42)


class TestSerializerStage1(unittest.TestCase):
    """Test suite for Stage 1 Serializer architecture."""

    @classmethod
    def setUpClass(cls) -> None:
        if Application.instance is None:
            cls.app = Application(100, 100, "Serializer Test")

    def setUp(self) -> None:
        Globals._hook_executed = False
        self.scene = Scene()
        Globals.scene = self.scene

    def test_class_registration(self) -> None:
        """Verifies explicit class registration and retrieval."""
        self.assertEqual(Serializer.get_class("GameObject"), GameObject)
        self.assertEqual(Serializer.get_class("CustomTestObject"), CustomTestObject)

        with self.assertRaises(JazzException):
            Serializer.get_class("NonExistentClass123")

    def test_gameobject_serialization_roundtrip(self) -> None:
        """Verifies GameObject hierarchy serialization to dict and restoration."""
        parent = GameObject("parent_obj", pos=Vec2(100, 200), rotation=45, z=5)
        child = GameObject("child_obj", pos=Vec2(10, -5))
        parent.add_child(child)

        data = Serializer.serialize_object(parent)
        self.assertEqual(data["Class"], "GameObject")
        self.assertEqual(data["options"]["name"], "parent_obj")
        self.assertEqual(data["options"]["pos"], [100.0, 200.0])
        self.assertEqual(len(data["children"]), 1)

        restored_parent = Serializer.deserialize_object(data)
        self.assertEqual(restored_parent.name, "parent_obj")
        self.assertEqual(restored_parent.local_pos, Vec2(100, 200))
        self.assertEqual(restored_parent.local_rotation, 45)
        self.assertEqual(restored_parent.z, 5)
        self.assertEqual(restored_parent.child_count, 1)

        restored_child = list(restored_parent._children.values())[0]
        self.assertEqual(restored_child.name, "child_obj")
        self.assertEqual(restored_child.local_pos, Vec2(10, -5))

    def test_script_callback_resolution(self) -> None:
        """Verifies overriding object lifecycle methods via script options without subclassing."""
        data = {
            "Class": "GameObject",
            "options": {
                "name": "scripted_obj",
                "scripts": {
                    "on_load": "unit_tests.test_serializer_stage1.sample_on_load_hook"
                },
            },
        }
        obj = Serializer.deserialize_object(data)
        obj._on_load()
        self.assertTrue(getattr(Globals, "_hook_executed", False))

    def test_animation_resource_handler(self) -> None:
        """Verifies registering and loading animation resources."""
        res_data = [
            {
                "type": "animation",
                "id": "hero_walk_anim",
                "spritesheet": "hero_sheet",
                "animation_frames": [0, 1, 2, 3],
                "animation_fps": 12,
                "oneshot": False,
            }
        ]
        Serializer.process_resources(res_data)
        anim_config = Globals.resource.get_animation_resource("hero_walk_anim")
        self.assertIsNotNone(anim_config)
        self.assertEqual(anim_config["spritesheet"], "hero_sheet")
        self.assertEqual(anim_config["animation_fps"], 12)

    def test_custom_resource_type_registration(self) -> None:
        """Verifies custom resource type handlers and generic resource storage."""
        custom_loaded = []

        def handle_dialogue(data: dict) -> None:
            custom_loaded.append(data["id"])
            Globals.resource.add_resource("dialogue", data["id"], data)

        Serializer.register_resource_handler("dialogue", handle_dialogue)
        Serializer.process_resources(
            [{"type": "dialogue", "id": "intro_script", "text": "Welcome to Jazz!"}]
        )

        self.assertIn("intro_script", custom_loaded)
        retrieved = Globals.resource.get_resource("dialogue", "intro_script")
        self.assertEqual(retrieved["text"], "Welcome to Jazz!")

    def test_modular_external_resource_json_file(self) -> None:
        """Verifies loading external resource JSON files from a scene resources list."""
        ext_resources = [
            {
                "type": "animation",
                "id": "ext_anim",
                "spritesheet": "ext_sheet",
                "animation_fps": 24,
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(ext_resources, f)
            temp_path = f.name

        try:
            Serializer.process_resources([temp_path])
            config = Globals.resource.get_animation_resource("ext_anim")
            self.assertIsNotNone(config)
            self.assertEqual(config["animation_fps"], 24)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_scene_from_json_file(self) -> None:
        """Verifies factory instantiation of a Scene from a JSON file."""
        scene_dict = {
            "SceneClass": "Scene",
            "name": "Level1",
            "Resources": [
                {
                    "type": "animation",
                    "id": "idle_anim",
                    "spritesheet": "idle_sheet",
                }
            ],
            "Objects": [
                {
                    "Class": "GameObject",
                    "options": {"name": "player", "pos": [50, 60]},
                    "children": [
                        {
                            "Class": "CustomTestObject",
                            "options": {
                                "name": "weapon",
                                "custom_val": 99,
                            },
                        }
                    ],
                }
            ],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(scene_dict, f)
            temp_scene_path = f.name

        try:
            loaded_scene = Scene.from_json(temp_scene_path)
            self.assertEqual(loaded_scene.name, "Level1")
            self.assertEqual(len(loaded_scene._objects), 1)

            player_obj = loaded_scene["player"]
            self.assertIsNotNone(player_obj)
            self.assertEqual(player_obj.local_pos, Vec2(50, 60))

            weapon_child = list(player_obj._children.values())[0]
            self.assertIsInstance(weapon_child, CustomTestObject)
            self.assertEqual(weapon_child.custom_val, 99)
        finally:
            if os.path.exists(temp_scene_path):
                os.remove(temp_scene_path)

    def test_scene_custom_properties(self) -> None:
        """Verifies serializing and restoring custom scene properties."""
        s = Scene()
        s.name = "CustomPropScene"
        s.properties["gravity"] = -9.8
        s.properties["difficulty"] = "hard"

        data = s.to_dict()
        self.assertEqual(data["properties"]["gravity"], -9.8)
        self.assertEqual(data["properties"]["difficulty"], "hard")

        restored_scene = Scene.from_dict(data)
        self.assertEqual(restored_scene.name, "CustomPropScene")
    def test_gameobject_custom_properties(self) -> None:
        """Verifies serializing and restoring custom properties on GameObject instances."""
        obj = GameObject("prop_obj", pos=(10, 20))
        obj.properties["health"] = 100
        obj.properties["faction"] = "hero"

        data = Serializer.serialize_object(obj)
        self.assertEqual(data["options"]["properties"]["health"], 100)

        restored = Serializer.deserialize_object(data)
        self.assertEqual(restored.properties["health"], 100)
        self.assertEqual(restored.properties["faction"], "hero")

    def test_scene_scripts_callback(self) -> None:
        """Verifies resolving and attaching script callbacks to Scene instances."""
        scene_data = {
            "SceneClass": "Scene",
            "name": "ScriptedScene",
            "scripts": {
                "on_load": "unit_tests.test_serializer_stage1.sample_scene_on_load"
            },
        }
        loaded_scene = Scene.from_dict(scene_data)
        self.assertTrue(hasattr(loaded_scene, "on_load"))
        loaded_scene.on_load(data={})
        self.assertTrue(getattr(Globals, "_scene_hook_executed", False))


if __name__ == "__main__":
    unittest.main()
