from enum import Enum


class DrawingType(Enum):
    
    PEN = 1
    RECT = 2
    OVAL = 3
    LINE = 4
    ERASER = 5
    CLEAR = 6
    PING = 7
    TEXT = 8

    def __str__(self):
        return self.name.capitalize()
