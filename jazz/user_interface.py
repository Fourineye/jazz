import pygame as pg

from .engine.base_object import GameObject
from .utils import color_mult, map_range

pg.font.init()
# Constants declaration
SYS_FONT = pg.font.SysFont(pg.font.get_fonts()[0], 24)
DEFAULT_FONT = SYS_FONT
BUTTON_PRESSED = pg.USEREVENT
H_CENTERED = 1
V_CENTERED = 2
ON_RELEASE = 4
CLEAR_ON_INPUT = 8
CLEAR_ON_FIRST_INPUT = 16


def set_default_font(font):
    global DEFAULT_FONT
    if not isinstance(font, pg.font.Font):
        raise TypeError("Must pass a Font object")
    DEFAULT_FONT = font


# Base UI Class
class BaseUI(GameObject):
    def __init__(self, **kwargs):
        super().__init__(self, name="UI",**kwargs)
        self.screen_layer = kwargs.get("screen_layer", True)
        self.font = kwargs.get("font", DEFAULT_FONT)


# Container Class
class UIContainer:
    def __init__(self, initial_items=None, visible=True, **kwargs):
        self.game_process = kwargs.get("game_process", True)
        self.pause_process = kwargs.get("pause_process", False)
        self.game_input = kwargs.get("game_input", True)
        self.screen_layer = kwargs.get("screen_layer", True)
        self.visible = kwargs.get("visible", True)
        if initial_items:
            self.elements = initial_items
        else:
            self.elements = []
        self.visible = visible

    def process(self, delta):
        if not self.visible:
            return
        for element in self.elements:
            element.process(delta)

    def input(self, INPUT):
        if not self.visible:
            return
        for element in self.elements[::-1]:
            if element.input(INPUT):
                return

    def draw(self, surface, offset=None):
        if not self.visible:
            return
        for element in self.elements:
            element.draw(surface, offset)

    def toggle_visible(self):
        self.visible = not self.visible

    def set_visible(self, visible=True):
        self.visible = visible

    def add(self, element):
        self.elements.append(element)
        element.game_process = False
        element.pause_process = False
        element.game_input = False

    def remove(self, element):
        self.elements.remove(element)
        element.game_process = True
        element.game_input = True


# Vertical Container
class Vbox(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, buttons, event_tag, **kwargs):
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)

        self.buttons = []
        self.padding = kwargs.get("padding", 5)
        self.radius = kwargs.get("radius", 3)
        button_height = (y_dim - self.padding * (buttons + 1)) / buttons
        flags = kwargs.get("flags", 3)

        for button in range(buttons):
            but = SimpleButton(
                x + self.padding,
                y + self.padding + (button_height + self.padding) * button,
                x_dim - self.padding * 2,
                button_height,
                "button",
                [event_tag, button],
                flags,
                font=self.font,
            )

            self.buttons.append(but)
        text = kwargs.get("text", None)
        if text:
            if len(text) == buttons:
                for i, t in enumerate(text):
                    self.buttons[i].set_text(t)
        self.color = kwargs.get("color", (128, 128, 128))
        self.visible = kwargs.get("visible", True)
        pg.draw.rect(
            self.image, self.color, self.image.get_rect(), border_radius=self.radius
        )

    def input(self, INPUT):
        if self.visible:
            for button in self.buttons:
                if button.input(INPUT):
                    return True
            if INPUT.mouse.click("left"):
                if self.rect.collidepoint(INPUT.mouse.pos):
                    return True
        return False

    def process(self, delta):
        if self.visible:
            for button in self.buttons:
                button.process(delta)

    def draw(self, surface, offset=None):
        if self.visible:
            surface.blit(self.image, self.rect)
            for button in self.buttons:
                button.draw(surface)

    def toggle_visible(self):
        self.visible = not self.visible

    def set_text(self, index, text):
        if index < len(self.buttons):
            self.buttons[index].set_text(text)
        else:
            return False


# TODO Horizontal Container
class HBox(BaseUI):
    pass


