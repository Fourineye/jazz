"""Main menu scene: title, idle bird, best score, Play and Quit buttons."""

from typing import Any

from jazz import Globals

from scenes.base import FlappyScene
from config import SCROLL_SPEED, WIDTH, Z_UI
from objects.bird import Bird
from objects.ground import Ground
from objects.ui import ShadowLabel, add_art, add_background, bob, make_button
from save import load_best


class MenuScene(FlappyScene):
    """Title screen. Space, Enter, Play or a click anywhere except Quit starts the game."""

    name = "menu"

    def __init__(self) -> None:
        """Initializes the MenuScene."""
        super().__init__()
        self.ground: Ground | None = None
        self.quit_button = None
        self.starting: bool = False

    def on_load(self, data: dict[Any, Any]) -> None:
        """Builds the menu.

        Args:
            data (dict[Any, Any]): Data from the previous scene. Unused.
        """
        add_background(self)
        self.ground = self.add_object(Ground())

        title = add_art(self, "title", (WIDTH / 2, 180))
        self.add_object(bob(title, amplitude=8, period=1.6))

        bird = self.add_object(Bird(pos=(WIDTH / 2, 300), z=Z_UI))
        self.add_object(bob(bird, amplitude=10, period=0.8))

        self.add_object(ShadowLabel(text=f"Best: {load_best()}", fontsize=32, pos=(WIDTH / 2, 390)))

        self.add_object(make_button("play", (WIDTH / 2, 480), self.start_game))
        self.quit_button = self.add_object(make_button("quit", (WIDTH / 2, 560), Globals.app.stop))

    def update(self, delta: float) -> None:
        """Scrolls the ground and listens for keyboard or click starts.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        self.ground.scroll(SCROLL_SPEED * delta)
        if Globals.key.press("space") or Globals.key.press("enter"):
            self.start_game()
        elif Globals.mouse.click("left") and not self.quit_button.rect.collidepoint(Globals.mouse.pos):
            self.start_game()

    def start_game(self) -> None:
        """Switches to the game scene."""
        if self.starting:
            return
        self.starting = True
        Globals.app.set_next_scene("game")
        self.stop()
