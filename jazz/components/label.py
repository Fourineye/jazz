import pygame


from .sprite import Sprite
from ..global_dict import Globals
from ..utils import Vec2


class Label(Sprite):
    """UI Component for displaying static or dynamic text content."""

    def __init__(self, name: str = "label", **kwargs) -> None:
        """Initializes the Label component.

        Args:
            name (str, optional): The name of the label. Defaults to "label".
            fontsize (int, optional): The size of the text. Defaults to 24.
            font (Font, optional): Custom pygame Font object. Defaults to Roboto-Regular.
            text_color (tuple | Color, optional): RGB/Color values for text color. Defaults to white.
            text (str, optional): The initial text content. Defaults to " ".
        """
        font_size = kwargs.get("fontsize", 24)
        self.font = kwargs.get("font", None)
        if self.font is None:
            self.font = Globals.resource.get_font(size=font_size)

        self.text_color = kwargs.get("text_color", (255, 255, 255))
        self.text_content: str = kwargs.get("text", " ")
        self._dirty: bool = True
        self._real_size: Vec2 = Vec2()

        super().__init__(name, **kwargs)

    def _update_text_texture(self) -> None:
        """Re-renders the font surface to update the underlying texture if marked dirty."""
        if not hasattr(self, "text_content") or not self._dirty or self.font is None:
            return
        self._dirty = False
        if self.text_content:
            surf = self.font.render(self.text_content, True, self.text_color)
            self.texture = surf
        else:
            surf = self.font.render(" ", True, self.text_color)
            self.texture = surf
            self._real_size = Vec2(0, self._real_size.y)
            self._hardware_offset()


    @property
    def _size(self) -> Vec2:
        """Vec2: Gets the size vector of the label sprite, updating if dirty."""
        if self._dirty:
            self._update_text_texture()
        return self._real_size

    @_size.setter
    def _size(self, val: Vec2) -> None:
        self._real_size = Vec2(val)

    @property
    def texture(self):
        """Texture | Image: Gets the active text texture asset, re-rendering if dirty."""
        if self._dirty:
            self._update_text_texture()
        return super().texture

    @texture.setter
    def texture(self, new_texture) -> None:
        """Sets the texture asset, refreshing dimensions and offsets.

        Args:
            new_texture (str | Texture | Image | Surface): Asset key or source image surface.
        """
        fset = Sprite.texture.fset
        if fset is not None:
            fset(self, new_texture)

    def set_text(self, text: str) -> None:
        """Updates the text content and marks the label dirty.

        Args:
            text (str): The new text string to show.
        """
        if not isinstance(text, str):
            text = str(text)
        if self.text_content != text:
            self.text_content = text
            self._dirty = True

    def append_text(self, text: str) -> None:
        """Appends text to the existing content and updates the label.

        Args:
            text (str): The string to append.
        """
        self.set_text(self.text_content + text)

    def render(self, offset: Vec2) -> None:
        """Draws the text sprite onto the display, re-rendering text if dirty.

        Args:
            offset (Vec2): Viewport rendering offset to apply.
        """
        if self._dirty:
            self._update_text_texture()
        super().render(offset)


