from jazz import Globals, Scene


class Test(Scene):
    def __init__(self):
        super().__init__()
        self._caption_timer = 0.5

    def on_load(self, data):
        self.update_title()
        Globals.app.set_next_scene(data.get("menu", self.name))

    def late_update(self, _):
        if Globals.key.press("space"):
            self.stop()

    def update_title(self):
        Globals.app.set_caption(f"{Globals.app.get_fps():2.2f} fps")
        self.create_timer(self._caption_timer, self.update_title, ())
