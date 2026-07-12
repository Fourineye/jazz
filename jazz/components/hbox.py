from .sprite import Sprite

class HBox(Sprite):
    """Stub class for HBox UI container component."""
    def __init__(self, name: str = "HBox", **kwargs) -> None:
        """Initializes the HBox component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "HBox".
        """
        super().__init__(name, **kwargs)