#  Button Class
class SimpleButton(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, text, event_tag, flags=3, **kwargs):
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)
        self.event = pg.event.Event(
            BUTTON_PRESSED, {"source": "Button", "flag": event_tag}
        )
        self.callback = kwargs.get("callback", None)

        self.radius = kwargs.get("radius", 3)
        self.padding = kwargs.get("padding", 5)
        self.text_color = kwargs.get("text_color", (255, 255, 255))

        self.text = self.font.render(text, True, self.text_color)
        self.text_size = self.text.get_size()
        self._color = kwargs.get("color", (128, 128, 128))
        self.unpressed_color = self.color
        self.pressed_color = color_mult(self.color, 0.9)
        self.hover_color = color_mult(self.color, 1.2)

        # Flags
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.on_release = flags & 4 == 4
        self.pressed = False

        self.update_image()

    def input(self, INPUT):
        if not self.visible:
            return
        if INPUT.mouse.click("left"):
            if self.rect.collidepoint(INPUT.mouse.pos):
                if not self.on_release:
                    if callable(self.callback):
                        self.callback()
                    pg.event.post(self.event)
                self.pressed = True
                self._color = self.pressed_color
                return True
        if INPUT.mouse.release("left"):
            if self.rect.collidepoint(INPUT.mouse.pos):
                if self.on_release and self.pressed:
                    if callable(self.callback):
                        self.callback()
                    pg.event.post(self.event)
                self.pressed = False
                self._color = self.unpressed_color
                return True
        return False

    def process(self, _delta):
        if not self.visible:
            return
        mouse_pos = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and not self.pressed:
            self._color = self.hover_color
        elif not self.pressed:
            self._color = self.unpressed_color
        elif not self.rect.collidepoint(mouse_pos):
            self.pressed = False
            self._color = self.unpressed_color
        self.update_image()

    def draw(self, surface, offset=None):
        if self.visible:
            surface.blit(self.image, self.rect)

    def set_flags(self, flags):
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.on_release = flags & 4 == 4
        self.update_image()

    def set_text(self, text):
        self.text = self.font.render(text, True, self.text_color)
        self.text_size = self.text.get_size()
        self.update_image()

    def update_image(self):
        draw_pos = [self.padding, self.padding]

        if self.h_cent:
            draw_pos[0] = self.rect.width / 2 - self.text_size[0] / 2
        if self.v_cent:
            draw_pos[1] = self.rect.height / 2 - self.text_size[1] / 2

        if self.pressed:
            border_color = color_mult(self.color, 0.5)
        else:
            border_color = color_mult(self.color, 1.5)

        pg.draw.rect(
            self.image, self.color, self.image.get_rect(), border_radius=self.radius
        )
        pg.draw.rect(
            self.image,
            border_color,
            self.image.get_rect(),
            border_radius=self.radius,
            width=self.radius,
        )
        self.image.blit(self.text, draw_pos)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self.unpressed_color = self.color
        self.pressed_color = color_mult(self.color, 0.9)
        self.hover_color = color_mult(self.color, 1.2)


# Text Box
class Label(BaseUI):
    def __init__(self, text, flags=3, **kwargs):
        super().__init__(name="label", **kwargs)
        self.color = kwargs.get("color", (128, 128, 128))
        self.text_color = kwargs.get("text_color", (255, 255, 255))

        self.text_content = text
        self.source = self.font.render(text, True, self.text_color)
        self.size = self.source.get_size()

        # Flags
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.update_image()

    def draw(self, surface, offset=None):
        if offset is None:
            offset = pg.Vector2()
        surface.blit(self.image, self.rect.topleft + offset)

    def set_text(self, text):
        if self.text_content != text:
            self.text_content = text
            self.source = self.font.render(text, True, self.text_color)
            self.text_size = self.text.get_size()
            self.update_image()

    def update_image(self):
        draw_pos = [self.padding, self.padding]
        if self.h_cent:
            draw_pos[0] = self.rect.width / 2 - self.text_size[0] / 2
        if self.v_cent:
            draw_pos[1] = self.rect.height / 2 - self.text_size[1] / 2

        pg.draw.rect(
            self.image, self.color, self.image.get_rect(), border_radius=self.radius
        )
        self.image.blit(self.text, draw_pos)

    def set_flags(self, flags):
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.update_image()

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)



