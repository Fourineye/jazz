"""Shared constants, asset paths and input helpers for the Flappy Bird example."""

import os

from jazz import Globals

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Pixel art is drawn at 144x256 and scaled up at runtime
PIXEL_SCALE = 3
WIDTH = 144 * PIXEL_SCALE
HEIGHT = 256 * PIXEL_SCALE
GROUND_Y = 216 * PIXEL_SCALE

# Gameplay tuning, in screen pixels and seconds
GRAVITY = 2000.0
FLAP_VELOCITY = -600.0
MAX_FALL_SPEED = 900.0
SCROLL_SPEED = 180.0
PIPE_INTERVAL = 1.5
PIPE_GAP = 150
PIPE_GAP_MARGIN = 90
MEDALS = ((40, "platinum"), (30, "gold"), (20, "silver"), (10, "bronze"))

# Draw order
Z_BACKGROUND = 0
Z_PIPES = 1
Z_GROUND = 2
Z_BIRD = 3
Z_UI = 5
Z_FLASH = 10

# Physics layers: obstacles (pipes and ground) and score gates
LAYER_OBSTACLES = "0001"
LAYER_GATES = "0010"
LAYER_NONE = "0000"


def asset(name: str) -> str:
    """Returns the absolute path of a file in the asset folder.

    Args:
        name (str): File name, including extension.

    Returns:
        str: Absolute path to the asset.
    """
    return os.path.join(ASSET_DIR, name)


def assets_present() -> bool:
    """Checks that the asset generator has been run.

    Returns:
        bool: True if the asset folder contains the generated files.
    """
    return os.path.isfile(asset("bird.png")) and os.path.isfile(asset("swoosh.wav"))


def play_sound(name: str) -> None:
    """Plays a sound effect from the asset folder.

    Args:
        name (str): Sound name, without extension.
    """
    Globals.sound.play_sound(asset(f"{name}.wav"))


def flap_pressed() -> bool:
    """Checks whether any flap input was pressed this frame.

    Returns:
        bool: True if Space, Up or the left mouse button was pressed.
    """
    return Globals.key.press("space") or Globals.key.press("up") or Globals.mouse.click("left")


def medal_for(score: int) -> str | None:
    """Returns the medal earned for a score.

    Args:
        score (int): Final score.

    Returns:
        str | None: Medal name, or None if the score earns no medal.
    """
    for threshold, name in MEDALS:
        if score >= threshold:
            return name
    return None
