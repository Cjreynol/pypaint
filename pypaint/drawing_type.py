from enum import Enum


class DrawingType(Enum):
    
    PEN = 1
    RECT = 2
    OVAL = 3
    LINE = 4
    ERASER = 5
    CLEAR = 6
    PING = 7

    def __str__(self):
        lookup = {self.PEN : "Pen", self.RECT : "Rectangle", 
                    self.OVAL : "Oval", self.LINE : "Line", 
                    self.ERASER : "Eraser", self.CLEAR : "Clear",
                    self.PING : "Ping"}
        return lookup[self]