# Input Box
class InputBox(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, text, flags=2, **kwargs):
        """
        UI Element for user string input

        Render an input box in the window that allows user to select and input
        text.

        Parameters
        ----------
        x : int
            Leftmost x position in pixels.
        y : int
            Topmost y position in pixels.
        x_dim : int
            Width of the graphical input box in pixels.
        y_dim : int
            Height of the graphical input box in pixels.
        """
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)

        self.text_content = text
        self.text_color = kwargs.get("text_color", (255, 255, 255))
        self.color = kwargs.get("color", (128, 128, 128))
        self.active_color = kwargs.get("active_color", (192, 192, 192))
        self.padding = kwargs.get("padding", 5)
        self.radius = kwargs.get("radius", 3)
        self.text = self.font.render(text, True, self.text_color)
        self.text_size = self.text.get_size()

        self.active = False
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.clear_on_input = flags & 8 == 8
        self.clear_on_first_input = flags & 16 == 16
        self.clear = self.clear_on_first_input

    def input(self, INPUT):
        if INPUT.just_pressed(0, True):
            if self.rect.collidepoint(INPUT.mouse_pos):
                self.active = True
                # pg.key.start_text_input()
            else:
                self.active = False
                # pg.key.stop_text_input()
                if not self.clear:
                    self.clear = self.clear_on_input

        if INPUT._just_pressed and self.active:
            if self.clear:
                self.text_content = ""
                self.clear = False
            for keypress in INPUT._just_pressed:
                if keypress == pg.K_BACKSPACE:
                    self.text_content = self.text_content[:-1]
                elif keypress == pg.K_RETURN:
                    self.active = False
                else:
                    self.text_content += pg.key.name(keypress)
            self.update_text()

    def draw(self, surface, offset=None):
        if self.active:
            color = self.active_color
        else:
            color = self.color

        draw_pos = [self.padding, self.padding]
        if self.h_cent:
            draw_pos[0] = self.rect.width / 2 - self.text_size[0] / 2
        if self.v_cent:
            draw_pos[1] = self.rect.height / 2 - self.text_size[1] / 2

        pg.draw.rect(
            self.image, color, self.image.get_rect(), border_radius=self.radius
        )
        pg.draw.rect(
            self.image,
            self.color,
            self.image.get_rect(),
            width=3,
            border_radius=self.radius,
        )
        self.image.blit(self.text, draw_pos)
        surface.blit(self.image, self.rect)

    def set_text(self, text):
        self.text_content = text
        self.text = self.font.render(text, True, self.text_color)
        self.text_size = self.text.get_size()

    def get_text(self):
        text = self.text_content
        self.set_text("")
        return text

    def update_text(self):
        text = self.text_content
        self.text = self.font.render(text, True, self.text_color)
        self.text_size = self.text.get_size()

    def set_pos(self, v_centered, h_centered):
        self.v_cent = v_centered
        self.h_cent = h_centered

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)


