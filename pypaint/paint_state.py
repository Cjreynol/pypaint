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

        self.draw_active = True
        self.send_active = False
        self.dragging = False

    def clear_drawing_state(self):
        self.start_pos = None
        self.dragging = False

    def add_to_send_queue(self, data):
        if self.send_active:
            self.send_queue.put(data)

    @property
    def id_available(self):
        return not self.drawing_ids.is_empty

    def add_to_draw_queue(self, drawing):
        """
        Add the drawing to the queue to be drawn.

        Note:  Important to not include any logic to do with drawing history 
                here, the program is structured around processing all of that 
                logic when items come out of the draw queue to match up with 
                the user's visual knowledge.
        """
        self.draw_queue.put(drawing)

    def get_last_drawing_id(self):
        return self.drawing_ids.pop()

    def add_last_drawing_id(self, id_value):
        if id_value is not None:
            self.drawing_ids.push(id_value)

    def add_last_drawing(self, drawing):
        if drawing is not None:
            if drawing.shape is DrawingType.UNDO and self.drawing_history:
                self.drawing_history.pop()
            elif drawing.shape is DrawingType.CLEAR:
                self.clear_drawing_ids()
            elif drawing.shape not in {DrawingType.PING, DrawingType.SYNC}:
                self.drawing_history.append(drawing)

    def clear_drawing_ids(self):
        self.drawing_history = []
        self.drawing_ids.clear()

    def stop(self):
        self.draw_active = False
        self.send_active = False
        self.add_to_draw_queue(None)  # release drawing thread
