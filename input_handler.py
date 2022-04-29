"""Module that holds The input wrappers"""

import pygame
from pygame import Vector2

from pygame_engine.utils import key_from_value


class InputHandler:
    """Input Wrapper"""

    def __init__(self):
        self.mouse = Mouse()
        self.key = Keyboard()
        self.user_events = []

    def update(self):
        """Called every frame to update user input."""
        self.user_events = []
        self.mouse.update()
        self.key.update()

        for event in pygame.event.get(pygame.USEREVENT):
            self.user_events.append(event)

        for event in pygame.event.get():
            pass


class Mouse:
    """Wrapper for mouse inputs."""

    LEFT = 0
    RIGHT = 1
    MIDDLE = 2
    BUTTONS = [
        "left",
        "right",
        "middle",
    ]

    def __init__(self):
        self._just_pressed = [False] * 6
        self._pressed = [False] * 6
        self._just_released = [False] * 6
        self._pos = Vector2()
        self.rel = Vector2()

    def update(self):
        """Called every frame to update mouse inputs."""
        self._just_pressed = {}
        self._just_released = {}
        self._pos = Vector2(pygame.mouse.get_pos())
        self.rel = Vector2(pygame.mouse.get_rel())
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            button = event.button - 1
            if button < len(Mouse.BUTTONS):
                button = Mouse.BUTTONS[button]
            self._just_pressed[button] = True
        for event in pygame.event.get(pygame.MOUSEBUTTONUP):
            self._just_released[event.button - 1] = True
        self._pressed = pygame.mouse.get_pressed()

    def click(self, key):
        if isinstance(key, int):
            if key < len(Mouse.BUTTONS):
                key = Mouse.BUTTONS[key]
        return self._just_pressed.get(key, False)

    def release(self, key):
        if isinstance(key, int):
            if key < len(Mouse.BUTTONS):
                key = Mouse.BUTTONS[key]
        return self._just_released.get(key, False)

    def held(self, key):
        if isinstance(key, str):
            if key.lower() in Mouse.BUTTONS:
                key = Mouse.BUTTONS.index(key.lower())
            else:
                raise ValueError("Expected either a int between 0-2, or a valid string")
        if key < 0 or key > 2:
            raise ValueError("Expected either a int between 0-2, or a valid string")
        return self._pressed[key]

    @property
    def x(self):
        """Returns the x component of pos."""
        return self.pos.x

    @property
    def y(self):
        """Returns the y component of pos."""
        return self.pos.y

    @property
    def pos(self):
        return Vector2(self._pos)

    @pos.setter
    def pos(self, new_pos):
        self._pos = Vector2(new_pos)
        pygame.mouse.set_pos(new_pos)

    @property
    def dx(self):
        """Retruns the x compnent of rel."""
        return self.rel.x

    @property
    def dy(self):
        """Returns the y component of rel."""
        return self.rel.y


class Keyboard:
    """Wrapper for keyboard inputs."""

    def __init__(self):
        self._just_pressed = {}
        self._pressed = [False] * 200
        self._just_released = {}

    def update(self):
        """Called every frame to update keyboard inputs."""
        self._just_pressed = {}
        self._just_released = {}

        for event in pygame.event.get(pygame.KEYDOWN):
            key = Keyboard.KEYS.get(event.key, False)
            if key:
                self._just_pressed[key] = True
        for event in pygame.event.get(pygame.KEYUP):
            key = Keyboard.KEYS.get(event.key, False)
            if key:
                self._just_released[key] = True
        self._pressed = pygame.key.get_pressed()

    def press(self, key):
        if isinstance(key, int):
            if key in Keyboard.KEYS:
                key = Keyboard.KEYS[key]
        return self._just_pressed.get(key, False)

    def release(self, key):
        if isinstance(key, int):
            if key in Keyboard.KEYS:
                key = Keyboard.KEYS[key]
        return self._just_released.get(key, False)

    def held(self, key):
        if isinstance(key, str):
            key = key_from_value(Keyboard.KEYS, key)
            if key:
                return self._pressed[key]
            else:
                return False
        else:
            raise ValueError("Expected a valid string")

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
