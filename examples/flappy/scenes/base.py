"""Base scene shared by every Flappy Bird scene."""

from jazz import Globals, Scene

DEBUG_KEY = "F3"


class FlappyScene(Scene):
    """Scene with an F3 toggle for jazz's debug rendering, kept on across scene changes."""

    # Class-level so the setting survives the scene being rebuilt on every switch
    debug_enabled: bool = False

    def __init__(self) -> None:
        """Initializes the scene with the current debug setting."""
        super().__init__()
        self._debug = FlappyScene.debug_enabled

    def late_update(self, delta: float) -> None:
        """Toggles debug rendering when F3 is pressed.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        if Globals.key.press(DEBUG_KEY):
            self.toggle_debug()
            FlappyScene.debug_enabled = self._debug
