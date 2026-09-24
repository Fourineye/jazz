"""
Script callbacks for JSON-serialized showcase scenes.
"""

from jazz import Globals, Vec2, Color, Draw, Texture, pygame, ProgressBar


def return_to_menu(data=None) -> None:
    """Navigates back to the JSON Menu scene."""
    if hasattr(Globals, "app") and Globals.app is not None:
        Globals.app.set_next_scene("MenuV2")
        Globals.scene.stop()


def check_space_return(scene, delta: float) -> None:
    """Frame update callback checking for Space key press to return to Menu."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        return_to_menu()


def rotate_object(self, delta: float) -> None:
    """Updates object rotation."""
    self.rotate(60 * delta)


def move_bar(obj: ProgressBar, delta: float) -> None:
    """Frame update callback that advances the progress bar value, wrapping at max_value."""
    obj.update_value((obj.value + delta) % obj.max_value)

def on_debug_square_update(obj, delta: float) -> None:
    """Rotates square in debug test."""
    obj.rotate(36 * delta)


def on_form_submit(text: str = "") -> None:
    """Handles submission of settings form text input."""
    label = Globals.scene["status_label"] if "status_label" in Globals.scene else None
    if label is not None:
        label.set_text(f"Status: Submitted '{text}'!")
