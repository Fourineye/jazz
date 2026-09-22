"""
Unit tests for Stage 3 Physics & Animation Serialization in Jazz Engine.
"""

import json
import unittest

from jazz import (
    Area,
    Body,
    CircleCollider,
    GameObject,
    PhysicsObject,
    PolyCollider,
    Ray,
    RectCollider,
    Scene,
    Serializer,
    Timer,
    Tween,
    Vec2,
)
from unit_tests.support import JazzTestCase

# Names of the sample callbacks that have run, cleared before each test
callback_calls: list[str] = []


def sample_timer_callback() -> None:
    """Sample callback for timer expiration."""
    callback_calls.append("timer_expired")


class TestSerializerStage3(JazzTestCase):
    """Test suite for Stage 3 Physics & Animation serialization."""

    def setUp(self) -> None:
        super().setUp()
        callback_calls.clear()

    def test_physics_object_serialization(self) -> None:
        """Verifies PhysicsObject layers serialization round-trip."""
        po = PhysicsObject(layers="0010", collision_layers="0001")
        po.add_collider("Circle", radius=10)
        data = Serializer.serialize_object(po)

        self.assertEqual(data["Class"], "PhysicsObject")
        self.assertEqual(data["options"]["layers"], "0010")

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, PhysicsObject)
        self.assertEqual(restored._layers, 2)

    def test_body_serialization(self) -> None:
        """Verifies Body static property serialization round-trip."""
        body = Body(static=True, layers="0001")
        body.add_collider("Rect", w=40, h=40)
        data = Serializer.serialize_object(body)

        self.assertEqual(data["Class"], "Body")
        self.assertTrue(data["options"]["static"])

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Body)
        self.assertTrue(restored.static)

    def test_area_serialization(self) -> None:
        """Verifies Area sensor zone serialization round-trip."""
        area = Area(active=True)
        area.add_collider("Circle", radius=25)
        data = Serializer.serialize_object(area)

        self.assertEqual(data["Class"], "Area")
        self.assertTrue(data["options"]["active"])

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Area)
        self.assertTrue(restored._active)

    def test_ray_serialization(self) -> None:
        """Verifies Ray component serialization round-trip."""
        ray = Ray(length=150, active=True)
        data = Serializer.serialize_object(ray)

        self.assertEqual(data["Class"], "Ray")
        self.assertEqual(data["options"]["length"], 150)

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Ray)
        self.assertEqual(restored.length, 150)

    def test_colliders_serialization(self) -> None:
        """Verifies individual Collider shapes serialization round-trip."""
        rect_c = RectCollider(w=30, h=60)
        r_data = Serializer.serialize_object(rect_c)
        self.assertEqual(r_data["Class"], "RectCollider")
        self.assertEqual(r_data["options"]["w"], 30)

        circle_c = CircleCollider(radius=15)
        c_data = Serializer.serialize_object(circle_c)
        self.assertEqual(c_data["Class"], "CircleCollider")
        self.assertEqual(c_data["options"]["radius"], 15)

        poly_c = PolyCollider(vertices=[Vec2(0, 0), Vec2(10, 0), Vec2(0, 10)])
        p_data = Serializer.serialize_object(poly_c)
        self.assertEqual(p_data["Class"], "PolyCollider")
        self.assertEqual(len(p_data["options"]["vertices"]), 3)

        restored_circle = Serializer.deserialize_object(c_data)
        self.assertIsInstance(restored_circle, CircleCollider)
        self.assertEqual(restored_circle._radius, 15)

    def test_timer_serialization(self) -> None:
        """Verifies Timer countdown component serialization round-trip."""
        timer = Timer(
            time_left=5.0,
            callback="unit_tests.test_serializer_stage3.sample_timer_callback",
            pause_process=True,
            one_shot=True,
        )
        data = Serializer.serialize_object(timer)
        self.assertEqual(data["Class"], "Timer")
        self.assertEqual(data["options"]["time_left"], 5.0)
        self.assertEqual(data["options"]["callback"], "unit_tests.test_serializer_stage3.sample_timer_callback")

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Timer)
        self.assertEqual(restored.time_left, 5.0)
        self.assertTrue(restored._pause_process)
        restored.callback()
        self.assertEqual(callback_calls, ["timer_expired"])

    def test_tween_serialization(self) -> None:
        """Verifies Tween component serialization round-trip."""
        dummy = GameObject("dummy_target", pos=(0, 0))
        tween = Tween(
            target_object=dummy,
            target_property="pos",
            target_value=100,
            time=2.0,
            loop=True,
        )
        data = Serializer.serialize_object(tween)
        self.assertEqual(data["Class"], "Tween")
        self.assertEqual(data["options"]["target_property"], "pos")
        self.assertEqual(data["options"]["target_value"], 100)

        restored = Serializer.deserialize_object(data)
        self.assertIsInstance(restored, Tween)
        self.assertEqual(restored.target_property, "pos")
        self.assertEqual(restored.target_value, 100)

    def test_full_physics_scene_from_json(self) -> None:
        """Verifies instantiating a scene with physics objects and colliders from JSON."""
        scene_json = {
            "SceneClass": "Scene",
            "name": "PhysicsScene",
            "Objects": [
                {
                    "Class": "Body",
                    "options": {
                        "name": "ground",
                        "pos": [0, 100],
                        "static": True,
                    },
                    "children": [
                        {
                            "Class": "RectCollider",
                            "options": {"w": 400, "h": 20},
                        }
                    ],
                },
                {
                    "Class": "Ray",
                    "options": {
                        "name": "sensor_ray",
                        "pos": [0, 0],
                        "length": 80,
                    },
                },
            ],
        }

        scene_str = json.dumps(scene_json)
        loaded_scene = Scene.from_json(scene_str)
        self.assertEqual(loaded_scene.name, "PhysicsScene")
        self.assertEqual(len(loaded_scene._objects), 2)

        ground = loaded_scene["ground"]
        self.assertIsInstance(ground, Body)
        self.assertTrue(ground.static)


if __name__ == "__main__":
    unittest.main()
