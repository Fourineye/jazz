"""Shared scenery and UI helpers: background, outlined labels, image buttons, flash overlay and bob tweens."""

import math
from typing import Callable

from jazz import Button, GameObject, Globals, Image, Label, Scene, Sprite, Tween, Vec2

from config import HEIGHT, PIXEL_SCALE, WIDTH, Z_BACKGROUND, Z_FLASH, Z_UI, asset

TEXT_OUTLINE = (84, 56, 71)


class ShadowLabel(GameObject):
    """Screen-space text drawn twice (a dark drop shadow, then the text) for readability."""

    def __init__(self, text: str = "", fontsize: int = 48, color: tuple[int, int, int] = (255, 255, 255), anchor: tuple[str, str] = ("center", "center"), **kwargs) -> None:
        """Initializes the ShadowLabel.

        Args:
            text (str, optional): Initial text. Defaults to "".
            fontsize (int, optional): Font size. Defaults to 48.
            color (tuple[int, int, int], optional): Text colour. Defaults to white.
            anchor (tuple[str, str], optional): Horizontal and vertical anchor. Defaults to centred.
            pos (tuple | Vec2, optional): Position. Defaults to (0, 0).
        """
        kwargs.setdefault("screen_space", True)
        kwargs.setdefault("z", Z_UI)
        super().__init__("ShadowLabel", **kwargs)
        shadow = max(2, fontsize // 16)
        self.shadow: Label = self.add_child(
            Label(text=text, fontsize=fontsize, text_color=TEXT_OUTLINE, pos=(shadow, shadow), anchor=anchor)
        )
        self.label: Label = self.add_child(Label(text=text, fontsize=fontsize, text_color=color, anchor=anchor))

    def set_text(self, text: str) -> None:
        """Updates the text of the label and its shadow.

        Args:
            text (str): New text.
        """
        self.shadow.set_text(text)
        self.label.set_text(text)


def add_background(scene: Scene) -> Sprite:
    """Adds the sky and city background to a scene.

    Args:
        scene (Scene): The scene to add it to.

    Returns:
        Sprite: The background sprite.
    """
    return scene.add_object(
        Sprite(
            texture=asset("background.png"),
            scale=(PIXEL_SCALE, PIXEL_SCALE),
            anchor=("left", "top"),
            z=Z_BACKGROUND,
        )
    )


def add_art(scene: Scene, name: str, pos: tuple[float, float] | Vec2, **kwargs) -> Sprite:
    """Adds a centred, pixel-scaled sprite from the asset folder.

    Args:
        scene (Scene): The scene to add it to.
        name (str): PNG name, without extension.
        pos (tuple | Vec2): Centre position.
        **kwargs: Extra Sprite arguments.

    Returns:
        Sprite: The new sprite.
    """
    kwargs.setdefault("z", Z_UI)
    kwargs.setdefault("screen_space", True)
    return scene.add_object(
        Sprite(
            texture=asset(f"{name}.png"),
            scale=(PIXEL_SCALE, PIXEL_SCALE),
            anchor=("center", "center"),
            pos=pos,
            **kwargs,
        )
    )


def make_button(name: str, pos: tuple[float, float], callback: Callable[[], None], **kwargs) -> Button:
    """Creates a pixel-art Button from the button_<name> textures.

    Args:
        name (str): Button name (play, quit, retry, menu).
        pos (tuple[float, float]): Centre position.
        callback (Callable[[], None]): Called when the button is clicked.
        **kwargs: Extra Button arguments.

    Returns:
        Button: The new button. Add it to a scene to use it.
    """
    kwargs.setdefault("z", Z_UI)
    return Button(
        unpressed=Globals.resource.get_texture(asset(f"button_{name}.png")),
        hover=Globals.resource.get_texture(asset(f"button_{name}_hover.png")),
        pressed=Globals.resource.get_texture(asset(f"button_{name}_pressed.png")),
        scale=(PIXEL_SCALE, PIXEL_SCALE),
        pos=pos,
        callback=callback,
        **kwargs,
    )


def add_flash(scene: Scene) -> Sprite:
    """Adds a full-screen white overlay, fully transparent until its alpha is raised.

    The texture is wrapped in an Image because jazz only applies Sprite.alpha to
    Image-backed sprites, see FINDINGS.md #2.

    Args:
        scene (Scene): The scene to add it to.

    Returns:
        Sprite: The overlay sprite.
    """
    return scene.add_object(
        Sprite(
            texture=Image(Globals.resource.get_texture(asset("white.png"))),
            scale=(WIDTH, HEIGHT),
            anchor=("left", "top"),
            alpha=0,
            z=Z_FLASH,
            screen_space=True,
        )
    )


def bob(target: GameObject, amplitude: float = 10.0, period: float = 0.8, phase: float = 0.0) -> Tween:
    """Creates a looping Tween that bobs an object up and down around its current position.

    Args:
        target (GameObject): The object to bob.
        amplitude (float, optional): Vertical distance in pixels. Defaults to 10.
        period (float, optional): Seconds per full bob. Defaults to 0.8.
        phase (float, optional): Starting phase, in cycles. Defaults to 0.

    Returns:
        Tween: The playing tween. Add it to a scene to run it.
    """
    return Tween(
        target_object=target,
        target_property="pos",
        target_value=target.pos + Vec2(0, -amplitude),
        time=period,
        easing=lambda t: math.sin(2 * math.pi * (t + phase)),
        loop=True,
        play=True,
    )
