"""
Script callbacks for JSON-serialized showcase scenes.
"""

from jazz import Globals, Vec2, Color, Draw, Texture, pygame


def return_to_menu(data=None) -> None:
    """Navigates back to the JSON Menu scene."""
    if hasattr(Globals, "app") and Globals.app is not None:
        Globals.app.set_next_scene("MenuV2")


def check_space_return(obj, delta: float) -> None:
    """Frame update callback checking for Space key press to return to Menu."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        return_to_menu()


def rotate_object(obj, delta: float) -> None:
    """Updates object rotation."""
    obj = Globals.scene["rotating_object"] if "rotating_object" in Globals.scene else None
    if obj is not None:
        obj.rotate(60 * delta)


def on_debug_square_update(obj, delta: float) -> None:
    """Rotates square in debug test."""
    obj = Globals.scene["square"] if "square" in Globals.scene else None
    if obj is not None:
        obj.rotate(36 * delta)


def on_form_submit(text: str = "") -> None:
    """Handles submission of settings form text input."""
    label = Globals.scene["status_label"] if "status_label" in Globals.scene else None
    if label is not None:
        label.set_text(f"Status: Submitted '{text}'!")
