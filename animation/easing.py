def LINEAR(t):
    return t


def EASE_IN_QUADRATIC(t):
    return t**2


def EASE_OUT_QUADRATIC(t):
    return 1 - (1 - t) ** 2


def EASE_IN_OUT_QUADRATIC(t):
    return 2 * t**2 if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def EASE_IN_CUBIC(t):
    return t**3


def EASE_OUT_CUBIC(t):
    return 1 - (1 - t) ** 2


def EASE_IN_OUT_CUBIC(t):
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def EASE_IN_QUARTIC(t):
    return t**4


def EASE_OUT_QUARTIC(t):
    return 1 - (1 - t) ** 4


def EASE_IN_OUT_QUARTIC(t):
    return 8 * t**4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2


def EASE_IN_QUINTIC(t):
    return t**5


def EASE_OUT_QUINTIC(t):
    return 1 - (1 - t) ** 5


def EASE_IN_OUT_QUINTIC(t):
    return 16 * t**5 if t < 0.5 else 1 - (-2 * t + 2) ** 5 / 2


def EASE_IN_EXPO(t):
    return 0 if t == 0 else 2 ** (10 * t - 10)


def EASE_OUT_EXPO(t):
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def EASE_IN_OUT_EXPO(t):
    return (
        0
        if t == 0
        else 1
        if t == 1
        else 2 ** (20 * t - 10) / 2
        if t < 0.5
        else (2 - 2 ** (-20 * t + 10)) / 2
    )


def EASE_IN_BACK(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t**3 - c1 * t**2


def EASE_OUT_BACK(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def EASE_IN_OUT_BACK(t):
    c1 = 1.70158
    c2 = c1 * 1.525
    in_ = ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    out_ = ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    return (
        in_ if t < 0.5 else out_
    )  # (Math.pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2


EASINGS = [
    LINEAR,
    EASE_IN_QUADRATIC,
    EASE_OUT_QUADRATIC,
    EASE_IN_OUT_QUADRATIC,
    EASE_IN_CUBIC,
    EASE_OUT_CUBIC,
    EASE_IN_OUT_CUBIC,
    EASE_IN_QUARTIC,
    EASE_OUT_QUARTIC,
    EASE_IN_OUT_QUARTIC,
    EASE_IN_QUINTIC,
    EASE_OUT_QUINTIC,
    EASE_IN_OUT_QUINTIC,
    EASE_IN_EXPO,
    EASE_OUT_EXPO,
    EASE_IN_OUT_EXPO,
    EASE_IN_BACK,
    EASE_OUT_BACK,
    EASE_IN_OUT_BACK,
]
