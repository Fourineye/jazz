from .sprite import Sprite

class VBox(Sprite):
    """Stub class for VBox UI container component."""
    def __init__(self, name: str = "VBox", **kwargs) -> None:
        """Initializes the VBox component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "VBox".
        """
        super().__init__(name, **kwargs)
