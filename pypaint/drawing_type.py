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

    @staticmethod
    def is_draggable(drawing_type):
        return drawing_type in {DrawingType.RECT, DrawingType.OVAL, 
                                DrawingType.LINE}

    @staticmethod
    def is_motion_related(drawing_type):
        return drawing_type in {DrawingType.PEN, DrawingType.RECT, 
                                DrawingType.OVAL, DrawingType.LINE, 
                                DrawingType.ERASER} 
