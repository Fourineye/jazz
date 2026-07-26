"""
Unit tests for Stage 2 Component & UI Serialization in Jazz Engine.
"""

import json
import tempfile
import unittest

from jazz import (
    AnimatedSprite,
    Application,
    Button,
    Globals,
    HBox,
    Label,
    ProgressBar,
    Scene,
    Serializer,
    Sprite,
    TextBox,
    UIContainer,
    VBox,
    Vec2,
)


def sample_button_click() -> None:
    """Sample callback for button press."""
    Globals._button_clicked = True


def sample_text_submit(text: str) -> None:
    """Sample callback for text box submit."""
    Globals._text_submitted = text


class TestSerializerStage2(unittest.TestCase):
    """Test suite for Stage 2 Component & UI serialization."""

    @classmethod
    def setUpClass(cls) -> None:
        if Application.instance is None:
            cls.app = Application(200, 200, "Serializer Stage 2 Test")

    def setUp(self) -> None:
        Globals._button_clicked = False
        Globals._text_submitted = ""
        self.scene = Scene()
        Globals.scene = self.scene

    def test_sprite_serialization(self) -> None:
        """Verifies Sprite serialization round-trip."""
        sprite = Sprite("test_sprite", pos=(10, 20), flip_x=True, alpha=200, scale=(2, 2))
        data = Serializer.serialize_object(sprite)
        self.assertEqual(data["Class"], "Sprite")
        self.assertTrue(data["options"]["flip_x"])
        self.assertEqual(data["options"]["alpha"], 200)

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Sprite)
        self.assertTrue(restored.flip_x)
        self.assertEqual(restored.alpha, 200)
        self.assertEqual(restored.scale, Vec2(2, 2))

    def test_animated_sprite_serialization(self) -> None:
        """Verifies AnimatedSprite serialization round-trip."""
        anim_sprite = AnimatedSprite(
            "hero_anim",
            pos=(50, 50),
            animation_fps=15,
            playing=True,
            oneshot=True,
        )
        data = Serializer.serialize_object(anim_sprite)
        self.assertEqual(data["Class"], "AnimatedSprite")
        self.assertEqual(data["options"]["animation_fps"], 15)
        self.assertTrue(data["options"]["oneshot"])

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, AnimatedSprite)
        self.assertEqual(restored.animation_fps, 15)
        self.assertTrue(restored._one_shot)

    def test_label_serialization(self) -> None:
        """Verifies Label serialization round-trip."""
        label = Label("title_label", text="Hello Jazz", fontsize=32, text_color=(255, 0, 0))
        data = Serializer.serialize_object(label)
        self.assertEqual(data["Class"], "Label")
        self.assertEqual(data["options"]["text"], "Hello Jazz")
        self.assertEqual(data["options"]["fontsize"], 32)

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Label)
        self.assertEqual(restored.text_content, "Hello Jazz")

    def test_button_serialization(self) -> None:
        """Verifies Button serialization round-trip and script callback binding."""
        btn = Button(
            "start_btn",
            size=(120, 40),
            label="Start",
            callback="unit_tests.test_serializer_stage2.sample_button_click",
        )
        data = Serializer.serialize_object(btn)
        self.assertEqual(data["Class"], "Button")
        self.assertEqual(data["options"]["callback"], "unit_tests.test_serializer_stage2.sample_button_click")

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Button)
        self.assertIsNotNone(restored._callback)
        restored._callback()
        self.assertTrue(getattr(Globals, "_button_clicked", False))

    def test_ui_containers_serialization(self) -> None:
        """Verifies UIContainer, VBox, and HBox serialization round-trip."""
        vbox = VBox("main_vbox", padding=10, spacing=5, align="center")
        label = Label("vbox_label", text="Header")
        vbox.add_child(label)

        data = Serializer.serialize_object(vbox)
        self.assertEqual(data["Class"], "VBox")
        self.assertEqual(data["options"]["padding"], 10)
        self.assertEqual(data["options"]["spacing"], 5)
        self.assertEqual(len(data["children"]), 1)

        restored_vbox = Serializer.deserialize_object(data)
        self.assertIsInstance(restored_vbox, VBox)
        self.assertEqual(restored_vbox.padding, 10)
        self.assertEqual(restored_vbox.spacing, 5)
        self.assertEqual(restored_vbox.child_count, 1)

    def test_textbox_serialization(self) -> None:
        """Verifies TextBox serialization round-trip."""
        tb = TextBox(
            "name_input",
            text="Player1",
            on_submit="unit_tests.test_serializer_stage2.sample_text_submit",
        )
        data = Serializer.serialize_object(tb)
        self.assertEqual(data["Class"], "TextBox")
        self.assertEqual(data["options"]["text"], "Player1")

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, TextBox)
        self.assertEqual(restored.text, "Player1")

    def test_progress_bar_serialization(self) -> None:
        """Verifies ProgressBar serialization round-trip."""
        pb = ProgressBar(value=75, max_value=100, size=(150, 25), color=(0, 255, 0))
        data = Serializer.serialize_object(pb)
        self.assertEqual(data["Class"], "ProgressBar")
        self.assertEqual(data["options"]["value"], 75)
        self.assertEqual(data["options"]["max_value"], 100)

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, ProgressBar)
        self.assertEqual(restored.value, 75)
        self.assertEqual(restored.max_value, 100)

    def test_full_ui_scene_from_json(self) -> None:
        """Verifies instantiating a complex UI layout scene from JSON string."""
        scene_json = {
            "SceneClass": "Scene",
            "name": "UIScene",
            "Objects": [
                {
                    "Class": "VBox",
                    "options": {
                        "name": "ui_menu",
                        "pos": [10, 10],
                        "padding": 10,
                        "spacing": 8,
                    },
                    "children": [
                        {
                            "Class": "Label",
                            "options": {"name": "menu_title", "text": "Game Menu", "fontsize": 20},
                        },
                        {
                            "Class": "Button",
                            "options": {"name": "play_button", "size": [100, 30], "label": "Play"},
                        },
                        {
                            "Class": "ProgressBar",
                            "options": {"name": "hp_bar", "value": 100, "max_value": 100, "size": [120, 20]},
                        },
                    ],
                }
            ],
        }

        scene_str = json.dumps(scene_json)
        loaded_scene = Scene.from_json(scene_str)
        self.assertEqual(loaded_scene.name, "UIScene")
        self.assertEqual(len(loaded_scene._objects), 1)

        menu_obj = loaded_scene["ui_menu"]
        self.assertIsInstance(menu_obj, VBox)
        self.assertEqual(len(menu_obj._children), 3)
        self.assertEqual(menu_obj.child_count, 4)


if __name__ == "__main__":
    unittest.main()
