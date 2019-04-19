from .drawing_type  import DrawingType


class PaintState:

    THICKNESS_MIN = 1
    THICKNESS_MAX = 10
    
    def __init__(self):
        """
        TODO CJR:  Add send/receive queues here
        """
        self.current_type = DrawingType.PEN
        self.current_thickness = self.THICKNESS_MIN

        self.start_pos = None
        self.last_drawing_id = None

    def clear_drawing_state(self):
        self.start_pos = None
        self.last_drawing_id = None
