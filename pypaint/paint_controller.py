from pypaint.shape_type import ShapeType
from pypaint.paint_view import PaintView


class PaintController:
    """
    Manages the View, drawing history, and interface event handling.
    """

    BUTTON_PRESS = '4'
    BUTTON_RELEASE = '5'
    MOTION = '6'

    def __init__(self):
        self.view = self._create_view()
        self.history = []

        self.start_pos = None
        self.current_mode = ShapeType.RECT

    def _create_view(self):
        """
        Return a view with the necessary callbacks registered.
        """
        view = PaintView()
        view.initialize()

        for event_type in ["<Button-1>", "<ButtonRelease-1>", "<B1-Motion>"]:
            view.bind_canvas_callback(event_type, self.handle_event)
        view.bind_toggle_callback(self.toggle)
        return view

    def start(self):
        self.view.start()

    def toggle(self):
        """
        Change the current drawing mode.
        """
        if self.current_mode == ShapeType.RECT:
            self.current_mode = ShapeType.LINE
        elif self.current_mode == ShapeType.LINE:
            self.current_mode = ShapeType.RECT
        else:
            raise RuntimeError("Unexpected shape type {}".format(self.current_mode))

    def handle_event(self, event):
        """
        Call the appropriate event handler based on the current drawing mode.
        """
        if self.current_mode == ShapeType.RECT:
            self._handle_event_rect(event)
        elif self.current_mode == ShapeType.LINE:
            self._handle_event_line(event)
        else:
            raise RuntimeError("Unexpected shape type {}".format(self.current_mode))

    def _handle_event_rect(self, event):
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            self._add_to_history(ShapeType.RECT, 
                                    self.start_pos + event_coord)
            self.start_pos = None
            self.view.clear_draw_history(self.history)
        elif event.type == self.MOTION:
            self.view.clear_draw_history(self.history)
            self.view.draw_rect(self.start_pos + event_coord)
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))

    def _handle_event_line(self, event):
        event_coord = event.x, event.y
        if event.type == self.BUTTON_PRESS:
            self.start_pos = event_coord
        elif event.type == self.BUTTON_RELEASE:
            pass
        elif event.type == self.MOTION:
            coords = self.start_pos + event_coord
            self._add_to_history(ShapeType.LINE, coords)
            self.view.draw_line(coords)
            self.start_pos = event_coord
        else:
            raise RuntimeError("Unexpected event type {}".format(event.type))

    def _add_to_history(self, shape_type, coords):
        self.history.append((shape_type, coords))
