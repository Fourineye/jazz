from .engine import Application, Scene, InputHandler, Keyboard, Mouse, SoundManager
from .utils import Surface


class Globals:
    app: Application | None = None
    scene: Scene | None = None
    input: InputHandler | None = None
    key: Keyboard | None = None
    mouse: Mouse | None = None
    display: Surface | None = None
    sound: SoundManager | None = None


SETTINGS = {"master_volume": 1.0, "music_volume": 1.0, "sound_volume": 1.0}
