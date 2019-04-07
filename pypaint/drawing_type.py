from enum import Enum, auto


class DrawingType(Enum):
    
    PEN = auto()
    RECT = auto()
    OVAL = auto()
    LINE = auto()
    ERASER = auto()
    CLEAR = auto()
    PING = auto()
    TEXT = auto()

    def __str__(self):
        return self.name.capitalize()
