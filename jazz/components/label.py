from .sprite import Sprite
from ..global_dict import Globals


class Label(Sprite):
    def __init__(self, name="label", **kwargs):
        super().__init__(name, **kwargs)
        self.font = kwargs.get("font", Globals.scene.get_font(size=24))
        self.text_color = kwargs.get("text_color", (255, 255, 255))

        self.text_content = kwargs.get("text", "")
        self.texture = self.font.render(
            self.text_content, True, self.text_color
        )

    def set_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        if self.text_content != text:
            self.text_content = text
            self.texture = self.font.render(text, True, self.text_color)

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)
