from ..engine.base_object import GameObject

class UIContainer(GameObject):
    """Stub class for UIContainer component."""
    def __init__(self, name: str = "UIContainer", **kwargs) -> None:
        """Initializes the UIContainer component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "UIContainer".
        """
        super().__init__(name, **kwargs)
