

from typing import Union

numeric = Union[int, float]

class Position:
    __slots__ = 'x', 'y'
    def __init__(self, x: numeric, y: numeric) -> None:
        if not isinstance(x, numeric):
            raise ValueError(f"x-coordinates must be int or float, '{x}' was given")
        if not isinstance(y, numeric):
            raise ValueError(f"y-coordinates must be int or float, '{x}' was given")
        self.x = x
        self.y = y

class Cell:
    def __init__(self) -> None:
        pass