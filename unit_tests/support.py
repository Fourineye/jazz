"""Shared fixtures for the Jazz engine unit tests.

``JazzTestCase`` gives every test the same headless ``Application``, a fresh
``Scene`` and a clean copy of ``Globals`` and ``SETTINGS``. The mock classes
stand in for GPU resources when a test only needs sizes and draw calls.
"""

import copy
import unittest
from unittest import mock

import pygame

from jazz import Application, Globals, Scene
from jazz.global_dict import SETTINGS

APP_SIZE = (800, 600)

_app: Application | None = None


def get_app() -> Application:
    """Returns the shared headless Application, creating it on first use.

    ``load_ini`` is patched out so creating the Application does not write
    ``.jini`` into the working directory.

    Returns:
        Application: The Application shared by every test.
    """
    global _app
    if _app is None:
        with mock.patch("jazz.engine.application.load_ini"):
            _app = Application(*APP_SIZE, "Jazz Tests")
    return _app


def _bind_globals(app: Application) -> None:
    """Points every ``Globals`` system at the shared Application.

    Args:
        app (Application): The Application whose systems are exposed.
    """
    Globals.app = app
    Globals.input = app._input
    Globals.key = app._input.key
    Globals.mouse = app._input.mouse
    Globals.window = app._window
    Globals.renderer = app._renderer
    Globals.display = app._display
    Globals.sound = app._sound
    Globals.resource = app._resource


def _restore(saved_globals: dict[str, object], saved_settings: dict[str, dict]) -> None:
    """Restores ``Globals`` and ``SETTINGS`` from a snapshot.

    Args:
        saved_globals (dict[str, object]): Public ``Globals`` attributes to set back.
        saved_settings (dict[str, dict]): Deep copy of ``SETTINGS`` to restore.
    """
    for key, value in saved_globals.items():
        setattr(Globals, key, value)
    SETTINGS.clear()
    SETTINGS.update(saved_settings)


class JazzTestCase(unittest.TestCase):
    """Test case with the shared Application and a fresh Scene per test.

    ``Globals`` and ``SETTINGS`` are restored after every test, so tests do not
    depend on run order. Subclasses that override ``setUp`` must call
    ``super().setUp()``.

    Attributes:
        app (Application): The shared headless Application.
        scene (Scene): A new Scene, also set as ``Globals.scene``.
    """

    def setUp(self) -> None:
        """Snapshots ``Globals`` and ``SETTINGS``, binds the shared Application and creates a Scene."""
        saved_globals = {k: v for k, v in vars(Globals).items() if not k.startswith("_")}
        self.addCleanup(_restore, saved_globals, copy.deepcopy(SETTINGS))

        self.app = get_app()
        _bind_globals(self.app)
        self.scene = Scene()
        Globals.scene = self.scene

    def patch_globals(self, **values: object) -> None:
        """Replaces ``Globals`` attributes for the rest of the test.

        Args:
            **values: Attribute names on ``Globals`` mapped to their replacements.
        """
        for name, value in values.items():
            patcher = mock.patch.object(Globals, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)


class MockTexture:
    """Texture stand-in with a size and a no-op draw."""

    def __init__(self, size: tuple[int, int] = (32, 32)) -> None:
        self.width = size[0]
        self.height = size[1]

    def draw(self, *args, **kwargs) -> None:
        pass

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.width, self.height)


class MockFont:
    """Font stand-in where every character is 10px wide and lines are 20px tall."""

    def size(self, text: str) -> tuple[int, int]:
        return (len(text) * 10, 20)

    def get_height(self) -> int:
        return 20

    def render(self, *args, **kwargs) -> MockTexture:
        return MockTexture()


class MockResource:
    """ResourceManager stand-in that hands out MockTextures."""

    def __init__(self) -> None:
        self._textures = {}

    def clear(self) -> None:
        pass

    def get_texture(self, name) -> MockTexture:
        if isinstance(name, MockTexture):
            return name
        return MockTexture()

    def add_texture(self, texture, id, force=False) -> MockTexture:
        if not isinstance(texture, MockTexture):
            texture = MockTexture(texture.get_size()) if hasattr(texture, "get_size") else MockTexture()
        self._textures[id] = texture
        return texture

    def purge_sprite_textures(self, sprite_id: str) -> None:
        for key in [k for k in self._textures if k == sprite_id or k.startswith(f"{sprite_id}:")]:
            del self._textures[key]

    def get_color(self, color) -> MockTexture:
        return MockTexture()

    def get_font(self, size: int = 24) -> MockFont:
        return MockFont()

    def get_styled_texture(self, size, color, *args, **kwargs) -> MockTexture:
        return MockTexture(size)
