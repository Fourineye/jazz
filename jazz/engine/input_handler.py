"""Module that holds The input wrappers"""

from typing import Callable, Any
import pygame

from ..global_dict import Globals
from ..utils import Vec2, key_from_value


class InputHandler:
    """Dispatches pygame input events to Keyboard and Mouse helper classes."""

    def __init__(self) -> None:
        """Initializes the InputHandler wrapping Keyboard and Mouse sub-handlers."""
        self.mouse = Mouse()
        self.key = Keyboard()
        self.user_events = []
        self.event_handler = None

    def set_event_handler(self, method: Callable[[pygame.event.Event], None]) -> None:
        """Registers a custom callback function for processing raw Pygame events.

        Args:
            method (callable): The callback function that takes a Pygame Event as argument.
        """
        if callable(method):
            self.event_handler = method


    def update(self) -> None:
        """Called every frame to update user input."""
        self.user_events = []
        self.mouse.update()
        self.key.update()
        

        for event in pygame.event.get(pygame.USEREVENT):
            self.user_events.append(event)

        for event in pygame.event.get():
            if self.event_handler is not None:
                self.event_handler(event)


class Mouse:
    """Wrapper for mouse inputs."""

    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
    BUTTONS = [
        "left",
        "middle",
        "right",
    ]

    def __init__(self) -> None:
        """Initializes the Mouse input tracker with empty states and positions."""
        self._just_pressed = {}
        self._pressed = [False] * 6
        self._just_released = {}
        self._pos = Vec2()
        self._world_offset = Vec2()
        self.rel = Vec2()

    def update(self) -> None:
        """Called every frame to update mouse inputs."""
        self._just_pressed = {}
        self._just_released = {}
        self._pos = Vec2(pygame.mouse.get_pos())
        self.rel = Vec2(pygame.mouse.get_rel())
        if Globals.scene is not None:
            self._world_offset = Globals.scene.camera_offset
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            button = event.button - 1
            if button < len(Mouse.BUTTONS):
                button = Mouse.BUTTONS[button]
            self._just_pressed[button] = True
        for event in pygame.event.get(pygame.MOUSEBUTTONUP):
            button = event.button - 1
            if button < len(Mouse.BUTTONS):
                button = Mouse.BUTTONS[button]
            self._just_released[button] = True
        self._pressed = pygame.mouse.get_pressed()

    def click(self, key: str | int, consume: bool = False) -> bool:
        """Checks if a mouse button was clicked (pressed down) in the current frame.

        Args:
            key (str | int): Button name ("left", "middle", "right") or index (0-2).
            consume (bool, optional): If True, marks the click event as consumed/handled. Defaults to False.

        Returns:
            bool: True if clicked, otherwise False.
        """
        if isinstance(key, int):
            if key < len(Mouse.BUTTONS):
                key = Mouse.BUTTONS[key]
        click = self._just_pressed.get(key, False)
        if click and consume:
            self._just_pressed[key] = False
        return click

    def release(self, key: str | int) -> bool:
        """Checks if a mouse button was released in the current frame.

        Args:
            key (str | int): Button name ("left", "middle", "right") or index (0-2).

        Returns:
            bool: True if released, otherwise False.
        """
        if isinstance(key, int):
            if key < len(Mouse.BUTTONS):
                key = Mouse.BUTTONS[key]
        return self._just_released.get(key, False)

    def held(self, key: str | int) -> bool:
        """Checks if a mouse button is currently being held down.

        Args:
            key (str | int): Button name ("left", "middle", "right") or index (0-2).

        Raises:
            ValueError: If input is invalid.

        Returns:
            bool: True if held, otherwise False.
        """
        if isinstance(key, str):
            if key.lower() in Mouse.BUTTONS:
                key = Mouse.BUTTONS.index(key.lower())
            else:
                raise ValueError("Expected either a int between 0-2, or a valid string")
        if key < 0 or key > 2:
            raise ValueError("Expected either a int between 0-2, or a valid string")
        return self._pressed[key]

    @property
    def x(self) -> float:
        """Returns the x component of pos."""
        return self.pos.x

    @property
    def y(self) -> float:
        """Returns the y component of pos."""
        return self.pos.y

    @property
    def pos(self) -> Vec2:
        """Vec2: Gets the mouse coordinate in screen space."""
        return Vec2(self._pos)

    @pos.setter
    def pos(self, new_pos: Vec2 | tuple[float, float]) -> None:
        """Sets the mouse coordinate in screen space.

        Args:
            new_pos (Vec2 | tuple): The new coordinate to warp the mouse cursor to.
        """
        self._pos = Vec2(new_pos)
        pygame.mouse.set_pos(new_pos)

    @property
    def global_pos(self) -> Vec2:
        """Vec2: Gets the mouse coordinate in global world space (compensating for camera offset)."""
        return self.pos - self._world_offset

    @property
    def dx(self) -> float:
        """Retruns the x compnent of rel."""
        return self.rel.x

    @property
    def dy(self) -> float:
        """Returns the y component of rel."""
        return self.rel.y


