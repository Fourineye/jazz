import pygame
from ..sprite import Sprite
from .label import Label
from ...global_dict import Globals
from ...utils import Color, Rect, Surface, Vec2, Texture

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
            radius (int, optional): Corner rounding radius for the textbox background. Defaults to 4.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
            border_color (tuple | Color, optional): Border outline color. Defaults to light gray.
            border_width (int, optional): Border stroke thickness. Defaults to 1.
            field_color (tuple | Color, optional): Background color of the text input area. Defaults to None (transparent/bg_color).
            shadow_offset (tuple, optional): X and Y offset for the textbox shadow. Defaults to (0, 0).
            shadow_color (tuple | Color, optional): Color of the textbox shadow. Defaults to black with alpha 80.
            shadow_blur (int, optional): Soft blur step size of the textbox shadow. Defaults to 0.
            hover_bg_color (tuple | Color, optional): Background color when hovered/active. Defaults to slightly brightened bg_color.
            hover_border_color (tuple | Color, optional): Border color when hovered/active. Defaults to slightly brightened border_color.
        """
        self._kwargs = kwargs.copy()
        on_submit_arg = kwargs.get("on_submit", None)
        if isinstance(on_submit_arg, str):
            self._on_submit_path = on_submit_arg
            from ...engine.serializer import Serializer
            kwargs["on_submit"] = Serializer.resolve_script(on_submit_arg)

        on_change_arg = kwargs.get("on_change", None)
        if isinstance(on_change_arg, str):
            self._on_change_path = on_change_arg
            from ...engine.serializer import Serializer
            kwargs["on_change"] = Serializer.resolve_script(on_change_arg)

        font = kwargs.get("font", None)
        if font is None:
            font_size = kwargs.get("fontsize", 24)
            font = Globals.resource.get_font(size=font_size)
        text_color = kwargs.get("text_color", Color(255, 255, 255))
        text = kwargs.get("text", " ")
        # Extract styled texture options
        radius = kwargs.get("radius", 4)
        style = kwargs.get("style", "flat")
        bg_color = kwargs.get("bg_color", Color(32, 32, 35))
        border_color = kwargs.get("border_color", Color(60, 60, 65))
        border_width = kwargs.get("border_width", 1)
        shadow_offset = kwargs.get("shadow_offset", (0, 0))
        shadow_color = kwargs.get("shadow_color", Color(0, 0, 0, 80))
        shadow_blur = kwargs.get("shadow_blur", 0)
        
        if "texture" not in kwargs:
            if "size" in kwargs:
                size = Vec2(kwargs["size"])
            else:
                if text.strip():
                    size = Vec2(font.size(text)) + (10, 10)
                else:
                    size = Vec2(150, font.get_height() + 10)
            
            kwargs["texture"] = Globals.resource.get_styled_texture(
                size,
                bg_color,
                radius=radius,
                shadow_offset=shadow_offset,
                shadow_color=shadow_color,
                shadow_blur=shadow_blur,
                style=style,
                border_color=border_color,
                border_width=border_width
            )
            
        super().__init__(name, **kwargs)
        self.font = font
        
        # Compile hover texture
        self._unhovered_texture = self.texture
        self._hovered_texture = self.texture
        
        if "texture" not in kwargs:
            bg_col = Color(bg_color)
            default_hover_bg = Color(
                min(255, bg_col.r + 15),
                min(255, bg_col.g + 15),
                min(255, bg_col.b + 15),
                bg_col.a
            )
            if border_color is not None:
                border_col = Color(border_color)
                default_hover_border = Color(
                    min(255, border_col.r + 30),
                    min(255, border_col.g + 30),
                    min(255, border_col.b + 30),
                    border_col.a
                )
            else:
                default_hover_border = None
                
            hover_bg_color = kwargs.get("hover_bg_color", kwargs.get("hover_color", default_hover_bg))
            hover_border_color = kwargs.get("hover_border_color", default_hover_border)
            
            self._hovered_texture = Globals.resource.get_styled_texture(
                self._size,
                hover_bg_color,
                radius=radius,
                shadow_offset=shadow_offset,
                shadow_color=shadow_color,
                shadow_blur=shadow_blur,
                style=style,
                border_color=hover_border_color,
                border_width=border_width
            )
        
        # Inner field color background directly behind text (if specified)
        field_color = kwargs.get("field_color", None)
        if field_color is not None:
            pad_x = abs(shadow_offset[0]) + shadow_blur * 2
            pad_y = abs(shadow_offset[1]) + shadow_blur * 2
            visible_w = self._size.x - pad_x * 2
            visible_h = self._size.y - pad_y * 2
            
            field_w = visible_w - border_width * 2
            field_h = visible_h - border_width * 2
            
            if field_w > 0 and field_h > 0:
                field_surf = pygame.Surface((int(field_w), int(field_h)), pygame.SRCALPHA)
                field_radius = max(0, radius - border_width)
                pygame.draw.rect(field_surf, pygame.Color(field_color), (0, 0, int(field_w), int(field_h)), border_radius=field_radius)
                field_tex = Texture.from_surface(Globals.renderer, field_surf)
                
                field_pos = (self._draw_offset[0] + border_width, self._draw_offset[1] + border_width)
                self._field_bg = Sprite(name="field_bg", texture=field_tex, pos=field_pos, anchor=(0, 0))
                self.add_child(self._field_bg)
        
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
        self._text_content = text
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
            self.set_text(self._text_content)

    def _engine_update(self, delta: float) -> None:
        """Processes time deltas, cursor blinks, keyboard key presses, and focus click selections.

        Args:
            delta (float): Time since the last frame in seconds.
        """
        # Update hover texture state
        is_hovered = self.rect.collidepoint(Globals.mouse.pos)
        if is_hovered or self.active:
            self.texture = self._hovered_texture
        else:
            self.texture = self._unhovered_texture

        if self.active:
            self._blink += delta
            if self._blink >= self._blink_rate:
                self._blink -= self._blink_rate
                self._cursor.visible = not self._cursor.visible

            # Handle text input
            if Globals.key.text:
                self.set_text(self._text_content + Globals.key.text)
                self._blink = 0.0
                self._cursor.visible = True

            # Handle backspace
            if Globals.key.press("backspace"):
                self.set_text(self._text_content[:-1])
                self._blink = 0.0
                self._cursor.visible = True

            # Handle enter
            if Globals.key.press("enter"):
                self.active = False
                if callable(self._on_submit):
                    self._on_submit(self._text_content)

            # Deactivate if user clicks outside
            if Globals.mouse.click(0) and not self.rect.collidepoint(Globals.mouse.pos):
                self.active = False
        else:
            if Globals.mouse.click(0) and self.rect.collidepoint(Globals.mouse.pos):
                self.active = True

    def set_text(self, text: str) -> None:
        """Updates text display contents, handles scrolling bounds, and updates cursor coordinates.

        Args:
            text (str): The new text string.
        """
        old_full_text = getattr(self, "_text_content", "")
        self._text_content = text
        
        # Calculate the available width for drawing text
        available_w = max(0, self._size.x - 12)
        
        # Squeeze or slice text to fit within the box bounds based on active state
        if self.active:
            # Show the suffix (last characters) so that the cursor stays on screen
            start_idx = 0
            while start_idx < len(text):
                w = self.font.size(text[start_idx:])[0]
                if w <= available_w:
                    break
                start_idx += 1
            visible_text = text[start_idx:]
        else:
            # Show the prefix (first characters) for normal read order
            end_idx = len(text)
            while end_idx > 0:
                w = self.font.size(text[:end_idx])[0]
                if w <= available_w:
                    break
                end_idx -= 1
            visible_text = text[:end_idx]

        self._text.set_text(visible_text)
        
        self._cursor.local_pos = (
            self._text.local_pos.x + self._text._size.x,
            self._text.local_pos.y
        )
        
        if old_full_text != text and callable(self._on_change):
            self._on_change(text)

    @property
    def text(self) -> str:
        """str: Gets the full text string content of the textbox."""
        return self._text_content

    @text.setter
    def text(self, new_text: str) -> None:
        """Sets the full text string content of the textbox.

        Args:
            new_text (str): The new text contents.
        """
        self.set_text(new_text)


from ...engine.serializer import Serializer

Serializer.register_class(TextBox)
