import pygame
from .sprite import Sprite
from .label import Label
from ..global_dict import Globals
from ..utils import Color, Rect, Surface, Vec2

class TextBox(Sprite):
    """Event-driven interactive input TextBox component supporting keyboard entry and focus toggles."""

    def __init__(self, name: str = "TextBox", **kwargs) -> None:
        """Initializes the TextBox component.

        Args:
            name (str, optional): The name of the textbox. Defaults to "TextBox".
            font (Font, optional): Custom pygame Font object. Defaults to None.
            fontsize (int, optional): Size of font to generate if no custom font is provided. Defaults to 24.
            text_color (tuple | Color, optional): RGB/Color value for input text. Defaults to white.
            text (str, optional): The initial text contents. Defaults to " ".
            size (tuple, optional): Manual width and height. Defaults to bounds computed based on text.
            bg_color (tuple | Color, optional): Background fill color. Defaults to dark gray.
            blink_rate (float, optional): Cursor blinking cycle interval in seconds. Defaults to 0.25.
            on_submit (callable, optional): Callback triggered when 'enter' is pressed. Defaults to None.
            on_change (callable, optional): Callback triggered when text content changes. Defaults to None.
        """
        font = kwargs.get("font", None)
        if font is None:
            font_size = kwargs.get("fontsize", 24)
            font = Globals.resource.get_font(size=font_size)
        
        text_color = kwargs.get("text_color", Color(255, 255, 255))
        text = kwargs.get("text", " ")
        
        if "texture" not in kwargs:
            if "size" in kwargs:
                size = Vec2(kwargs["size"])
            else:
                if text.strip():
                    size = Vec2(font.size(text)) + (10, 10)
                else:
                    size = Vec2(150, font.get_height() + 10)
            box = Surface(size)
            box.fill(kwargs.get("bg_color", Color(32, 32, 32)))
            kwargs["texture"] = box
            
        super().__init__(name, **kwargs)
        
        self._text = Label(
            font=font,
            text_color=text_color,
            text=text,
            pos=(self._draw_offset[0] + 5, self._draw_offset[1] + self._size.y / 2),
            anchor=(0, 1)
        )
        self.add_child(self._text)

        self._cursor = Label(
            font=font,
            text_color=text_color,
            text="|",
            anchor=(0, 1),
            pos=(self._draw_offset[0] + self._size.x, self._draw_offset[1] + self._size.y / 2),
            visible=False
        )
        self.add_child(self._cursor)

        self._blink_rate: float = kwargs.get("blink_rate", 0.25)
        self._blink: float = 0.0
        self._active: bool = False
        
        self._on_submit = kwargs.get("on_submit", None)
        self._on_change = kwargs.get("on_change", None)
        
        # Initialize cursor position
        self.set_text(text)

    @property
    def active(self) -> bool:
        """bool: Check if the textbox is active/focused and accepting text input."""
        return self._active

    @active.setter
    def active(self, val: bool) -> None:
        if self._active != val:
            self._active = val
            self._blink = 0.0
            self._cursor.visible = val
            if val:
                Globals.key.start_text_input()
            else:
                Globals.key.stop_text_input()

    def update(self, delta: float) -> None:
        """Processes time deltas, cursor blinks, keyboard key presses, and focus click selections.

        Args:
            delta (float): Time since the last frame in seconds.
        """
        if self.active:
            self._blink += delta
            if self._blink >= self._blink_rate:
                self._blink -= self._blink_rate
                self._cursor.visible = not self._cursor.visible

            # Handle text input
            if Globals.key.text:
                self.set_text(self._text.text_content + Globals.key.text)
                self._blink = 0.0
                self._cursor.visible = True

            # Handle backspace
            if Globals.key.press("backspace"):
                self.set_text(self._text.text_content[:-1])
                self._blink = 0.0
                self._cursor.visible = True

            # Handle enter
            if Globals.key.press("enter"):
                self.active = False
                if callable(self._on_submit):
                    self._on_submit(self._text.text_content)

            # Deactivate if user clicks outside
            if Globals.mouse.click(0) and not self.rect.collidepoint(Globals.mouse.pos):
                self.active = False
        else:
            if Globals.mouse.click(0) and self.rect.collidepoint(Globals.mouse.pos):
                self.active = True

    def set_text(self, text: str) -> None:
        """Updates text display contents, re-renders the label, and updates cursor coordinates.

        Args:
            text (str): The new text string.
        """
        old_text = self._text.text_content
        self._text.set_text(text)
        self._cursor.local_pos = (
            self._text.local_pos.x + self._text._size.x,
            self._text.local_pos.y
        )
        if old_text != text and callable(self._on_change):
            self._on_change(text)

    @property
    def text(self) -> str:
        """str: Gets the text string content of the textbox."""
        return self._text.text_content

    @text.setter
    def text(self, new_text: str) -> None:
        self.set_text(new_text)