# Multiline Text Box
class MultilineTextBox(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, text, flags=0, **kwargs):
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)

        self.text_color = kwargs.get("text_color", (255, 255, 255))
        self.color = kwargs.get("color", (128, 128, 128))
        self.padding = kwargs.get("padding", 5)
        self.radius = kwargs.get("radius", 0)
        self.text_content = text
        self.text = []
        self.text_height = self.font.get_height()
        for string in text:
            self.text.append(self.font.render(string, True, self.text_color))
        self.bottom_align = kwargs.get("bottom_align", False)
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2
        self.update_image()

    def set_flags(self, flags):
        self.h_cent = flags & 1 == 1
        self.v_cent = flags & 2 == 2

    def update_image(self):
        # Set the intial draw position
        if self.bottom_align:
            draw_pos = [
                self.padding,
                self.rect.height - self.padding - self.text_height,
            ]
        else:
            draw_pos = [self.padding, self.padding]

        # Draw the background of the text box
        pg.draw.rect(
            self.image, self.color, self.image.get_rect(), border_radius=self.radius
        )

        # Loop through the text and draw it onto the background
        if self.bottom_align:
            if self.v_cent:
                draw_pos[1] = (
                    self.rect.height / 2
                    + (
                        len(self.text_content) * (self.text_height + self.padding)
                        + self.padding
                    )
                    / 2
                )
            for text in self.text[::-1]:
                if self.h_cent:
                    draw_pos[0] = self.rect.width / 2 - text.get_width() / 2
                self.image.blit(text, draw_pos)
                draw_pos[1] -= self.text_height + self.padding
        else:
            if self.v_cent:
                draw_pos[1] = (
                    self.rect.height / 2
                    - (
                        len(self.text_content) * (self.text_height + self.padding)
                        + self.padding
                    )
                    / 2
                )
            for text in self.text:
                if self.h_cent:
                    draw_pos[0] = self.rect.width / 2 - text.get_width() / 2
                self.image.blit(text, draw_pos)
                draw_pos[1] += self.text_height + self.padding

    def draw(self, surface, offset=None):
        # Draw the image onto the given surface
        surface.blit(self.image, self.rect)

    def set_text(self, text):
        self.text_content = text
        self.text = []
        for string in text:
            self.text.append(self.font.render(string, True, self.text_color))

    def append_text(self, text):
        self.text_content.append(text)
        if (
            len(self.text_content) * (self.text_height + self.padding) + self.padding
            > self.rect.height
        ):
            self.text_content.pop(0)
        self.set_text(self.text_content)


# TODO Slider
class Slider(BaseUI):
    pass


# Progress Bar
class ProgressBar(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, value, max_value, **kwargs):
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)

        self.value = value
        self.max_value = max_value
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.color = kwargs.get("color", (100, 100, 200))
        self.line_color = kwargs.get("line_color", (50, 50, 50))
        self.radius = kwargs.get("radius", 0)
        self.line_width = kwargs.get("line_width", 3)
        self.update_image()

    def update_image(self):
        # Draw the background color
        pg.draw.rect(
            self.image, self.bg_color, self.image.get_rect(), border_radius=self.radius
        )
        # Draw the bar fill
        if self.value > 0:
            fill_height = self.image.get_height() - self.line_width * 2
            fill_width = map_range(
                self.value,
                0,
                self.max_value,
                0,
                self.image.get_width() - self.line_width * 2,
            )
            fill_rect = pg.Rect(
                self.line_width, self.line_width, fill_width, fill_height
            )
            pg.draw.rect(self.image, self.color, fill_rect)
        # Draw the border
        if self.line_width > 0:
            pg.draw.rect(
                self.image,
                self.line_color,
                self.image.get_rect(),
                self.line_width,
                border_radius=self.radius,
            )

    def update_value(self, value):
        self.value = value
        self.update_image()

    def update_max_value(self, max_value):
        self.max_value = max_value
        self.update_image()

    def draw(self, surface, offset=None):
        surface.blit(self.image, self.rect)


class ImageBox(BaseUI):
    def __init__(self, x, y, x_dim, y_dim, image, flags=3, **kwargs):
        BaseUI.__init__(self, x, y, x_dim, y_dim, **kwargs)

        self.contained_image = image
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.line_color = kwargs.get("line_color", (50, 50, 50))
        self.radius = kwargs.get("radius", 0)
        self.line_width = kwargs.get("line_width", 0)

        self.h_centered = flags & H_CENTERED
        self.v_centered = flags & V_CENTERED

        self.update_image()

    def update_image(self):
        # Draw the background color
        pg.draw.rect(
            self.image, self.bg_color, self.image.get_rect(), border_radius=self.radius
        )
        # Draw the border
        pg.draw.rect(
            self.image,
            self.line_color,
            self.image.get_rect(),
            self.line_width,
            border_radius=self.radius,
        )
        # Draw the image contained
        draw_pos = [self.radius, self.radius]
        if self.h_centered:
            draw_pos[0] = self.rect.width / 2 - self.contained_image.get_width() / 2
        if self.v_centered:
            draw_pos[1] = self.rect.height / 2 - self.contained_image.get_height() / 2
        self.image.blit(self.contained_image, draw_pos)

    def set_image(self, image):
        self.contained_image = image
        self.update_image()

    def draw(self, surface, offset):
        surface.blit(self.image, self.rect)
