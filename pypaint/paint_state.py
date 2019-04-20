from queue      import Queue

from .drawing_type  import DrawingType


class PaintState:

    THICKNESS_MIN = 1
    THICKNESS_MAX = 10
    
    def __init__(self):
        self.current_type = DrawingType.PEN
        self.current_thickness = self.THICKNESS_MIN

        self.start_pos = None
        self.last_drawing_id = None

        self.send_queue = Queue()
        self.receive_queue = Queue()
        self.draw_queue = Queue()

        self.active = True

    def clear_drawing_state(self):
        self.start_pos = None
        self.last_drawing_id = None

    def add_to_send_queue(self, data):
        """
        TODO CJR: Should there be a conditional on this so that things are 
        not added to the queue on start up?
        """
        self.send_queue.put(data)