class Keyboard:
    """Wrapper for keyboard inputs."""

    ALLOWED_TEXT_INPUT_KEYS = {
        "backspace",
        "enter",
        "num enter",
        "escape",
        "tab",
        "left",
        "right",
        "up",
        "down",
        "del",
    }

    def __init__(self) -> None:
        """Initializes the Keyboard input tracker."""
        self._just_pressed = {}
        self._pressed = [False] * 200
        self._just_released = {}
        self._mods = 0
        self.text = ""
        self._text_input = False

    def start_text_input(self) -> None:
        """Enables system text input mode for receiving unicode character entries."""
        pygame.key.start_text_input()
        self._text_input = True

    def stop_text_input(self) -> None:
        """Disables system text input mode."""
        pygame.key.stop_text_input()
        self._text_input = False

    def update(self) -> None:
        """Called every frame to update keyboard inputs."""
        self._just_pressed = {}
        self._just_released = {}
        self.text = ""

        for event in pygame.event.get(pygame.TEXTINPUT):
            self.text = event.text

        for event in pygame.event.get(pygame.KEYDOWN):
            key = Keyboard.KEYS.get(event.key, False)
            if key:
                self._just_pressed[key] = True
        for event in pygame.event.get(pygame.KEYUP):
            key = Keyboard.KEYS.get(event.key, False)
            if key:
                self._just_released[key] = True
        self._pressed = pygame.key.get_pressed()
        self._mods = pygame.key.get_mods()

    def press(self, key: str | int) -> bool:
        """Checks if a key was pressed down in the current frame.

        Args:
            key (str | int): Key name string or pygame key code.

        Returns:
            bool: True if pressed, otherwise False.
        """
        if isinstance(key, int):
            if key in Keyboard.KEYS:
                key = Keyboard.KEYS[key]
        if not self._text_input or key in self.ALLOWED_TEXT_INPUT_KEYS:
            return self._just_pressed.get(key, False)
        return False

    def mod(self, key: str) -> bool:
        """Checks if a modifier key (shift, control, alt, meta) is currently active.

        Args:
            key (str): Modifier name.

        Returns:
            bool: True if active, otherwise False.
        """
        if self._mods & self.MODS.get(key, 0):
            return True
        return False

    def release(self, key: str | int) -> bool:
        """Checks if a key was released in the current frame.

        Args:
            key (str | int): Key name string or pygame key code.

        Returns:
            bool: True if released, otherwise False.
        """
        if isinstance(key, int):
            if key in Keyboard.KEYS:
                key = Keyboard.KEYS[key]
        if not self._text_input or key in self.ALLOWED_TEXT_INPUT_KEYS:
            return self._just_released.get(key, False)
        return False

    def held(self, key: str) -> bool:
        """Checks if a key is currently being held down.

        Args:
            key (str): Key name string.

        Raises:
            ValueError: If input is not a string.

        Returns:
            bool: True if held, otherwise False.
        """
        if isinstance(key, str):
            key_code = key_from_value(Keyboard.KEYS, key)
            if key_code:
                if not self._text_input or key in self.ALLOWED_TEXT_INPUT_KEYS:
                    return self._pressed[key_code]
                return False
            else:
                return False
        else:
            raise ValueError("Expected a valid string")

    MODS = {
        "shift": pygame.KMOD_SHIFT,
        "control": pygame.KMOD_CTRL,
        "alt": pygame.KMOD_ALT,
        "meta": pygame.KMOD_META,
    }

    KEYS = {
        pygame.K_BACKSPACE: "backspace",
        pygame.K_TAB: "tab",
        pygame.K_CLEAR: "clear",
        pygame.K_RETURN: "enter",
        pygame.K_PAUSE: "pause",
        pygame.K_ESCAPE: "escape",
        pygame.K_SPACE: "space",
        pygame.K_EXCLAIM: "exclaim",
        pygame.K_QUOTEDBL: '"',
        pygame.K_HASH: "#",
        pygame.K_DOLLAR: "$",
        pygame.K_AMPERSAND: "&",
        pygame.K_QUOTE: "'",
        pygame.K_LEFTPAREN: "(",
        pygame.K_RIGHTPAREN: ")",
        pygame.K_ASTERISK: "*",
        pygame.K_PLUS: "+",
        pygame.K_COMMA: ",",
        pygame.K_MINUS: "-",
        pygame.K_PERIOD: ".",
        pygame.K_SLASH: "/",
        pygame.K_0: "0",
        pygame.K_1: "1",
        pygame.K_2: "2",
        pygame.K_3: "3",
        pygame.K_4: "4",
        pygame.K_5: "5",
        pygame.K_6: "6",
        pygame.K_7: "7",
        pygame.K_8: "8",
        pygame.K_9: "9",
        pygame.K_COLON: ":",
        pygame.K_SEMICOLON: ";",
        pygame.K_LESS: "<",
        pygame.K_EQUALS: "=",
        pygame.K_GREATER: ">",
        pygame.K_QUESTION: "?",
        pygame.K_AT: "@",
        pygame.K_LEFTBRACKET: "[",
        pygame.K_BACKSLASH: "\\",
        pygame.K_RIGHTBRACKET: "]",
        pygame.K_CARET: "^",
        pygame.K_UNDERSCORE: "_",
        pygame.K_BACKQUOTE: "`",
        pygame.K_a: "a",
        pygame.K_b: "b",
        pygame.K_c: "c",
        pygame.K_d: "d",
        pygame.K_e: "e",
        pygame.K_f: "f",
        pygame.K_g: "g",
        pygame.K_h: "h",
        pygame.K_i: "i",
        pygame.K_j: "j",
        pygame.K_k: "k",
        pygame.K_l: "l",
        pygame.K_m: "m",
        pygame.K_n: "n",
        pygame.K_o: "o",
        pygame.K_p: "p",
        pygame.K_q: "q",
        pygame.K_r: "r",
        pygame.K_s: "s",
        pygame.K_t: "t",
        pygame.K_u: "u",
        pygame.K_v: "v",
        pygame.K_w: "w",
        pygame.K_x: "x",
        pygame.K_y: "y",
        pygame.K_z: "z",
        pygame.K_DELETE: "del",
        pygame.K_KP0: "num 0",
        pygame.K_KP1: "num 1",
        pygame.K_KP2: "num 2",
        pygame.K_KP3: "num 3",
        pygame.K_KP4: "num 4",
        pygame.K_KP5: "num 5",
        pygame.K_KP6: "num 6",
        pygame.K_KP7: "num 7",
        pygame.K_KP8: "num 8",
        pygame.K_KP9: "num 9",
        pygame.K_KP_PERIOD: "num period",
        pygame.K_KP_DIVIDE: "num divide",
        pygame.K_KP_MULTIPLY: "num multiply",
        pygame.K_KP_MINUS: "num minus",
        pygame.K_KP_PLUS: "num plus",
        pygame.K_KP_ENTER: "num enter",
        pygame.K_KP_EQUALS: "num equals",
        pygame.K_UP: "up",
        pygame.K_DOWN: "down",
        pygame.K_RIGHT: "right",
        pygame.K_LEFT: "left",
        pygame.K_INSERT: "insert",
        pygame.K_HOME: "home",
        pygame.K_END: "end",
        pygame.K_PAGEUP: "page up",
        pygame.K_PAGEDOWN: "page down",
        pygame.K_F1: "F1",
        pygame.K_F2: "F2",
        pygame.K_F3: "F3",
        pygame.K_F4: "F4",
        pygame.K_F5: "F5",
        pygame.K_F6: "F6",
        pygame.K_F7: "F7",
        pygame.K_F8: "F8",
        pygame.K_F9: "F9",
        pygame.K_F10: "F10",
        pygame.K_F11: "F11",
        pygame.K_F12: "F12",
        pygame.K_F13: "F13",
        pygame.K_F14: "F14",
        pygame.K_F15: "F15",
        pygame.K_NUMLOCK: "numlock",
        pygame.K_CAPSLOCK: "capslock",
        pygame.K_SCROLLOCK: "scrollock",
        pygame.K_RSHIFT: "right shift",
        pygame.K_LSHIFT: "left shift",
        pygame.K_RCTRL: "right control",
        pygame.K_LCTRL: "left control",
        pygame.K_RALT: "right alt",
        pygame.K_LALT: "left alt",
        pygame.K_RMETA: "right meta",
        pygame.K_LMETA: "left meta",
        pygame.K_LSUPER: "left win",
        pygame.K_RSUPER: "right win",
        pygame.K_MODE: "mode shift",
        pygame.K_HELP: "help",
        pygame.K_PRINT: "print screen",
        pygame.K_SYSREQ: "sysrq",
        pygame.K_BREAK: "break",
        pygame.K_MENU: "menu",
        pygame.K_POWER: "power",
        pygame.K_EURO: "euro",
    }
