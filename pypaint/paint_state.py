from queue              import Queue

from chadlib.collection import Stack

from .drawing_type      import DrawingType


class PaintState:

    THICKNESS_MIN = 1
    THICKNESS_MAX = 10
    
    def __init__(self):
        self.current_type = DrawingType.PEN
        self.current_thickness = self.THICKNESS_MIN
        self.current_color = "#000000"      # default to black

        self.start_pos = None
        self.drawing_ids = Stack()
        self.drawing_history = []

        self.send_queue = Queue()
        self.receive_queue = Queue()
        self.draw_queue = Queue()

        self.active = True
        self.dragging = False

    def clear_drawing_state(self):
        self.start_pos = None
        self.dragging = False

    def add_to_send_queue(self, data):
        """
        TODO CJR: Should there be a conditional on this so that things are 
        not added to the queue on start up?
        """
        self.send_queue.put(data)

    @property
    def id_available(self):
        return not self.drawing_ids.is_empty

    def add_to_draw_queue(self, drawing):
        self.drawing_history.append(drawing)
        self.draw_queue.put(drawing)

    def get_last_drawing_id(self):
        return self.drawing_ids.pop()

    def add_last_drawing_id(self, value):
        self.drawing_ids.push(value)

    def clear_drawing_ids(self):
        self.drawing_history = []
        self.drawing_ids.clear()
