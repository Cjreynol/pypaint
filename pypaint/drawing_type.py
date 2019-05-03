from enum import Enum, auto, unique


@unique
class DrawingType(Enum):
    
    PEN = auto()
    RECT = auto()
    OVAL = auto()
    LINE = auto()
    ERASER = auto()
    CLEAR = auto()
    PING = auto()
    TEXT = auto()
    UNDO = auto()
    SYNC = auto()

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

    @staticmethod
    def has_no_location(drawing_type):
        return drawing_type in {DrawingType.CLEAR, DrawingType.UNDO, 
                                DrawingType.SYNC}
