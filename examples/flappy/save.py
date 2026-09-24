"""High score persistence for the Flappy Bird example."""

import json
import os

from config import BASE_DIR

SAVE_PATH = os.path.join(BASE_DIR, "save.json")


def load_best() -> int:
    """Loads the saved high score.

    Returns:
        int: The best score, or 0 if there is no valid save file.
    """
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return int(json.load(f).get("best", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def save_best(score: int) -> None:
    """Writes the high score to disk.

    Args:
        score (int): The score to save.
    """
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump({"best": score}, f)
