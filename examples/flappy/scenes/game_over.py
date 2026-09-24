"""Game over scene: animated banner, score panel with count-up, medal, best score and navigation."""

from typing import Any

from jazz import EASE_OUT_BACK, Globals, Label, Sprite, Tween, Vec2

from scenes.base import FlappyScene
from config import HEIGHT, PIXEL_SCALE, WIDTH, asset, medal_for, play_sound
from objects.ground import Ground
from objects.ui import TEXT_OUTLINE, add_art, add_background, make_button
from save import load_best, save_best

PANEL_Y = 380
COUNT_UP_TIME = 0.6


def panel_offset(x: float, y: float) -> Vec2:
    """Converts a point on the 113x57 panel art to a screen offset from the panel's centre.

    Args:
        x (float): Art x coordinate.
        y (float): Art y coordinate.

    Returns:
        Vec2: Offset in screen pixels.
    """
    return Vec2((x - 113 / 2) * PIXEL_SCALE, (y - 57 / 2) * PIXEL_SCALE)


class GameOverScene(FlappyScene):
    """Shows the result of a run. Space or Retry plays again, Menu returns to the title."""

    name = "game_over"

    def __init__(self) -> None:
        """Initializes the GameOverScene."""
        super().__init__()
        self.score: int = 0
        self.best: int = 0
        self.new_best: bool = False
        self.shown_score: float = 0.0
        self.counting: bool = False
        self.ready: bool = False
        self.panel: Sprite | None = None
        self.score_label: Label | None = None
        self.score_shadow: Label | None = None
        self.best_shadow: Label | None = None
        self.best_label: Label | None = None
        self.medal: Sprite | None = None
        self.new_badge: Sprite | None = None
        self.buttons = []

    def on_load(self, data: dict[Any, Any]) -> None:
        """Saves the high score and starts the intro animations.

        Args:
            data (dict[Any, Any]): Must contain "score" from the game scene.
        """
        self.score = int(data.get("score", 0))
        previous_best = load_best()
        self.new_best = self.score > previous_best
        self.best = max(self.score, previous_best)
        if self.new_best:
            save_best(self.best)

        add_background(self)
        self.add_object(Ground())

        banner = add_art(self, "game_over", (WIDTH / 2, 60))
        self.add_object(
            Tween(target_object=banner, target_property="pos", target_value=banner.pos + Vec2(0, 110), time=0.5, easing=EASE_OUT_BACK, play=True)
        )

        self.build_panel()
        self.create_timer(0.5, self.slide_in_panel, ())

        self.buttons = [
            self.add_object(make_button("retry", (WIDTH / 2 - 80, 540), self.retry, visible=False)),
            self.add_object(make_button("menu", (WIDTH / 2 + 80, 540), self.menu, visible=False)),
        ]

    def build_panel(self) -> None:
        """Creates the score panel below the screen with its labels, medal and NEW badge as children."""
        self.panel = add_art(self, "panel", (WIDTH / 2, HEIGHT + 120))

        font = Globals.resource.get_font(size=36)
        # Shadows are added first so they draw underneath the numbers
        self.score_shadow = self.panel.add_child(self.make_number("0", font, TEXT_OUTLINE, panel_offset(106, 21) + Vec2(2, 2)))
        self.best_shadow = self.panel.add_child(self.make_number(str(self.best), font, TEXT_OUTLINE, panel_offset(106, 45) + Vec2(2, 2)))
        self.score_label = self.panel.add_child(self.make_number("0", font, (255, 255, 255), panel_offset(106, 21)))
        self.best_label = self.panel.add_child(self.make_number(str(self.best), font, (255, 255, 255), panel_offset(106, 45)))
        self.medal = self.panel.add_child(
            Sprite(texture=asset("medal_bronze.png"), scale=(PIXEL_SCALE, PIXEL_SCALE), anchor=("center", "center"), pos=panel_offset(24, 34), visible=False)
        )
        self.new_badge = self.panel.add_child(
            Sprite(texture=asset("new_badge.png"), scale=(PIXEL_SCALE, PIXEL_SCALE), anchor=("center", "center"), pos=panel_offset(66, 38), visible=False)
        )

    @staticmethod
    def make_number(text: str, font: Any, color: tuple[int, int, int], pos: Vec2) -> Label:
        """Creates a right-aligned number label for the panel.

        Args:
            text (str): Initial text.
            font (Any): Pygame font to render with.
            color (tuple[int, int, int]): Text colour.
            pos (Vec2): Offset from the panel's centre.

        Returns:
            Label: The new label.
        """
        return Label(text=text, font=font, text_color=color, pos=pos, anchor=("right", "center"))

    def set_score_text(self, text: str) -> None:
        """Updates the panel's score number and its shadow.

        Args:
            text (str): New text.
        """
        self.score_label.set_text(text)
        self.score_shadow.set_text(text)

    def slide_in_panel(self) -> None:
        """Slides the panel up into place, then starts the score count-up."""
        play_sound("swoosh")
        self.add_object(
            Tween(target_object=self.panel, target_property="pos", target_value=Vec2(WIDTH / 2, PANEL_Y), time=0.5, easing=EASE_OUT_BACK, on_end=self.start_count, play=True)
        )

    def start_count(self) -> None:
        """Begins counting the score up on the panel."""
        self.counting = True

    def finish_count(self) -> None:
        """Shows the final score, medal, NEW badge and the buttons."""
        self.counting = False
        self.set_score_text(str(self.score))
        medal = medal_for(self.score)
        if medal is not None:
            self.medal.texture = asset(f"medal_{medal}.png")
            self.medal.visible = True
        if self.new_best:
            self.new_badge.visible = True
            play_sound("point")
        for button in self.buttons:
            button.visible = True
        self.ready = True

    def update(self, delta: float) -> None:
        """Runs the count-up and listens for Space.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        if self.counting:
            step = max(self.score / COUNT_UP_TIME, 1.0) * delta
            self.shown_score = min(self.score, self.shown_score + step)
            self.set_score_text(str(int(self.shown_score)))
            if self.shown_score >= self.score:
                self.finish_count()
        elif self.ready and Globals.key.press("space"):
            self.retry()

    def retry(self) -> None:
        """Starts a new run."""
        Globals.app.set_next_scene("game")
        self.stop()

    def menu(self) -> None:
        """Returns to the main menu."""
        Globals.app.set_next_scene("menu")
        self.stop()
